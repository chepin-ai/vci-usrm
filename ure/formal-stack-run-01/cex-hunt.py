#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FORMAL-STACK-RUN-01 器三：ATP 反例狩猎器（搜索层服务验证层）
模型沿用 genealogy-run-01 的状态抽象：三命题×四状态
  DECLARED=0 → CONSTRUCTED=1 → VERIFIED=2 → JUDGED=3，T=4 步；
  commit[i]=首达 CONSTRUCTED 步号，challenge[i]=首达 VERIFIED 步号。
两臂对照 = 「狩猎-修复-回归」闭环实证：
  臂①（含疵变体 FLAWED）：转移关系 seeded 疵——允许一步 +2 跳态（0→2），
      即允许 commit_ts==challenge_ts 的时序倒置路径；
      断言「∃执行：commit_ts≥challenge_ts 且到达 JUDGED」→ 期望 SAT（反例猎获，
      输出反例模型=时序倒置路径，登记为负样本）。
  臂②（无疵变体 SOUND，同 genealogy-run-01 I2）：每步原地或+1；
      同一断言 → 期望 UNSAT（回归臂：修复后无反例）。
诚实档：seeded 疵为教学性注入，非真漏洞；小型状态机编码非全链形式化【候】。
确定性：z3 统计剔 time/memory；本报告无 ts，全量可复算。
"""
import json, os, sys
from z3 import Int, Solver, Or, And, If, sat, unsat

BASE = os.path.dirname(os.path.abspath(__file__))
N, T = 3, 4

def build(flawed):
    """构造状态机；flawed=True 时转移关系注入 +2 跳步疵。"""
    s = [[Int(f"s_{i}_{t}") for t in range(T)] for i in range(N)]
    commit = [Int(f"commit_{i}") for i in range(N)]
    challenge = [Int(f"challenge_{i}") for i in range(N)]
    sol = Solver()
    for i in range(N):
        sol.add(s[i][0] == 0)
        for t in range(T):
            sol.add(s[i][t] >= 0, s[i][t] <= 3)
        for t in range(T - 1):
            if flawed:  # seeded 疵：允许一步 +2 跳态 → commit_ts==challenge_ts 可行
                sol.add(Or(s[i][t + 1] == s[i][t],
                           s[i][t + 1] == s[i][t] + 1,
                           s[i][t + 1] == s[i][t] + 2))
            else:       # 无疵：原地或 +1（同 genealogy-run-01）
                sol.add(Or(s[i][t + 1] == s[i][t], s[i][t + 1] == s[i][t] + 1))
        sol.add(commit[i] == sum([If(s[i][t] < 1, 1, 0) for t in range(T)]))
        sol.add(challenge[i] == sum([If(s[i][t] < 2, 1, 0) for t in range(T)]))
    return sol, s, commit, challenge

def hunt(flawed):
    """断言：∃执行 commit_ts≥challenge_ts 且到达 JUDGED（时序倒置仍通过）。"""
    sol, s, commit, challenge = build(flawed)
    sol.add(Or([And(s[i][T - 1] == 3, commit[i] >= challenge[i]) for i in range(N)]))
    r = sol.check()
    stats = {k: v for k, v in sol.statistics() if k not in ("time", "memory")}
    model_path = None
    if r == sat:
        m = sol.model()
        # 提取反例模型：找一条时序倒置路径（首个满足条件的命题）
        for i in range(N):
            path = [m.eval(s[i][t]).as_long() for t in range(T)]
            c = m.eval(commit[i]).as_long()
            ch = m.eval(challenge[i]).as_long()
            if path[-1] == 3 and c >= ch:
                model_path = {"prop_index": i, "state_path": path,
                              "commit_ts": c, "challenge_ts": ch,
                              "inversion": f"commit_ts({c})>=challenge_ts({ch})："
                                           f"路径 {path} 一步跳态绕过『先构造后验证』时序",
                              "registered_as": "负样本 NEG-I2-INVERSION-01"}
                break
    return str(r), stats, model_path

def main():
    # 臂①：含疵变体 → 期望 SAT（狩猎臂：反例必须存在，否则狩猎器本身失效）
    r_flawed, st_flawed, cex = hunt(flawed=True)
    # 臂②：无疵变体 → 期望 UNSAT（回归臂：修复后同一断言无反例）
    r_sound, st_sound, _ = hunt(flawed=False)

    arms = [
     {"id": "ARM-FLAWED", "variant": "含疵变体：转移允许一步 +2 跳态（seeded 疵，教学性注入）",
      "assertion": "∃执行：commit_ts≥challenge_ts 且到达 JUDGED",
      "expect": "sat", "result": r_flawed, "hit": r_flawed == "sat",
      "counterexample": cex, "stats": st_flawed},
     {"id": "ARM-SOUND", "variant": "无疵变体：每步原地或+1（同 genealogy-run-01 I2 编码）",
      "assertion": "∃执行：commit_ts≥challenge_ts 且到达 JUDGED",
      "expect": "unsat", "result": r_sound, "hit": r_sound == "unsat",
      "counterexample": None, "stats": st_sound}]
    closed_loop = (r_flawed == "sat" and r_sound == "unsat")
    out = {
     "run_id": "FORMAL-STACK-RUN-01-E1",
     "tool": "cex-hunt",
     "backend": "z3 " + __import__("z3").get_version_string(),
     "model": "三命题×四状态(DECLARED=0→CONSTRUCTED=1→VERIFIED=2→JUDGED=3)，T=4 步；"
              "commit/challenge=首达 CONSTRUCTED/VERIFIED 步号",
     "closed_loop": "狩猎-修复-回归：含疵 SAT(猎获反例) ∧ 无疵 UNSAT(修复后无反例) 双中方为闭环",
     "closed_loop_holds": closed_loop,
     "arms": arms,
     "negative_samples": [cex["registered_as"]] if cex else [],
     "honesty": ["seeded 疵（+2 跳态转移）为教学性注入，非 genealogy-run-01 真漏洞",
                 "小型状态机编码非全链形式化【候】：仅覆盖跃迁结构抽象层",
                 "z3 统计剔 time/memory 保确定性；本报告无 ts，全量可复算"]}
    with open(os.path.join(BASE, "cex-results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"[cex-hunt] ARM-FLAWED={r_flawed}(expect sat)  ARM-SOUND={r_sound}(expect unsat)  "
          f"closed_loop={'HOLDS' if closed_loop else 'BROKEN'}")
    if cex:
        print(f"[cex-hunt] 反例猎获：prop{cex['prop_index']} path={cex['state_path']} "
              f"commit_ts={cex['commit_ts']}>=challenge_ts={cex['challenge_ts']} → {cex['registered_as']}")
    return 0 if closed_loop else 1

if __name__ == "__main__":
    sys.exit(main())
