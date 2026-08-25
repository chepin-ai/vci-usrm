# CAPSULE n3 · 规则必形式闭环（P-B 深研蒸馏）

cap_id: n3-rules-01 · 2026-08-25 · 会话端 P-B 产出 · 供 URE n3 节点（规则形式化→ATP 回灌）

## 1. 问题
n3 使命：N-Must/M-Code/Δ-Base 的形式化公式集 → ATP 回灌（规则必形式闭环）。收口判据：教义规则不仅被形式化，且其主要命题获得机器证明，证明件常驻 CI。

## 2. 闭环证据链（全部已发生，本胶囊做收口索引）

| 阶段 | 产物 | 锚点 |
|---|---|---|
| 形式化 | N-Must 8 + M-Code 7 + Δ-Base 3 公式集 + Rules.lean 骨架 | vci-library spec/rules-formal-01（5e853bcd/8d96f0ee） |
| 扩展 | N9-N12 必链公式 + 活性定理 + 证据谓词族 | SPEC-NMUST-01/02 |
| 结构统一 | 八关系范畴学（伴随/忠实/互模拟/自同构/Galois/蕴涵格/偏序/桥） | SPEC-NMUST-04 |
| **ATP 回灌** | P1 七态格 proved｜P2 双队列活性 unsat+单FIFO反迹 sat｜P3 Galois unsat｜P4 编解码正确+正交+降秩泄露反例｜P5 阶梯单调 proved｜P6 Whittle 归纳不变式 unsat | atp/oblig/ + atp/results/2026-08-25.jsonl（run 32833879985/32841980507，24 条结论） |
| 动态化 | 正反互补双轨 + 证出 attest / 反例 residual 入 Gen | SPEC-WALL-01 §4 范式 |

## 3. 论证：闭环的三个判据均满足
1. **表达完备**：教义三元组每条都有 LTL/格论/范畴形式（NMUST 四卷 §1 解构完备性论证）
2. **证明覆盖**：主要设计命题（格结构/队列活性/对偶/穿墙/阶梯/调度不变式）全有机器 verdict；每个"proved"配"反驳失败"对照——不是只挑能证的证
3. **回灌通路**：ATP 结论→链/roadmap 证据→义务闭合→规格立法（K7 执行例）——证明不是摆设，是义务机的法定证据类型（N10 V(tested/verified)）

## 4. 残留（诚实）
- Rules.lean 的 sorry 本体回填（bandit 遗憾界等深度命题）——V3 长征线，STRAT-grounding 已确认全证明器空白，不承诺
- P4 玩具域（F₂⁸）→ 真实 Fernet 语义的规约距离：玩具证的是代数形态，密码强度仍归约到 IND-CPA 假设（声明已入 WALL-01 §2）
- 传播定理（n1 胶囊 §3）形式证明未做 → n4 排期

## 5. 结论句式
规则必形式：已形成。形式必机器判：主要命题已判。判必回灌：通路已立法且通电。**n3 使命达成，申请收口**。
