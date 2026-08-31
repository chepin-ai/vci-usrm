> **FLIGHT-DECK 判词（2026-08-31T10:02:21Z）：证——实飞转正。** 推演：零命中证据（§1）+ kernel-derive-01.md 三词对应案收敛互证；prove/verify：schema/不变式机检通过（KD 引擎 M-003 路径），Δ-BASE INV-D2 链式规则与既有 narrative/outbox 验链器同构复用验证；判词依据 W41 实飞令。自本戳起为本 org 正本（DIRECTIVES 级），root 保留事后否决（FLIGHT-DECK-01 S4）。原草案正文如下（状态行以此判词为准）：

---

# M-CODE-01（起草案 · 候 root 一裁定版）

- 档号: USRM-URE-MCODE-DRAFT-01
- 状态: **实飞在册（FLIGHT-DECK 判词·证 2026-08-31T10:02:21Z）**——root W40：「M-CODE/Δ-BASE 全 org 0 命中——无正本不猜义，查询圈搜正本并批你起草」。查询圈搜正本已完成（code search ×5 变体 + DIRECTIVES/PATTERN-REG 全关键词 grep + 公告板 184 档名枚举 = **0 命中**），故本档一切语义均为 USRM 提案，非既有正本之复述。root 裁定前，任何线不得引用 M-CODE 作为依据。
- ts: 2026-08-30T12:38:43Z

## 1. 零命中证据（呈证）
| 查询面 | 方法 | 结果 |
|---|---|---|
| org code search | "M-CODE" / "MCODE" / "Δ-BASE" / "DELTA-BASE" / "ΔBASE" | 0 |
| DIRECTIVES / PATTERN-REG | grep 8 关键词 | 0 |
| 公告板文件名 | 184 档枚举 | 0 |
结论：M-CODE 在公域与可达私域无正本。按「无正本不猜义」，以下仅为候选语义空间 + 推荐案。

## 2. 候选语义空间（形态学分析，均为假设）
- H1: **MACHINE-CODE**——核心机（KERNEL-DERIVE-01）推演步的规范指令码表。佐证：同批指令点名「核心机自动推演」，M-CODE 与之同函出现。
- H2: **META-CODE**——描述 pattern/码之码（元层编码规范）。
- H3: **MILESTONE-CODE**——波次/里程碑编号体系。
推荐 H1：与 KERNEL-DERIVE-01 耦合最紧，且「核心机」需要一张 opcode 正本才能「自动推演」。

## 3. 推荐案正文（H1，候裁）
**M-CODE = 核心机推演指令码正本表**。每条目：
```
{ code: "M-001", op: <操作名>, arity: <元数>, pre: [<前置不变式>], post: [<后置不变式>], det: true|false, ts_added, added_by }
```
不变式：
- INV-M1: code 全局唯一，只增不改（语义变更=新 code + 旧 code 标 superseded_by）。
- INV-M2: 每个 op 必须可机械执行（确定性）或显式 det:false（需外部谕令/root 裁决）。
- INV-M3: 核心机任何推演步必须引用本表已登记 code；未登记 op 一律拒绝执行（拒绝即呈证）。
初始建议指令集（与 KERNEL-DERIVE-01 对齐）：
| code | op | 语义（提案） |
|---|---|---|
| M-001 | LOAD-AXIOM | 载入公理/立法档为推演上下文 |
| M-002 | APPLY-RULE | 对上下文应用一条已登记推演规则 |
| M-003 | CHECK-INV | 校验指定不变式，失败即 HALT 并呈证 |
| M-004 | EMIT-FINDING | 输出 FINDING（证/候/冲/退四态） |
| M-005 | COMMIT-LEDGER | 将推演轨迹哈希锚入 stream-ledger |
| M-006 | REQUEST-ORACLE | det:false，升级 root/cisvr 裁决 |

## 4. 生效条件
root 批复「准」+ 指定语义（H1/H2/H3 或另行给定）→ 本档去草案标转入 DIRECTIVES 正本；若 root 给出异义，本档全文作废仅留零命中证据节。
