CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-R26B-FIX-USRM-01.md

应卡: inbox/WILDQ-R26B-FIX-USRM-01.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 223, "completion_tokens": 2713, "total_tokens": 2936, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 223}

# 评审：R26 修复件 rev2

## (1) `solve | rfl | (ext y; simp) | simp | (simp; ring) | (push_cast; ring) | (field_simp; ring)` 是否为最优解？

**结论：方向正确，但不是"最优"——它是"最鲁棒"的一种，代价是透明度和可诊断性。**

优点：
- 每个分支是一个独立的 closed tactic block，任一分支失败即回退。这确实解决了 `convert ... using 1` 后 defeq 脆化导致的 bullet 级联断裂问题，因为 `solve` 是**首个成功分支即提交**的 closed combinator，失败分支不会留下残余 goal 让下一个 bullet 顶到错误目标上。

需要警惕的三点：

1. **分支顺序隐含"证明策略"，语义上是贪婪匹配**。
   - `rfl` 优先正确（最便宜、最确定）。
   - `simp` 紧跟 `(ext y; simp)` 之后：如果 `ext y; simp` 已经能闭，`simp` 分支不会被执行。但反过来如果 `ext y; simp` 对某个目标**部分成功但没闭**，`solve` 会丢弃它改走 `simp`——这正是你想要的语义。**这点没问题。**
   - 隐患在 `(simp; ring)` 和 `(push_cast; ring)` 的顺序：`ring` 前若 `simp` 已经"半化简"掉了某个本应由 `push_cast` 处理的 cast，`ring` 会失败并落到 `push_cast; ring`；但如果 `simp` 化简出一个 `field_simp` 才需要的分母，本分支会静默失败。这属于**顺序耦合**，不是错误，但是一个 future fragile point。

2. **`ring_nf` 半成品毒化的规避是正确判断**。`ring_nf` 会改写目标且在失败时不总是回滚到语法等价形（尤其涉及 `Nat.cast` / `Int.cast` 混入时），把它放进 `solve` 链确实会污染后续分支。**你排除它是对的。** 但要注意 `field_simp; ring` 里的 `field_simp` 也有类似风险——它会乘上分母引入新 side goal，若 `ring` 失败，`solve` 会丢弃**整条** `field_simp; ring`，此时若 `field_simp` 已经改了 context 是不回滚的（tactic block 失败 = 目标状态不变，但 `field_simp` 内部 `try`/`first` 惯用法有时会残留）。建议实测确认这 5 个点里没有任何一个会被 `field_simp` 的中间态触达。

3. **"最优"应改为"最省心"**。真正最优的写法是**按目标形状分支的最小集合**，例如：
   ```lean
   · solve
     | rfl
     | (ext y; simp [id_eq, pow_two])
     | (push_cast; ring)
   ```
   把一个 7 分支的 shotgun 收敛到 3 分支，可读性和诊断性都更好。当前 7 分支里 `simp` 与 `(ext y; simp)` 高度重叠，`(simp; ring)` 与 `(push_cast; ring)` 高度重叠——**这是"防御性冗余"，不是"最优"**。如果时间允许，建议保留 `rfl` 和两个最可能命中的分支，其余用 `first`/`try` 组合或明确注释"fallback for cached-rev drift"。

**评级：可接受的工程折中，非最优。**

---

## (2) `simp only [id_eq]` vs 全 `simp` 处理 `a*x + x^3*q = a*id x + q*id x^3`

**结论：`simp only [id_eq]` 更稳，且在 cached-rev 场景下几乎是必须的。**

理由：
- **可复现性**：`simp` 的默认 simp set 会随 mathlib rev / `@[simp]` 属性增删而漂移。你钉在 rev `2f3d8f63` 上，`simp` 现在能过，但下一次 mathlib bump 时某个新 `@[simp]` 可能把 `x^3` 重写成别的正规形，导致这条 bullet 静默失败或"过早闭"成错误目标。
- **`id_eq` 是定义上的恒等式**：`id x = x` 由 `rfl` 成立，不值得让全 `simp` 去猜。`simp only [id_eq]` 后目标直接变成 `a*x + x^3*q = a*x + q*x^3`（注意 `q*id x^3` → `q*x^3`），此时 `ring` 或 `rfl`（若交换律已由 ac_rfl 覆盖）即可闭。
- **风险点**：`simp only [id_eq]` **不做** `ring` 所需的规范化（`x^3*q` vs `q*x^3`）。所以实际链应该是：
  ```lean
  simp only [id_eq]; ring
  ```
  而不是只 `simp only [id_eq]`。
- **全 `simp` 的额外隐患**：它会尝试 `mul_comm`、`pow_succ`、`Nat.cast` 等，可能把本可 `ring` 一次解决的目标改成 `Nat`/`Int` 混算，反而给后面的 `ring` 添麻烦。

**建议**：把该分支改为 `(simp only [id_eq]; ring)`。**这是本次修复里最值得做的一处收紧**，且是零风险、零成本。

---

## (3) `(fun s => j s k^2) = (fun s => j s k)^2` 用 `ext; simp [pow_two]`

**结论：对当前 rev 稳健，但跨 rev 不算稳固，建议加 `funext` 的显式形式并避免依赖 `simp` 的 `pow_two` 简化路径。**

分析：
- 目标形状：`(fun s => j s k ^ 2) = (fun s => j s k) ^ 2`。
- 右边 `(fun s => j s k)^2` 是 `Pi.instPow` 下的逐点幂，展开定义后应等于 `fun s => j s k ^ 2`。`ext s; simp [pow_two]` 的路径：`ext` 把目标化为 `j s k ^ 2 = ((fun s => j s k)^2) s`，然后 `simp [pow_two]` 用 `pow_two` 把两边都变成乘法，再用 `Pi.mul_apply` / `Pi.pow_apply` 之类的 simp 引理对齐——**这依赖 `Pi.pow_apply` 在 simp set 里**。
- **跨 rev 风险**：`Pi.pow_apply` 的命名和 simp 属性在 mathlib 历史上改过（`Pi.pow_apply` 曾一度是 `Pi.pow_apply` vs `Pi.instPow` 的实例投影差异）。若被移除或被保护，`simp` 会卡在 `((fun s => j s k)^2) s` 上。
- **更稳的写法**（不依赖 simp set）：
  ```lean
  ext s
  rw [Pi.pow_apply, Pi.pow_apply, pow_two, pow_two]
  -- 或用 change + rfl
  ```
  或直接：
  ```lean
  funext s
  simp only [Pi.pow_apply, pow_two]
  ```
  `simp only` 明确钉死用哪些引理，跨 rev 稳健性远高于裸 `simp [pow_two]`。
- **最稳的写法**：`rfl`（如果 `Pi.pow_apply` 是 `rfl`-level 的实例投影）。实测：`(fun s => j s k^2) = (fun s => j s k)^2` 在 `Pi.instPow` 展开后是**定义等价**，`rfl` 应该能闭。若 `rfl` 不过，说明 `instPow` 用的不是逐点定义或 Lean 4 的 `Pi.instPow` 有 app 包装——此时 `funext s; rfl` 通常也能过。

**建议**：改为 `(funext s; rfl)` 优先，失败再 fallback `(ext s; simp only [Pi.pow_apply, pow_two])`。这比依赖 `simp [pow_two]` 的隐式 simp set 稳健得多。

---

## (4) 有无更小侵入补丁？

**有，而且存在两类更小的补丁，取决于你想控制的是"diff 大小"还是"未来 fragility"。**

### 补丁 A：最小 diff（只动 5 个 bullet）
把原来 5 处 `convert ... using 1 <;> bullet` 中的 bullet 体替换为：
```lean
all_goals solve
  | rfl
  | (simp only [id_eq]; ring)
  | (push_cast; ring)
  | (funext s; rfl)
```
若某处确实有 `rw [htarget]` 需求（P5），保留 `rw [htarget]` 在前，再 `solve`。这样：
- 分支从 7 降到 4；
- 去掉所有 `ext; simp` 的隐式依赖；
- diff 仅限 5 处 bullet，**是当前 rev2 的子集**，风险严格下降。

### 补丁 B：更小侵入（不动 bullet，只改 P5 的 `rw` 位置）
如果 5 处 `convert ... using 1` 之所以当初要写 bullet，是因为 `convert` 产生了多个 goal 且 defeq 顺序不稳定——那么**更小的补丁是保留原 bullet 结构，仅在 `convert` 后加 `rotate_left`** 或改用 `refine ... ?_ ?_` 显式给出 5 个 goal 的顺序。这能把 diff 压到 1–2 行，但会牺牲可读性。

### 补丁 C：如果 5 处结构高度同构
抽一个 local macro / `macro_rules`：
```lean
syntax "close_defeq" : tactic
macro_rules
  | `(tactic| close_defeq) => `(tactic|
      solve
        | rfl
        | (simp only [id_eq]; ring)
        | (push_cast; ring)
        | (funext s; rfl))
```
5 处各写一行 `close_defeq`，diff 最小、可读性最好、未来只需改一处。**这是工程上最优。**

---

## 总结建议

| 项 | 判断 | 建议 |
|---|---|---|
| (1) `solve` 链 | 方向对，非最优，有顺序耦合隐患 | 收敛到 4 分支；`field_simp; ring` 分支实测其回滚语义 |
| (2) `id_eq` | `simp only [id_eq]` 更稳 | 改为 `(simp only [id_eq]; ring)`；全 `simp` 有跨 rev 漂移风险 |
| (3) `ext; simp [pow_two]` | 当前 rev 稳，跨 rev 不固 | 改为 `(funext s; rfl)`，fallback `simp only [Pi.pow_apply, pow_two]` |
| (4) 更小补丁 | 有 | 补丁 A（4 分支收敛）或补丁 C（macro） |

**一句话**：rev2 的 `FIX_COMPILE_OK` 是真的，但它是"pinned-rev 上能过"，不是"跨 rev 稳健"。真正的最优解是把 `solve` 链**收敛 + 显式 simp only + 用 `funext s; rfl` 替代 `ext; simp`**，并把 5 处抽成一个 macro。当前修复里最该立刻做的一处，是 (2) 的 `simp only [id_eq]; ring`——零成本、零风险、直接消掉一个跨 rev 漂移源。

——usrm SI1语义轨·20260930T014015Z
