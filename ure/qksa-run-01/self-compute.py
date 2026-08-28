#!/usr/bin/env python3
"""QKSA-RUN-01 测2：自运算四算子实测 → self-compute-report.json

对象基座：qfk-chain-self、usrm-narrative。
纪律：零编数；toy 档显式声明；FORECAST 灰件不跑真数，如实 SKIP。

算子覆盖：
  VERIFY   qfk-chain-self：qfk.chain 建 5-entry 链（payload=survey §3.1 五件名），
           全量重放 verify() + 5 叶 Merkle inclusion proof 逐叶核验。
           诚实注记：TILE=8 规格下 5 entry 未成 tile，prove() 的 tile-checkpoint
           双证路径不适用，故 inclusion 用 qfk.chain.merkle_path/merkle_verify
           在 5 叶集合上直证（仍是 qfk 原语真跑）。
           usrm-narrative：seq190→192 链律复算（toy 档，显式声明）。
  RESIDUAL qfk-chain-self：3 条残差（info/warn/breaking 各一）走
           FindingEngine produce→classify→route，breaking 须人工闸。
  CLOSURE  双基座共用：toy 谱系 DAG（6 节点 5 边）传递闭包 + 断环检测。
  FORECAST 灰件（tensor.factor_forecast 灰件，无真实序列）→ SKIP，不编造。
"""
import hashlib
import json
import sys

sys.path.insert(0, "/mnt/agents/output/wave5")

from qfk.chain import Chain, canon, merkle_path, merkle_root, merkle_verify, sha256  # noqa: E402
from qfk.findings import FindingEngine, make_residual  # noqa: E402

OUT = "/mnt/agents/output/wave5/qksa-run-01/self-compute-report.json"

# survey §3.1 usrm 线五件名（照录）
FIVE_ITEMS = [
    "T58 knowledge_ledger.py",
    "T125 research_net.json",
    "T142 res_search.py",
    "narrative_outbox.json",
    "fullcap 五件(continuity/deliverables-index/file-tensor-net/session-tensor-net/selfcheck)",
]


def op_verify_qfk() -> dict:
    ch = Chain()
    for i, name in enumerate(FIVE_ITEMS):
        ch.append("usrm-line-item", canon({"i": i, "item": name}), ts=1700001000.0 + i)
    replay_ok = ch.verify()
    leaves = [e.hash for e in ch.entries]
    root = merkle_root(leaves)
    proofs = []
    for i, e in enumerate(ch.entries):
        path = merkle_path(leaves, i)
        ok = merkle_verify(e.hash, path, root)
        proofs.append({"seq": i, "item": FIVE_ITEMS[i], "inclusion": ok})
    all_inc = all(p["inclusion"] for p in proofs)
    return {
        "op": "VERIFY", "base": "qfk-chain-self",
        "result": "PASS" if (replay_ok and all_inc and len(proofs) == 5) else "FAIL",
        "evidence": {
            "entries": len(ch.entries),
            "payloads": "survey §3.1 五件名（照录）",
            "replay_verify": replay_ok,
            "merkle_root": root.hex(),
            "inclusion_proofs": proofs,
            "honest_note": "5 entry 未达 TILE=8，tile-checkpoint 双证不适用；inclusion 为 5 叶集合直证（qfk.chain.merkle_* 原语）",
        },
    }


def op_verify_narrative() -> dict:
    """seq190→192 链律复算（toy 档）：hash=sha256(prev.hash+canon)[:12]。
    prev 起点用 seq190 的 toy 前置（非在案真值，显式声明 toy）。"""
    toy_prev = hashlib.sha256(b"toy:narrative:seq189").hexdigest()[:12]
    contents = [(190, "toy 叙事条目 190"), (191, "toy 叙事条目 191"),
                (192, "toy 叙事条目 192")]
    entries = []
    prev = toy_prev
    for seq, content in contents:
        body = {"seq": seq, "content": content, "prev": prev}
        h = hashlib.sha256((prev + canon(body).decode("utf-8")).encode("utf-8")).hexdigest()[:12]
        entries.append({"seq": seq, "hash": h, "prev": prev})
        prev = h
    # 重放复算：从 toy_prev 重算全链，逐节比对
    re_prev = toy_prev
    replay_ok = True
    for e, (_, content) in zip(entries, contents):
        body = {"seq": e["seq"], "content": content, "prev": re_prev}
        h = hashlib.sha256((re_prev + canon(body).decode("utf-8")).encode("utf-8")).hexdigest()[:12]
        if h != e["hash"] or e["prev"] != re_prev:
            replay_ok = False
        re_prev = h
    return {
        "op": "VERIFY", "base": "usrm-narrative",
        "result": "PASS" if replay_ok and entries[-1]["seq"] == 192 else "FAIL",
        "evidence": {
            "toy": True,
            "toy_note": "seq190→192 为自造 3 条 toy entry（prev 起点 toy，非在案真链）；链律复算逻辑为真跑",
            "rule": "hash=sha256(prev.hash+canon(entry))[:12]",
            "entries": entries,
            "replay_ok": replay_ok,
            "reference": "在案真 tip=78f5464a04a0 见 BASE-REG usrm-narrative（本算子不触碰真链）",
        },
    }


def op_residual() -> dict:
    eng = FindingEngine()
    residuals = [
        make_residual("qksa_selftest_info", "self-compute.verify", "info",
                      "informational", "自测信息档残差（type 未登记→开放世界按产出方 severity 放行）", 1),
        make_residual("qksa_selftest_warn", "self-compute.closure", "warn",
                      "soft_mismatch", "自测警告档残差", 2),
        make_residual("qksa_selftest_break", "self-compute.reg", "breaking",
                      "reg_integrity", "自测断路档残差（应路由人工闸）", 3),
    ]
    routed = []
    for r in residuals:
        f = eng.produce(r, "chain")
        routed.append({"id": f.id, "type": f.type, "severity_in": r["severity"],
                       "severity_classified": f.severity, "routed_to": f.routed_to,
                       "human_gate": f.human_gate, "status": f.status})
    brk = [r for r in routed if r["severity_in"] == "breaking"][0]
    ok = (len(routed) == 3
          and all(r["severity_classified"] == r["severity_in"] for r in routed)
          and brk["routed_to"] == "human" and brk["human_gate"] is True
          and all(r["routed_to"] == "auto" for r in routed if r["severity_in"] != "breaking"))
    return {
        "op": "RESIDUAL", "base": "qfk-chain-self",
        "result": "PASS" if ok else "FAIL",
        "evidence": {
            "residuals": routed,
            "loop": "produce→classify→route（FindingEngine 真跑）",
            "breaking_gate": {"routed_to": brk["routed_to"], "human_gate": brk["human_gate"]},
            "note": "type 均为未登记自测名（qksa_selftest_*），走开放世界放行档；分类主循环与 breaking 人工闸路由为真跑",
        },
    }


def op_closure() -> dict:
    """toy 谱系 DAG：T58→T125→T142→qfk→qksa→run01（6 节点 5 边，链状）。"""
    nodes = ["T58", "T125", "T142", "qfk", "qksa", "run01"]
    edges = [("T58", "T125"), ("T125", "T142"), ("T142", "qfk"),
             ("qfk", "qksa"), ("qksa", "run01")]
    # 传递闭包（DFS reachability）
    adj = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)
    closure = {}
    for n in nodes:
        seen, stack = set(), list(adj[n])
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj[x])
        closure[n] = sorted(seen)
    # 断环检测（三色 DFS）
    color = {n: 0 for n in nodes}  # 0=white 1=gray 2=black
    has_cycle = False

    def dfs(u):
        nonlocal has_cycle
        color[u] = 1
        for v in adj[u]:
            if color[v] == 1:
                has_cycle = True
            elif color[v] == 0:
                dfs(v)
        color[u] = 2
    for n in nodes:
        if color[n] == 0:
            dfs(n)
    reach_ok = closure["T58"] == ["T125", "T142", "qfk", "qksa", "run01"] and closure["run01"] == []
    return {
        "op": "CLOSURE", "base": "qfk-chain-self+usrm-narrative(共用 toy 谱系)",
        "result": "PASS" if (reach_ok and not has_cycle) else "FAIL",
        "evidence": {
            "toy": True,
            "toy_note": "谱系 DAG 为自造 toy 档（节点名照录真实谱系号线，边为 toy 声明）",
            "nodes": nodes, "edges": [f"{a}->{b}" for a, b in edges],
            "transitive_closure": closure,
            "cycle_detected": has_cycle,
        },
    }


def op_forecast() -> dict:
    return {
        "op": "FORECAST", "base": "qfk-chain-self",
        "result": "SKIP",
        "evidence": {
            "reason": "灰件不跑真数：qfk.tensor.factor_forecast 为灰件（survey §2 在案），且无真实时间序列可喂；零编数纪律下不编造序列、不产出伪预测",
            "skipped": True,
        },
    }


def main():
    ops = [op_verify_qfk(), op_verify_narrative(), op_residual(), op_closure(), op_forecast()]
    n_pass = sum(1 for o in ops if o["result"] == "PASS")
    n_skip = sum(1 for o in ops if o["result"] == "SKIP")
    n_fail = sum(1 for o in ops if o["result"] == "FAIL")
    doc = {
        "doc": "self-compute-report",
        "run": "QKSA-RUN-01",
        "ops": ops,
        "summary": {"PASS": n_pass, "SKIP": n_skip, "FAIL": n_fail,
                    "note": "VERIFY(qfk)/VERIFY(narrative)/RESIDUAL/CLOSURE 四件全 PASS 且 FORECAST 诚实 SKIP 即测2达标"},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    for o in ops:
        print(f"{o['op']:9s} {o['base']:40s} {o['result']}")
    print(f"summary PASS={n_pass} SKIP={n_skip} FAIL={n_fail}")
    print(f"written={OUT}")


if __name__ == "__main__":
    main()
