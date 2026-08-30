# ARCHAEOLOGY-FREE-01 ｜ QF-OS 替代考古的机制 ｜ 2026-08-30T02:42:04Z ｜ usrm
（root W34 问：QF-OS 实现替代考古的机制是？彻底回溯/清查）

## 命题
**考古**=从 git 史/旧会话/散落文档反向发掘状态——本质是**状态无处可查**的症状。QF-OS 的替代机制=**状态即查询，非发掘**：一切状态活在事件溯源账本+内容寻址锚+机生注册表四面。

## 四面机制（已在役/本波次补齐）
1. **事件溯源脊**：stream-ledger.jsonl（append-only、hash 链、seq 单调）——「发生过什么」永远查链头不查历史。
2. **内容寻址锚**：narrative/outbox tip（sha12）、heartbeat cross（sha16）、manifest sha16——任何件「是不是那一件」一锚即证，无需翻 commit。
3. **机生注册表**：outboxes.json/registry/lines/*.json/findings/——「现在什么态」机检直读（BOARD 岗报机生化案=同理）。
4. **双保险镜像**：BACKUP-SYNC-01——正本毁则从镜像+sha16 验真回灌，恢复亦不考古。

## 回溯/清查结果（考古债清单→转化）
| 考古债 | 现状 | 转化 |
|---|---|---|
| 300 件 G-DIR stale-open | 账在 DIRECTIVES 无人跟进 | STALL-TRIAGE 分批清；完成即核核销账 |
| tombstone 指 git 史 | kimi.link 6 件立碑 | 碑即正本，史只作证据层 |
| 已删 OTP 遗物 | git 史可复 | 删除事件已入 ledger seq224=锚 |
| M-CODE/Δ-BASE 词面无正本 | org 0 命中 | 候投正本或批起草——**不准靠考古猜义** |
| ci-control-backup 眼件（eye/bench×21） | 归档只读 | LLM-BENCH-U6 已重构接续，旧件留档不发掘 |

## 立法（自此刻我面执行，请 root 批为公律）
**A-F-01**：任何「我去翻了 git 史/旧档才搞清」的事件=一件 FINDING（状态缺位），立案同时必须把结论**回填为可查锚/索引/注册表项**——考古一次，永不再考。（M11 考古必钩之执行面）
— usrm
