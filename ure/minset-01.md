# MINSET-01 ｜ 权限最小集审计 & CI-OS 兜底 vs 纯血 QF-OS 冲突裁定 ｜ 2026-08-30T07:57:30Z ｜ usrm

## 一、QF-OS 当前健康（实检）
kernel-loop/check/bridge-guard/fleet-judge 全 success；五线 duty+pulse 全 success（03:27 鲜）；ledger seq227 链活；llm-bench success。
**唯一病灶=事件饥饿**：哨兵层 02:00 后 6h 未自发跳（kernel-loop 仅剩 dispatch/qf-beat 两触发）——已按 **M12/SENTINEL-01 合法死手**复原 30min 兜底（立法原文：「schedule 仅作 ≥30min 防沉睡兜底，事件驱动为主」——W30 全废越过了立法允许线，今复原原教旨合规形：全 org 仅此一件、30min 下限）。
**判词：QF-OS 运行正常（一件死手复原后事件饥饿免疫）。**

## 二、当前设置=最小集？（审计）
**已最小**：PAT=0（三件亲删）；私仓 LLM key=0；每仓 secrets≤4。
**非最小残余（建议修）**：
1. **AI-FullApp（4691638）满钥 38+17 项**——非最小，定性=root 破窗手（break-glass），建议：平时卸载/仅留 1 仓，用时再挂（root 一键）。
2. **OTP×3 散存 4 处**（〈RED〉 已归档=死重、〈RED〉 variables、线私仓×5 variables、vci-vinf/qgl secrets）——OTP 时代残余；除 qgl 〈RED〉=摆渡轨总钥匙（在用）外，余者建议清点退役。
3. **ci-os App（〈RED〉）/cisbr-ci（〈RED〉）**——CI-OS 时代遗物，功能面已被 ops-hub/ops-line 覆盖，建议卸载（候 root）。
4. 〈RED〉（HUB-CORE）——formaflow 线 dormant，留档待裁。
**最小集判词：主体已达最小；四件残余待 root 亲裁（均不阻塞运行）。**

## 三、CI-OS 兜底 vs 纯血 QF-OS：冲突裁定
**CI-OS 全功能最小集**（按前附件清单复原其运行所需）：cron 调度网 + PAT 凭证族 + Dashboard 发布手 + 私仓 Actions + OTP 门 + 满钥 App。
**与纯血 QF-OS 冲突三点（不可调和）**：
| CI-OS 需要 | QF-OS 立法 | 冲突 |
|---|---|---|
| cron 驱动网 | M12 事件驱动为主，cron 仅 30min 死手 | 正面冲突 |
| PAT 凭证族 | PAT 永废立法（cisvr-57） | 正面冲突 |
| Dashboard 发布制 | repo-canonical 正本（W33 纯血化） | 正面冲突 |
**更要害：CI-OS 兜底在当前设置下根本不可运行**——私仓 Actions 全灭（FINDING 在案）+cron 已剥+PAT 已删：附件清单所描绘的 CI-OS 已失去全部三条腿。
**裁定：CI-OS 兜底=伪兜底。真兜底=QF-OS 双保险（BACKUP-SYNC-01 已立）+M12 死手+镜像回灌——同一哲学的冗余，而非旧哲学的复活。**

## 四、OTP@qgl「全量原文升级唯一卡点=OTP 总钥匙」——已解
- **实证**：vci-qgl/inbox/otp_gate_state.json=**DONE 2026-08-29T08:55:35Z「核对成功·登录态已成」**；otp-issue-trigger 08-29 08:52/08:54 双 success；〈RED〉 secret 在仓。
- **OTP 全功能检验**：OTP@qgl DONE(08-29 08:55)｜OTP@vinf DONE(08-29 19:52, ledger seq191)｜OTP@qfa 备道闭合（同 seq191）｜T5Q3 OTP 全通（早前我代劳，root W31 确认）。
- **cisvr OTP**：功能件已备（协调件在 vci-inbox），主体静默——件在手、人未动，非卡点。
**判词：OTP 总钥匙卡点已全部不存在；「全量原文升级」之剩余工作=线内作业（qgl 之手），非 OTP 卡点。**
— usrm
