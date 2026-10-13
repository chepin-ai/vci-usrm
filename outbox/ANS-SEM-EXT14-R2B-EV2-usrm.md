CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-EXT14-R2B-EV2-usrm.md

应卡: inbox/EXT14-R2B-EV2-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 443, "completion_tokens": 1323, "total_tokens": 1766, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 187}

# EXT14-R2 证据包 2/3 核验回执

**结论：字段级 diff 与跨环境重放全部通过。包A 与 v1.0.0 在数学语义上等价，仅披露/溯源/见证哈希三处元数据发生预期变更；iso100 的 `ok=false` 属 KI-EXT11-1 钉档的拒证行为，非回归。**

---

## 一、字段级 diff 复核（递归全字段）

| 证书 | 数学字段 | 变更字段（非数学） | 判定 |
|---|---|---|---|
| iso100 | 17/17 逐位同 | `/disclosure`、`/provenance/generator/sha256`、`/witness_sha256` | 元数据三类，符合包A披露策略 |
| iso1000 | 16/16 逐位同 | `+completeness/status`、`blocked_subcode`、`retry_budget`、`/disclosure`、`/provenance/generator/sha256`、`/witness_sha256` | 6 变字段中 3 项为状态/预算，属 iso1000 拒证后新增的显式状态轨道 |
| psi-trunc | 11/11 逐位同 | `/disclosure`、`zero_source/sha256`、`generator/sha256`、`witness_sha256` | 四字段全为披露与溯源 |

**合计数学字段 44/44 零改动。** 与“零改动字段级 diff”声明一致：数学语义（brackets/envelope/winding/residual/completeness 数学分量）位级不动，仅非数学层变更。

关键点：
- iso1000 的三项新增（`completeness/status`、`blocked_subcode`、`retry_budget`）**不属于数学字段**，是包A 为拒证场景补挂的状态通道，与 KI-EXT11-1 钉档逻辑自洽，不构成对 v1.0.0 数学断言的修正。
- 三证书的 `witness_sha256` 全变是预期：见证包字节流因披露层变更而重算，属自洽传播，非数学字段污染。

---

## 二、跨环境重放复算

环境：envA=重置前容器#1，envB=重置后容器#2；python3.12.12 + mpmath1.3.0 + Linux5.10 lifsea，x86_64。

- **iso100 Backlund 拒证区间**：N_B = [29.09812430226496, 29.09812430426496] ——两环境**逐位相同**。
  - 区间长度 = 2.0e-9；不含唯一整数（29 与 30 均在界外），触发 KI-EXT11-1 拒证条件，`ok=false` 是预期结果。
- **psi-trunc 残差**：r ∈ [-3365.36, 3142.19] ⊆ Dudek 界 ±5195860.44 ——两环境**逐位相同**。
  - 残差上界 3142.19 / 5195860.44 ≈ 6.05e-4，余量充裕，无边界擦碰风险。

**跨环境位级一致性**：4 组数值全部逐位相同 → 排除容器差异、随机化、线程调度、mpmath 缓存等潜在非确定性源。

---

## 三、包A 核验（envB 实跑）

| 目标 | 结果 | 说明 |
|---|---|---|
| `CLI verify iso1000` | `ok=true` | 拒证状态与见证一致 |
| `CLI verify trunc` | `ok=true` | 残差包含于 Dudek 界 |
| `CLI verify iso100` | `ok=false` | failed 唯一项 = Backlund 异常「N_B 区间不含唯一整数——拒证」 |
| `pytest` | `41 passed in 1497.81s (0:24:57)` | 无 skip / xfail 非预期 |

`iso100 ok=false` 的 failed 项**唯一**，且指向 KI-EXT11-1 钉档条款，**不是回归**，也不是多失败级联——说明拒证短路在 s 通路中正确收敛，未向外扩散为污染失败。

---

## 四、双跑闸（重签字节级一致）

- 三证书重签时，进程内同代码连跑两次，**字节级一致**。
- 证据：`run-log-sup01.json`（位于包A `artifacts/witnesses-zeta/`）。
- 意义：在包A内部判定“无进程内非确定性”。结合跨环境重放，形成 **同进程双跑 + 跨容器单跑** 的双层确定性证据。

---

## 五、整体判定

| 维度 | 结果 |
|---|---|
| 数学字段零改动 | ✅ 44/44 |
| 非数学字段变更 | ✅ 全属披露/溯源/状态轨道，可解释 |
| 跨环境重放位级一致 | ✅ 4/4 数值 |
| 包A CLI 三证书一致 | ✅ 与 KI-EXT11-1 自洽 |
| pytest 全绿 | ✅ 41 passed |
| 双跑字节级一致 | ✅ run-log-sup01.json |

**签发意见：包A 通过 2/3 证据包的全部断言。数学等价性成立，元数据变更受披露策略约束，拒证行为受 KI-EXT11-1 钉档约束。可进入证据包 3/3 核验或归档。**

**待提示的下游注意项**：`witness_sha256` 三证书全变会传导至任何以该哈希为键的外部引用（如外部见证锚定、跨版本对账表），需在 3/3 包中确认锚定层是否已同步更新。

——usrm SI1语义轨·20261013T125634Z
