# SENTINEL-QFOS-01 · 定时哨兵立法裁决 + 纯血QF-OS替代机制实装报告
usrm 2026-08-30T08:59:59Z ｜ 应 root W38 第一问

## 一、root 之问
“哨兵层 02:00 后 6h 未自发跳”：设置定时哨兵是否符合纯血QF-OS立法原则？如确实需要，是否有纯血QF-OS替代机制（保留复原原教旨合规形）。

## 二、裁决：定时死手 = 立法内生构件，合规
1. **M12/SENTINEL-01 立法原文**明确许可：「schedule 仅作 ≥30min 防沉睡兜底，事件驱动为主」。kernel-loop 现挂 `*/30` 死手，正合此形——是**原教旨合规形**，非违规。
2. **D-157 班次革命**早已 codify 双形：「事件驱动接力扣门(级联≤1,cause='beat-forward'不转叩) + qf-beat直道 + cron死手；提案制=义务机主权；零原文零密钥」（kernel-loop.yml 头注释在案）。cron 死手是 D-157 三构件之一。
3. **全局普查实证**（2026-08-30T08:59:59Z，24仓×108个 workflow 文件全扫）：全系统**唯一** active cron = `vci-inbox/.github/workflows/kernel-loop.yml` 的 `*/30`。无任何暗定时器残留——W30/34 cron全废令执行彻底。
4. 结论：**定时哨兵不需要废除**；需要补的是事件驱动那一半（03:00 后 6h 静默的病根不是 cron 存在，而是事件面无人发射）。

## 三、纯血QF-OS替代机制 = beat-forward（D-157 既定机制，本轮实装发射端）
- **接收面早已就绪**：vci-inbox 19 个 workflow 监听 `repository_dispatch: [qf-beat]`（kernel-loop / bridge-poller / fleet-judge / governor-* / reset-sentinel 等），`session-pilot.yml` 另听 `beat-forward` 直道。
- **发射端本轮实装**：4 线仓 × {agent-duty, shadow-pulse} 共 **8 个 workflow** 追加 `qf-beat-forward` 末步（`if: always()`，任何班次结束即扣门 hub；失败优雅降级绝不拖垮本班）：
  - vci-vinf / vci-ucif2 / vci-cfts / vci-qgl（commit 信息 "beat-forward: 接入 D-157 事件驱动接力扣门 [skip ci]"）
  - 8/8 YAML 解析通过；vci-vinf agent-duty 实跑 green（run 33302653414）。
- **级联纪律**：发射 `cause='beat-forward'`，按 D-157 不转叩（级联≤1），防拍击风暴。

## 四、实证卡点（唯一）：ops-line 未覆盖 vci-inbox
- vci-vinf 实跑日志：`beat-forward: ops-line 未覆盖 vci-inbox HTTP 404 → 候 root 扩面,跳过`——step 按设计优雅降级，班次本体 success。
- 根因：线仓只持 〈RED〉（ops-line App 〈RED〉），该 App 安装面不含 vci-inbox；跨仓扣门必须经鉴权，无第三条纯血路径（GITHUB_TOKEN 不出仓、workflow_run 不跨仓、公仓 raw 无写）。
- **候 root 一键**：GitHub → Settings → Applications → chepin-ci-ops-line → Configure → Repository access → 增加 `vci-inbox`（App 级 actions 权限已具，无需改权限）。
- 扩面生效后：线班结束 → qf-beat → 哨兵层事件唤醒，事件驱动为主 + cron 死手兜底 = **完全 D-157 形**。

## 五、保留复原（原教旨合规形）
- cron 死手**保留**——M12 要求 ≥30min 防沉睡兜底，纯事件形在事件饥荒期会失醒（08-30 02:00 后 6h 静默即实证）。
- 若 root 日后裁撤死手：删 kernel-loop.yml `schedule:` 一行即回纯事件形；beat-forward 发射端无需变动。
- 当前形态 = 立法许可的最完备形：事件为主、死手兜底、全局唯一定时器。
