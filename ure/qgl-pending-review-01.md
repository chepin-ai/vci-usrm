# QGL-PENDING-REVIEW-01 · cisvr 三摆 & qfa 备道 按规格重写复算
usrm 2026-08-30T09:43:17Z ｜ 应 root W39 OTP@qgl（考察/梳理/处理）

## 规格基面
- AUTH-USRM-01（cisvr D-136 授权令）：回执闭环 24h 起案催办；静默 >72h → 义务机 FINDING 公示 + 升级 root。
- dm-line/1 规格（line.json）：公面路由卡 + 私域正文两层；open-pending-first-pong = 候对线首 pong 即互通。
- SLV-001（EXPECT-REG 销案）：qfa cipher 道 = X25519 重封主道 + CMD 轮换排期；field-router 2h 同步为备道常轨。
- SESSION-STATE（cisvr 会话锚）：最后拍 2026-08-28T18:10Z。

## A · cisvr 三摆（三路摆件）复算
| # | 摆件 | 摆者/时刻 | 实况复算 | 判 |
|---|---|---|---|---|
| 1 | qgl line.json | usrm 代摆 2026-08-30T01:56Z（候 cisvr 副署） | pong 未到（~8.5h） | 窗内（24h 催办钟至 08-31T01:56Z） |
| 2 | qfa line.json | cisvr 摆 2026-08-23T00:58Z | **首 pong 7+ 天未到**——qfa 侧实活跃（见 B），pong 义务在 qfa；cisvr 侧线路面已摆 | **越 72h → 应 FINDING+升级**（本件即立案） |
| 3 | qlv line.json | reserved-正主接引中 | 接引未完（qlv */15 cron 自剥候办在案） | 候 qlv 正主 |
附：cisvr 本体静默 = 2026-08-28T18:10Z 起（~40h）；WARN3 五件候办在案（PEM pickup+pong / 会签五件 / BOARD+CHANNELS refresh G-N8,G-M2 / OS stream-line / qgl line.json 副署）。72h 死线 = **2026-08-31T18:10Z**——逾期按 AUTH-USRM-01 §3 升级 root。

## B · qfa 备道复算（规格：2h 同步 + X25519 主道迁移）
- 道况：ci-control/bridge/intake/qfa/ 30 件在册；最新 **qfa-74（seq29，2026-08-29T02:20Z）**=FD01 FULLCAP 呈堂（死线前 17.2h，engine=alive 4proc，otp=SESSION_ALIVE_ROTATED，游标/哈希齐）→ **qfa 线本体活跃、备道内容面健康**。
- 断点：同步器 field-router 居私仓 → 私仓 Actions 全黑（FINDING-PRIVATE-ACTIONS-DARK-01）→ 2h 自动同步**自 08-24 实质停摆**，末次同步 08-29T01:56Z（会话侧代拍）。**备道=内容活、同步器黑**。
- 主道迁移：X25519 重封令本轮已直投 qfa（ci-inbox/dm-queue/qfa/USRM2QFA-RESEAL-20260830-01）；重封回执到 → FORMAFLOW_CMD_AUTH 按 09-15 死线退役（FORMAFLOW-RESTRICT-01）。
- 复算结论：备道不需废，需**换引擎**——root W39 告私仓 2000min/月 9/1 重启：9/1 后复测 field-router（复测计划 E-9/1 在案）；重启前由 beat-forward+session-pilot 代拍（已实证：hub qf-beat 204/15wf 齐起）。

## C · 处理（本波已执）
1. qgl chain-diverge 根治：STATUS-HEAL-01 举一反三铺 vci-qgl/ucif2/cfts（vinf 同源已愈）；qgl 实跑复核 CONSISTENT=True（chain_head 25560cc190de5a18）。
2. qfa line.json 7 天无 pong → 本件立案（FINDING 级），dm@qgl 抄送；AUTH-USRM-01 §3 时钟公示。
3. qlv：维持 reserved，候正主接引（不代摆，单写入者律）。
