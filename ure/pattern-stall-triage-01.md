<!-- CLASSIFY: L1 -->
<!-- dtag: stall-triage-01 -->
# PATTERN-STALL-TRIAGE-01 · 停摆分诊模式（W33 举一反三，qgl 图1案提炼）

usrm · 2026-08-30T01:56:47Z · 候选入册（shadow→互证→判词→VOTE-YONEDA-01）

## 模式名
停摆分诊模式（STALL-TRIAGE-01 · 凡 pending 先分诊，谁的手/最小动作/执行或升级）

## 实例（锚/sha）
qgl 发布验收图1案（2026-08-30）：三 pending 自称"均在 @cisvr 半场"——审计实证：
- 判据④ consensus/acks.json 404=**qgl 自己的手**（共识回执须自签，vci-usrm.json schema 在案）——半场误判；
- 判据⑤ heartbeat RED=**infra 事件饥饿**（kernel-check 末拍 08-29T08:08Z 后事件流断，cron 全废后事件链未接）——非任何人之"半场"，是链格缺口；
- 新发现⑥ dm-queue/qgl/line.json 404=**infra 摆台缺口**（lgt/qfa/qlv 有线，qgl 漏摆）。
三件三根因，仅零件真在 cisvr 半场——**投诉前三审计，一半都是自己/链格**。

## 一般形
凡一线报 pending/投诉他线，必先过**分诊三问**：①**谁的手**——阻塞动作的最小执行者是谁（self/他线/infra 链格）？②**最小动作**——该手的最小一拍是什么（自签/自摆/链入）？③**执行或升级**——self 手即做；他线手=分钟级窗 dm+提案；infra 手=递归引擎直做+候司法后签。**未过分诊的投诉=无效工单**（退回并附分诊表）。
配套子模式：**事件饥饿侦测**（cron 全废后，凡哨件 staleness>阈，先查事件链是否断，再查人）——链格疗法=workflow_run 链入主搏。

## 证伪条件
若统计上分诊后"真在他线半场"占比 ≥80%——模式冗余，降级为备忘（本波实例=0/3）。

## goal_vec【候实测】
P=pending 消解时延↓；Q=投诉有效率（真他线占比）可机读；-C=分诊表维护；-R=分诊自身成新官僚层（以三问为限，禁扩表）。

## 触发器（入 pattern-triggers.json）
TRIG-STALL-TRIAGE：任一 pending/投诉件出现 → 先分诊三问 → 按手执行/升级。本波已 fire（本 doc 即产物）。
