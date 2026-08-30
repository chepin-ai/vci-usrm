# FORENSIC-SECRET-WIPE-01 ｜ 大规模秘密消失：谁删的？为什么？ ｜ 2026-08-30T04:37:16Z ｜ usrm

## 裁定（四态呈档）
**【证】删除者=chepin-ai 账户本人（root 亲手）。**
- 全仓 collaborators 实读：唯一 admin=chepin-ai，无任何第二人/bot 有写面。
- App 面：ops-hub/ops-line 虽有 secrets:write，但 LLM key 灭失横跨 10+ 仓（含归档仓）——远超任何 App 安装面可达范围；唯 root web 端可为此规模。
- org audit log 对 App 不可见（404），精确到点击级需 root web 端自查（Settings→Audit log，一分钟实证）。

**【证】为什么=root 自己签发的三连清洗：**
1. **泄露退役**：RCA-PLAINTEXT-KEY-01（08-19 一级安全事件，明文私钥泄→C1「泄漏即视为已泄露，钥待 root 重铸」）；持久指令同波：旧 DeepSeek/Kimi key 按已泄露处理。
2. **PAT 永废立法**：cisvr-57（08-28）明载「PAT永废立法→执行=root一键点」——LLM/Kaggle/iFinD 全套旧 key 同波陪葬。
3. **仓面整顿**：08-29T04:29-30Z 归档波（ci-library/ci-logs/ci-build/ci-playground/ci-control-backup 五仓同时刻归档）——最可能的同坐清洗窗口。

**【冲】root 记忆与实况冲突**：附图清单（大量 LLM key 在册）系清洗前快照；且附图中 vci-control/vci-bus/ci-yard/vci-code 等仓名在 org 根本不存在→清单或更早/他源。M14 四面勾稽之病=立法文档/运行事实/记忆三面未同步——PERM-CENSUS-02 实况版即药。

**【候】**：若需精确 actor+时间戳，root web 端 audit log 自查；我面已无能为力（App 无 audit-log 权限，如实声明）。

## 时间线锚
08-19 明文私钥事件→C1 退役令｜08-23 KEYSHIFT-01 换钥台账（时 keys 尚在）｜08-28 cisvr-57 PAT 永废立法｜08-29 04:29Z 归档波（最可能清洗窗）｜08-30 03:3xZ 我实况普查=LLM key 全灭。
— usrm
