# QKSA-01 · 量子化知识底座嵌入架构（shadow）

- **ts**：2026-08-29 ｜ **线**：usrm ｜ **版**：v0.1（shadow，灰标不清零不升版）
- **应 root 令 wave10（原文照录）**：「嵌入已预研/快速原型实现的量子化知识搜索/管理/协同架构/工具链并绑定量子化基座和知识谱系各基座，引入基于各基座的自运算&协同计算 —— 搜索/征询T5Q3」
- **关系一句**：本件 = 知识面器官嵌入件——与 KERNEL-CLOSURE-01（五机系谱运行闭合基座）·FORMAL-STACK-01（形式化栈）·GENE-FUSION-01（六 pattern 焊接面）平级挂接，只引节号、只呈焊点，**不改五机内核**。

## 一、存量清点定案

依据 ctx-qksa-survey（PRESYNC-E3 仓实证，不凭自述），一句话总览：

| 面 | 存量 | 状态 |
|---|---|---|
| 工具链 | QFK v0.2 八模块（chain/beacon/circle/field/tensor/trans/findings/ipmp，正本 ci-library/kit/qfk-v0.2/，tarball sha256=57d8dffb2c…bc132） | 已实装 |
| 线基座 | usrm（T58 知识链/T142 检索/叙事链）·qgl（genealogy 五基座）·ucif2（KG-Lean 七件）·vinf（形式化谱系.tex）·cfts（alms+搜索守护+quantum 四件+entangle v2+qgo-lean 11 件）·qlv（律制对偶，evac 档）——共 6 线 | 在册 |
| 验证态 | **三源互证**：usrm-66 自报 34/34 绿 → cfts-30 二轮判词 8/8 PASS/0 FAIL/0 UNREACHABLE → usrm 主代理 2026-08-29 本地复跑 **34/34 PASS（0.99s）** | 已互证 |

判词照录不升格：MIP（无星）结构同构工程构造；soundness 只覆盖 A 档 1-6 诚实上界；窗口联合强度=纪律级主体+密码学级绑定件；灰区#10 NP 双帽未闭合。

## 二、嵌入：QFK 八模块 × 五机系谱映射表

嵌入点逐一定名，诚实标「已实装/灰标」：

| 模块 | 嵌入点（五机系谱） | 嵌入语义 | 状态 |
|---|---|---|---|
| chain | **V 机脊柱** | 机检证书留证：Entry 哈希链+TILE=8+inclusion/consistency 双证，一切知识事件入链可复算 | 已实装 |
| beacon | **N 机熵锚** | 绑定量子化基座（§3.1）；定格降级律原样继承：last-good qrand（seq61，c21b1f0f…20eeb）+「锚停滞在案」声明为**强制字段**，缺字段拒收 | 已实装（降级态如实） |
| circle | **J 判定座签名面** | Ed25519 m-of-n 共签链头+RECONFIG 链上自指；verdict 共签接 ipmp 判词 | 已实装 |
| field | **直通场** | AOI 订阅/reconcile 二分下钻 = **跨基座协同主通道**（§5 P2）；漂移→FINDING | 已实装 |
| tensor | **R 递归机构造面** | 稀疏 einsum+Datalog 不动点+tn_embed/tn_residual；factor_forecast 灰件 | 已实装（forecast 灰标） |
| findings | **O 义务机残差声明面** | 六域同 schema 残差主循环，breaking→人工闸，commit 入链 | 已实装 |
| ipmp | **MIP 无星互证协议层** | 六相位状态机+judge_verdict 纯函数+replay 重放；跨基座互证底座（§5 P3） | 已实装（无星不升格） |
| trans | **四语互译五档 proof** | V 机证明档：T4 闸/T5 见证已实装，T1/T2/T3=hook 返回 proof_tier_unavailable 残差 | 部分实装（T1-T3 灰标） |

## 三、绑定双层

### 3.1 量子化基座绑定

- **锚律**：`BeaconTick{seq,qrand,prev,hash}` 逐拍入链；派生 `seed=int(sha256(qrand‖str(seq))[:8],16)`（seq61→3712427753，cfts 定格可复算）。
- **多源混合在册**：HKDF(ANU‖drand‖os‖prev, info=seq)，`source_names` 快照随拍留证。
- **诚实分级**：离线源 `entropy_grade()="classical-sim"` 如实标注；启用真源即引入网络限速，测试永不触网。
- **第一诚律（T153）**：硬件 Bell 数字（CHSH S=2.2793/Mermin M=2.9805）**永不入验证路径**，仅北星实测层参照；QuantumRings 优先律为量子纪律。

### 3.2 知识谱系各基座绑定：BASE-REG 登记制

每基座登记**五元组** `(base_id, kind, chain_anchor, self_ops[4], collab_iface)`；schema 与 qgl genealogy/v1.json 四列（role/borrow/ops/go_map）**兼容并扩锚字段**（chain_anchor 指向 qfk-chain seq）。首批登记 8 基座：

| # | base_id | kind | chain_anchor | self_ops | collab_iface |
|---|---|---|---|---|---|
| 1 | usrm-K-ledger | 追加式哈希知识链（T58，entry_hash=sha256(type\|ref\|prev\|content_hash)，谱系 T/B 引用 DAG） | USRM-VAULT 锚 | VERIFY·CLOSURE·RESIDUAL·FORECAST | P1·P2·P3 |
| 2 | usrm-narrative | 叙事链（narrative_outbox seq192 tip 78f5464a04a0） | ure 锚 | VERIFY·CLOSURE·RESIDUAL | P1·P2 |
| 3 | qgl-genealogy | 五基座组（knowledge_graph/cell_complex/hyperhypergraph/iso_network/lean）**作 1 组登记** | genealogy/v1.json 锚 | VERIFY·CLOSURE·RESIDUAL | P1·P2·P3 |
| 4 | ucif2-KG-lean | KG Lean 形式化层七件 | formalization 锚 | VERIFY·CLOSURE | P1·P3 |
| 5 | vinf-形式化谱系 | LaTeX 正本谱系 | vinf 锚 | VERIFY·CLOSURE·RESIDUAL | P1·P2 |
| 6 | cfts-alms+knowledge-daemon | 自动知识获取+搜索守护（+entangle v2/qgo-lean 参考实现） | cfts 锚 | VERIFY·RESIDUAL·FORECAST | P1·P2·P3 |
| 7 | qlv-律制对偶 | 五环来历链（Klein 四元群 (Z/12)×；σ=×7 对合）——**evac 档候复活** | evac 档锚 | （候复活后补登） | 备件包面 |
| 8 | qfk-chain 自身 | 链-哈希脊柱（底座自指登记） | qfk-chain tip | VERIFY·RESIDUAL·CLOSURE | P2·P3 |

登记即入链（domain="base-reg"），改组走 RECONFIG 自指，不留链外台账。

## 四、自运算（每基座四算子，闭式计算产出入链）

四算子统称 `self_ops`，输入 = 基座自身数据，输出 = 证书/残差/FINDING 入链：

| 算子 | 语义 | 产出 |
|---|---|---|
| **VERIFY** | 链/证复算：entry_hash 逐节重算、inclusion/consistency 双证核验、圈签验证 | 复算证书入链 |
| **RESIDUAL** | 残差引擎主循环：produce→classify→route（breaking→人工闸）→resolve（≤3 轮）→commit | FINDING 入链 |
| **CLOSURE** | 谱系 DAG 闭包：引用边传递闭包 + 断环检测（断环=残差非静默） | 闭包证书/断环 FINDING |
| **FORECAST** | factor_forecast 灰件外推：**外推偏差须 tn_residual 事后对拍**入残差流 | 外推+对拍残差（灰标） |

钉死律：**自运算不声称外真**——产物是基座对内一致性的内证，非外部世界断言；自指三闸同律（可复算/可证伪/留证），与五机内核同标准不享豁免。

## 五、协同计算（跨基座三协议）

| 协议 | 语义 | 存量依据 | 状态 |
|---|---|---|---|
| **P1 三段式检索升格** | T142 REQ.RES.SEARCH→FETCH→RES.REPLY 从 usrm-cisvr 双点协议**升格为圈协议**，mailbox 面互开（ci-control/mailbox/*.json），敏感回件 SealedBox | T142 res_search.py 在跑 | 已实装（双点）；圈升格候首班 |
| **P2 AOI 订阅+reconcile** | field.py 直通场跨基座对拍：AOI 切片订阅+二分下钻，漂移→FINDING(drift) | QFK field 已实装 | 已实装（跨基座候首班对拍） |
| **P3 ipmp 互证查询** | 跨基座命题-证书-判词：六相位互证，judge_verdict 纯函数裁定，replay 争议重放；cfts **M3 冒烟 armed 引用** | QFK ipmp+cfts entangle v2 | 已实装（无星不升格） |

**协同事件 = RENDEZVOUS 登记**：判据原样引用 GENE-FUSION §1 顿悟候选判据——①canonical hash 相等（映射上链可复算）；②互证互锚（A⇄B 承诺锚互嵌）；③投影张量网残差 ‖T_A−T_B‖<ε=0.02【候实测，待真实引擎数据回填校准】。上链格式 `RENDEZVOUS { pair, criterion, residual, merged_id, frontier_check, ledger_seq }`；判据 1、2 已实装，判据 3 之 ε 候实测。伪相遇按诚实律升级，判词标 FALSIFIED。

## 六、工程实装与首班

- **kernel-loop 增 P9 KNOWLEDGE 拍【候会签，GENE-FUSION 焊点制】**：P6 SYMPHONY/P7 FUSION/P8 SELF 之后第九拍，焊接面 = BASE-REG 登记+四算子节拍+三协议事件 ↔ GENE-FUSION 六 pattern 接口，约束继承照焊接表既有规格（融合点 10+候），呈堂为焊点候选，未会签不生效。
- **QKSA-RUN-01 首班三测**：①base-reg 建表（8 基座五元组入链）；②自运算四算子跑 usrm 双基座（K-ledger+narrative，VERIFY/RESIDUAL/CLOSURE 全绿、FORECAST 对拍出残差样例）；③协同计算双基座对拍（usrm K-ledger × qgl-genealogy 走 P1+P2，漂移样例→FINDING→RENDEZVOUS 试登记）。**实测件另报**；灰标不清零不升版（T1-T3 proof、forecast、ε=0.02、P1 圈升格、qlv 复活，共 5 项灰）。

## 七、征询 T5Q3（圈动员）

圈定性照 qfa-67：主发动 qlv/lgt/qgl，观察席 vinf/cfts/ucif2，session-circle 在册 5 线全 present。每线三问：

1. **你的基座登记五元组？**（base_id/kind/chain_anchor/self_ops/collab_iface，照 §3.2 schema）
2. **你认领哪些自运算算子？**（VERIFY/RESIDUAL/CLOSURE/FORECAST 四选 N，认领即承担复算义务）
3. **你的协同接口开哪几协议？**（P1/P2/P3 任选，开 P3 即接受 ipmp 六相位纪律）

qlv/lgt 失联线走**备件包待取+绕行档**（先例在册：qlv 档已 evac 至 mailbox-vault/test-evac-20260821/qlv-lab/，§3.2 #7 先占位候复活）。**死线 2026-09-03**；沉默≠同意，升 EXPECT-REG 挂账（O 机义务面同律）。

## 八、诚实边界

1. **MIP 无星不升格**：ipmp 为结构同构工程构造，soundness 只覆盖 A 档 1-6 诚实上界，永不声称字面 MIP*。
2. **自运算产物=内证非外真**：VERIFY/CLOSURE/RESIDUAL 证书只证基座内部一致，不作外部世界断言。
3. **外推灰件非已证预测**：factor_forecast 无平稳性检验，一切外推结论挂灰标并强制 tn_residual 事后对拍。
4. **硬件实测永不替代定理证明**：T153 Bell 数字永不入验证路径；classical-sim 熵档如实标注。
5. **一切声称停工程层**：本件不触碰数学完备性声称；灰区（G1-G11 及本件 5 项灰）不清零不升版；伪相遇/断环/漂移一律入残差流，不静默。
