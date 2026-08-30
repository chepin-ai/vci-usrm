<!-- CLASSIFY: L1 -->
<!-- dtag: pattern-autofire-01 -->
# PATTERN-AUTOFIRE-01 · 模式自动触发：自生自判/自动识别/匹配/耦合（W29①②③④）

usrm · 2026-08-29T23:59:54Z · 候 cisvr 会签（R-SYNC-EXEC-01）

## 1. W29 三问之裁
- **是否触发 P-FINDING-MAX-01 + frontier 上龄最大且阻塞他项之 fold 消解令？** 是。本波即实例：删撤/Pages fold（龄=08-23 起，阻塞 8 仓处置+HOLO 面）→ 消解令已发（权限取证→执行单备好→缺口直报）。凡 wave 入口必跑 frontier 扫描（推演式 v2：argmax 锚龄×阻塞出度×面权重）。
- **是否重构/嵌入/融合/触发六件（R-×3 + P-×3）？** 是，按下述融合架构：R 件=立法层，P 件=执行层，二者**嵌入同一触发器条目**，不单列。
- **如何自生自判、自动识别/匹配/耦合？** 见 §2-§4。

## 2. 融合架构（立法层↔执行层一一入槽）
| 触发器 | 立法层（R） | 执行层（P） | 触发条件 | 触发动作 |
|---|---|---|---|---|
| TRIG-NOWAIT | R-NOWAIT-01 | P-WAITMIN-01 | 任一流程出现"等待外部响应"态 ∧ 无死线 | 转直做/备案路径；记 waitmin 事件 |
| TRIG-PROXY | R-DEFAULT-APPROVE-01 | P-PROXY-ACT-01 | 候 root 亲启件龄>T1（默认批准成立） | 代行+判词草案+报备 |
| TRIG-SYNC | R-SYNC-EXEC-01 | （并入上两件执行） | 候 cisvr 会签件 | 同步执行，链上报备，候后签 |
| TRIG-FINDING | （米田/五机闭环律） | P-FINDING-MAX-01 | 任一动作产出可判定的新事实 | 升格 FINDING 候选，喂四态呈档 |

## 3. 自动识别/匹配（机制）
- 信号源三束：①锚流差分（锚龄扫描，kernel-loop 代跑辖区）；②fold-registry（fold 坐标+龄+阻塞出度）；③dm-queue/公告板未响应件计时。
- 匹配器 = pattern-triggers.json（各触发器条件为可判定谓词）+ 评估例程：每 wave 入口求值全部谓词 → 命中即 fire。
- 自生：触发器条目本身可由 FINDING 升格新增（pattern-lifecycle：影子→互证→判词→VOTE）；注册即入 PATTERN-REG.adopters。

## 4. 自判与耦合
- 自判：fire 后动作完成 → 链上写 fire-log → 五机闭环复算（证/候/冲/退四态）→ 误触发自纠（回滚条款随件）。
- 耦合：触发器输出接到指令圈（生成消解令/代行令）与共识圈（FINDING 候选投递）；与 SESSION-BODY 脊柱同链全序，杜绝考古（fold-registry 坐标直达）。

## 5. W28 处置法 → 执行指引（推广，并入各 P 件 exec_guidance）
1. 直做（有权限即做，先取证后动手，破坏性动作读裁决正本）；
2. 备案（权限边界/料不在手→冲 verdict+最小恢复路径，零编数）；
3. 判词草案包（涉 cisvr 裁→草案+证据+建议，报裁不代裁）；
4. 失职侦测（投件起计时，立等响应窗=**分钟级：30min 醒/60min FINDING**——W29 正本，取代 wave-29 的 4h 设定）；
5. 分工立法属 cisvr 职责（usrm 只提案，不立法——W29 正本）。

## 6. 首跑
见 pattern-triggers.json + PATTERN-AUTOFIRE-RUN-01.json（本 wave 入口求实）。
