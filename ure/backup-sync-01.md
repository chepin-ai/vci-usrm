# BACKUP-SYNC-01 ｜ 脊柱双保险机制（纯 QF-OS）｜ 2026-08-30T02:42:04Z ｜ usrm

## 设计
- **镜像对象**（HUB-CORE 脊柱六件+最新 findings）：stream-ledger.jsonl / PATTERN-REG.json / INST-REG.json / DIRECTIVES.json / bridge-heartbeat.json / PERM-TABLE-01.json
- **镜像目标**：`〈RED〉:spine-mirror/`（私仓、可写、安装面内）
- **驱动**：纯事件——随 usrm 链账波次镜像，零 cron；manifest.json 记每件 sha16+bytes，与正本交叉锚可证一致
- **恢复径**：正本毁 → 取 manifest 验 sha16 → 镜像件回灌 HUB-CORE

## 关于 〈RED〉（root 问）
**现状：该仓已 archived（只读），写不了**——面内无权解归档（administration 在 〈RED〉 App，PEM 通道候 cisvr/root）。
候件：① root web 端解归档，或 ② 〈RED〉 App 激活后 API 解归档 → 镜像目标一键切回 〈RED〉（仅改 manifest target 一行）。
过渡期 〈RED〉 承担双保险，语义同为私仓系统面，R1 合规（脊柱件含系统内部信息，永不落公仓）。

## 建立必启用
本机制首跑即实证：六件+findings 已镜像（manifest.json 在 〈RED〉:spine-mirror/）。
— usrm
