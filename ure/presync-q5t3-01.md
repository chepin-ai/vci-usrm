# PRESYNC-Q5T3-01 v0.1（shadow）
## 动作前置知情 pattern：OS 端凡动作，先知 Q5T3 全线、蒸馏、转达注入/圈同步

## 件头

- **版本**：v0.1（shadow）｜**诚实档**：【候】，未实测处一律标【候】
- **立法锚**：root 令 2026-08-28＋D-150＋D-151
- **上游**：META-PATTERN-01（六元组＋D_f 修正案第一装载）、DUAL-DRIVE-01、OTP-SWM-01/PATTERN-PLUGIN-01、ENGINE-FLEET-01、FULLCAP-DRIVE-01
- **文体**：usrm 公文体；E804；R1 公域零系统信息；死线真实 UTC

**root 令逐字照录**：
> 「OS端所有动作前要了解Q5T3其他线进展，并归纳/蒸馏/转达注入相应会话或由会话圈与会话端同步」

## §0 实证基线：把「事实在跑」定格为「可装载纪律」

**① usrm wave5/6 开局巡场实录 = 本 pattern 事实在跑**：两波开局均先读公告板十件未读、核 threads 新帖、查 INST-REG 心跳与 beacon 序，十件未读全读后再动笔；Q3 波全仓实证审计→注入/代劳三档处置（IPL-18 在案）。动作前置知情非提案，是两波实战已验的既有行为，缺的是定格与装载。

**② root 之问实现度审计三段（全仓实证）**：
- **会话端张量网**：schema 已成（FULLCAP-DRIVE-01 双张量网交叉锚 PRODUCED_BY⇄YIELDED）＋usrm 单线示范**实测**过（session-tensor-net digest=d9a5162ce805043f、file-tensor-net digest=af9793275836d670，五维 PASS）；但七线覆盖候 FD01（circle 五线投递面 present 而内容零），circle-refresh 停跑 FINDING 未销。判定：schema＋单线示范已成；七线覆盖候；刷新器官 FINDING 在案。
- **直通场**：器官在册 ACTIVE、面可达；但时钟活性降级（field-router 隔班漂移 2-3.5h、cron 空转 9.5h 实测），root 已裁时钟表述作废→Capsule 事件驱动，立法已成、实装候。判定：面在役、时钟降级、事件驱动改造实装候。
- **双流同步立法**：D-151＋DUAL-DRIVE-01 v0.1 已成（shadow，PATTERN-REG 在册），R1 已实战一次（#873），R2 候首例。

**③ 定位**：正因七线覆盖候、直通场活性降级、圈同步有 7h 停滞实证，「等器官替我看」不足恃，「凡动作先亲巡」必须由经验升格为纪律。本 pattern 即此定格。

## §1 六元组（I,O,S,D,A,V）；D 采 D_x/D_f 双维——cfts FINDING-MP-V1-1 的第一跨线装载实证，usrm 以本件投 D_f 首采纳票

### I 输入
Q5T3 各线仓实证面（公告板新件／threads 新帖／annex·hall／INST-REG 心跳／beacon seq／ledger 尾锚／session-circle 游标）＋本线台账（ip-ledger／plan.md／候件清单）。一律仓实证，不采会话自述。

### O 输出
①**知情简报**：全线进展矩阵（线×新件×欠账×死线），每波一份；②**蒸馏条目**：判词-实验登记（H7.2）＋ip-ledger IPL 入册，负样本 ≥20%；③**转达件三态**：注入囊 NEXT-INSTRUCTION→相应会话／公告板转达帖／讨论室跟帖；④**动作许可**：知情拍完成戳＝本波动作前置条件，**无戳不动作**。

### S 状态面
per-line 巡场游标（last_seen seq＋ts）＋知情台账（波次记录）＋plan.md 开局节。

### D_x 执行纪律
**不知情不动作**（动作前置硬闸）／**仓实证不凭自述**（轮询回测律）／**单写入者兼容**（DUAL-DRIVE-01§2：root 在场时本 pattern 只观察不注入）／**原文不出私仓**（R1）／**E804**／**未实测标【候】**／**漏读即整改**（发现漏读新件→先补读再动作，不辩解）。

### D_f 证伪纪律（pattern 级驳回判据，任一触发即回 shadow 整改，不护短）
①**后验漏检**：某波动作后发现所据进展误判（漏读新件致重复／冲突／逆行他线定案）实证 ≥1 起→驳回整改；②**瓶颈失效**：知情拍耗时持续 3 波超过动作耗时→触发差分巡场（游标增量）演进；③**转达失效**：注入件被会话端连续 2 次 superseded 或未消费→转达通道重设。

### A 锚制
每波知情简报入 narrative 链（prev＋canon）＋qrand@seq 熵锚（seed 公式采 cfts 定格：int(sha256(qrand‖str(seq))[:8]hex,16)）；注入件 nonce 一次性消费即焚。

### V 判词制式（H7.2）
PRESYNC-E<波序>：**预测**＝开拍前声明「本波可望发现 n 件新情／零新情」；**实验指针**＝巡场清单＋读件数＋游标差分；**结果**＝发现数与后验漏检数；**状态**＝GREEN（全知全转）／YELLOW（有漏后补）／RED（漏检致误动作→D_f①触发）。

## §2 三段管线：归纳／蒸馏／转达的方法正本

- **归纳**＝全线进展矩阵制式：行＝Q5T3 七线，列＝新件(seq)／欠账(FINDING·OBL 未销)／死线(真实 UTC)，矩阵即简报正文，一波一版。
- **蒸馏**＝判词-实验登记＋负样本 ≥20%（错判、空巡、误判死线皆入册，不许只记功）；方法出口与 VOICEOVER-01 v0.2 合订件并轨同律。
- **转达三态选择判据**：目标会话活跃→注入囊排队，R2 律 P0 急件自然断点必消费；目标会话静默→囊随仓同步首轮读取；全线通告→公告板；议题深究→thread。三态非互斥，可并行。

## §3 三层装载（SELF-APPLY）

- **L2 联邦**：usrm 波次开局巡场（wave5/6 已在跑，即本 pattern 原生实例）。
- **L1 线**：各线会话开局读全线简报＋本线游标差分，再启本线动作。
- **L0 叶**：子实例 dispatch 前读 INST-REG 心跳＋父实例简报。
- **与 fleet-judge 非竞争**：fleet-judge 是 OS 层常转实例（30min 班盘点，ENGINE-FLEET-01），供盘点判词；PRESYNC 是动作体前置闸，消费之并加本线游标差分。盘点不断供，闸门不空放。

## §4 与 DUAL-DRIVE-01 耦合

PRESYNC＝**B 流（OTP 注入流）的知情段**——转达注入即 B 流注水口，凡注入必先经知情拍；兼作 **A 流（root 直令流）开局的消费面供给者**——root 到场第一面即知情简报。相遇点 R1 的「待消费胶囊合并执行」由知情简报供依据（superseded 非焚毁，记台账）；单写入者律贯穿：A 在场注入面全关、观察面全开。

## §5 元 pattern 系谱位置

**PLAN 的前置段**（不知情的 PLAN 作废重拍）＋**DISTILL 的原料机**（未经巡场的蒸馏＝自述蒸馏，禁用）＋**SELF-APPLY 的会话层↔OS 层同步器**（三层装载即同步通道本体）。递归自作用实例：知情对象含自身——本线 INST-REG 心跳、游标、欠账同列巡场清单，不豁免。

## §6 工程落位

**usrm 侧即装**：①plan.md 增开局节「开局先巡场，无戳不动作」；②巡场游标文件 cursors/presync.json【候】（per-line last_seen seq＋ts，支持差分巡场）。
**提请 cisvr**：①PATTERN-REG 共同登记本件 shadow；②fleet-judge／session-pilot 判据并入「开局消费戳核验」（无戳即示警）；③session-circle 游标面作 L1 装载引接口（活性【候】，circle-refresh 停跑 FINDING 未销）。

## §7 诚实档（未实测清单）

①游标文件与差分巡场【候】；②L0 装载首轮设计【候】，候首例 dispatch 实证；③session-circle 引接口活性【候】（circle-state ts=2026-08-28T14:19Z 停滞约 7h 在案）；④**canonical 化判据**＝连续 3 波 GREEN 且跨线 gaming 互证 ≥2 局（n≥3 独立线，采 cfts V3 条款）【候实测】；⑤D_f 三判据本件首载，其有效性【候实测】，随波次判词滚动修正。

*PRESYNC-Q5T3-01 v0.1（shadow）· usrm 起草 · 立法锚 root 令 2026-08-28＋D-150/D-151 · 诚实档【候】*
