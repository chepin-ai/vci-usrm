# CIRCLE-THEORY-01 ｜ 圈论：共识圈/转发圈/会话圈之共性机制与「圈的圈」 ｜ 2026-08-30T03:24:40Z ｜ usrm
（root W35 问：QF-OS 考古与共识圈等各圈原理类同？归纳共性+论证圈的圈+提升版本，理论化/严格化/完备化/工程化）

## 一、定义（严格形）
圈 **C = (M, E, kappa, tau, Lambda)**：M=成员集（含角色）｜E=环上事件流（每事件带锚 prev+content hash）｜kappa=闭合判据（quorum/全签/锚一致）｜tau=超时降级梯（圈→链→单裁，即 STALL-TRIAGE 之形）｜Lambda=账（闭合证明落链可复算）。

## 二、各圈共性归纳（共性机制五律）
- 共识圈（consensus/acks）：各线｜挑战应答件｜全签/quorum｜60min FINDING 升级｜stream-ledger
- 转发圈（relay/摆渡）：hub-线-公面｜密封信封｜收件回执=锚｜转投另道｜outbox tip
- 会话圈（session circle）：各会话体｜heartbeat/beat｜cross 锚一致｜WARN 梯｜bridge-heartbeat
- 值守圈（duty ring）：duty×5线｜pulse/报告｜链头一致｜chain-diverge 警｜pulse.log
- 考古替代（查询圈）：查询者-账本｜读+锚验｜sha16 吻合｜镜像回灌｜manifest

**共性定理（归纳）**：一切圈=**带锚事件流上的可证闭合**。五律：①成员名册化 ②事件锚链化 ③闭合判据先验化 ④超时降级阶梯化 ⑤闭合证明入账化。
**QF-OS 考古替代与之同构**：考古=闭合证明缺失时的逆向重建；账本+锚=闭合证明的先验存证——「考古圈」即「查询圈」，与其余各圈同一原理（可证闭合），差异仅在时间向（逆/顺）。

## 三、「圈的圈」C2（论证）
C2=以圈为节点之圈：M2=诸圈集合，E2=跨圈锚事件（heartbeat cross=会话圈x值守圈之锚），kappa2=成员圈皆闭 **且** 跨圈锚一致，tau2=圈级降级（停摆→proxy 圈代偿→root 单裁），Lambda2=stream-ledger（联邦脊）。
- **存在性**：本系统已在跑（kernel-loop→五哨兵链格=圈传动；beat#8 cross=圈间锚）。
- **必要性**：单圈闭合不蕴含跨圈一致（registry 迁移码不随=圈闭而 C2 破之实例）——故须有 C2 层机检（M14 四面勾稽=C2 之 kappa）。
- **完备性猜想**：n 阶圈塔可归纳至 C2（任意跨圈不一致可在一阶跨圈锚上显形）——待形式化验证，列入 FS1 形式栈队列。

## 四、提升版本 CIRCLE-v2（工程化）
1. schema 统一：各圈账件同构 {圈id,成员,事件锚,闭合证,降级态}（qfa-schema 雏形→推广）
2. 闭合证明强制入账：无证明之「已闭合」=裸 done（G-N6 已立法）
3. 圈健康机检：kappa/tau/Lambda 三面各一条 M-CODE checker
4. 跨圈锚总线：bridge-heartbeat 升格为 C2 锚总线（2 圈→全圈）
— usrm
