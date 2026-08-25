#!/usr/bin/env python3
"""URE obligation sub-machine tick (SPEC-NMUST-01 §4 executable recursion).

Obligation closure machine: every obligation o walks the N-MUST lattice
  raised -> fixed -> implemented -> tested -> verified -> legislated
                                                        | wontfix (L3-sealed)
and every transition must carry evidence (N10); evidence is hash-anchored
on the chain (N11). This script is the sweeper-side executable.

Dual-queue upgrade (SPEC fix: strict single FIFO was blocked by the
human-domain obligation head -- that blocking is a design defect; defect
is residue; residue drives repair):

  * Machine queue (domain=machine): strict FIFO over the oldest non-closed
    machine obligation, at most ONE clearing per round (n9 rolling cadence)
    -- the original logic, unchanged in spirit.
  * Human queue (domain=human): NEVER blocks the machine queue. Human
    obligations are swept independently through an age-based escalation
    ladder:
        L0  age <=  24h : suspended (honest wait, log only)
        L1  age >   24h : on-chain heartbeat reminder
                          (RPT.OBLIG note=escalate-L1)
        L2  age >   72h : comment reminder to root on vci-inbox issue#1
                          (+ RPT.OBLIG note=escalate-L2 bookkeeping)
        L3  age >  168h : mark critical escalation
                          (RPT.OBLIG note=escalate-L3, once)
    Idempotence: at most one L1/L2 reminder per obligation per UTC day
    (throttled via chain entries). The moment closing evidence lands in
    the ledger, a human obligation fast-tracks to `legislated`.

  1. Build obligation set O from three sources:
       - ure/obligations.jsonl            (ledger, one obligation per line)
       - ure/chain.jsonl entries with intent in {INCIDENT, WARN, FINDING}
       - kit/INDEX.md F-table (chepin-ai/vci-library, cross-repo read-only GET)
     Newly discovered source items are appended to the ledger as `raised`
     with domain=machine (machine-observable sources).
  2. For each o, check evidence progress: a later chain entry whose payload
     references o.id (intent=RPT.OBLIG transition record or an `evidence`
     field) counts as an anchor; the ledger state is the source of truth.
  3. Machine queue: pick the oldest non-closed machine o* (FIFO by
     `opened`; wontfix excluded). At most ONE clearing per round: report +
     verify evidence existence (commit shas resolvable in local checkout).
  4. Human queue: ladder sweep as above, independent of the machine pick.
  5. Append chain entries intent=RPT.OBLIG {oid, from, to, note, queue}
     (v2 hash chaining, hash = sha256(prev + canon), same as pareto_tick).
     `queue` in {machine, human} records which queue emitted the entry.
     Open obligations never block the Whittle arm (soft priority: the
     obligation arm runs first and leaves a bookkeeping entry).
  6. All closed -> print "clean" and idle (I8 explicit halt state).

Secrets only via env/Authorization headers; logs carry zero secrets and
zero personal identifiers.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

CHAIN = "ure/chain.jsonl"
LEDGER = "ure/obligations.jsonl"
KIT_INDEX_URL = os.environ.get(
    "OBLIG_KIT_INDEX_URL",
    "https://raw.githubusercontent.com/chepin-ai/vci-library/main/kit/INDEX.md")
VCI_INBOX_ISSUE_URL = os.environ.get(
    "OBLIG_VCI_INBOX_ISSUE_URL",
    "https://api.github.com/repos/chepin-ai/vci-inbox/issues/1/comments")
TOKEN = os.environ.get("URE_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""

SOURCE_INTENTS = {"INCIDENT", "WARN", "FINDING"}
LATTICE = ["raised", "fixed", "implemented", "tested", "verified", "legislated"]
TERMINAL = {"legislated", "wontfix"}
DOMAINS = {"machine", "human"}
HEXSHA = re.compile(r"\b[0-9a-f]{7,40}\b")

# Human-domain escalation ladder thresholds (hours).
L1_AGE_H = 24
L2_AGE_H = 72
L3_AGE_H = 168


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def chain_tail():
    """Return (last_seq, last_hash, all_entries); v2 header comment tolerated."""
    entries = []
    if os.path.exists(CHAIN):
        with open(CHAIN) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entries.append(json.loads(line))
    if not entries:
        return 0, "0" * 64, entries
    return entries[-1].get("seq", 0), entries[-1].get("hash", "0" * 64), entries


def append_chain_rpt(oid, from_state, to_state, note, ts, queue):
    """Append intent=RPT.OBLIG entry with v2 hash chaining and queue tag."""
    prev_seq, prev_hash, _ = chain_tail()
    entry = {"seq": prev_seq + 1, "ts": ts, "intent": "RPT.OBLIG",
             "oid": oid, "from": from_state, "to": to_state, "note": note,
             "queue": queue, "prev": prev_hash}
    entry["hash"] = hashlib.sha256((prev_hash + canon(entry)).encode()).hexdigest()
    with open(CHAIN, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load_ledger():
    obligations = []
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                obligations.append(json.loads(line))
    return obligations


def save_ledger(obligations):
    header = ""
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            for line in f:
                if line.startswith("#"):
                    header += line
                else:
                    break
    with open(LEDGER, "w") as f:
        if header:
            f.write(header)
        for o in obligations:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")


def domain_of(o):
    """Ledger schema v2: domain in {machine,human}; legacy rows default machine."""
    d = o.get("domain", "machine")
    return d if d in DOMAINS else "machine"


def age_hours(o, now_dt):
    """Age of an obligation in hours since `opened` (UTC ISO ts)."""
    opened = o.get("opened", "")
    try:
        t0 = datetime.strptime(opened, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return 0.0
    return max(0.0, (now_dt - t0).total_seconds() / 3600.0)


# ---------------------------------------------------------------------------
# Obligation discovery (delta-base generator: obs -> O_new)
# ---------------------------------------------------------------------------

def discover_from_chain(entries, known_ids):
    """Chain entries with intent in {INCIDENT, WARN, FINDING} -> obligations."""
    new = []
    for e in entries:
        intent = e.get("intent")
        if intent not in SOURCE_INTENTS:
            continue
        oid = f"o-chain-seq{e.get('seq', '?')}"
        if oid in known_ids:
            continue
        new.append({"id": oid,
                    "src": f"chain seq{e.get('seq')} {intent} entry",
                    "state": "raised", "evidence": [],
                    "domain": "machine",
                    "opened": e.get("ts", utcnow())})
    return new


def discover_from_kit(known_ids, offline=False):
    """kit/INDEX.md F-table (vci-library, cross-repo read-only GET)."""
    if offline:
        return new_from_kit_text("", known_ids, skipped="offline")
    try:
        req = urllib.request.Request(KIT_INDEX_URL)
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode()
    except Exception as exc:  # noqa: BLE001 - discovery must never crash tick
        print(f"::warning::kit INDEX fetch failed ({type(exc).__name__}); "
              "F-table scan skipped this round")
        return []
    return new_from_kit_text(text, known_ids)


def new_from_kit_text(text, known_ids, skipped=None):
    new = []
    if skipped:
        return new
    for m in re.finditer(r"告诫\s*F(\d+)[：:]([^\n]+)", text):
        fid = f"F{m.group(1)}"
        oid = f"o-kit-{fid}"
        if oid in known_ids:
            continue
        summary = re.sub(r"\s+", " ", m.group(2)).strip()[:120]
        new.append({"id": oid,
                    "src": f"kit/INDEX.md {fid} admonition: {summary}",
                    "state": "raised", "evidence": [],
                    "domain": "machine", "opened": utcnow()})
    return new


# ---------------------------------------------------------------------------
# Evidence progress check (N10/N11)
# ---------------------------------------------------------------------------

def chain_anchors(oid, entries):
    """Later chain entries referencing o.id (RPT.OBLIG or evidence field)."""
    refs = []
    for e in entries:
        if oid in json.dumps(e, ensure_ascii=False):
            refs.append(e.get("seq"))
    return refs


def verify_evidence_existence(o):
    """Do what this run can do: resolve commit-sha-like evidence tokens
    against the local checkout (informational; never fatal)."""
    resolvable, unresolvable = 0, 0
    for ev in o.get("evidence", []):
        for sha in HEXSHA.findall(ev):
            r = subprocess.run(["git", "cat-file", "-t", sha],
                               capture_output=True)
            if r.returncode == 0:
                resolvable += 1
            else:
                unresolvable += 1
    return resolvable, unresolvable


def pick_oldest_open(obligations, domain="machine"):
    """FIFO: oldest non-terminal obligation of one queue; wontfix excluded."""
    open_os = [o for o in obligations
               if o.get("state") not in TERMINAL and domain_of(o) == domain]
    if not open_os:
        return None
    return min(open_os, key=lambda o: (o.get("opened", ""), o.get("id", "")))


# ---------------------------------------------------------------------------
# Human-domain escalation ladder (independent of the machine FIFO queue)
# ---------------------------------------------------------------------------

def reminded_today(oid, level, entries, today):
    """Idempotence: at most one L1/L2 reminder per obligation per UTC day,
    throttled via this day's RPT.OBLIG chain entries (note=escalate-L*)."""
    marker = f"note=escalate-{level}"
    for e in entries:
        if e.get("intent") != "RPT.OBLIG" or e.get("oid") != oid:
            continue
        if not str(e.get("ts", "")).startswith(today):
            continue
        if marker in str(e.get("note", "")):
            return True
    return False


def remind_root_issue_comment(o, age_h, offline=False):
    """L2: post a reminder comment to vci-inbox issue#1 for root action.
    Offline mode simulates the comment (no network write) so the ladder
    remains testable; failures warn but never crash the tick."""
    body = (f"[URE oblig escalator] human-domain obligation `{o['id']}` "
            f"open for {age_h:.1f}h (> {L2_AGE_H}h, ladder L2). "
            f"src: {o.get('src', '')[:200]} -- root action requested. "
            "Closing evidence in ure/obligations.jsonl fast-tracks it to "
            "legislated. (automated reminder; at most one per day)")
    if offline:
        print(f"[offline] L2 comment to vci-inbox issue#1 simulated for "
              f"{o['id']} (age {age_h:.1f}h)")
        return True
    if not TOKEN:
        print("::warning::L2 reminder skipped: no URE_TOKEN/GITHUB_TOKEN "
              "available for vci-inbox comment")
        return False
    try:
        req = urllib.request.Request(
            VCI_INBOX_ISSUE_URL, method="POST",
            data=json.dumps({"body": body}).encode(),
            headers={"Authorization": f"Bearer {TOKEN}",
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return 200 <= r.status < 300
    except Exception as exc:  # noqa: BLE001 - reminder must never crash tick
        print(f"::warning::L2 vci-inbox comment failed "
              f"({type(exc).__name__}); will retry next round")
        return False


def human_ladder_sweep(obligations, entries, ts, now_dt, offline=False):
    """Sweep open human-domain obligations through the age ladder.
    Returns count of chain entries emitted. Never touches the machine queue."""
    emitted = 0
    today = ts[:10]
    for o in obligations:
        if domain_of(o) != "human" or o.get("state") in TERMINAL:
            continue
        age_h = age_hours(o, now_dt)

        # Closure evidence arrived -> fast-track to legislated (N10/N11).
        if o.get("evidence"):
            from_state = o.get("state", "raised")
            o["state"] = "legislated"
            o.pop("escalation", None)
            note = ("human-domain closure evidence received "
                    f"({len(o['evidence'])} item(s)); fast-track "
                    f"{from_state} -> legislated (ladder exit)")
            entry = append_chain_rpt(o["id"], from_state, "legislated",
                                     note, ts, queue="human")
            print(f"RPT.OBLIG seq={entry['seq']}: {o['id']} "
                  f"{from_state} -> legislated (human closure, "
                  f"age {age_h:.1f}h)")
            emitted += 1
            continue

        if age_h > L3_AGE_H:
            # L3 critical escalation: mark once, idempotent via ledger field.
            if o.get("escalation") == "critical":
                print(f"human oblig {o['id']}: age {age_h:.1f}h, L3 "
                      "critical already marked; no duplicate entry")
                continue
            o["escalation"] = "critical"
            note = (f"note=escalate-L3 human-domain critical escalation: "
                    f"age {age_h:.1f}h > {L3_AGE_H}h; ledger marked "
                    "escalation=critical; root action overdue")
            entry = append_chain_rpt(o["id"], o.get("state", "raised"),
                                     o.get("state", "raised"), note, ts,
                                     queue="human")
            print(f"RPT.OBLIG seq={entry['seq']}: {o['id']} escalate-L3 "
                  f"(age {age_h:.1f}h, critical)")
            emitted += 1
        elif age_h > L2_AGE_H:
            # L2: comment reminder to root on vci-inbox issue#1 (<=1/day).
            if reminded_today(o["id"], "L2", entries, today):
                print(f"human oblig {o['id']}: age {age_h:.1f}h, L2 "
                      "reminder already sent today; idempotent skip")
                continue
            if remind_root_issue_comment(o, age_h, offline=offline):
                note = (f"note=escalate-L2 human-domain root reminder "
                        f"posted to vci-inbox issue#1: age {age_h:.1f}h "
                        f"> {L2_AGE_H}h")
                entry = append_chain_rpt(o["id"], o.get("state", "raised"),
                                         o.get("state", "raised"), note, ts,
                                         queue="human")
                print(f"RPT.OBLIG seq={entry['seq']}: {o['id']} "
                      f"escalate-L2 (age {age_h:.1f}h)")
                emitted += 1
        elif age_h > L1_AGE_H:
            # L1: on-chain heartbeat reminder (<=1/day).
            if reminded_today(o["id"], "L1", entries, today):
                print(f"human oblig {o['id']}: age {age_h:.1f}h, L1 "
                      "reminder already sent today; idempotent skip")
                continue
            note = (f"note=escalate-L1 human-domain heartbeat reminder: "
                    f"age {age_h:.1f}h > {L1_AGE_H}h; awaiting root action")
            entry = append_chain_rpt(o["id"], o.get("state", "raised"),
                                     o.get("state", "raised"), note, ts,
                                     queue="human")
            print(f"RPT.OBLIG seq={entry['seq']}: {o['id']} escalate-L1 "
                  f"(age {age_h:.1f}h)")
            emitted += 1
        else:
            print(f"human oblig {o['id']}: age {age_h:.1f}h <= {L1_AGE_H}h, "
                  "L0 suspended (honest wait; machine queue unaffected)")
    return emitted


def oblig_tick(offline=False):
    ts = utcnow()
    now_dt = datetime.now(timezone.utc)
    prev_seq, _, entries = chain_tail()
    obligations = load_ledger()
    known = {o["id"] for o in obligations}

    # --- obligation generation (Gen): chain intents + kit F-table ----------
    new = discover_from_chain(entries, known)
    new += discover_from_kit(known | {o["id"] for o in new}, offline=offline)
    for o in new:
        obligations.append(o)
        known.add(o["id"])
        print(f"obligation raised: {o['id']} <- {o['src'][:100]}")

    # --- per-obligation status report (evidence progress check) ------------
    for o in obligations:
        anchors = chain_anchors(o["id"], entries)
        o["anchors"] = anchors  # runtime only, not persisted
        print(f"oblig {o['id']}: domain={domain_of(o)} state={o['state']} "
              f"evidence={len(o.get('evidence', []))} anchors={anchors}")

    # --- human queue: independent escalation-ladder sweep -------------------
    # Runs regardless of machine-queue state; a human head NEVER blocks the
    # machine FIFO (design-defect repair).
    n_human = human_ladder_sweep(obligations, entries, ts, now_dt,
                                 offline=offline)
    if n_human:
        # re-read tail so the machine entry chains on top of human entries
        _, _, entries = chain_tail()

    # --- machine queue: select oldest open o* and clear at most one --------
    o_star = pick_oldest_open(obligations, domain="machine")
    n_open = sum(1 for o in obligations if o.get("state") not in TERMINAL)

    if o_star is None:
        print(f"machine queue idle at {ts}: no open machine obligation; "
              f"human ladder emitted {n_human} entrie(s) this round")
        if n_open == 0 and n_human == 0:
            print(f"oblig tick clean at {ts}: all {len(obligations)} "
                  "obligation(s) closed (legislated/wontfix); idle round")
        save_ledger([{k: v for k, v in o.items() if k != "anchors"}
                     for o in obligations])
        return 0

    from_state = o_star.get("state", "raised")
    res, unres = verify_evidence_existence(o_star)
    # This run's capability for o*: report + evidence-existence verification.
    # No transition without a satisfiable evidence predicate (N10).
    to_state = from_state
    note = (f"oldest-open machine FIFO pick; evidence-existence check: "
            f"{res} resolvable / {unres} unresolvable sha token(s) in "
            f"ledger evidence; chain anchors={o_star['anchors']}")
    if not o_star.get("evidence"):
        note += "; no evidence yet -- stays raised (N12 honest suspension)"

    entry = append_chain_rpt(o_star["id"], from_state, to_state, note, ts,
                             queue="machine")
    print(f"RPT.OBLIG seq={entry['seq']}: {o_star['id']} "
          f"{from_state} -> {to_state} ({note[:120]}...)")

    save_ledger([{k: v for k, v in o.items() if k != "anchors"}
                 for o in obligations])
    print(f"oblig tick complete at {ts}: {n_open} open obligation(s) "
          f"(machine clearing <=1 done; human ladder emitted {n_human}; "
          "soft priority: Whittle arm not blocked)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="URE obligation sub-machine tick")
    ap.add_argument("--offline", action="store_true",
                    help="skip cross-repo kit F-table fetch and vci-inbox "
                         "L2 comment (local dry-run)")
    args = ap.parse_args()
    return oblig_tick(offline=args.offline)


if __name__ == "__main__":
    sys.exit(main())
