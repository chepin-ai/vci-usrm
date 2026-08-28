# FORMAL-STACK-RUN-01-E1 判词（H7.2）——形式化工具链「自指规约」实测

**注册编号**：FORMAL-STACK-RUN-01-E1。
**预测（先行声明）**：①重放全绿——genealogy-run-01 全工件独立重放，transcript 哈希链连续、verdict_hash=ae6c6c1cff7c 三方一致、三命题闭账；②狩猎 SAT——含疵变体「commit_ts≥challenge_ts 且到达 JUDGED」必猎获反例；③无疵 UNSAT——同一断言作用于无疵变体无反例；④对位 diff=0——五机制式契约字段全部在案。
**实验指针**：四器工件为锚——toolchain-manifest.json（manifest_hash=285164e8ff917ca5）、replay-report.json、cex-results.json、contract-report.json；被测对象=/mnt/agents/output/wave5/genealogy-run-01/ 全工件（transcript tip=8fc607888bece60f）；熵锚=last-good qrand@seq61（锚停滞在案，降级声明随锚）。

## 结果逐项

| 器 | 预测 | 实测 | 判定 |
|---|---|---|---|
| 器一 manifest-builder | 13 件登记、谱系 v0.1 创世 | tools=13（GREEN=2/GRAY=11），manifest_hash=285164e8ff917ca5，谱系 v0.1(prev=null)，gap_ledger=11 条 | PASS |
| 器二 replay-regression | 重放全绿 | REGRESSION-GREEN，12/12 检查 PASS（R1 链连续+tip 一致、R2 verdict_hash 五向一致、R3 闭账+证书判词一致+z3 双 UNSAT 在案、R4 种子公式复算一致） | PASS |
| 器三 cex-hunt | 含疵 SAT ∧ 无疵 UNSAT | ARM-FLAWED=**sat**（反例猎获：prop1 path=[0,0,2,3]，commit_ts=2≥challenge_ts=2，登记负样本 NEG-I2-INVERSION-01）；ARM-SOUND=**unsat**；closed_loop=HOLDS | PASS |
| 器四 self-contract-check | 对位 diff=0 | CONTRACT-PASS，写入点 13（7 工件 jdump+6 相位 record_phase）+字段 71，84/84 PASS，diff=0 | PASS |

**状态**：判闭合。四项预测全部命中，无升级项。「狩猎-修复-回归」闭环实证在案：同一断言在含疵变体 SAT（猎获时序倒置反例并登记负样本）、在无疵变体 UNSAT（修复后回归无反例），搜索层（z3 反例搜索）服务验证层（不变量机检）之自指循环跑通。

## 资源账

run-log.txt 实测：ts_start=2026-08-28T21:58:22.342452Z → ts_end=21:58:22.555050Z，总 wall≈213ms（四器串行，含 z3 两次求解）。输出字节：五 JSON+日志合计约 36.7KB（toolchain-manifest 8030B / replay-report 2645B / cex-results 3221B / contract-report 13085B / run-log 870B；四器源码 26837B）。cost_acc≈0.00213 元（名义折算声明：toy 费率 0.01 元/机时秒，非真实计费凭证）。

## 确定性

四件 JSON 输出均无 ts 字段；连跑两轮逐字节 cmp 比对：toolchain-manifest.json / replay-report.json / cex-results.json / contract-report.json 全 DETERMINISTIC（z3 统计已剔 time/memory）。关键输出除 run-log.txt 的 ts 外全量可复算。

## 诚实档

①**toy/原型档**：本实测为教学性原型——manifest 工具表为内置登记表，GRAY=11 件仅注册/引用无实测背书（缺口与验法逐条在 gap_ledger 在案）；kernel-loop/audit-ring 为联邦器官引用，无本地锚。②**seeded 疵为教学性注入非真漏洞**：cex-hunt 含疵变体的「+2 跳态转移」是人为注入，用于验证狩猎器能猎获反例；genealogy-run-01 本体无此疵。③**锚停滞在案**：沿用 genealogy-run-01 last-good qrand@seq61，非新鲜熵，降级声明随锚。④**静态对位非全语义契约【候】**：器四只验「源码写入点存在 ∧ 契约字段在工件 JSON 存在」，字段值级一致性由器二覆盖，完整语义契约（类型/不变式/时序）为缺口#7 后续项。⑤**小型状态机编码非全链形式化【候】**：z3 仅覆盖跃迁结构抽象层，未形式化哈希链内容与文件 IO。⑥cost_acc 为名义机时折算，费率自定义，非真实计费。
