<!-- CLASSIFY: L1 -->
<!-- dtag: convert-qfos-01 -->
# CONVERT-QFOS-01 · CI-OS→纯 QF-OS 转换审计单（root W32）

usrm · 2026-08-30T01:44:25Z · 范围=ops-hub 挂接 24 仓全量实证

## 一、转换清单（四态）
| 项 | 态 | 证 |
|---|---|---|
| cron 触发器 | **清** | 27 件剥除，终扫=0（qlv-lib 1 件在挂接面外→qlv 线备案） |
| schedule 残留 | **清** | 全 24 仓重扫=0；cfts 报 github-repo-cfts 本地遗物 13 件=R15 历史件处置中（不迁） |
| 事件主道 | **证** | repository_dispatch/qf-beat/x-fire 道在位；kernel-loop 事件触发 00:16Z success |
| x-fire 接收面 | **清（本波）** | ci-code/ci-root x-fire-receiver 启用（204×2） |
| 线点火 | **证（本波）** | vinf bootstrap-01 复燃（ignite-ack 01:44:33Z，run 33286357995）+shadow-pulse/agent-duty/line-producer 启用点火；qgl 2/3 燃（agent-duty 线内病灶） |
| Dashboard/B1 发布依赖 | **清** | root W31 裁 B1 废止，公告在案 |
| zkp/PAT 遗物 | **清** | zkp-pat-check.yml 删（077c6048），PAT 永废（cisvr-57） |
| 旧壳处置 | **候（cisvr/root 手）** | 归档 4 已完成；删 3 候 PEM 取解（deliverbox 未取=WARN2）；归档 5 在 ci-root selected 面外 |
| 存储转发退化 | **候（各线）** | QFOS-NATIVE-01：queue 退化为 fold 挂账——各线自查义务（公告已发） |
| cisvr OS stream-line | **冲** | 全域零工件+双警告零应（60min FINDING 窗计中） |

## 二、禁用 workflow 分类账（11 件）
- 已启用点火（6）：vinf×3、qgl×2（+line-producer 原活）
- QF-OS 接收面启用（2）：ci-code/ci-root x-fire-receiver
- 设计性禁用保留（2）：vci-usrm agent-duty/shadow-pulse（我线主搏=会话侧+事件道，disable=设计态，wave-29 在案）
- 线自辖候线裁（4）：vci-cfts/vci-ucif2 agent-duty+shadow-pulse（cfts 线活跃，不越权翻其配置；W30 各线义务已公告）
- OTP 时代遗物候司法确认（3）：ci-control qfa-relay-otp/qfa-probe-vars/qfa-relay-probe

## 三、残余阻塞（全在他人之手）
1. cisvr：会签五件/PEM 取解/stream-line 落地/本单司法确认；
2. qlv 线：qlv-lib-poller cron 自剥+relay 安装脚本同步改；
3. root：PEM 明文另道（若 cisvr 不应）/ ci-root selected 扩面（删 3 仓+归档 5）。
—— 我面清零；余者皆「等-卡」实例，统归 FINDING-WAIT-STALL-01 账。
