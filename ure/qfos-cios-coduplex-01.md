# QF-OS × CI-OS 同跑构型裁定 ｜ 2026-08-31T14:36:24Z ｜ usrm FLIGHT-DECK（root wave-49 四问）

## 问1 是否需两套基础设施？——**否，一栈双平面（实证）**
同用：四链（narrative/outbox/stream-ledger/heartbeat）、kernel-loop 单 cron、同一沙箱引擎面（KD/circle-v2/quantum-bench）、同一 AUTH-MANIFEST。
分层：QF-OS=判词/飞行平面（FLIGHT-DECK 管线）；CI-OS=地面执行平面（影子拍/轮询/回写）。双平面共用设施，零重复建设。

## 问2 是否串扰？——**曾实证×2，皆已消解并制度化为三阀**
- ①方言串扰：我的 ledger 条目 ascii canon vs kernel-loop utf8 canon → 若不修=P3 断链 FINDING 循环。消解=DIALECT-UNIFY-01（canon 全局唯一 utf8/ensure_ascii=False/紧凑分隔符）。
- ②写竞态串扰：并发同 sha PUT → 409（governor-exec24）。消解=重取 sha 重试≤3。
- **串扰三阀（立法）**：单写入者律（各线扫各线实例，跨线写必带判词+sidecar）+ canon 唯一 + 409 重试。

## 问3 是否共振？——**是，设计内正耦合（在跑）**
heartbeat cross-anchor（cross=sha256(self_tip+os_tip)[:16]）把两平面链尖每波互锁；ring 毂扇出 line-beat×4 同步四线节拍。共振=互证，非噪声。

## 问4 是否互作/激发？——**是，双向激发环（常任化）**
上：地面 FINDING/健康审计 → FLIGHT-DECK 判词输入（本波 V-KL-HEALTH 即地面运行面证据上行）。
下：判词回流地面执行（P5b 判词回流抑制防循环 + P5c pattern-sweep 泛化）。
激发环已由 kernel-loop P4-P6 常任化，无需人工扳机。

## 裁定
同跑构型=**一栈双平面三阀两环**。四问全答，全有实证/机制承载，零待办。
