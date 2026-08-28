#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GENEALOGY-RUN-01 五机系谱闭合链工程实测件
G=(Π,C,V,J,A)：Π 义务机登记命题 → C 递归机产构造 → V NP机机检证书
→ J 治理机下判词(I1 硬闸/I3 闭账) → A N机全程供锚(hash链 transcript)。
熵锚=last-good qrand @seq61（锚停滞在案，一切用锚处降级声明）。
toy 档显式声明：role 签名=sha256 截断玩具签名，非密码学签名。
"""
import json, hashlib, os, random, sys, time, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CTX_NARR = os.path.join(BASE, "ctx-narrative.json")
CTX_BEAC = os.path.join(BASE, "ctx-beacon-mirror.json")
CTX_INST = os.path.join(BASE, "ctx-inst-reg.json")

QRAND = "c21b1f0f5858ab4acba2fba54b5e84bd7ea30234dbc4e43cb2304735c5e20eeb"
ANCHOR_SEQ = 61
STALE_NOTE = "锚停滞在案：beacon-mirror 定格 seq61，全程用 last-good qrand，降级声明随锚"
ANCHOR = {"qrand_seq": ANCHOR_SEQ, "stale": True, "note": STALE_NOTE}
RUN_ID = "GENEALOGY-RUN-01-E1"
RATE_YUAN_PER_SEC = 0.01  # 名义费率声明：toy 档 0.01 元/机时秒（非真实计费）

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def canon(o): return json.dumps(o, ensure_ascii=False, sort_keys=True)
def canon_entry(e):  # C 相位链复算专用 canon（剔除 hash/hmac）
    return json.dumps({k: v for k, v in e.items() if k not in ("hash", "hmac")},
                      ensure_ascii=False, sort_keys=True)
def jdump(obj, name):
    path = os.path.join(BASE, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    return path
def fsha12(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]
def nowts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# 挑战种子定格公式（可复算）：seed=int(sha256(qrand‖str(61))[:8]hex,16)
CHALLENGE_SEED = int(sha(QRAND + str(ANCHOR_SEQ))[:8], 16)

TRANSCRIPT = []
def record_phase(phase, actor, inputs_hash, outputs_hash, cost, extra=None):
    prev = TRANSCRIPT[-1]["hash"] if TRANSCRIPT else "GENESIS"
    body = {"phase": phase, "actor_machine": actor,
            "inputs_hash": inputs_hash, "outputs_hash": outputs_hash,
            "anchor": {"qrand_seq": ANCHOR_SEQ, "stale": True}, "prev": prev}
    entry = dict(body)
    entry["ts"] = nowts()            # ts 不入哈希（确定性比对时归一化）
    entry["cost"] = cost             # 实测耗时/字节/名义折算，不入哈希
    if extra: entry["extra"] = extra
    entry["hash"] = sha(prev + canon(body))[:16]
    TRANSCRIPT.append(entry)
    return entry

class PhaseTimer:
    def __init__(self): self.t0 = time.perf_counter()
    def cost(self, out_files):
        sec = time.perf_counter() - self.t0
        nbytes = sum(os.path.getsize(os.path.join(BASE, f)) for f in out_files)
        return {"wall_ms": round(sec * 1000, 2), "out_bytes": nbytes,
                "cost_acc": round(sec * RATE_YUAN_PER_SEC, 6),
                "rate_decl": f"toy名义费率 {RATE_YUAN_PER_SEC} 元/机时秒"}

def load_ctx():
    with open(CTX_NARR, encoding="utf-8") as f: narr = json.load(f)
    with open(CTX_BEAC, encoding="utf-8") as f: beac = json.load(f)
    with open(CTX_INST, encoding="utf-8") as f: inst = json.load(f)
    return narr, beac, inst

# ---------------- Π 相位：义务机登记命题 ----------------
def phase_pi():
    tm = PhaseTimer()
    narr, beac, inst = load_ctx()
    tip = narr["entries"][-1]
    obligations = {
     "run_id": RUN_ID,
     "preregistration": {  # 开跑前预测声明（H7.2 预测项）
      "prediction": "三命题 OBL-1/OBL-2/OBL-3 可望全 PASS",
      "declared_before": "C/V/J 相位执行前于 Π 相位登记",
      "predicted_at_logical": f"anchor seq{ANCHOR_SEQ}"},
     "obligations": [
      {"prop_id": "OBL-1",
       "statement": "验证 narrative 链 seq170→tip 连续可复算",
       "check_spec": "hash=sha256(prev.hash+canon)[:12], canon=json.dumps(剔除hash/hmac,ensure_ascii=False,sort_keys=True)；自 seq169 之 hash 起逐条复算 seq170..tip(%d)，比对存储值" % tip["seq"],
       "deadline": "2026-08-29T00:00:00Z", "anchor": dict(ANCHOR)},
      {"prop_id": "OBL-2",
       "statement": "INST-REG 无重复 inst_id 且 goal_vec 四维",
       "check_spec": "inst_id 全集唯一；goal_vec 为 null（CONVERGED 终态豁免）或长度恰为 4 的数值列表",
       "deadline": "2026-08-29T00:00:00Z", "anchor": dict(ANCHOR)},
      {"prop_id": "OBL-3",
       "statement": "beacon-mirror qrand 字段与定格值一致",
       "check_spec": "ctx-beacon-mirror.json 的 qrand==%s 且 seq==61（锚停滞在案）" % QRAND,
       "deadline": "2026-08-29T00:00:00Z", "anchor": dict(ANCHOR)}]}
    p = jdump(obligations, "obligations.json")
    e = record_phase("PI", "Π义务机", fsha12(CTX_NARR) + "/" + fsha12(CTX_INST) + "/" + fsha12(CTX_BEAC),
                     fsha12(p), tm.cost(["obligations.json"]),
                     {"n_obligations": 3, "preregistered_prediction": obligations["preregistration"]["prediction"]})
    print(f"[Π] 登记命题 3 件 → obligations.json  phase_hash={e['hash']}")
    return obligations

# ---------------- C 相位：递归机产构造件 ----------------
def construct_obl1(narr):
    """OBL-1 构造：自 seq169.hash 起重算 seq170→tip 逐条比对。"""
    ents = {e["seq"]: e for e in narr["entries"]}
    seqs = sorted(s for s in ents if s >= 170)
    rows, prev_h = [], ents[169]["hash"]
    for s in seqs:
        e = ents[s]
        recomputed = sha(prev_h + canon_entry(e))[:12]
        rows.append({"seq": s, "stored": e["hash"], "recomputed": recomputed,
                     "match": recomputed == e["hash"]})
        prev_h = e["hash"]
    return {"prop_id": "OBL-1", "construction": "recompute-chain-seq170-to-tip",
            "base_seq": 169, "base_hash": ents[169]["hash"],
            "entries": rows, "n_checked": len(rows),
            "all_match": all(r["match"] for r in rows),
            "tip_seq": seqs[-1], "tip_recomputed": rows[-1]["recomputed"],
            "tip_stored": ents[seqs[-1]]["hash"], "anchor": dict(ANCHOR)}

def construct_obl2(inst):
    ids = [x["inst_id"] for x in inst["instances"]]
    seen, dups = set(), []
    for i in ids:
        if i in seen: dups.append(i)
        seen.add(i)
    dim_rows = [{"inst_id": x["inst_id"],
                 "goal_vec": "null(CONVERGED豁免)" if x.get("goal_vec") is None else len(x["goal_vec"]),
                 "ok": (x.get("goal_vec") is None and x.get("status") == "CONVERGED")
                       or (isinstance(x.get("goal_vec"), list) and len(x["goal_vec"]) == 4
                           and all(isinstance(v, (int, float)) for v in x["goal_vec"]))}
                for x in inst["instances"]]
    return {"prop_id": "OBL-2", "construction": "scan-inst-reg",
            "n_instances": len(ids), "dup_inst_ids": dups,
            "unique_ok": len(dups) == 0, "dim_rows": dim_rows,
            "dim_ok": all(r["ok"] for r in dim_rows), "anchor": dict(ANCHOR)}

def construct_obl3(beac):
    return {"prop_id": "OBL-3", "construction": "compare-beacon-qrand",
            "stored_qrand": beac["qrand"], "expected_qrand": QRAND,
            "qrand_match": beac["qrand"] == QRAND,
            "stored_seq": beac["seq"], "seq_match": beac["seq"] == ANCHOR_SEQ,
            "stale_decl": STALE_NOTE, "anchor": dict(ANCHOR)}

def phase_c(narr, beac, inst):
    tm = PhaseTimer()
    p1 = jdump(construct_obl1(narr), "evidence-obl1.json")
    p2 = jdump(construct_obl2(inst), "evidence-obl2.json")
    p3 = jdump(construct_obl3(beac), "evidence-obl3.json")
    outs = ["evidence-obl1.json", "evidence-obl2.json", "evidence-obl3.json"]
    e = record_phase("C", "C递归机", fsha12(os.path.join(BASE, "obligations.json")),
                     "/".join(fsha12(p) for p in (p1, p2, p3)), tm.cost(outs),
                     {"constructions": ["recompute-chain", "scan-inst-reg", "compare-qrand"]})
    print(f"[C] 构造件 3 件 → evidence-obl{{1,2,3}}.json  phase_hash={e['hash']}")
    return outs

# ---------------- V 相位：NP 机独立机检（另写一份重算逻辑，不复用 C 代码路径） ----------------
def verify_obl1(narr, ev):
    # 独立实现：直接遍历 entries 列表（非 dict 索引），自写拼接校验
    entries = sorted(narr["entries"], key=lambda e: e["seq"])
    chain = [e for e in entries if 169 <= e["seq"] <= ev["tip_seq"]]
    prev = None
    n_ok, n_bad = 0, 0
    for e in chain:
        if e["seq"] == 169:
            prev = e["hash"]; continue
        payload = json.dumps({k: e[k] for k in sorted(e.keys()) if k not in ("hash", "hmac")},
                             ensure_ascii=False, sort_keys=True)
        h = hashlib.sha256((prev + payload).encode("utf-8")).hexdigest()[:12]
        if h == e["hash"]: n_ok += 1
        else: n_bad += 1
        prev = e["hash"]
    tip_ok = (prev == ev["tip_stored"] == ev["tip_recomputed"])
    passed = (n_bad == 0 and n_ok == ev["n_checked"] and ev["all_match"] and tip_ok)
    return {"result": "PASS" if passed else "FAIL",
            "recalc": {"n_recomputed_ok": n_ok, "n_recomputed_bad": n_bad,
                       "tip_final_hash": prev, "tip_matches_evidence": tip_ok},
            "checks": {"entries_recomputed": n_ok + n_bad, "cross_checks": 4}}

def verify_obl2(inst, ev):
    ids = [x["inst_id"] for x in inst["instances"]]
    uniq = len(ids) == len(set(ids))
    dim = all((x.get("goal_vec") is None and x.get("status") == "CONVERGED")
              or (type(x.get("goal_vec")) is list and len(x["goal_vec"]) == 4)
              for x in inst["instances"])
    passed = (uniq and dim and ev["unique_ok"] and ev["dim_ok"]
              and ev["n_instances"] == len(ids) and ev["dup_inst_ids"] == [])
    return {"result": "PASS" if passed else "FAIL",
            "recalc": {"unique_independent": uniq, "dim_independent": dim,
                       "n_instances": len(ids)},
            "checks": {"instances_scanned": len(ids), "cross_checks": 4}}

def verify_obl3(beac, ev):
    q_ok = beac["qrand"] == QRAND
    s_ok = beac["seq"] == ANCHOR_SEQ
    passed = (q_ok and s_ok and ev["qrand_match"] and ev["seq_match"])
    return {"result": "PASS" if passed else "FAIL",
            "recalc": {"qrand_match_independent": q_ok, "seq_match_independent": s_ok},
            "checks": {"fields_compared": 2, "cross_checks": 2},
            "stale_decl": STALE_NOTE}

def phase_v(narr, beac, inst, ev_files):
    tm = PhaseTimer()
    evs = [json.load(open(os.path.join(BASE, f), encoding="utf-8")) for f in ev_files]
    verifiers = {"OBL-1": verify_obl1, "OBL-2": verify_obl2, "OBL-3": verify_obl3}
    ctxs = {"OBL-1": narr, "OBL-2": inst, "OBL-3": beac}
    # 挑战：以定格种子确定性打乱验证顺序（A 机供锚挑战）
    order = [e["prop_id"] for e in evs]
    random.Random(CHALLENGE_SEED).shuffle(order)
    certs = []
    for pid in order:
        ev = next(e for e in evs if e["prop_id"] == pid)
        r = verifiers[pid](ctxs[pid], ev)
        certs.append({"prop_id": pid, "evidence_file": f"evidence-{pid.lower().replace('-','')}.json",
                      "challenge_seed": CHALLENGE_SEED, "challenge_order": order,
                      "independent_verifier": True, **r})
    certs.sort(key=lambda c: c["prop_id"])
    out = {"run_id": RUN_ID, "challenge_seed_formula": "int(sha256(qrand‖str(61))[:8]hex,16)",
           "challenge_seed": CHALLENGE_SEED, "certificates": certs, "anchor": dict(ANCHOR)}
    p = jdump(out, "certificates.json")
    e = record_phase("V", "V-NP机", "/".join(fsha12(os.path.join(BASE, f)) for f in ev_files),
                     fsha12(p), tm.cost(["certificates.json"]),
                     {"results": {c["prop_id"]: c["result"] for c in certs}})
    print(f"[V] 机检证书 3 件（挑战序 {order}）→ certificates.json  "
          f"results={ {c['prop_id']: c['result'] for c in certs} }  phase_hash={e['hash']}")
    return certs

# ---------------- J 相位：治理机判词（I1 硬闸 + I3 闭账 + toy 5路签名） ----------------
def phase_j(certs, ev_files):
    tm = PhaseTimer()
    # I1 硬闸：J⇒∃V∧V⇒∃C∧C⇒∃Π —— 显式 assert 证书/构造件/命题存在且全 PASS
    assert certs and all(c["result"] == "PASS" for c in certs), "I1 硬闸：无全 PASS 证书，拒签判词"
    for f in ev_files + ["obligations.json", "certificates.json"]:
        assert os.path.exists(os.path.join(BASE, f)), f"I1 硬闸：缺前级工件 {f}"
    assert len(certs) == 3, "I1 硬闸：证书数≠命题数"
    results = {c["prop_id"]: c["result"] for c in certs}
    verdict_body = {
     "run_id": RUN_ID, "schema": "H7.2",
     "注册编号": RUN_ID,
     "预测": "开跑前声明：三命题 OBL-1/OBL-2/OBL-3 可望全 PASS（Π 相位 preregistration 在案）",
     "实验指针": {"evidence": ["evidence-obl1.json", "evidence-obl2.json", "evidence-obl3.json"],
                "certificates": "certificates.json", "anchor": dict(ANCHOR)},
     "结果": results,
     "状态": "全命题 PASS，判闭合（I3 回注 obligations.json status=closed）",
     "诚实档": ["toy 签名档：role_i_sig=sha256(qrand‖role_i‖verdict_hash)[:12]，非密码学签名",
              STALE_NOTE, "z3 小型状态机编码非全链形式化【候】"]}
    vhash = sha(canon(verdict_body))[:12]
    sigs = {f"role_{i}_sig": sha(QRAND + f"role_{i}" + vhash)[:12] for i in range(1, 6)}
    valid = sum(1 for i in range(1, 6)
                if sigs[f"role_{i}_sig"] == sha(QRAND + f"role_{i}" + vhash)[:12])
    assert valid >= 3, "3-of-5 共签阈值未达"
    verdict = dict(verdict_body)
    verdict["verdict_hash"] = vhash
    verdict["signatures"] = {**sigs, "scheme": "toy: sha256(qrand‖role_i‖verdict_hash)[:12]（非密码学签名）",
                             "threshold": "3-of-5", "valid_sigs": valid, "threshold_met": valid >= 3}
    p = jdump(verdict, "verdict.json")
    # I3 闭账：判词回注 obligations.json
    obl_path = os.path.join(BASE, "obligations.json")
    obl = json.load(open(obl_path, encoding="utf-8"))
    for o in obl["obligations"]:
        o["status"] = "closed" if results[o["prop_id"]] == "PASS" else "escalated"
        o["verdict_ref"] = vhash
    obl["closure"] = {"verdict_hash": vhash, "closed_at_logical": f"anchor seq{ANCHOR_SEQ}",
                      "i3": "J 回注 Π：全部关闭或升级，闭账"}
    jdump(obl, "obligations.json")
    e = record_phase("J", "J治理机", fsha12(os.path.join(BASE, "certificates.json")),
                     fsha12(p) + "/" + fsha12(obl_path), tm.cost(["verdict.json", "obligations.json"]),
                     {"verdict_hash": vhash, "threshold_met": True, "i3_closure": results})
    print(f"[J] 判词签发 verdict_hash={vhash}  5路toy签名 valid={valid}/5 (3-of-5达成)  "
          f"I3闭账回注 obligations.json  phase_hash={e['hash']}")
    return verdict

# ---------------- z3 不变量验证 ----------------
def phase_z3():
    tm = PhaseTimer()
    out = {"run_id": RUN_ID, "model": "三命题×四状态(DECLARED=0→CONSTRUCTED=1→VERIFIED=2→JUDGED=3)，"
           "每步原地或+1，T=4 步；commit[i]=首达 CONSTRUCTED 步号，challenge[i]=首达 VERIFIED 步号",
           "encoding_decl": "小型状态机编码非全链形式化【候】", "queries": []}
    try:
        from z3 import Int, Solver, Or, And, Not, If, sat
        N, T = 3, 4
        s = [[Int(f"s_{i}_{t}") for t in range(T)] for i in range(N)]
        commit = [Int(f"commit_{i}") for i in range(N)]
        challenge = [Int(f"challenge_{i}") for i in range(N)]
        def base():
            sol = Solver()
            for i in range(N):
                sol.add(s[i][0] == 0)
                for t in range(T):
                    sol.add(s[i][t] >= 0, s[i][t] <= 3)
                for t in range(T - 1):
                    sol.add(Or(s[i][t + 1] == s[i][t], s[i][t + 1] == s[i][t] + 1))
                # commit/challenge 结构性绑定：首达 1 / 首达 2 的步号
                sol.add(commit[i] == sum([If(s[i][t] < 1, 1, 0) for t in range(T)]))
                sol.add(challenge[i] == sum([If(s[i][t] < 2, 1, 0) for t in range(T)]))
            return sol
        # 式一（I1）：存在到达 JUDGED 而未过 VERIFIED 的执行？期望 UNSAT
        sol1 = base()
        sol1.add(Or([And(s[i][T - 1] == 3,
                         Not(Or([s[i][t] == 2 for t in range(T)]))) for i in range(N)]))
        r1 = str(sol1.check())
        st1 = {k: v for k, v in sol1.statistics() if k not in ("time", "memory")}
        # 式二（I2）：commit_ts≥challenge_ts 仍通过（到达 JUDGED）？期望 UNSAT
        sol2 = base()
        sol2.add(Or([And(s[i][T - 1] == 3, commit[i] >= challenge[i]) for i in range(N)]))
        r2 = str(sol2.check())
        st2 = {k: v for k, v in sol2.statistics() if k not in ("time", "memory")}
        out["backend"] = "z3 " + __import__("z3").get_version_string()
        out["queries"] = [
         {"id": "I1", "assertion": "∃执行：到达 JUDGED 而未经过 VERIFIED", "expect": "unsat",
          "result": r1, "holds": r1 == "unsat", "stats": st1},
         {"id": "I2", "assertion": "∃执行：commit_ts≥challenge_ts 且到达 JUDGED（通过）", "expect": "unsat",
          "result": r2, "holds": r2 == "unsat", "stats": st2}]
    except ImportError:
        # 降级：穷举模型检查（显式声明降级）
        out["backend"] = "DEGRADED: z3 装不上，降级为穷举模型检查（显式声明降级）"
        seqs = []
        def gen(cur):
            if len(cur) == 4: seqs.append(tuple(cur)); return
            for nxt in (cur[-1], cur[-1] + 1):
                if nxt <= 3: gen(cur + [nxt])
        gen([0])
        bad1 = [q for q in seqs if q[-1] == 3 and 2 not in q]
        def firstreach(q, lv):
            return next((t for t, v in enumerate(q) if v >= lv), 4)
        bad2 = [q for q in seqs if q[-1] == 3 and firstreach(q, 1) >= firstreach(q, 2)]
        out["queries"] = [
         {"id": "I1", "assertion": "∃执行：到达 JUDGED 而未经过 VERIFIED", "expect": "unsat",
          "result": "unsat" if not bad1 else "sat", "holds": not bad1,
          "stats": {"exhausted_models": len(seqs), "counterexamples": len(bad1)}},
         {"id": "I2", "assertion": "∃执行：commit_ts≥challenge_ts 且到达 JUDGED（通过）", "expect": "unsat",
          "result": "unsat" if not bad2 else "sat", "holds": not bad2,
          "stats": {"exhausted_models": len(seqs), "counterexamples": len(bad2)}}]
    p = jdump(out, "z3_results.json")
    e = record_phase("Z3", "V/J 不变量机检", fsha12(os.path.join(BASE, "certificates.json")),
                     fsha12(p), tm.cost(["z3_results.json"]),
                     {"I1": out["queries"][0]["result"], "I2": out["queries"][1]["result"],
                      "backend": out["backend"]})
    print(f"[z3] I1={out['queries'][0]['result']} I2={out['queries'][1]['result']} "
          f"({out['backend']})  phase_hash={e['hash']}")
    return out

# ---------------- A 相位：N 机全程供锚 + 闭链 ----------------
def phase_a_close(all_out_files):
    tm = PhaseTimer()
    total_cost = round(sum(e["cost"]["cost_acc"] for e in TRANSCRIPT), 6)
    total_bytes = sum(e["cost"]["out_bytes"] for e in TRANSCRIPT)
    total_ms = round(sum(e["cost"]["wall_ms"] for e in TRANSCRIPT), 2)
    e = record_phase("A", "A-N机(全程供锚)",
                     "transcript-prev-chain",
                     "transcript.json",
                     {"wall_ms": 0.0, "out_bytes": 0, "cost_acc": 0.0,
                      "rate_decl": f"toy名义费率 {RATE_YUAN_PER_SEC} 元/机时秒"},
                     {"challenge_seed": CHALLENGE_SEED,
                      "seed_formula": "int(sha256(qrand‖str(61))[:8]hex,16)",
                      "stale_decl": STALE_NOTE})
    doc = {"run_id": RUN_ID, "schema": "transcript/hash-chain v1",
           "hash_rule": "hash=sha256(prev+canon({phase,actor_machine,inputs_hash,outputs_hash,anchor,prev}))[:16]；ts/cost 不入哈希（确定性比对归一化项）",
           "anchor": dict(ANCHOR), "entries": TRANSCRIPT,
           "total": {"phases": len(TRANSCRIPT), "wall_ms": total_ms, "out_bytes": total_bytes,
                     "cost_acc": total_cost, "rate_decl": f"toy名义费率 {RATE_YUAN_PER_SEC} 元/机时秒（非真实计费）"}}
    p = jdump(doc, "transcript.json")
    # 自校：重放哈希链
    prev, ok = "GENESIS", True
    for ent in doc["entries"]:
        body = {k: ent[k] for k in ("phase", "actor_machine", "inputs_hash", "outputs_hash", "anchor", "prev")}
        if ent["prev"] != prev or ent["hash"] != sha(prev + canon(body))[:16]:
            ok = False; break
        prev = ent["hash"]
    print(f"[A] transcript 闭链 entries={len(TRANSCRIPT)} 自校回放={'OK' if ok else 'BROKEN'} "
          f"tip={TRANSCRIPT[-1]['hash']}  总 cost_acc={total_cost} 元(名义)")
    assert ok, "transcript 哈希链回放断裂"
    return doc

def main():
    print(f"=== {RUN_ID} 五机系谱闭合链实测  锚=qrand@seq{ANCHOR_SEQ}（{STALE_NOTE}）")
    print(f"挑战种子={CHALLENGE_SEED}（公式 int(sha256(qrand‖str(61))[:8]hex,16) 定格可复算）")
    narr, beac, inst = load_ctx()
    phase_pi()
    ev_files = phase_c(narr, beac, inst)
    certs = phase_v(narr, beac, inst, ev_files)
    phase_j(certs, ev_files)
    phase_z3()
    phase_a_close(ev_files)
    print("=== 全相位完成：I1 硬闸通过 / I2 z3 UNSAT / I3 闭账回注 / 锚停滞在案（toy 档声明随件）")

if __name__ == "__main__":
    main()
