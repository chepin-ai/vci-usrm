#!/usr/bin/env python3
"""URE obligation sub-machine tick (SPEC-NMUST-01 §4 executable recursion).

Obligation closure machine: every obligation o walks the N-MUST lattice
  raised -> fixed -> implemented -> tested -> verified -> legislated
                                                        | wontfix (L3-sealed)
and every transition must carry evidence (N10); evidence is hash-anchored
on the chain (N11). This script is the sweeper-side executable:

  1. Build obligation set O from three sources:
       - ure/obligations.jsonl            (ledger, one obligation per line)
       - ure/chain.jsonl entries with intent in {INCIDENT, WARN, FINDING}
       - kit/INDEX.md F-table (chepin-ai/vci-library, cross-repo read-only GET)
     Newly discovered source items are appended to the ledger as `raised`.
  2. For each o, check evidence progress: a later chain entry whose payload
     references o.id (intent=RPT.OBLIG transition record or an `evidence`
     field) counts as an anchor; the ledger state is the source of truth.
  3. Pick the oldest non-closed o* (FIFO by `opened`; wontfix excluded).
     At most ONE clearing per round (n9 rolling cadence): do what this run
     can do for o* -- here: report + verify evidence existence (commit shas
     resolvable in the local checkout) -- then update state.
  4. Append chain entry intent=RPT.OBLIG {oid, from, to, note}
     (v2 hash chaining, hash = sha256(prev + canon), same as pareto_tick).
     Open obligations never block the Whittle arm (soft priority: the
     obligation arm runs first and leaves a bookkeeping entry).
  5. All closed -> print "clean" and idle (I8 explicit halt state).

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
TOKEN = os.environ.get("URE_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""

SOURCE_INTENTS = {"INCIDENT", "WARN", "FINDING"}
LATTICE = ["raised", "fixed", "implemented", "tested", "verified", "legislated"]
TERMINAL = {"legislated", "wontfix"}
HEXSHA = re.compile(r"\b[0-9a-f]{7,40}\b")


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


def append_chain_rpt(oid, from_state, to_state, note, ts):
    """Append intent=RPT.OBLIG entry with v2 hash chaining."""
    prev_seq, prev_hash, _ = chain_tail()
    entry = {"seq": prev_seq + 1, "ts": ts, "intent": "RPT.OBLIG",
             "oid": oid, "from": from_state, "to": to_state, "note": note,
             "prev": prev_hash}
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
                    "state": "raised", "evidence": [], "opened": utcnow()})
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


def pick_oldest_open(obligations):
    """FIFO: oldest non-terminal obligation; wontfix excluded (L3 terminal)."""
    open_os = [o for o in obligations if o.get("state") not in TERMINAL]
    if not open_os:
        return None
    return min(open_os, key=lambda o: (o.get("opened", ""), o.get("id", "")))


def oblig_tick(offline=False):
    ts = utcnow()
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
        print(f"oblig {o['id']}: state={o['state']} "
              f"evidence={len(o.get('evidence', []))} anchors={anchors}")

    # --- select oldest open o* and clear at most one (n9 cadence) ----------
    o_star = pick_oldest_open(obligations)
    if o_star is None:
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
    note = (f"oldest-open FIFO pick; evidence-existence check: "
            f"{res} resolvable / {unres} unresolvable sha token(s) in "
            f"ledger evidence; chain anchors={o_star['anchors']}")
    if not o_star.get("evidence"):
        note += "; no evidence yet -- stays raised (N12 honest suspension)"

    entry = append_chain_rpt(o_star["id"], from_state, to_state, note, ts)
    print(f"RPT.OBLIG seq={entry['seq']}: {o_star['id']} "
          f"{from_state} -> {to_state} ({note[:120]}...)")

    save_ledger([{k: v for k, v in o.items() if k != "anchors"}
                 for o in obligations])
    n_open = sum(1 for o in obligations if o.get("state") not in TERMINAL)
    print(f"oblig tick complete at {ts}: {n_open} open obligation(s) "
          f"(soft priority: RPT.OBLIG recorded, Whittle arm not blocked)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="URE obligation sub-machine tick")
    ap.add_argument("--offline", action="store_true",
                    help="skip cross-repo kit F-table fetch (local dry-run)")
    args = ap.parse_args()
    return oblig_tick(offline=args.offline)


if __name__ == "__main__":
    sys.exit(main())
