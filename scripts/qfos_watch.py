#!/usr/bin/env python3
r"""QF-OS dynamic tracker — the obligation machine's new sense organ.

Continuously watches cisvr's QF-OS design surfaces across the federation
(read-only cross-repo API) and turns every drift into residue/obligation:

    watch list (path prefixes):
      chepin-ai/ci-control : bridge/design/, bridge/adjudications-pending/,
                             bridge/governor/, bridge/ENCODER-01.md,
                             bridge/IC-CROSSWALL-01.md,
                             bridge/EPHEMERAL-KEY-RELAY-01.md
      chepin-ai/vci-inbox  : disc/QFOS*  (QFOS / QFOS-RFC prefixed items)
      chepin-ai/vci-root   : whole tree
      chepin-ai/qlv-lab    : toolchain/distilled/qgo/, formal/

    state (ure/qfos_watch_state.json):
      {ts, baseline, files: {"repo:path": {sha, ts}}, recent_events: [...]}
      Each round the live git-tree snapshot is diffed against `files`:
      new path / changed blob sha -> event
      {type: qfos_change, repo, path, old_sha, new_sha, kind: added|modified}

    change = obligation:
      - federation view gains a `qfos` field
        {last_change_ts, changes_24h, latest[], watched_files}
        committed to the same targets as oblig_monitor;
      - ure/chain.jsonl appends intent=RPT.QFOS (v2 hash chain;
        idempotent: an identical change sha-set is never appended twice);
      - a major new design file (kind=added and path under design/ or
        disc/) auto-registers a machine obligation
        o-qfos-review-YYYYMMDD-NN (src=qfos-watch, note=new path) in
        ure/obligations.jsonl (idempotent by id+path).

    First-ever round is the baseline: every watched file is recorded and
    the round reports clean (no events, no chain/ledger writes).

    --offline: snapshots come from a local fixture file (--snapshot)
    instead of the network; all reads/writes stay under --root.
    --selftest: sandbox fixture run covering added / modified /
    idempotency paths in a temp dir; no network, no repo writes.

Secrets only via env / Authorization headers; view, chain, state and
ledger carry zero secrets and zero personal identifiers (iron rule).
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ORG = "chepin-ai"
REPO_USRM = f"{ORG}/vci-usrm"

WATCH = {
    f"{ORG}/ci-control": [
        "bridge/design/",
        "bridge/adjudications-pending/",
        "bridge/governor/",
        "bridge/ENCODER-01.md",
        "bridge/IC-CROSSWALL-01.md",
        "bridge/EPHEMERAL-KEY-RELAY-01.md",
    ],
    f"{ORG}/vci-inbox": ["disc/QFOS"],
    f"{ORG}/vci-root": [""],
    f"{ORG}/qlv-lab": ["toolchain/distilled/qgo/", "formal/"],
}

STATE_PATH = "ure/qfos_watch_state.json"
CHAIN = "ure/chain.jsonl"
LEDGER = "ure/obligations.jsonl"
VIEW_MIRROR = "ure/federation_oblig_view.json"

GENESIS = "0" * 64
LATEST_MAX = 10
RECENT_KEEP_H = 48.0
WINDOW_24H = 24.0


def utcnow_dt():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    if not s or not isinstance(s, str):
        return None
    try:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None


def age_h(ts, now):
    dt = parse_ts(ts)
    if dt is None:
        return float("inf")
    return (now - dt).total_seconds() / 3600.0


def canon_v2(obj):
    """Canonical JSON, identical to pareto_tick/oblig_tick canon."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def jsonl_load(path):
    entries = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


# ------------------------------------------------------------ snapshot ----

def match_path(repo, path):
    """Is `path` inside repo's watch list? (prefix match, files only)"""
    return any(path.startswith(pre) for pre in WATCH[repo])


def snapshot_online(repo):
    """Whole-tree blob map {path: sha} filtered to the watch list.
    Read-only git trees API; one call per repo."""
    import oblig_monitor as om
    s, r = om.gh_req(f"/repos/{repo}/git/trees/main?recursive=1")
    if s != 200 or not isinstance(r, dict) or "tree" not in r:
        raise RuntimeError(f"tree fetch failed for {repo}: HTTP {s}")
    out = {}
    for t in r["tree"]:
        if t.get("type") == "blob" and match_path(repo, t["path"]):
            out[t["path"]] = t["sha"]
    if r.get("truncated"):
        print(f"::warning::{repo} tree response truncated; "
              "snapshot may be partial this round")
    return out


def snapshots_online():
    return {repo: snapshot_online(repo) for repo in WATCH}


# ---------------------------------------------------------------- diff ----

def diff_snapshots(state_files, snaps, ts):
    """Compare live snapshots with recorded state.
    Returns (events, new_files_map). Deletions are residue-free drift:
    noted as modified events with new_sha=null is deliberately avoided;
    a removed file simply leaves the watch set (recorded in state)."""
    events = []
    new_files = {}
    for repo in sorted(snaps):
        for path in sorted(snaps[repo]):
            key = f"{repo}:{path}"
            sha = snaps[repo][path]
            old = state_files.get(key)
            new_files[key] = {"sha": sha, "ts": (old or {}).get("ts") or ts}
            if old is None:
                events.append({"type": "qfos_change", "repo": repo,
                               "path": path, "old_sha": None,
                               "new_sha": sha, "kind": "added", "ts": ts})
            elif old.get("sha") != sha:
                events.append({"type": "qfos_change", "repo": repo,
                               "path": path, "old_sha": old.get("sha"),
                               "new_sha": sha, "kind": "modified",
                               "ts": ts})
    return events, new_files


def is_major_design(event):
    """Major new design file: added under design/ or disc/."""
    return (event["kind"] == "added"
            and ("design/" in event["path"] or "disc/" in event["path"]))


def changes_signature(events):
    """Idempotency signature: the sorted sha-set of a change batch."""
    return sorted(f"{e['repo']}:{e['path']}:{e['new_sha']}" for e in events)


# ---------------------------------------------------------------- state ---

def load_state(root):
    path = os.path.join(root, STATE_PATH)
    if os.path.exists(path):
        try:
            with open(path) as f:
                st = json.load(f)
            if isinstance(st, dict) and "files" in st:
                return st
        except json.JSONDecodeError:
            pass
    return {"version": 1, "ts": None, "baseline": False,
            "files": {}, "recent_events": []}


def save_state(root, state):
    path = os.path.join(root, STATE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(json.dumps(state, ensure_ascii=False, indent=1,
                           sort_keys=True) + "\n")


def prune_recent(state, now):
    state["recent_events"] = [
        e for e in state.get("recent_events", [])
        if age_h(e.get("ts"), now) <= RECENT_KEEP_H]


def changes_24h(state, now):
    return sum(1 for e in state.get("recent_events", [])
               if age_h(e.get("ts"), now) <= WINDOW_24H)


# ----------------------------------------------------------------- chain --

def last_qfos_signature(entries):
    for e in reversed(entries):
        if e.get("intent") == "RPT.QFOS":
            return changes_signature(e.get("changes") or [])
    return None


def append_chain_qfos(chain_path, events, ts):
    """Append intent=RPT.QFOS (v2 hash chain). Idempotent: skipped when
    the change sha-set equals the previous RPT.QFOS entry's."""
    if not events:
        return None
    entries = jsonl_load(chain_path)
    if entries and last_qfos_signature(entries) == changes_signature(events):
        return None
    prev_seq = entries[-1].get("seq", 0) if entries else 0
    prev_hash = entries[-1].get("hash", GENESIS) if entries else GENESIS
    entry = {"seq": prev_seq + 1, "ts": ts, "intent": "RPT.QFOS",
             "count": len(events),
             "changes": [{"repo": e["repo"], "path": e["path"],
                          "kind": e["kind"], "old_sha": e["old_sha"],
                          "new_sha": e["new_sha"]} for e in events],
             "note": "QF-OS watch: cisvr design surface drift detected "
                     "(qfos-watch residual alarm)",
             "prev": prev_hash}
    entry["hash"] = hashlib.sha256(
        (prev_hash + canon_v2(entry)).encode()).hexdigest()
    with open(chain_path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


# ---------------------------------------------------------------- ledger --

def register_review_obligations(ledger_path, events, now):
    """Auto-register machine obligations for major new design files.
    o-qfos-review-YYYYMMDD-NN, src=qfos-watch, note=new path.
    Idempotent by id+path (and by path across days)."""
    ledger = jsonl_load(ledger_path)
    day = now.strftime("%Y%m%d")
    existing_paths = set()
    max_nn = 0
    for o in ledger:
        oid = o.get("id") or ""
        if oid.startswith("o-qfos-review-"):
            note = o.get("note") or ""
            for line in note.splitlines():
                if line.startswith("path="):
                    existing_paths.add(line[5:])
            if oid.startswith(f"o-qfos-review-{day}-"):
                try:
                    max_nn = max(max_nn, int(oid.rsplit("-", 1)[1]))
                except ValueError:
                    pass
    added = []
    for e in events:
        if not is_major_design(e):
            continue
        full = f"{e['repo']}:{e['path']}"
        if full in existing_paths:
            continue
        max_nn += 1
        ob = {"id": f"o-qfos-review-{day}-{max_nn:02d}",
              "src": "qfos-watch",
              "domain": "machine", "state": "raised", "evidence": [],
              "opened": iso(now),
              "note": f"需评审的新件 path={full}"}
        ledger.append(ob)
        existing_paths.add(full)
        added.append(ob)
    if added:
        header = ""
        if os.path.exists(ledger_path):
            with open(ledger_path) as f:
                head = f.read()
            header = "".join(l for l in head.splitlines(keepends=True)
                             if l.startswith("#"))
        with open(ledger_path, "w") as f:
            if header:
                f.write(header if header.endswith("\n") else header + "\n")
            for o in ledger:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    return added


# ------------------------------------------------------------------ view --

def qfos_field(state, events, now, ts):
    latest = (state.get("recent_events", []))[-LATEST_MAX:]
    return {"spec": "QF-OS dynamic tracker v1 (qfos-watch): cisvr design "
                    "surface drift -> residual alarm",
            "watched_files": len(state.get("files", {})),
            "watched_repos": sorted(WATCH),
            "last_change_ts": (state.get("recent_events") or [{}])[-1].get("ts")
                              if state.get("recent_events") else None,
            "changes_24h": changes_24h(state, now),
            "last_round_ts": ts,
            "last_round_events": len(events),
            "latest": [{"repo": e["repo"], "path": e["path"],
                        "kind": e["kind"], "ts": e["ts"]}
                       for e in latest]}


def merge_view_local(root, qfos):
    path = os.path.join(root, VIEW_MIRROR)
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            view = json.load(f)
    except json.JSONDecodeError:
        return False
    view["qfos"] = qfos
    with open(path, "w") as f:
        f.write(json.dumps(view, ensure_ascii=False, indent=1,
                           sort_keys=True) + "\n")
    return True


# ------------------------------------------------------------- one round --

def run_round(root, snaps, now):
    """One watch round against local state under `root`.
    Returns a result dict; writes state/chain/ledger/view locally."""
    ts = iso(now)
    state = load_state(root)
    prune_recent(state, now)
    result = {"ts": ts, "baseline": False, "events": [],
              "chain_entry": None, "obligations": [],
              "watched_files": 0}

    if not state.get("baseline"):
        # First-ever round: record the baseline, report clean.
        files = {}
        for repo in sorted(snaps):
            for path, sha in sorted(snaps[repo].items()):
                files[f"{repo}:{path}"] = {"sha": sha, "ts": ts}
        state.update({"ts": ts, "baseline": True, "files": files})
        save_state(root, state)
        qfos = qfos_field(state, [], now, ts)
        qfos["baseline_ts"] = ts
        merge_view_local(root, qfos)
        result.update({"baseline": True, "watched_files": len(files),
                       "qfos": qfos})
        return result

    events, new_files = diff_snapshots(state["files"], snaps, ts)
    state["files"] = new_files
    state["ts"] = ts
    result["watched_files"] = len(new_files)
    if events:
        state["recent_events"].extend(events)
        chain_entry = append_chain_qfos(os.path.join(root, CHAIN),
                                        events, ts)
        added = register_review_obligations(os.path.join(root, LEDGER),
                                            events, now)
        result.update({"events": events, "chain_entry": chain_entry,
                       "obligations": added})
    save_state(root, state)
    qfos = qfos_field(state, events, now, ts)
    merge_view_local(root, qfos)
    result["qfos"] = qfos
    return result


# ------------------------------------------------------------- selftest ---

def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def _jl(objs):
    return "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in objs)


def selftest():
    """Sandbox: baseline / added / modified / idempotency, temp dir only."""
    now = datetime(2026, 8, 26, 3, 0, 0, tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory() as root:
        _w(os.path.join(root, LEDGER),
           "# URE obligation ledger (test)\n")
        _w(os.path.join(root, VIEW_MIRROR),
           json.dumps({"ts": "2026-08-26T00:00:00Z"}) + "\n")

        r_ctl = f"{ORG}/ci-control"
        r_inbox = f"{ORG}/vci-inbox"
        r_root = f"{ORG}/vci-root"
        r_lab = f"{ORG}/qlv-lab"
        s0 = {
            r_ctl: {"bridge/design/FOO-01.md": "a1",
                    "bridge/ENCODER-01.md": "e1",
                    "bridge/other/unwatched.md": "x"},
            r_inbox: {"disc/QFOS-01.md": "q1",
                      "disc/other.md": "z"},
            r_root: {"README.md": "r1"},
            r_lab: {"toolchain/distilled/qgo/e.py": "g1",
                    "src/unwatched.py": "u"},
        }
        # filter fixture through the same watch predicate the API path uses
        s0 = {repo: {p: s for p, s in files.items()
                     if match_path(repo, p)}
              for repo, files in s0.items()}
        assert len(s0[r_ctl]) == 2 and len(s0[r_inbox]) == 1 \
            and len(s0[r_root]) == 1 and len(s0[r_lab]) == 1, \
            "watch-list prefix filter mismatch"

        # round 1: baseline -> clean, no chain, no ledger entries
        r1 = run_round(root, s0, now)
        assert r1["baseline"] and r1["watched_files"] == 5
        assert not jsonl_load(os.path.join(root, CHAIN))
        assert not jsonl_load(os.path.join(root, LEDGER))
        with open(os.path.join(root, VIEW_MIRROR)) as f:
            v = json.load(f)
        assert v["qfos"]["watched_files"] == 5
        assert v["qfos"]["changes_24h"] == 0
        assert v["qfos"]["last_change_ts"] is None

        # round 2: one added design file, one modified, one added non-design
        now2 = now + timedelta(hours=1)
        s1 = json.loads(json.dumps(s0))
        s1[r_ctl]["bridge/design/BAR-02.md"] = "b2"          # major added
        s1[r_ctl]["bridge/ENCODER-01.md"] = "e2"             # modified
        s1[r_inbox]["disc/QFOS-RFC9.md"] = "q9"              # major added
        s1[r_root]["witness-latest.json"] = "w1"             # added, minor
        r2 = run_round(root, s1, now2)
        kinds = {(e["repo"], e["path"]): e["kind"] for e in r2["events"]}
        assert len(r2["events"]) == 4, r2["events"]
        assert kinds[(r_ctl, "bridge/design/BAR-02.md")] == "added"
        assert kinds[(r_ctl, "bridge/ENCODER-01.md")] == "modified"
        assert kinds[(r_inbox, "disc/QFOS-RFC9.md")] == "added"
        mod = next(e for e in r2["events"] if e["kind"] == "modified")
        assert mod["old_sha"] == "e1" and mod["new_sha"] == "e2"

        chain = jsonl_load(os.path.join(root, CHAIN))
        assert len(chain) == 1 and chain[0]["intent"] == "RPT.QFOS"
        assert chain[0]["count"] == 4 and chain[0]["prev"] == GENESIS
        want = hashlib.sha256(
            (GENESIS + canon_v2({k: v for k, v in chain[0].items()
                                 if k != "hash"})).encode()).hexdigest()
        assert chain[0]["hash"] == want, "v2 chain hash broken"

        ledger = jsonl_load(os.path.join(root, LEDGER))
        assert len(ledger) == 2, ledger
        ids = [o["id"] for o in ledger]
        assert ids == [f"o-qfos-review-20260826-01",
                       f"o-qfos-review-20260826-02"], ids
        assert all(o["src"] == "qfos-watch" and o["domain"] == "machine"
                   and o["state"] == "raised" for o in ledger)
        assert "path=" in ledger[0]["note"]

        v = json.load(open(os.path.join(root, VIEW_MIRROR)))
        assert v["qfos"]["changes_24h"] == 4
        assert v["qfos"]["last_change_ts"] == iso(now2)
        assert len(v["qfos"]["latest"]) == 4

        # round 3: identical snapshot -> clean; chain/ledger untouched
        now3 = now2 + timedelta(hours=1)
        r3 = run_round(root, s1, now3)
        assert r3["events"] == [] and r3["chain_entry"] is None
        assert len(jsonl_load(os.path.join(root, CHAIN))) == 1
        assert len(jsonl_load(os.path.join(root, LEDGER))) == 2

        # round 3b: chain-level idempotency backstop — same sha-set forced
        # through append must not duplicate even if events were re-fed.
        dup = append_chain_qfos(os.path.join(root, CHAIN),
                                r2["events"], iso(now3))
        assert dup is None, "same sha-set must not re-append"
        assert len(jsonl_load(os.path.join(root, CHAIN))) == 1

        # round 4: ledger-level idempotency — re-feed same added events;
        # a genuinely new design file gets the next NN.
        now4 = now3 + timedelta(hours=25)  # next UTC day
        s2 = json.loads(json.dumps(s1))
        s2[r_ctl]["bridge/design/BAZ-03.md"] = "b3"
        r4 = run_round(root, s2, now4)
        ledger = jsonl_load(os.path.join(root, LEDGER))
        assert len(ledger) == 3
        assert ledger[-1]["id"] == f"o-qfos-review-20260827-01", ledger[-1]
        # changes_24h window decays: only round-4 events are inside 24h
        v = json.load(open(os.path.join(root, VIEW_MIRROR)))
        assert v["qfos"]["changes_24h"] == 1, v["qfos"]

        # state file round-trips and carries per-path {sha, ts}
        st = load_state(root)
        rec = st["files"][f"{r_ctl}:bridge/ENCODER-01.md"]
        assert rec["sha"] == "e2" and rec["ts"]
        print("selftest: baseline/added/modified/idempotent paths OK")


# ----------------------------------------------------------------- main ---

def main():
    ap = argparse.ArgumentParser(
        description="QF-OS dynamic tracker (cisvr design surface watch)")
    ap.add_argument("--selftest", action="store_true",
                    help="sandbox fixture tests in a temp dir; no network")
    ap.add_argument("--offline", action="store_true",
                    help="no network; snapshots from --snapshot fixture, "
                         "all reads/writes under --root")
    ap.add_argument("--snapshot", default=None,
                    help="JSON fixture {repo: {path: sha}} for --offline")
    ap.add_argument("--root", default=".",
                    help="repo root (default: cwd)")
    ap.add_argument("--no-write", action="store_true",
                    help="compute and print only; no remote commits")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0

    root = args.root
    now = utcnow_dt()

    if args.offline:
        if not args.snapshot:
            print("FATAL: --offline requires --snapshot fixture")
            return 1
        with open(args.snapshot) as f:
            snaps = json.load(f)
        snaps = {repo: {p: s for p, s in files.items()
                        if repo in WATCH and match_path(repo, p)}
                 for repo, files in snaps.items()}
        result = run_round(root, snaps, now)
        print(json.dumps({"ts": result["ts"], "baseline": result["baseline"],
                          "watched_files": result["watched_files"],
                          "events": len(result["events"]),
                          "obligations": [o["id"] for o in
                                          result["obligations"]],
                          "chain_seq": (result["chain_entry"] or {})
                          .get("seq")},
                         ensure_ascii=False))
        return 0

    # online round: cross-repo read-only snapshots, then local round,
    # then federation commits (state + view + chain + ledger).
    import oblig_monitor as om
    if not om.TOKEN:
        print("FATAL: CI_ROOT_TOKEN/GH_TOKEN env required")
        return 1
    snaps = snapshots_online()
    result = run_round(root, snaps, now)
    ts = result["ts"]
    print(f"qfos watch {ts}: baseline={result['baseline']} "
          f"watched_files={result['watched_files']} "
          f"events={len(result['events'])}")
    for e in result["events"]:
        print(f"  {e['kind']:8s} {e['repo']}:{e['path']} "
              f"{(e['old_sha'] or '-')[:8]}->{(e['new_sha'] or '-')[:8]}")

    if args.no_write:
        print("--no-write: remote commits skipped")
        return 0

    wrote = []
    # state file: commit on baseline or on any change round
    if result["baseline"] or result["events"]:
        with open(os.path.join(root, STATE_PATH)) as f:
            ok, _ = om.put_file(
                om.REPO_USRM, STATE_PATH, f.read(),
                f"ure: qfos watch state {ts} [skip ci]")
        wrote.append((STATE_PATH, ok))
    # view qfos field -> all view targets (fresh read, merge, write back)
    prev = None
    for repo, path in om.view_targets():
        old = om.get_text(repo, path)
        if old:
            try:
                prev = json.loads(old)
                break
            except json.JSONDecodeError:
                continue
    if prev is not None:
        prev["qfos"] = result["qfos"]
        payload = json.dumps(prev, ensure_ascii=False, indent=1,
                             sort_keys=True) + "\n"
        for repo, path in om.view_targets():
            ok, _ = om.put_file(repo, path, payload,
                                f"federation: qfos watch {ts} [skip ci]")
            wrote.append((f"{repo}/{path}", ok))
    else:
        print("::warning::no readable view target; qfos field not merged "
              "upstream this round")
    # chain entry -> vci-usrm (remote tail re-check, same as relations)
    ce = result["chain_entry"]
    if ce is not None:
        remote = om.get_text(om.REPO_USRM, CHAIN)
        if remote is not None:
            rlines = [l for l in remote.splitlines()
                      if l.strip() and not l.startswith("#")]
            rlast = json.loads(rlines[-1]) if rlines else None
            if rlast and rlast.get("hash") == ce["prev"]:
                ok, _ = om.put_file(
                    om.REPO_USRM, CHAIN,
                    remote.rstrip("\n") + "\n"
                    + json.dumps(ce, ensure_ascii=False) + "\n",
                    f"ure: RPT.QFOS seq{ce['seq']} "
                    "(qfos-watch drift) [skip ci]")
                wrote.append((CHAIN, ok))
            else:
                print("::warning::remote chain tail moved; local RPT.QFOS "
                      "kept, remote append deferred")
    # ledger -> vci-usrm (fresh read + merge new lines by id)
    if result["obligations"]:
        remote = om.get_text(om.REPO_USRM, LEDGER)
        if remote is not None:
            have = set()
            for l in remote.splitlines():
                l = l.strip()
                if not l or l.startswith("#"):
                    continue
                try:
                    have.add(json.loads(l).get("id"))
                except json.JSONDecodeError:
                    continue
            newlines = [json.dumps(o, ensure_ascii=False)
                        for o in result["obligations"]
                        if o["id"] not in have]
            if newlines:
                ok, _ = om.put_file(
                    om.REPO_USRM, LEDGER,
                    remote.rstrip("\n") + "\n" + "\n".join(newlines) + "\n",
                    f"ure: qfos review obligations {ts} [skip ci]")
                wrote.append((LEDGER, ok))
            else:
                print("ledger: review obligations already present upstream")
    for name, ok in wrote:
        print(f"commit {name}: {'ok' if ok else 'FAILED'}")
    if not wrote:
        print("clean round: no drift, nothing to commit")
    if result["obligations"]:
        print("review obligations:",
              ", ".join(o["id"] for o in result["obligations"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
