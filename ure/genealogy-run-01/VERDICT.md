# GENEALOGY-RUN-01-E1 判词（H7.2）

**注册编号**：GENEALOGY-RUN-01-E1。**预测**：开跑前于 Π 相位 preregistration 在案——三命题可望全 PASS。**实验指针**：构造件 evidence-obl1/2/3.json＋证书 certificates.json 为锚；全程熵锚=last-good qrand@seq61（锚停滞在案，降级声明随锚）。**结果**：三命题全 PASS。**状态**：判闭合，verdict_hash=ae6c6c1cff7c，已回注 obligations.json 闭账；5 路签名齐全，3-of-5 阈值机检达成（5/5）。

## 三命题结果表

| 命题 | 结果 | 复算摘要 |
|---|---|---|
| OBL-1 链复算 | PASS | seq170→190 独立重算 21 条全对，tip=af470d11516b 与存储一致 |
| OBL-2 注册表 | PASS | 27 实例 inst_id 唯一；goal_vec 皆四维或 null（CONVERGED 豁免） |
| OBL-3 信标 | PASS | qrand 与定格值一致且 seq=61，独立复检通过 |

## z3 两式（z3 5.1.0）

模型=三命题×四状态（DECLARED→CONSTRUCTED→VERIFIED→JUDGED）小型状态机，每步原地或进一，commit/challenge 绑定首达构造/验证之步号。式一（I1）：「存在到达 JUDGED 而未过 VERIFIED 的执行」→UNSAT，成立；式二（I2）：「commit_ts≥challenge_ts 仍通过」→UNSAT，成立。统计剔 time/memory 保确定性，落 z3_results.json。

## 不变量机检声明

I1 双保险：J 相位显式 assert 三件全 PASS 证书及前级工件齐全（硬闸），且 z3 式一 UNSAT。I2：z3 式二 UNSAT，锚 seq61≤挑战（种子由 seq61 定格公式派生）。I3：判词回注 obligations.json，三命题 status=closed、verdict_ref 同上，闭账在案。

## 资源账

transcript 六节哈希链自校回放 OK，tip=8fc607888bece60f。总 wall=119.37ms、输出 14490 字节、cost_acc=0.001194 元（名义折算，toy 费率 0.01 元/机时秒，非真实计费）；z3 相位 106.8ms 为最大开销。

## 确定性

实跑两次，归一化 ts/cost 后比对：normalized_equal=True，六节哈希逐节一致，两跑 tip 相同。

## 诚实档

①toy 签名档：role_i_sig=sha256(qrand‖role_i‖verdict_hash)[:12]，3-of-5 仅机检计数，非密码学签名，不抗伪造。②锚停滞在案：beacon-mirror 定格 seq61，挑战种子=int(sha256(qrand‖str(61))[:8]hex,16)=3712427753 定格可复算，非新鲜熵。③小型状态机编码非全链形式化【候】：z3 仅覆盖跃迁结构抽象层，未形式化哈希链内容与文件 IO。④cost_acc 为名义机时折算，费率自定义，非真实计费凭证。
