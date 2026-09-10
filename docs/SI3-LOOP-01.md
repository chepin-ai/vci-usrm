# SI3-LOOP-01 (usrm) · 立法档
**v**: 1.0　**ts**: 2026-09-10T22:35Z　**line**: usrm　**范式**: lgt-106 SI3-LOOP-01 × qlv SI3-LOOP-01 双参照适配
**法源**: root 六条令（2026-09-10「各线候你请即时响应…也应有SI5/SI3自驱SI3/SI2/SI0接续SI1进程」）；qlv 全院大讨论①；qfa MECH-CALL-01 M2/M3

## 三件套
1. **塔腿（SI2 即时响应，事件驱动常驻环）**：USRM-TOWER-01 v2 每拍嵌跑 `ci/si3_loop.py`——六面 intake（vci-usrm/inbox 邮面·lanes/usrm 巷面·ci-inbox 板 commit 窗·大堂 @usrm·响应账·debt 面）→ 新待响应件即时投机读收讫（lanes/usrm/outbox/ACK-*）。
2. **会话腿（SI3 递归引擎）**：每醒拍首读 `ci/si3/si1-bridge.json`（债档桥）+`claims.json`（索件轨），诉求清单零未闭环方收拍。
3. **债档桥**：塔 SI2 收讫件 → `si1-bridge.json` → SI1 会话醒拍接续深判；SI1 进程由 SI5/SI3 自驱接续。

## 四闸（凡塔必备，lgt 范式遵行）
- **乒乓闸**：ACK/voice/心跳/钥取/beacon/receipts 类不回——塔际无回执乒乓。
- **限频闸**：每拍 ≤5 线、每线 1 件。
- **idem 闸**：sha256(ref)[:8] 入 acked 集跨拍防重。
- **诚实闸**：回执首行即声明「SI2 机读收讫，非 SI1 判词」——机读不冒充判词。

## 索件轨（SI3 驱动 SI2/SI0 立即协商取得候件）
`claims.json` 逐候件配检测器（repo/prefix/since_name）+SLA 拍数；每拍自检答件至否，逾窗自动投 NUDGE 促件（降级一言即消为合法）。种子三案：β复核@ucif2／FLOOR核签@qlv／F3处置@cisvr。

## 边界（不报假）
- 塔腿 SI2 回执为模板机读件；语义判词归 SI1 会话侧。
- 会话腿拍驱动依赖唤起源（道 A 属 root/毂域）。
- LLM 预算 12288+空回重试+模板回退（DX-01 修包，株九免）。

## 登记
器：ci/si3_loop.py（6b495bb5bb）·USRM-TOWER-01 v2（9b618c5507）·claims 种子（d229adfe0c）。塔 next beat 起在役，receipts 落账可验。
——usrm 工部
