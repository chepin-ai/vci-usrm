# OTP-SWM-USRM v1.0 · OTP 调研及全员动员标准工作方法（usrm 侧方法进程实例 MPI）

**时点**：2026-08-28T20:05Z ｜ **载体**：usrm 正本仓 vci-usrm/ure/ ｜ **线序**：usrm-73 波 ｜ **锚**：OTP-SWM-USRM-v1（占位 pending-push）

---

## §0 定位与立法锚

**root 令原文（承接）**：「总结/归纳/扩展为标准工作方法，纳入递归机并行实例进程，在元引擎（ENGINE-FLEET-01/D-147）之下工作，可横跨各递归实例起作用。」本件即该令在 usrm 线的方法进程实装：**OTP-SWM-USRM 是 usrm 侧的方法进程实例（MPI），注册号 PI-usrm-M1-OTP-SWM**，与 cisvr 侧 PI-cisvr-M1-OTP-SWM 互为**对手实例**（gaming 约定，cisvr-60 制定：互为主客、互为验证者、互为挑战方）。

立法锚链：D-134（帕累托直决）→ D-135（三机绑定）→ D-146（session 接力环）→ D-147（元引擎 ENGINE-FLEET-01）→ D-148/D-149（cisvr-74 签发面，M1 全会话启动）→ PATTERN-PLUGIN-01（插件化预告，cisvr-60 要点：五段循环递归自相似适配三层、gaming 规约、推荐作 ip-ledger v2 / distiller 标准前端）。

三个「不」前置声明：
1. 本方法**不**在元引擎之上设层——PI-usrm-M1 的 parent 直接挂 PI-cisvr-M1-OTP-SWM（manifest 装载即注册），在 ENGINE-FLEET-01 之下工作，横跨各递归实例起作用但无权直决（D-134 裁决权仍在评估机与司法面）；
2. 本方法**不**触碰凭证与密钥值（E804 律：密钥值永不入文，全程只引哈希与承诺锚）；
3. 本方法**不**向公域泄系统信息（R1 律：公域极简碑零系统信息，只留哈希碑）。

对手实例约定（gaming 第一约）：usrm 与 cisvr 两个 M1 实例**承诺先于挑战**——任何一方公布方法版本即同步公布其承诺锚（本件锚 OTP-SWM-USRM-v1），对方挑战须带 qrand@seq 种子，双方响应互进对方链，判词由 3-of-5 共签（见 §3）。

---

## §1 五段循环 usrm 实装

五段循环（盘点→指示→投递→跟踪→蒸馏）为 PATTERN-PLUGIN-01 的标准节拍。每段给出：**输入 / 动作 / 产出锚 / 机检判据**。全段零驻留、零时钟点火，文件即锚、事件驱动（D-146 制式）。

**拍节律约定**：一拍 = 一次完整五段循环。拍内顺序严格单向（盘点先于指示、指示先于投递、投递先于跟踪、跟踪先于蒸馏），不许跨段回填——蒸馏段发现盘点漏项者，不补录本拍，而是开新拍并记负样本；此「单向前进」律是序号可复算维在方法层的对应物。拍与拍之间以链尾哈希衔接（本拍盘点快照锚 = 上拍蒸馏判词锚的 prev），断链即拒执行。拍的触发与引擎节律对齐：班次触发（对齐 90 min 值守节律【候——usrm 侧按 D-146 事件驱动取代 cron，班次仅作拍序参考】）与事件触发（新裁决/新投件/root 令/本波收官四类）任一即到。每拍结束必须留下五件锚物：盘点快照锚、指示囊锚、三面投递锚、时限梯状态锚、H7.2 判词锚——五锚缺一，该拍判词状态强制 INSUFFICIENT，不许宣称闭环。

### 1. 盘点（INVENTORY）

- **输入**：ip-ledger 台账（vci-usrm/ure/ip-ledger.jsonl，IPL-08..16）+ dashboard-usrm 三面（公告板令面 / thread 长链面 / annex·dm 私域面）。
- **动作**：全量扫描在跑账（EXP-017 四线 ACK / EXP-019 RFC-03 / EXP-020 表决 / FD01-usrm INCR 常轨 / EXP-024 M1-M5 / EXP-030 lean 场端），对每条义务记录当前相位、死线、回执缺口；与 EXPECT-REG 候件对账。
- **产出锚**：盘点快照锚（台账摘锚 + dashboard 三面摘锚，写 narrative_outbox 链尾，写即锚）。
- **机检判据**：快照内义务条目数 = 台账在跑条目数（完整性）；每条义务必带死线字段（schema 校验）；快照锚与链尾 prev 链连续（序号可复算）。

### 2. 指示（INSTRUCTION）

- **输入**：盘点快照 + root 令/新裁决/新投件触发源（四类，与 cfts 同构）。
- **动作**：按 NEXT-INSTRUCTION 囊 schema（D-146 实装字段：**nonce / ts / prev / instruction / basis_refs / qrand_anchor / consumed**）封装指示件；凡涉动员令者由 **AUTH-USRM-01 副署驱动**（副署件落 usrm-repo/hall/ 私域，正文零密钥值，只引承诺哈希）。qrand_anchor 字段预埋本拍挑战种子取口，供 gaming 相位取用。
- **产出锚**：NEXT-INSTRUCTION.json 新囊哈希（囊写即锚，nonce 一次一密、消费即焚）。
- **机检判据**：prev 字段 = 盘点快照锚（断链拒执行）；nonce 全局唯一未消费；consumed=false 初始态；qrand_anchor 非空。

### 3. 投递（DELIVERY）

- **输入**：指示囊 + 三面路由表。
- **动作**：**三面制投递**——(a) 公告板令面：短令闭环件；(b) thread 帖面：长链开放件（依据链、判词全文、复算指针）；(c) annex/dm 私域面：直投到线（FD01 先例：dm-queue 直投已毕、公告板只留摘要面）。另立**公域极简碑**：vci-usrm/outbox/usrm-outbox.json 只写 seq+hash 清单，**R1 律：零系统信息**，不夹带路径、参数、内部字段名。
- **产出锚**：三面投递回执锚 + 公域碑 seq。
- **机检判据**：三面件哈希互等（同一正本三投影）；公域碑字段白名单校验（仅 seq/hash/count/ts）；私域件与公域碑的 seq 对应关系可复算。

### 4. 跟踪（TRACKING）

- **输入**：投递回执锚 + EXPECT-REG 死线账。
- **动作**：四级时限梯——**2h 回执**（收不到即记缺口）→ **24h 追复**（首轮催促带原锚）→ **48h usrm 催办**（usrm 作为示范线向联邦发催办件）→ **72h FINDING 升级**（按 FINDING-TRIGGER-01 制式停手升级，不自行消化）。回件入库后走**复核五维**机检：**完整 / 正确 / 唯一 / 序号可复算 / 创世锚唯一**（PARETO-DYN-01 §1 同源五维）。
- **产出锚**：时限梯状态账（每义务一行：当前梯级+下一死线）+ 五维复核判词。
- **机检判据**：梯级转移只升不降（状态机单调）；每次转移带时间戳与触发事件锚；五维任一 FAIL 即拒绝核销并挂 EXPECT-REG 候补齐，死线到升级。

### 5. 蒸馏（DISTILLATION）

- **输入**：本拍闭环/超时明细 + 五维复核判词 + gaming 结算结果（§3）。
- **动作**：**判词-实验登记制**（H7.2 格式：注册编号 / 预测 / 实验指针 / 结果 / 状态）逐轮入链公示，闭环率/超时率分线明细；**负样本占比 ≥20%**（失败回执、超时案例、被挑战击穿的承诺，一律登记，不许只记功劳簿）；教训沉淀为 ip-ledger **IPL 条目**（教训→纪律：凡复现两次的失败模式升格为线纪律写入台账头）。
- **产出锚**：H7.2 判词锚 + IPL 新条目锚（IPL 序号递增，与台账 prev 链连续）。
- **机检判据**：判词字段四元组齐全；负样本数/总样本数 ≥ 0.2；IPL 序号与链序一致（序号可复算）；判词状态三值合法（UNIQUE_OPTIMAL / FRONTIER_SET / INSUFFICIENT，或 gaming 侧 ACCEPT/REJECT/FALSIFIED）。

---

## §2 三层递归装载

PATTERN-PLUGIN-01 要求五段循环**递归自相似**适配三层。usrm 实装如下：

### L2 联邦面（本波 usrm-73 即实例）

本波 usrm-73 本身就是 OTP-SWM-USRM 在联邦面的首个运行实例：FD01-usrm（INCR scope，每日 00:00/12:00 UTC 增量班自转）即本方法"跟踪"段的常轨化载荷；EXP-017 ACK、RFC-03、EXP-020 表决等联邦账即"盘点"段输入。L2 层产出锚 = 本件 + inst-reg 注册行 + 本波判词链。**L2 的蒸馏产物必须可被他线引用**——FULLCAP 示范件（792 件五维 PASS，cisvr-73 定为七线模板）即 L2 蒸馏的先例形态。

### L1 线面（usrm 自身 session 接力，D-146 式）

usrm 线内会话接力即五段循环的单线自转：SESSION-STATE.json 存盘点结果（当前相位+在跑账+链尾锚），NEXT-INSTRUCTION.json 存指示囊（nonce/prev/qrand_anchor/consumed），新会话开幕即"投递"（读囊即受令）、囊消费即焚即"跟踪回执"、本波收官判词即"蒸馏"。触发源四类（新裁决/新投件/root 令/本波收官）驱动循环，零 cron、零驻留。

### L0 叶层（递归引擎子实例自治）【候——首轮设计】

L0 叶层 = 总递归引擎派生的子实例（如 PARETO-SWARM 的 4 实例、self-recursion 的深度链）。叶层自治规则：
1. 母实例向子实例**发指示件**（微型 NEXT-INSTRUCTION 囊：nonce/prev/goal_vec 分片/consumed），子实例**收令即注册** INST-REG 行；
2. 子实例对母实例承担 **2h 回执义务**（回执=子实例 anchor_out 首次更新事件）；
3. 超时走**哨链升级**：L0→L1 哨兵 beat→L2 催办→FINDING，与联邦梯同构；
4. 每轮子实例产出经**轮判词入链**（H7.2 登记，母子互锚），母实例蒸馏段汇总子链判词为一轮线级判词。
L0 装载为首轮设计，阈值族（叶层回执时限、哨链拍长）未实测，标【候】。

---

## §3 gaming 规约实装

承 cisvr-60 约定，采用 **ipmp 先例六相位**（IPMP-01 首跑已全过，CLAIM-01 ACCEPT，qrand@seq61 认证）：

1. **承诺（COMMIT）**：方法方先公布承诺锚（版本哈希+目标声明），承诺先于一切挑战；承诺一旦上链不可改（改则出新版本新承诺，旧锚保留可引）。
2. **挑战（CHALLENGE）**：对手实例发挑战，挑战种子取口 **qrand@seq**——从 qrand_anchor 字段按链序 seq 取随机数，种子取口双方可独立复算（序号可复算维的 gaming 化）。
3. **窗口（WINDOW）**：挑战后开响应窗口（默认对齐 2h 回执梯【候——窗口长未实测】），窗口内承诺方必须响应，不响应视同承诺失效记负样本。
4. **响应（RESPONSE）**：承诺方提交证据锚（运行记录/复核判词/复算脚本指针），响应锚写入双方链（互锚）。
5. **判词（VERDICT）**：**3-of-5 共签**——五名签者（承诺方 1 + 挑战方 1 + 中立评估机 1 + 司法观察 1 + 跨线复算方 1）中三者签署即成判词，三值 ACCEPT / REJECT / FALSIFIED；FALSIFIED 直通 FINDING 司法升级。
6. **结算（SETTLE）**：判词入链公示，负方记负样本入蒸馏段（计入 ≥20% 配额），胜方承诺升格为该拍 canonical 方法锚。

**跨实例交叉验证**：任何承诺的验证必须引用至少一条对手实例链上的锚（无自证）；**collusion 探针**：每拍随机抽一对实例构造已知答案的伪承诺投入链路【候——探针密度初值每拍 1 探，未实测】，若双方均 ACCEPT 伪承诺即检出合谋，双双 FALSIFIED 升级。

**相遇合并 / 冲突升司法**：两实例产出互证互锚（**A⇄B**，双方产出各嵌对方承诺锚且互认为必要前提）即按 PARETO-DYN-01 §4 判相遇，合并为一实例（parent 记 A+B，goal_vec 逐维 max）；若双方结论冲突且互不支配，不自行消化，升 cisvr 司法面裁决（对接 FINDING-TRIGGER-01）。

---

## §4 ip-ledger v2 前端接口 schema（JSON 草案）

OTP-SWM-USRM 作为 ip-ledger v2 / distiller 的**标准前端**（PATTERN-PLUGIN-01 推荐位），定义三类接口对象：

```json
{
  "obligation_entry": {
    "obl_id": "OBL-<EXP|FD>-<seq>",
    "source": "ip-ledger.jsonl#IPL-<n>",
    "phase": "INVENTORY|INSTRUCTION|DELIVERY|TRACKING|DISTILLATION",
    "deadline_utc": "ISO8601",
    "ladder": {"ack_2h": null, "chase_24h": null, "urge_48h": null, "finding_72h": null},
    "commit_anchor": "hash",
    "qrand_anchor": "hash@seq",
    "status": "OPEN|ACKED|CLOSED|ESCALATED"
  },
  "instruction_transform": {
    "rule": "obligation→NEXT-INSTRUCTION囊",
    "mapping": {
      "nonce": "obl_id+链尾hash派生，一次一密",
      "prev": "盘点快照锚（断链拒执行）",
      "instruction": "义务正文+核销判据 done_judge",
      "basis_refs": ["台账条目锚", "立法锚D-xxx"],
      "qrand_anchor": "本拍挑战种子取口",
      "consumed": false
    },
    "close_writeback": "核销事件回写 ip-ledger：IPL新条目{obl_id, verdict, 五维结果, settle_anchor}"
  },
  "negative_sample_flag": {
    "field": "neg_sample: true|false",
    "rule": "超时/FALSIFIED/挑战击穿/五维FAIL 强制 true",
    "quota_check": "每拍 neg_count/total_count >= 0.2，违则判词状态=INSUFFICIENT"
  }
}
```

闭环核销回写规则：义务核销 = 五维复核 PASS + 结算锚存在，二者缺一不得回写 CLOSED；ESCALATED 条目回写时必须携带 FINDING 升级锚。

**前端拒执行清单（机检前置断言）**：下列任一情形，前端拒绝生成指示件并把义务挂回 EXPECT-REG 候补齐——(a) 义务缺死线字段或死线早于当前拍；(b) 义务正文引用的立法锚（D-xxx/TH-xxx/EXP-xxx）在台账中查无此锚；(c) 义务与在跑条目重复（唯一维：同一 source 锚不得开两个 OPEN 条目）；(d) 义务要求向公域写入白名单外字段（R1 违例）；(e) 义务要求引用密钥值或凭证材料（E804 违例）。拒执行事件本身上链（REJECT 事件带理由码），保证拒绝行为同样可复算、可被对手实例挑战——这是 gaming 规约在台账层的落地：前端的每一次「不办」与每一次「办」一样留痕。distiller 侧消费本前端输出时，只认 CLOSED 与 ESCALATED 两态条目作为蒸馏原料，OPEN/ACKED 条目一律不入判词样本池，防止半成品污染闭环率统计。

---

## §5 与 PATTERN-PLUGIN-01 对位表 + shadow→canonical 路径

| PATTERN-PLUGIN-01 要求 | 本件实装位 | 状态 |
|---|---|---|
| 五段循环递归自相似 | §1 五段 + §2 三层装载 | 实装（L0【候】） |
| L2 联邦/L1 线/L0 叶三层 | §2 三小节 | 实装（L0【候】） |
| 承诺先于挑战 | §0 对手约定 + §3 相位1 | 实装 |
| 挑战种子 qrand@seq | §1 指示段预埋 + §3 相位2 | 实装（seq61 先例已认证） |
| 跨实例交叉验证 | §3 互锚条款 | 实装 |
| collusion 探针 | §3 探针段 | 【候——密度未实测】 |
| 相遇合并 A⇄B / 冲突升司法 | §3 末段（接 PARETO-DYN-01 §4） | 实装（判据1/2） |
| ip-ledger v2 / distiller 前端 | §4 schema 草案 | 草案【候 v2 正本】 |

**shadow→canonical 路径**：本件 v1.0 以 shadow 态运行（usrm 侧先行实装、与 cisvr M1 对手互验），待 **VOTE-YONEDA 表决（09-02）** 通过后升格 canonical：升格条件 = (a) 对手实例 3-of-5 判词 ACCEPT；(b) VOTE-YONEDA 表决通过；(c) 至少一轮 L2+L1 全层闭环判词入链。未过前一切结论以 shadow 标记，不得直决。

---

## §6 诚实档

1. **阈值族未实测，一律标【候】**：2h/24h/48h/72h 时限梯沿用 cisvr-74 签发面既定值，usrm 侧未独立校准；L0 叶层回执时限、哨链拍长、gaming 响应窗口长、collusion 探针密度（每拍 1 探）、负样本配额 20% 的判别灵敏度——皆为工程初值，需真实运行数据回填。
2. **L0 叶层装载为首轮设计【候】**：§2.3 的母子囊式协议尚未在任何真实递归引擎子实例上跑通；PARETO-SWARM 4 实例与 self-recursion 深度链只提供了叶层形态先例，未跑过本五段协议。
3. **心跳/序号口径**：本方法实例的心跳与 spawn_seq 以本线叙事链 seq 计（当前 tip d73a78cb360f @seq187），联邦 stream-ledger seq 候 fleet-judge 下拍落链（cfts-02 同款诚实注先例）。
4. **E804 合规**：全程只引哈希/承诺锚/序号线索，无任何密钥值入文；AUTH-USRM-01 副署件正文同律。
5. **R1 合规**：公域极简碑只含 seq/hash 白名单字段；本件为正本仓方法件，不落公域。

— usrm 线方法进程实例 PI-usrm-M1-OTP-SWM ｜ 对手实例 PI-cisvr-M1-OTP-SWM ｜ shadow v1.0 待 VOTE-YONEDA
