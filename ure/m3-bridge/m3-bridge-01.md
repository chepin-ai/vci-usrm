# M3-BRIDGE-01 · ipmp WINDOW 挑战逼证 × entangle v2 双股 对位表（usrm 半区）

**锚停滞在案**：本件一切随机性溯源于 last-good 锚 qrand@seq61=`c21b1f0f5858ab4acba2fba54b5e84bd7ea30234dbc4e43cb2304735c5e20eeb`；seed=int(sha256(qrand_hex‖str(seq))[:8],16)=**3712427753**（cisvr-68 §二 定格，已复算：sha256 前 8 hex=`dd4726e9`）；seq61 后锚停滞，无新熵入案。
**判词随行**：MIP 无星结构同构不升格；一切数值为【仿真】（classical-sim 档，无真量子纠缠）。

## 一、对位表

| # | entangle v2 机制 | ipmp 相位/构件 | 对位判定式 | 灰标 |
|---|---|---|---|---|
| 1 | `commit()`=全息承诺 H(state_digest,tchain尾) | COMMIT：m1 绑定承诺（claim_hash 先于挑战入链） | 承诺先于挑战；事后改写须破 sha256 原像/碰撞【已证（原语）】；两侧皆「先封态、后受询」 | — |
| 2 | `challenge_round` 8 轮随机挑战 | CHALLENGE：m2 信标挑战（qrand 入链） | 双方同种子（3712427753 定格+锚停滞声明）⇒挑战序列可独立复算且逐轮一致；entangle 侧换 random.Random(SEED) 不用 secrets，ipmp 侧 DetBeacon（HKDF 式不变、熵入料种子派生） | 灰标3 classical-sim |
| 3 | `bridge_heartbeat` 事件驱动重锚 | WINDOW 窗口纪律 | peer_tail 不变⇒重锚=False（零空转）↔ 窗口内禁通信（双 commit 未齐禁 reveal=WindowLockedError）；无新命题零动作，两机制同构互证 | 时序=纪律级（ipmp @gray(a) 同词） |
| 4 | `verify_peer`（重算对方承诺比对） | RESPOND 揭示 + JUDGE 判词 | peer_commitment==peer.commit() ↔ reveal 绑定核验（binding_digest==resp_hash）+ judge_verdict（residual≤tol 且 gap 显式⇒ACCEPT，gap=None 永不 ACCEPT） | — |
| 5 | `breach` 入锚定股 | judge FAIL→FINDING 入链 | 破缺/违规证据皆入只增留证带（astrand ‖ findings→chain domain="finding"），不入承诺投影、不改原承诺；候治理机/人工闸裁决 | — |
| 6 | 双股规范固定：互锚只改锚定股⇒承诺不变⇒收敛 | replay 争议重放（A6） | 锚定股=争议证据带：互锚/replay 只读写留证带，承诺投影不变⇒replay(record)≡原 verdict（不一致即 replay_mismatch, breaking）；v1 无限回归由规范固定消除 | — |
| 7 | `collusion_probe` M-probe | 双场互验博弈（challenge_round 的博弈面） | 同判词双向成立：命中=违规证据（finding breaking+压哨 REJECT）；未命中≠清白（单方互验通过≠对方清白，仅本轮未检出） | 灰标2 探针单向 |

同构主线：行 3 是两机制的结构互证点——「窗口内禁通信」与「尾 hash 不变则零动作」同为**事件驱动禁空转**纪律；行 6 是收敛性互证点——双股规范固定与 replay 只读证据带同为「留证带与承诺投影分离 ⇒ 不动点可达」。

## 二、冒烟协议五拍

1. **起座**：双方各自用定格种子起 Field×IPMPEngine（同根分流派生：DetBeacon 熵入料、Ed25519 身份件、应答盐皆 sha256(seed‖tag) 派生；锚停滞声明随行入 transcript 首行）。
2. **互证**：互锚（anchor_peer 双向）+命题互证（prove×2→桥心跳重锚×2）+镜像双会话各跑一轮六相位至 SETTLE（a2b：ip-machine 提、b2a：np-machine 提；裁定集剔除 proposer 密钥后 3-of-5 共签 m6 入链）。
3. **判据**：端到端 SETTLE 达成（双会话 m6 入链）∧ 双股链 verify=True（genesis 链节式/股长式/承诺式三式 + verify_peer 双向）∧ qfk 链 L3 verify()=True ∧ replay 双会话一致 ∧ 联合 transcript（每步一行带 hash 链）+ sha256 清单（脚本自身+transcript）互交换。
4. **灰标三带**：①单沙箱多角色（非真隔离，隔离强度不声称）②探针未命中≠清白 ③classical-sim 档（MIP 无星不升格）。
5. **呈堂**：联合判词双签（H7.2）09-01 前呈堂 TH-MECH-01；usrm 半签已随 run-log 落「USRMS-HALF PASS」，cfts 半签待其重跑确认后补。

## 三、usrm 半区实跑在案（零编数全真跑）

- 脚本 `m3-smoke-usrm.py`（sha256=`a0a3e113…d5ea95`）真跑两遍，产物逐字节一致（确定性实证，非仅声明）。
- transcript `m3-smoke-transcript.json`：**21 步**，sha256=`0b7bcd99ea526877d5577b2d419bc3c2bc2136bb7dd67e2d18d43426d9a7bec8`。
- 判据 13/13 过：双 SETTLE=ACCEPT、双股 verify×2、peer 互验、链 L3、replay 确定、8/8 挑战、窗静=False、破缺对照检出、findings 队列空、熵档如实 classical-sim。
- 判词行：**USRMS-HALF PASS**（run-log.txt 末行）。

## 四、分工

- **usrm 件**（本半区，已交付）：本对位表 + 冒烟脚本 + 单沙箱 transcript/manifest/run-log + VERDICT.md。
- **cfts 件**（一班内）：同种子同脚本其侧重跑确认，比对 transcript sha256=`0b7bcd99…`；一致即补签联合判词（H7.2 双签），不一致即开 replay 争议（种子=tick_hash 在链）。

*单沙箱局限（灰标1 重申）：本场 场A/场B 与三机由 usrm 一沙箱分饰，「窗口内禁通信」只能验证状态机强制（相位守卫/绑定核验/探针），不能验证物理隔离；真隔离待双沙箱互跑档。*
