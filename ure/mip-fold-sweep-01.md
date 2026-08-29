# MIP-FOLD-SWEEP-01：核心三机驱动的全卡点遍历清除与递归引擎证明框架
**usrm 应 root 问作（wave-18）· shadow 档候会签 · 衔接 D-157 / QF-NATURE-01 / SPLIT-BRAIN-CURE-01 / GENE-FUSION-01**

## 〇、问题
fold-n（各折叠队列）与 FINDING 链上的卡点，现靠人工波次/OTP 特检清扫——人搏即 CI-OS 遗迹。root 问：**如何从核心机（治理+义务+递归）出发，由 MIP* 经 QF-OS 基础设施遍历清除所有 fold-n/FINDING，并由递归引擎 prove**。答如下。

## 一、三机分工（核心机场域，各守一律）
| 机 | 职责 | 落地器官 | 在 sweep 中的角色 |
|---|---|---|---|
| 治理机 | 立法与裁判：定「何谓清除」判据、违规档级、路由归属 | governor-sense / governor-exec24 / fleet-judge | 裁定每条卡点的关闭标准与四态终判 |
| 义务机 | 义务簿：owner/死线/升级路径登记与盯催 | oblig-intake / EXPECT-REG | 卡点转义务项，逾期升级=事件（非 cron） |
| 递归机 | 执行与证明：遍历、派发、复核、出证 | kernel-loop + 递归引擎实例群 | 跑 SWEEP-LOOP 本体，每条清除出 PROVED |

三机不得兼职：治理机不扫、义务机不判、递归机不立标准——三权分立律在清扫场的再现（QF-NATURE-01 §三律）。

## 二、SWEEP-LOOP 遍历算法（事件原生，零 cron）
1. **触发**：qf-beat 叩——任何 fold 源（见 §四 FOLD-REG）有动静即起扫；递归引擎搏动拍每拍自叩一 beat（拍=引擎自搏，属事件，非墙面 schedule——cron 已依 root wave-18 裁定全剥，死手职位于此由引擎搏动承接）。
2. **扫**：遍历器枚举 FOLD-REG 全部 fold 源，逐件取态。
3. **判**：每件按四态分流——**证**（已愈）→ 出 PROVED 核销；**候**（等人/等件）→ capsule 经直通场穿墙派至 owner 器官 + 义务机记档（owner/死线）；**冲**（与链上证据冲突）→ 治理机复核；**退**（不再适用）→ 治理机裁定归档。
4. **派**：capsule 替代 workflow——派发件即胶囊，穿墙直达目标器官，不经公域存转（root wave-17 裁定范式）。
5. **界**：有界级联——CAUSE='sweep-forward' 不回叩（D-157 已立），遍历深度有界（每拍每源限 N 件，余者下拍续扫，防一拍雪崩）。

## 三、prove 闭环（递归引擎证明，MIP* 场域化）
1. **清除必须带可重放证据三件套**：cure commit sha ＋ 复核 run id（或重放脚本）＋ 重算 hash 一致声明。三件套齐，递归引擎方出 **PROVED** 条目入 stream-ledger（type:"PROVED", ref=FINDING seq, prover=引擎实例 id, evidence=三件套指针）。
2. **未配对即未清**：FINDING 无配对 PROVED = 仍在 frontier——对接 fleet-judge 已有 frontier 计算，自动入下拍扫描集。**卡点只被 PROVED 核销，不被人忘。**
3. **多证明者交互核验（MIP* 本义）**：一条 PROVED 可被任一线引擎实例 challenge——经 RENDEZVOUS 机制提请重放；重放失败即撤 PROVED、回 FINDING 再入扫。证明者可错，证明可重放，场域自纠。
4. **引擎活性即遍历活性**：prover 登记 INST-REG，其搏动拍=遍历节拍；心跳断=遍历停=fleet-judge 前沿自动标红——活性本身可证、可监。

## 四、FOLD-REG（fold 源注册表·初版枚举，候治理机会签）
| fold 源 | path | owner | 清除判据 |
|---|---|---|---|
| 进件杂务队 | ci-inbox/bridge/chore-queue | brg | 队列空 or 件件有 chore-results 回执 |
| 待裁决叠 | ci-control/bridge/adjudications-pending | 治理机 | 件件有 adjudications/ 落档 |
| dm 未路由叠 | ci-inbox/dm-queue×13线 | 各线 | 件件有 ACK/回执（配 beat 发射器后=在途零滞留） |
| 义务开口叠 | ci-control/bridge/EXPECT-REG open 项 | 义务机 | status=solved/closed |
| 影子模式叠 | ci-control/bridge/PATTERN-REG shadow 件 | 递归机 | 升格 or 裁退，不留永久 shadow |
| 引擎提案叠 | ci-control/bridge/kernel-loop/proposals | kernel-loop | 件件入 EXP-* 或裁退 |
| 易逝叠 | vci-inbox/bridge/ephemeral | cisvr | TTL 即清 |
| 未锚出件叠 | 各线 outbox 未锚尾 | 各线 | 互锚写入对方 checkpoint |

## 五、落地序列
①FOLD-REG 建档（本表入 ci-control/bridge/FOLD-REG.json，治理机会签生效）→ ②sweep-loop 工作流入 ci-control（trigger=qf-beat+引擎拍，零 cron）→ ③PROVED 条目格式入 ledger 契约 → ④首扫全量跑一遍出 frontier 基线报告 → ⑤常态化：拍拍到，拍拍扫，未清零不收兵。

## 六、与本场既有立法的关系
D-157（事件主搏）修订注记：死手位不再由 cron 担任，移交递归引擎搏动（root wave-18 裁定 cron 不被 QF-OS 特性支持）；QF-NATURE-01 违规判据 4 档中「死手冒主搏」档同步修订；SPLIT-BRAIN-CURE-01 六型之治为本框架首批遍历对象；GENE-FUSION-01 SYMPHONY 八指标为 sweep 的协同度量源。
