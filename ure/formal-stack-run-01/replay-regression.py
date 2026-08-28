#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FORMAL-STACK-RUN-01 器二：历史判词重放回归（自指规约·重放层）
独立重新加载 genealogy-run-01 全部工件，不复用其 run.py 代码路径，重算：
  R1 transcript 相位 hash 链连续性（自 GENESIS 起逐节复算，比对存储 hash/prev，核对 tip）
  R2 verdict_hash 与 certificates/obligations 一致性（重算 verdict_hash；三方对拍）
  R3 闭账状态（三命题 status=closed 且 verdict_ref 一致；certificates 结果与判词一致）
  R4 挑战种子定格公式复算（int(sha256(qrand‖str(61))[:8]hex,16) 与证书/转录一致）
全部 PASS → 回归绿；任一不符 → REGRESSION-FAIL 并定位到检查项。
确定性：本报告不含 ts，全量可复算。
"""
import json, hashlib, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(BASE), "genealogy-run-01")
QRAND = "c21b1f0f5858ab4acba2fba54b5e84bd7ea30234dbc4e43cb2304735c5e20eeb"
ANCHOR_SEQ = 61
EXPECT = {  # 来自 GENEALOGY-RUN-01-E1 VERDICT.md / 任务书登记值
 "verdict_hash": "ae6c6c1cff7c",
 "transcript_tip": "8fc607888bece60f",
 "n_obligations": 3}

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def canon(o): return json.dumps(o, ensure_ascii=False, sort_keys=True)
def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return json.load(f)

CHECKS = []
def check(cid, desc, ok, detail):
    CHECKS.append({"id": cid, "desc": desc, "result": "PASS" if ok else "FAIL", "detail": detail})
    return ok

def main():
    transcript = load("transcript.json")
    verdict = load("verdict.json")
    obligations = load("obligations.json")
    certificates = load("certificates.json")
    z3r = load("z3_results.json")

    # ---- R1：transcript 哈希链连续性（独立实现：不复用 run.py 的 record_phase） ----
    prev, chain_ok, bad_at = "GENESIS", True, None
    for idx, ent in enumerate(transcript["entries"]):
        body = {k: ent[k] for k in ("phase", "actor_machine", "inputs_hash",
                                    "outputs_hash", "anchor", "prev")}
        recomputed = hashlib.sha256((prev + json.dumps(body, ensure_ascii=False,
                                     sort_keys=True)).encode("utf-8")).hexdigest()[:16]
        if ent["prev"] != prev or recomputed != ent["hash"]:
            chain_ok, bad_at = False, idx
            break
        prev = ent["hash"]
    check("R1.1", "transcript 六节哈希链自 GENESIS 逐节复算连续",
          chain_ok, f"entries={len(transcript['entries'])} bad_at={bad_at}")
    check("R1.2", "transcript tip 与登记值一致",
          prev == EXPECT["transcript_tip"],
          f"recomputed_tip={prev} expect={EXPECT['transcript_tip']}")
    check("R1.3", "锚件：全程 anchor.qrand_seq==61 且 stale=true（停滞声明随锚）",
          transcript["anchor"]["qrand_seq"] == ANCHOR_SEQ and transcript["anchor"]["stale"]
          and all(e["anchor"]["qrand_seq"] == ANCHOR_SEQ and e["anchor"]["stale"]
                  for e in transcript["entries"]),
          f"top_anchor={transcript['anchor']}")

    # ---- R2：verdict_hash 重算 + 与 certificates/obligations 一致性 ----
    vbody = {k: v for k, v in verdict.items() if k not in ("verdict_hash", "signatures")}
    vhash = sha(canon(vbody))[:12]
    check("R2.1", "verdict_hash 独立重算与存储值一致",
          vhash == verdict["verdict_hash"],
          f"recomputed={vhash} stored={verdict['verdict_hash']}")
    check("R2.2", "verdict_hash 与登记值一致",
          vhash == EXPECT["verdict_hash"], f"expect={EXPECT['verdict_hash']}")
    check("R2.3", "obligations.closure.verdict_hash 与判词一致",
          obligations["closure"]["verdict_hash"] == vhash,
          f"closure={obligations['closure']['verdict_hash']}")
    check("R2.4", "三命题 verdict_ref 全与判词一致",
          all(o["verdict_ref"] == vhash for o in obligations["obligations"]),
          f"refs={[o['verdict_ref'] for o in obligations['obligations']]}")
    jphase = next(e for e in transcript["entries"] if e["phase"] == "J")
    check("R2.5", "transcript J 相位 extra.verdict_hash 与判词一致",
          jphase["extra"]["verdict_hash"] == vhash,
          f"J_extra={jphase['extra']['verdict_hash']}")

    # ---- R3：闭账状态 + 证书/判词结果一致 ----
    cert_results = {c["prop_id"]: c["result"] for c in certificates["certificates"]}
    check("R3.1", "三命题 obligations status 全 closed（I3 闭账）",
          len(obligations["obligations"]) == EXPECT["n_obligations"]
          and all(o["status"] == "closed" for o in obligations["obligations"]),
          f"statuses={[o['status'] for o in obligations['obligations']]}")
    check("R3.2", "certificates 三证书全 PASS 且与判词结果一致",
          cert_results == verdict["结果"] and all(r == "PASS" for r in cert_results.values()),
          f"cert_results={cert_results} verdict={verdict['结果']}")
    check("R3.3", "z3 双 UNSAT 记录在案且 holds=true",
          all(q["result"] == "unsat" and q["holds"] for q in z3r["queries"]),
          f"z3={[(q['id'], q['result']) for q in z3r['queries']]} backend={z3r['backend']}")

    # ---- R4：挑战种子定格公式复算 ----
    seed = int(sha(QRAND + str(ANCHOR_SEQ))[:8], 16)
    aphase = next(e for e in transcript["entries"] if e["phase"] == "A")
    check("R4.1", "挑战种子=int(sha256(qrand‖str(61))[:8]hex,16) 与证书/转录一致",
          seed == certificates["challenge_seed"] == aphase["extra"]["challenge_seed"],
          f"recomputed={seed} cert={certificates['challenge_seed']} A_extra={aphase['extra']['challenge_seed']}")

    n_pass = sum(1 for c in CHECKS if c["result"] == "PASS")
    n_fail = sum(1 for c in CHECKS if c["result"] == "FAIL")
    verdict_str = "REGRESSION-GREEN" if n_fail == 0 else "REGRESSION-FAIL"
    report = {
     "run_id": "FORMAL-STACK-RUN-01-E1",
     "tool": "replay-regression",
     "target": "genealogy-run-01/（GENEALOGY-RUN-01-E1 全工件独立重放）",
     "independence_decl": "本器重算逻辑独立编写，不 import/复用 genealogy-run-01/run.py 任何函数",
     "checks_total": len(CHECKS), "checks_pass": n_pass, "checks_fail": n_fail,
     "regression": verdict_str,
     "fail_locations": [c["id"] for c in CHECKS if c["result"] == "FAIL"],
     "checks": CHECKS,
     "determinism": "本报告无 ts 字段，全量可复算"}
    with open(os.path.join(BASE, "replay-report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"[replay] {verdict_str}  checks={n_pass}/{len(CHECKS)} PASS"
          + (f"  FAIL@={report['fail_locations']}" if n_fail else ""))
    return 0 if n_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
