# Δ-BASE-01（起草案 · 候 root 一裁定版）

- 档号: USRM-URE-DELTABASE-DRAFT-01
- 状态: **草案（PROPOSED）**——零命中证据同 M-CODE-01 第 1 节（同批查询，0 命中）。root 裁定前，任何线不得引用 Δ-BASE 作为依据。
- ts: 2026-08-30T12:38:43Z

## 1. 候选语义空间（均为假设）
- H1: **DELTA-BASELINE 注册表**——以「基线锚 + 差量」方式登记系统各链/各网的状态基线，后续变化以 Δ 描述。佐证：org 内已有「dual-net baselines 05ece907/41f926f8」之实，baseline 概念在用。
- H2: **增量数据库**——只存差量、由重放还原全态的存储规范。
- H3: **版本差分基线**——各仓 HEAD 相对立法基线的偏离度量。
推荐 H1：与既有 baseline 实物衔接，且「Δ」天然对偶于链 tip。

## 2. 推荐案正文（H1，候裁）
**Δ-BASE = 差量基线注册表**。每条目：
```
{ base_id, scope: <链/网/仓>, anchor: <基线哈希/seq>, ts_anchor,
  deltas: [{ seq, delta_hash, note, ts }], tip: <当前尖>, status: ACTIVE|FROZEN|RETIRED }
```
不变式：
- INV-D1: anchor 一旦登记永不改写；纠错=新 anchor + 旧档 RETIRED。
- INV-D2: deltas 链式：delta_hash = sha256(prev.tip + canon(delta))[:12]——与 narrative/outbox 同构，复用既有验链器。
- INV-D3: 任何线引用基线必须给 (base_id, tip)；无 tip 引用视同未锚定。
- INV-D4: 首批登记对象（提案）：narrative 链、outbox 链、stream-ledger、张量双网（05ece907/41f926f8 既有锚直接收编为首批条目）。

## 3. 与 M-CODE 的关系（若两件同批准）
M-005 COMMIT-LEDGER 执行时同步向 Δ-BASE 追加 delta——推演轨迹与基线差量同源同锚。

## 4. 生效条件
同 M-CODE-01 第 4 节：root 一裁定义，本档转正或作废。
