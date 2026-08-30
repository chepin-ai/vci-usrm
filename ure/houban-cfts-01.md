# HOUBAN-CFTS-01 · cfts 候办（事件锚）机制梳理三答 + 处理
usrm 2026-08-30T09:43:17Z ｜ 应 root W39 OTP@cfts：①是否自动加载等候最小pattern ②是否按递归引擎决策自主运行 ③与核心机prove/verify/判定是否耦合/融合

## 证据基面（2026-08-30T00:39Z 实况）
- 线侧锚：`github-repo-cfts/health/engine-state.json` v3.1.1——「会话独立状态锚（任何会话/端读此文件可接续全部运行线）」；engine spec v2（八态机 S0..S6+HALT，INV1-6）；maturity=**L2（诚实判定，L3 不达成）**；running_lines SENTINEL「beat-5 DONE，beat-6 待命唤醒，唤醒词：哨兵第6拍」；open_obligations 16 项（SLA 多事件锚：候root/哨兵beat-6/WEDGE联动/2026-08-30T20:40Z 等）；verdict_registry 判定入册（FP-M4-1 成立 4.53× / DE-M4-2 n=20000 精确 / M3-SMOKE verify=True 逐字节一致）。
- hub 侧：EXPECT-REG-01 律「凡有期待必登记带截止钟；field-router 每 tick 扫描，超时→FINDING 自动立」（47 项在册）。
- 公面：vci-cfts agent-duty 追办台账（open findings ticks≥3 自动升级），事件驱动面已通（beat-forward 实装后 dispatch/push/线拍皆可燃）。

## 三答
### ① 是否自动加载等候最小pattern？
**半自动，三级分立**：
- hub 级=自动（EXPECT-REG + field-router 每 tick 扫，超时自动立 FINDING）——但 field-router 在私仓，私仓 Actions 全黑（08-24 起），实际由 session-pilot/kernel-loop 代拍；
- 线级=锚定手动（engine-state 设计为「读即接续」，唤醒词制；无事件触发自动加载器）；
- 公面级=自动（duty 台账 ticks≥3 升级，机检最小 pattern）。
全局最小 pattern = STALL-TRIAGE-01（PATTERN-REG#18：谁的手/最小动作/执行或升级）已在册。**缺口=线级事件锚→自动加载 OBL→恢复执行 无机关**。
**处理（已执）**：本轮把 open_obligations 摘要镜像至 `vci-cfts/inbox/obl-shadow-20260830.json`（id/what/sla/status 摘要级，零私域原文），供公面 duty/beat 消费；处方=cfts 会话侧每拍自续 shadow（一拍一覆写，同名幂等）。

### ② 是否按递归引擎决策自主运行？
**L2 自主（诚实态）**：会话内 five_phase（广搜→深研→博鉴→互证→融构→义务投递）闭环自主；跨会话靠状态锚接续（非自主唤醒）。L3 未达成的卡点=OBL-SYN-4「root 标定引擎 v2 θ/w 阈值」——**候 root 标定**（D-140：指定动作不指定结论，我不越权代标）。beat-forward 贯通后，跨会话唤醒可由事件面补足（唤醒词→事件锚直燃，处方可行）。

### ③ 与核心机 prove/verify/判定是否耦合/融合？
**纪录级已融合，强制级未融合**：verdict_registry 把 obligation→experiment→verdict 入册闭环（CLOSED-成立/UNREACHABLE/PASS 皆带证据）；但 OBL 关闭条件未强制绑定 verify 产物——存在「无验可闭」缝隙。处方（engine spec v2.1 候选）：INV 增一条「**无验不闭**」——凡 OBL/EXP 关闭必附验件哈希/transcript 锚，与 INV1-6 并列。

## 盯办
- OBL-SYN-3（cfts-05..17 回帖收割）SLA=2026-08-30T20:40Z，今夕到期——已过桥入 dm@cfts。
- 候 root：引擎 v2 θ/w 阈值标定（L3 判据）。
