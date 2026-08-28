# VERDICT · QKSA-RUN-01 首班三测总判

编制: usrm 线工程实测实例（coder）｜ 纪律: 零编数；toy 档显式声明；零网络（pip 除外）
底料: ctx-qksa-survey.md §3-§5 + QFK v0.2 包（/mnt/agents/output/wave5/qfk/）

## 总判: **PASS（3/3）**

| 测 | 对象 | 达标标准 | 结果 | 关键证据 |
|---|---|---|---|---|
| 测1 | base-reg-builder.py → BASE-REG.json | reg_hash 稳定 + 8 基座齐 | **PASS** | reg_hash=`cd7a4ec446e6`（两跑逐字节一致）；8 base_id 全齐无重 |
| 测2 | self-compute.py → self-compute-report.json | 三算子全 PASS | **PASS** | VERIFY(qfk)/VERIFY(narrative)/RESIDUAL/CLOSURE 4 件 PASS，FAIL=0；FORECAST 诚实 SKIP（灰件无真序列，不编造） |
| 测3 | collab-compute.py → collab-report.json | 三协议全 PASS | **PASS** | P1 三跳+dup-skip 正确；P2 reconcile 精确定位漂移叶 sub:leaf05 且 FINDING(drift) 入链；P3 六相位全程真跑 verdict=ACCEPT、3-of-5 judge 共签 settle、m6 入链 seq=3 |

## 测1 明细
- 8 基座五元组齐备（base_id/kind/chain_anchor/self_ops/collab_iface/status）。
- anchor 三档如实标注：`derived`（sha256 占位现算，5 件）、`recorded`（usrm-narrative 在案 tip=78f5464a04a0）、`computed`（qfk-chain-self 用 qfk.chain 真建 3-entry 链取链头，verify()=True）。
- qlv-temperament status=EVAC-候复活（survey §1 evac 档在案）。

## 测2 明细
- VERIFY/qfk-chain-self：5-entry 链（payload=survey §3.1 五件名照录）全量重放 verify()=True；5 叶 Merkle inclusion 逐叶真验全过。诚实注记：5 entry 未达 TILE=8，tile-checkpoint 双证路径不适用，inclusion 为 5 叶集合直证（qfk.chain.merkle_* 原语真跑）。
- VERIFY/usrm-narrative：seq190→192 链律（hash=sha256(prev.hash+canon)[:12]）复算重放一致。**toy 档显式声明**：3 条 entry 自造、prev 起点 toy，不触碰在案真链。
- RESIDUAL：info/warn/breaking 三残差走 FindingEngine produce→classify→route 真跑；breaking 正确路由 routed_to=human + human_gate=True，余两件 auto。
- CLOSURE：toy 谱系 DAG（T58→T125→T142→qfk→qksa→run01，6 节点 5 边）传递闭包正确 + 断环检测无环。**toy 档显式声明**。
- FORECAST：SKIP——tensor.factor_forecast 为灰件且无真实序列，零编数纪律下不跑不编。

## 测3 明细
- P1：toy mailbox（dict）模拟 REQ.RES.SEARCH→清单→REQ.RES.FETCH→RES.REPLY 三跳，每跳带 dtag 幂等键；重放第二跳 dup-skip 正确（mailbox 恒 3 件）。**toy 档显式声明**。
- P2：两棵 prolly-lite 树同 8 叶 + sub:leaf05 漂移；Field.reconcile 返回 DIFF 且 diff==["sub:leaf05"] 精确定位；FINDING(type=drift) 经 FindingEngine 入链（domain=finding），链 verify()=True。
- P3：命题="BASE-REG reg_hash 一致: reg_hash=cd7a4ec446e6"（读测1真产物）；COMMIT→CHALLENGE→WINDOW→RESPOND→JUDGE→SETTLE 六相位真跑，verdict=ACCEPT（residual_score≈0.008<tol，gap=0.01 显式），3 judge 共签过 m-of-n，m6 入链，全链 verify()=True。判词照录：MIP（无星）结构同构工程构造，不升格字面 MIP*。

## 确定性声明
- 测1、测2 **完全确定性**：所有 qfk.chain.append 显式传 ts，无时钟读取；重跑产物逐字节一致（reg_hash=cd7a4ec446e6 三跑稳定）。
- 测3 的 P3 使用 **ephemeral** Ed25519 密钥（进程临时生成）与 beacon 离线 classical-sim 熵（os.urandom）：密钥/熵取值随进程变化，但判词 ACCEPT 由 judge_verdict 纯函数对 (claim,qrand,r1,r2,gap) 裁定，**不依赖密钥/熵具体取值**，不影响判词。P1/P2 无随机源。
- 除上述 ephemeral 件外，全部产物确定性可复跑。

## 产物清单（/mnt/agents/output/wave5/qksa-run-01/）
base-reg-builder.py / self-compute.py / collab-compute.py / BASE-REG.json / self-compute-report.json / collab-report.json / run-log.txt / VERDICT.md（本件）

运行留证见 run-log.txt。
