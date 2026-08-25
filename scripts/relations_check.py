#!/usr/bin/env python3
r"""NMUST-04 §3 four-yellow federation executables: R3/R4/R6/R7 relations check.

SPEC-NMUST-04 §3 engineering criteria -- the four 🟡 machine checks, one file:

  R3 等价 (equivalence replay): replay ure/chain.jsonl under the v2 rule
      hash = sha256(prev + canon(entry-minus-hash)), plus the session-side
      narrative chain (vci-inbox inbox/usrm-outbox.json, when readable;
      its canon: json.dumps(entry minus hash/hmac, ensure_ascii=False,
      sort_keys=True), hash = sha256(prev+canon)[:12]; hmac fields are NOT
      verified, only their presence is recorded). Any broken link is a
      violation.
  R4 对称 (symmetry conservation): obligation-total conservation report --
      ledger counts {open, legislated, wontfix} vs the values derived by
      folding on-chain RPT.OBLIG transition events (initial state raised).
      Any imbalance is a violation (FINDING: 对称破缺).
  R6 蕴含 (basis evolution): minimal-basis version tracking via
      ure/basis.jsonl -- one rule primitive per line
      {id, rule, introduced, covers{obligation-class: count}}. Scanning the
      ledger: an obligation whose src class is covered by no primitive is
      reported as a 基不完备候选 (basis-incompleteness candidate). The check
      NEVER auto-adds basis primitives; it only outputs the suggestion.
      covers counts are refreshed as bookkeeping.
  R7 依赖 (deps DAG): topological sort over ure/roadmap.json node deps;
      a cycle is a violation (alarm). deps pointing at unknown nodes are
      recorded as missing-deps warnings, not cycle violations.

Integration (federation level, runs after oblig_monitor in oblig-monitor.yml):
  - the result is merged into the federation obligation view
    (federation_oblig_view.json, field "relations":
     {replay_ok, conservation_ok, basis_candidates[], dag_ok, violations[]})
    across the same view targets as oblig_monitor (OBLIG_VIEW_TARGETS);
  - when any violation exists, an intent=RPT.RELATIONS entry (v2 hash chain)
    is appended to ure/chain.jsonl (idempotent: a repeat run with an
    identical violation set does not duplicate the entry).

Modes:
  default    online: local reads + outbox fetch; API writes to view targets
  --offline  sandbox: no network at all; local reads/writes under --root
  --selftest fixture violation-path tests in a temp dir (broken chain,
             imbalanced ledger, cyclic roadmap, uncovered src class, broken
             outbox narrative chain), no network, no repo writes

Secrets only via env / Authorization headers; logs carry zero secrets and
zero personal identifiers (iron rule).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CHAIN = "ure/chain.jsonl"
LEDGER = "ure/obligations.jsonl"
ROADMAP = "ure/roadmap.json"
BASIS = "ure/basis.jsonl"
VIEW_MIRROR = "ure/federation_oblig_view.json"

OUTBOX_URL = os.environ.get(
    "RELATIONS_OUTBOX_URL",
    "https://raw.githubusercontent.com/chepin-ai/vci-inbox/main/inbox/usrm-outbox.json")

GENESIS = "0" * 64
OUTBOX_GENESIS = "0" * 12
TERMINAL = {"legislated", "wontfix"}
CHAIN_INTENT_RE = re.compile(r"^(INCIDENT|WARN|FINDING)\b")


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


# --------------------------------------------------------------------- R3 --

def replay_v2_chain(path):
    """R3a: replay a v2 chain file. Returns a per-chain report dict."""
    entries = jsonl_load(path)
    prev, verified, first_break = GENESIS, 0, None
    for e in entries:
        body = {k: v for k, v in e.items() if k != "hash"}
        want = hashlib.sha256((prev + canon_v2(body)).encode()).hexdigest()
        if e.get("prev") != prev or e.get("hash") != want:
            first_break = e.get("seq", verified + 1)
            break
        prev = e["hash"]
        verified += 1
    return {"chain": path, "rule": "v2 sha256(prev+canon)",
            "entries": len(entries), "verified": verified,
            "first_break": first_break}


def outbox_canon(entry):
    """Narrative-chain canon: json.dumps(entry minus hash/hmac,
    ensure_ascii=False, sort_keys=True) -- default separators per spec."""
    body = {k: v for k, v in entry.items() if k not in ("hash", "hmac")}
    return json.dumps(body, ensure_ascii=False, sort_keys=True)


def replay_outbox_chain(text):
    """R3b: replay the session-side narrative chain (12-char truncated
    hashes; hmac presence recorded, never verified)."""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return {"chain": "usrm-outbox", "status": "unparseable",
                "entries": 0, "verified": 0, "first_break": 1,
                "hmac_present": 0}
    entries = obj if isinstance(obj, list) else obj.get("entries", [])
    prev, verified, first_break, hmac_n = OUTBOX_GENESIS, 0, None, 0
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            first_break = i + 1
            break
        if "hmac" in e:
            hmac_n += 1
        want = hashlib.sha256((prev + outbox_canon(e)).encode()).hexdigest()[:12]
        if (e.get("prev", prev) != prev) or e.get("hash") != want:
            first_break = i + 1
            break
        prev = e["hash"]
        verified += 1
    return {"chain": "usrm-outbox", "status": "ok",
            "rule": "sha256(prev+canon)[:12], hmac recorded not verified",
            "entries": len(entries), "verified": verified,
            "first_break": first_break, "hmac_present": hmac_n}


def check_replay(root, offline=False, outbox_text=None):
    """R3: replay local chain + narrative chain. Returns (report, violations)."""
    reports = [replay_v2_chain(os.path.join(root, CHAIN))]
    if outbox_text is not None:
        reports.append(replay_outbox_chain(outbox_text))
    elif offline:
        reports.append({"chain": "usrm-outbox", "status": "skipped-offline",
                        "entries": 0, "verified": 0, "first_break": None,
                        "hmac_present": 0})
    else:
        try:
            req = urllib.request.Request(OUTBOX_URL)
            with urllib.request.urlopen(req, timeout=20) as r:
                reports.append(replay_outbox_chain(r.read().decode()))
        except Exception:  # noqa: BLE001 - unreadable outbox is not a violation
            reports.append({"chain": "usrm-outbox", "status": "unavailable",
                            "entries": 0, "verified": 0, "first_break": None,
                            "hmac_present": 0})
    violations = []
    for rep in reports:
        if rep.get("first_break") is not None:
            violations.append({"check": "R3", "kind": "等价断链",
                               "chain": rep["chain"],
                               "first_break": rep["first_break"],
                               "verified": rep["verified"],
                               "entries": rep["entries"]})
    return {"chains": reports}, violations


# --------------------------------------------------------------------- R4 --

def fold_rpt_oblig(chain_entries):
    """Fold RPT.OBLIG transitions: oid -> derived state (initial raised).
    Also collects from-field anomalies (entry.from != derived-so-far)."""
    derived, anomalies = {}, []
    for e in chain_entries:
        if e.get("intent") != "RPT.OBLIG":
            continue
        oid = e.get("oid")
        if not oid:
            continue
        cur = derived.get(oid, "raised")
        frm = e.get("from")
        if frm is not None and frm != cur:
            anomalies.append({"seq": e.get("seq"), "oid": oid,
                              "from": frm, "derived_before": cur})
        derived[oid] = e.get("to", cur)
    return derived, anomalies


def class_counts(states):
    c = {"open": 0, "legislated": 0, "wontfix": 0}
    for s in states:
        if s == "legislated":
            c["legislated"] += 1
        elif s == "wontfix":
            c["wontfix"] += 1
        else:
            c["open"] += 1
    return c


def check_conservation(ledger, chain_entries):
    """R4: ledger counts vs chain-derived counts. Imbalance -> violation."""
    derived, anomalies = fold_rpt_oblig(chain_entries)
    ledger_states = {o.get("id"): o.get("state", "raised") for o in ledger}
    mismatch = []
    for oid, lst in ledger_states.items():
        der = derived.get(oid, "raised")
        if der != lst:
            mismatch.append({"oid": oid, "derived": der, "ledger": lst})
    orphan_chain = sorted(oid for oid in derived if oid not in ledger_states)
    derived_counts = class_counts(
        derived.get(oid, "raised") for oid in ledger_states)
    ledger_counts = class_counts(ledger_states.values())
    report = {"ledger": ledger_counts, "derived": derived_counts,
              "mismatch": mismatch, "orphan_chain_oids": orphan_chain,
              "from_anomalies": anomalies}
    violations = []
    if mismatch or orphan_chain or anomalies:
        violations.append({"check": "R4", "kind": "对称破缺",
                           "ledger": ledger_counts, "derived": derived_counts,
                           "mismatch": mismatch,
                           "orphan_chain_oids": orphan_chain,
                           "from_anomalies": anomalies})
    return report, violations


# --------------------------------------------------------------------- R6 --

def classify_src(src):
    """Obligation src -> obligation class (basis-coverage taxonomy)."""
    s = src or ""
    if s.startswith("kit/INDEX.md") or "admonition" in s:
        return "kit-admonition"
    if CHAIN_INTENT_RE.match(s) or s.startswith("chain seq"):
        return "chain-intent"
    if s.startswith("root-action"):
        return "root-action"
    return "unclassified"


def check_basis(root, ledger, write=True):
    """R6: basis coverage scan. Returns (report, candidates, basis_changed).
    Never auto-adds primitives; uncovered classes are candidates only.
    covers counts are refreshed as pure bookkeeping."""
    path = os.path.join(root, BASIS)
    primitives = jsonl_load(path)
    class_tally = {}
    for o in ledger:
        cls = classify_src(o.get("src"))
        class_tally[cls] = class_tally.get(cls, 0) + 1
    covered = set()
    for p in primitives:
        covered |= set((p.get("covers") or {}).keys())
    candidates = []
    for cls in sorted(set(class_tally) - covered):
        oids = sorted(o["id"] for o in ledger
                      if classify_src(o.get("src")) == cls)
        candidates.append({"class": cls, "obligations": oids,
                           "suggestion": "基不完备候选: 无基元 covers "
                                         f"'{cls}'; 请经立法流程评估是否加基"
                                         " (relations_check 不自动加基)"})
    basis_changed = False
    for p in primitives:
        covers = p.get("covers") or {}
        new_covers = {cls: class_tally.get(cls, 0) for cls in covers}
        if new_covers != covers:
            p["covers"] = new_covers
            basis_changed = True
    if basis_changed and write:
        lines = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.startswith("#"):
                        lines.append(line.rstrip("\n"))
                    else:
                        break
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
            for p in primitives:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
    report = {"primitives": len(primitives),
              "covers": {p.get("id"): p.get("covers") for p in primitives},
              "class_tally": class_tally,
              "candidates": candidates,
              "counts_refreshed": basis_changed}
    return report, candidates, basis_changed


# --------------------------------------------------------------------- R7 --

def check_dag(root):
    """R7: topological sort over roadmap node deps. Cycle -> violation."""
    path = os.path.join(root, ROADMAP)
    try:
        with open(path) as f:
            rm = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return {"nodes": 0, "topo_ok": False,
                "error": f"roadmap unreadable: {type(exc).__name__}"}, [
            {"check": "R7", "kind": "依赖图不可读",
             "detail": f"{type(exc).__name__}"}]
    nodes = {n.get("id"): list(n.get("deps") or []) for n in rm.get("nodes", [])}
    missing = sorted({d for deps in nodes.values() for d in deps
                      if d not in nodes})
    # Kahn's algorithm over known nodes only.
    indeg = {n: 0 for n in nodes}
    for n, deps in nodes.items():
        for d in deps:
            if d in nodes:
                indeg[n] += 1
    queue = sorted(n for n, deg in indeg.items() if deg == 0)
    seen = []
    while queue:
        n = queue.pop(0)
        seen.append(n)
        for m, deps in nodes.items():
            if n in deps and m in indeg:
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)
        queue.sort()
    cycle = sorted(set(nodes) - set(seen))
    report = {"nodes": len(nodes), "topo_ok": not cycle,
              "topo_order": seen, "cycle": cycle,
              "missing_deps": missing}
    violations = []
    if cycle:
        violations.append({"check": "R7", "kind": "依赖环",
                           "cycle": cycle,
                           "detail": "roadmap deps 拓扑排序残留节点; "
                                     "deps DAG 存在环"})
    return report, violations


# ------------------------------------------------------------- aggregate --

def build_relations(root, offline=False, outbox_text=None, write_basis=True):
    """Run all four checks and build the relations view field."""
    ledger = jsonl_load(os.path.join(root, LEDGER))
    chain_entries = jsonl_load(os.path.join(root, CHAIN))
    replay, v3 = check_replay(root, offline=offline, outbox_text=outbox_text)
    conservation, v4 = check_conservation(ledger, chain_entries)
    basis, candidates, basis_changed = check_basis(root, ledger,
                                                   write=write_basis)
    dag, v7 = check_dag(root)
    violations = v3 + v4 + v7
    relations = {
        "ts": utcnow(),
        "spec": "NMUST-04 §3 four-yellow federation executables v1 "
                "(R3 replay / R4 conservation / R6 basis / R7 deps-DAG)",
        "replay_ok": not v3,
        "conservation_ok": not v4,
        "dag_ok": not v7,
        "basis_candidates": candidates,
        "violations": violations,
        "replay": replay,
        "conservation": conservation,
        "basis": basis,
        "dag": dag,
    }
    return relations, basis_changed


def violation_signature(violations):
    """Stable signature for idempotent RPT.RELATIONS appends."""
    return json.dumps(violations, sort_keys=True, ensure_ascii=False)


def last_relations_signature(chain_entries):
    for e in reversed(chain_entries):
        if e.get("intent") == "RPT.RELATIONS":
            return violation_signature(e.get("violations") or [])
    return None


def append_relations_chain(chain_path, relations):
    """Append intent=RPT.RELATIONS (v2 schema). Idempotent on identical
    violation sets. Returns the entry, or None when skipped."""
    if not relations["violations"]:
        return None
    entries = jsonl_load(chain_path)
    if entries and last_relations_signature(entries) == \
            violation_signature(relations["violations"]):
        return None
    prev_seq = entries[-1].get("seq", 0) if entries else 0
    prev_hash = entries[-1].get("hash", GENESIS) if entries else GENESIS
    entry = {"seq": prev_seq + 1, "ts": relations["ts"],
             "intent": "RPT.RELATIONS",
             "replay_ok": relations["replay_ok"],
             "conservation_ok": relations["conservation_ok"],
             "dag_ok": relations["dag_ok"],
             "basis_candidates": len(relations["basis_candidates"]),
             "violations": relations["violations"],
             "note": "NMUST-04 §3 relations check: violation(s) detected; "
                     "see federation oblig view relations field",
             "prev": prev_hash}
    entry["hash"] = hashlib.sha256(
        (prev_hash + canon_v2(entry)).encode()).hexdigest()
    with open(chain_path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def merge_view_local(root, relations):
    """Merge the relations field into the local view mirror (if present)."""
    path = os.path.join(root, VIEW_MIRROR)
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            view = json.load(f)
    except json.JSONDecodeError:
        return False
    view["relations"] = relations
    with open(path, "w") as f:
        f.write(json.dumps(view, ensure_ascii=False, indent=1,
                           sort_keys=True) + "\n")
    return True


def print_summary(relations, chain_entry=None):
    rep = relations
    print(f"relations check {rep['ts']}: "
          f"replay_ok={rep['replay_ok']} "
          f"conservation_ok={rep['conservation_ok']} "
          f"dag_ok={rep['dag_ok']} "
          f"basis_candidates={len(rep['basis_candidates'])} "
          f"violations={len(rep['violations'])}")
    for c in rep["replay"]["chains"]:
        print(f"  R3 {c['chain']}: status={c.get('status', 'ok')} "
              f"verified={c['verified']}/{c['entries']} "
              f"first_break={c['first_break']}")
    con = rep["conservation"]
    print(f"  R4 ledger={con['ledger']} derived={con['derived']} "
          f"mismatch={len(con['mismatch'])}")
    print(f"  R6 primitives={rep['basis']['primitives']} "
          f"candidates={[c['class'] for c in rep['basis_candidates']]}")
    print(f"  R7 nodes={rep['dag']['nodes']} topo_ok={rep['dag']['topo_ok']} "
          f"cycle={rep['dag'].get('cycle')} "
          f"missing_deps={rep['dag'].get('missing_deps')}")
    for v in rep["violations"]:
        print(f"::warning::RELATIONS VIOLATION {v['check']} "
              f"{v['kind']}: {json.dumps(v, ensure_ascii=False)[:300]}")
    if chain_entry:
        print(f"  chain: RPT.RELATIONS seq={chain_entry['seq']} appended")


# ------------------------------------------------------------- selftest ----

def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def _jl(objs):
    return "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in objs)


def _mkchain(bodies):
    """Build a valid v2 chain from body dicts (seq auto, ts fixed)."""
    out, prev = [], GENESIS
    for i, b in enumerate(bodies, 1):
        e = {"seq": i, "ts": f"2026-08-25T00:00:{i:02d}Z", **b, "prev": prev}
        e["hash"] = hashlib.sha256(
            (prev + canon_v2(e)).encode()).hexdigest()
        prev = e["hash"]
        out.append(e)
    return out


def _mkoutbox(bodies):
    """Build a valid narrative chain (12-char hashes, one hmac field)."""
    out, prev = [], OUTBOX_GENESIS
    for i, b in enumerate(bodies, 1):
        e = {"seq": i, **b, "prev": prev}
        if i == 2:
            e["hmac"] = "deadbeef"
        e["hash"] = hashlib.sha256(
            (prev + outbox_canon(e)).encode()).hexdigest()[:12]
        prev = e["hash"]
        out.append(e)
    return json.dumps(out, ensure_ascii=False)


def _fixture(root):
    """Clean sandbox fixture: valid chain, conserved ledger, DAG roadmap,
    full basis coverage. Returns (ledger, chain, outbox_text)."""
    ledger = [
        {"id": "o-a", "src": "INCIDENT seq1 (test)", "state": "legislated",
         "evidence": [], "domain": "machine", "opened": "2026-08-25T00:00:00Z"},
        {"id": "o-b", "src": "kit/INDEX.md F9 admonition: t", "state": "raised",
         "evidence": [], "domain": "machine", "opened": "2026-08-25T00:00:00Z"},
    ]
    chain = _mkchain([
        {"arm": "n1", "pi": None, "score": 0.1},
        {"intent": "RPT.OBLIG", "oid": "o-a", "from": "raised",
         "to": "legislated", "note": "t", "queue": "machine"},
    ])
    roadmap = {"nodes": [{"id": "n1", "deps": []},
                          {"id": "n2", "deps": ["n1"]},
                          {"id": "n3", "deps": ["n2"]}]}
    basis = [{"id": "b-001", "rule": "r", "introduced": "2026-08-25",
              "covers": {"chain-intent": 1}},
             {"id": "b-002", "rule": "r", "introduced": "2026-08-25",
              "covers": {"kit-admonition": 1}}]
    _w(os.path.join(root, LEDGER), _jl(ledger))
    _w(os.path.join(root, CHAIN), "# v2: hash=sha256(prev+canon)\n" + _jl(chain))
    _w(os.path.join(root, ROADMAP), json.dumps(roadmap))
    _w(os.path.join(root, BASIS), _jl(basis))
    _w(os.path.join(root, VIEW_MIRROR), json.dumps({"ts": "t", "per_repo": {}}))
    return ledger, chain, _mkoutbox([{"note": "s1"}, {"note": "s2"}])


def selftest():
    """Sandbox violation-path tests (temp dir, no network, no repo writes)."""
    with tempfile.TemporaryDirectory() as td:
        # --- clean fixture: all four green ---------------------------------
        fx = os.path.join(td, "clean")
        ledger, chain, outbox = _fixture(fx)
        rel, _ = build_relations(fx, offline=True, outbox_text=outbox)
        assert rel["replay_ok"], "clean fixture replay must pass"
        assert rel["conservation_ok"], "clean fixture conservation must pass"
        assert rel["dag_ok"], "clean fixture dag must pass"
        assert not rel["violations"] and not rel["basis_candidates"]
        ob = [c for c in rel["replay"]["chains"] if c["chain"] == "usrm-outbox"][0]
        assert ob["verified"] == 2 and ob["hmac_present"] == 1
        # no violations -> no chain append
        assert append_relations_chain(os.path.join(fx, CHAIN), rel) is None

        # --- R3: broken v2 chain -------------------------------------------
        fx = os.path.join(td, "broken")
        _fixture(fx)
        p = os.path.join(fx, CHAIN)
        rows = [l for l in open(p).read().splitlines() if not l.startswith("#")]
        bad = json.loads(rows[1])
        bad["score"] = 9.9  # tamper body without rehashing
        rows[1] = json.dumps(bad, ensure_ascii=False)
        _w(p, "# v2: hash=sha256(prev+canon)\n" + "\n".join(rows) + "\n")
        rel, _ = build_relations(fx, offline=True)
        assert not rel["replay_ok"], "tampered chain must break replay"
        v = [v for v in rel["violations"] if v["check"] == "R3"][0]
        assert v["first_break"] == 2 and v["verified"] == 1

        # --- RPT.RELATIONS append on a VALID chain (R4 violation) ----------
        fx = os.path.join(td, "append")
        ledger, chain, _ = _fixture(fx)
        ledger[0]["state"] = "raised"  # imbalance but chain itself valid
        _w(os.path.join(fx, LEDGER), _jl(ledger))
        rel, _ = build_relations(fx, offline=True)
        assert rel["violations"] and rel["replay_ok"]
        p = os.path.join(fx, CHAIN)
        e = append_relations_chain(p, rel)
        assert e and e["intent"] == "RPT.RELATIONS" and e["seq"] == 3
        assert replay_v2_chain(p)["first_break"] is None, \
            "chain with RPT.RELATIONS must still replay clean"
        # idempotent: same violation set -> no duplicate
        assert append_relations_chain(p, rel) is None
        # changed violation set -> a new entry
        rel["ts"] = "2026-08-25T01:00:00Z"
        rel["violations"] = rel["violations"] + [{"check": "R7", "kind": "依赖环"}]
        assert append_relations_chain(p, rel) is not None

        # --- R3b: broken narrative chain ------------------------------------
        outbox_bad = json.loads(_mkoutbox([{"note": "a"}, {"note": "b"}]))
        outbox_bad[1]["note"] = "tampered"
        rep = replay_outbox_chain(json.dumps(outbox_bad))
        assert rep["first_break"] == 2 and rep["verified"] == 1

        # --- R4: conservation imbalance -------------------------------------
        fx = os.path.join(td, "imbalance")
        ledger, chain, _ = _fixture(fx)
        ledger[0]["state"] = "raised"  # ledger rolled back, chain says legislated
        _w(os.path.join(fx, LEDGER), _jl(ledger))
        rel, _ = build_relations(fx, offline=True)
        assert not rel["conservation_ok"]
        v = [v for v in rel["violations"] if v["check"] == "R4"][0]
        assert v["kind"] == "对称破缺" and v["mismatch"][0]["oid"] == "o-a"
        # orphan chain oid also trips conservation
        rep, v = check_conservation(
            [{"id": "o-z", "state": "raised", "src": "chain seq1 WARN entry"}],
            [{"intent": "RPT.OBLIG", "oid": "o-ghost", "from": "raised",
              "to": "wontfix", "seq": 1}])
        assert v and v[0]["orphan_chain_oids"] == ["o-ghost"]

        # --- R6: basis-incompleteness candidate ------------------------------
        fx = os.path.join(td, "basis")
        ledger, chain, _ = _fixture(fx)
        ledger.append({"id": "o-c", "src": "root-action rotate", "state": "raised",
                       "evidence": [], "domain": "human",
                       "opened": "2026-08-25T00:00:00Z"})
        _w(os.path.join(fx, LEDGER), _jl(ledger))
        rel, changed = build_relations(fx, offline=True)
        assert rel["violations"] == [], "basis candidates are NOT violations"
        cls = [c["class"] for c in rel["basis_candidates"]]
        assert cls == ["root-action"], f"unexpected candidates: {cls}"
        assert "不自动加基" in rel["basis_candidates"][0]["suggestion"]

        # --- R7: dependency cycle --------------------------------------------
        fx = os.path.join(td, "cycle")
        _fixture(fx)
        _w(os.path.join(fx, ROADMAP), json.dumps({"nodes": [
            {"id": "n1", "deps": ["n3"]}, {"id": "n2", "deps": ["n1"]},
            {"id": "n3", "deps": ["n2"]}, {"id": "n4", "deps": ["ghost"]}]}))
        rel, _ = build_relations(fx, offline=True)
        assert not rel["dag_ok"]
        v = [v for v in rel["violations"] if v["check"] == "R7"][0]
        assert v["cycle"] == ["n1", "n2", "n3"]
        assert rel["dag"]["missing_deps"] == ["ghost"], \
            "unknown dep is a warning, not a cycle"

        # --- view merge round-trip -------------------------------------------
        fx = os.path.join(td, "clean")
        rel, _ = build_relations(fx, offline=True)
        assert merge_view_local(fx, rel)
        view = json.load(open(os.path.join(fx, VIEW_MIRROR)))
        for key in ("replay_ok", "conservation_ok", "basis_candidates",
                    "dag_ok", "violations"):
            assert key in view["relations"], f"relations.{key} missing"
    print("selftest: R3 break / R3b narrative break / R4 imbalance / "
          "R6 candidate / R7 cycle / chain append idempotence / "
          "view merge -- all OK")


# ----------------------------------------------------------------- main ----

def main():
    ap = argparse.ArgumentParser(
        description="NMUST-04 §3 relations check (R3/R4/R6/R7)")
    ap.add_argument("--offline", action="store_true",
                    help="sandbox: no network; local reads/writes under --root")
    ap.add_argument("--selftest", action="store_true",
                    help="fixture violation-path tests in a temp dir")
    ap.add_argument("--root", default=".",
                    help="repo root (default: cwd)")
    ap.add_argument("--outbox", default=None,
                    help="read narrative chain from a local file instead of "
                         "the network (offline fixtures)")
    ap.add_argument("--no-write", action="store_true",
                    help="compute and print only; no view/chain/basis writes")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0

    root = args.root
    outbox_text = None
    if args.outbox:
        with open(args.outbox) as f:
            outbox_text = f.read()

    relations, basis_changed = build_relations(
        root, offline=args.offline, outbox_text=outbox_text,
        write_basis=not args.no_write)

    chain_entry = None
    if relations["violations"] and not args.no_write:
        chain_entry = append_relations_chain(os.path.join(root, CHAIN),
                                             relations)
    if not args.no_write:
        merge_view_local(root, relations)

    if not args.offline and not args.no_write:
        # Federation writes: fresh view from first readable target, merge
        # relations, write back to all targets (same as oblig_monitor);
        # chain + basis committed to vci-usrm via contents API.
        import oblig_monitor as om
        if not om.TOKEN:
            print("::warning::no CI_ROOT_TOKEN/GH_TOKEN; federation API "
                  "writes skipped (local state already updated)")
        else:
            prev = None
            for repo, path in om.view_targets():
                old = om.get_text(repo, path)
                if old:
                    try:
                        prev = json.loads(old)
                        break
                    except json.JSONDecodeError:
                        continue
            if prev is None:
                print("::warning::no readable view target; relations not "
                      "merged upstream this round")
            else:
                prev["relations"] = relations
                payload = json.dumps(prev, ensure_ascii=False, indent=1,
                                     sort_keys=True) + "\n"
                msg = (f"federation: relations {relations['ts']} "
                       f"(NMUST-04 §3) [skip ci]")
                for repo, path in om.view_targets():
                    ok, _ = om.put_file(repo, path, payload, msg)
                    print(f"relations view -> {repo}/{path}: "
                          f"{'ok' if ok else 'FAILED'}")
            if chain_entry is not None:
                # re-read remote chain, append the same entry shape on its tail
                remote = om.get_text(om.REPO_USRM, CHAIN)
                if remote is not None:
                    rlines = [l for l in remote.splitlines()
                              if l.strip() and not l.startswith("#")]
                    rlast = json.loads(rlines[-1]) if rlines else None
                    if rlast and rlast.get("hash") == chain_entry["prev"]:
                        ok, _ = om.put_file(
                            om.REPO_USRM, CHAIN,
                            remote.rstrip("\n") + "\n"
                            + json.dumps(chain_entry, ensure_ascii=False)
                            + "\n",
                            f"ure: RPT.RELATIONS seq{chain_entry['seq']} "
                            "(NMUST-04 §3 violations) [skip ci]")
                        print(f"chain RPT.RELATIONS -> {om.REPO_USRM}: "
                              f"{'ok' if ok else 'FAILED (retry next round)'}")
                    else:
                        print("::warning::remote chain tail moved; local "
                              "RPT.RELATIONS kept, remote append deferred")
            if basis_changed:
                with open(os.path.join(root, BASIS)) as f:
                    ok, _ = om.put_file(om.REPO_USRM, BASIS, f.read(),
                                        "ure: basis covers counts refresh "
                                        "(NMUST-04 §3 R6) [skip ci]")
                print(f"basis refresh -> {om.REPO_USRM}: "
                      f"{'ok' if ok else 'FAILED'}")

    print_summary(relations, chain_entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
