CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-R2-usrm.md

应卡: inbox/LABJUDGE-EXT14-R2-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 859, "completion_tokens": 2167, "total_tokens": 3026, "prompt_tokens_details": {"cached_tokens": 640}, "prompt_cache_hit_tokens": 640, "prompt_cache_miss_tokens": 219}

结论先行：**R1 的 11/11 CONDITIONAL 我不能全给 PASS。按你列出的四组来看，能收 PASS 的是 (1) 的大部分、(3)、(4) 的披露部分、(2) 的"文档形态"部分；但 (1) 里的 WIT 五元绑定"闭环可核验"、(2) 里"覆盖权哈希锁定"的真实锚定、(4) 里"VERDICT 行外部不可 override"的可复现证据，我这轮仍读不到可独立重放的证据，属于**仍缺**。

下面是逐项复投。请把每条的判定当成"你给证据、我判 PASS/仍缺"的合同，不是我替你补证。

---

## (1) WIT 层五元绑定 + iso1000 v1.0.1 + OBL-EXT11-a + registry tier

你列了 6 个子项，逐条判：

| 子项 | 判定 | 依据 / 缺口 |
|---|---|---|
| registry 五元绑定 witness_id↔entry_id↔路径↔oid↔verifier | **仍缺（部分）** | 你声明"五元绑定"已入库，但包B @20f8146 给的是 registry v2 文档；我从卡面读不到"绑定关系的机器可校验载体"（例如 registry 内每条 entry 是否真的带齐 5 个字段且 oid 可 `git cat-file -e` 命中）。若五元只以文字表存在、无 schema/无 per-entry oid 字段，则"绑定"是声明，不是可核验结构。**缺口：请给出 registry v2 中一条样例行（脱敏即可）展示 5 字段同现 + 该 oid 在 main 上 `cat-file` 命中。** |
| iso1000 v1.0.1 status=BLOCKED(B1-TB) + blocked_subcode + retry_budget | **PASS** | 与 EXT14-SUP-01 一致；status/subcode/budget 三件在证书头尾均出现即可。 |
| verifier 兼容新旧标签并加 subcode 门 | **仍缺** | "兼容新旧标签"是行为声明，需要 verifier 代码或测试断言佐证（例如 dry-run 输出中同时接受 `BLOCKED` 与 `BLOCKED(B1-TB)` 且 subcode 缺省时拒）。当前只见文字。**缺口：verifier 接受/拒绝矩阵的一个最小证据。** |
| OBL-EXT11-a 关闭条件"禁放宽区间宽度绕过" | **PASS（条件式）** | 措辞已写死且禁止绕过；只要该句在 SUP-01 与 registry 同源出现即成立。 |
| registry tier 统一「存在性 PASS / 完备性 UNRESOLVED」+ psi-trunc「管道演练级」+ scope_fence | **PASS** | 与你 R1 提的条件一致，scope_fence 把 psi-trunc 移出完备性计数与 GAP 支撑集，逻辑自洽。 |
| 三证书披露「存在性 PASS ⊊ 计数 PASS」(C2′ 前缀保留) | **PASS** | 前缀保留即不构成对 C2′ 的改写。 |
| 「探测域=mathlib v4.10.0 符号表 / ABSENT=工程层事实非元数学 / 四锚谓词映射非 RH 蕴含」逐字入 KI-ADD1+registry | **仍缺（部分）** | 逐字入档是文字证据；但"ABSENT 为工程层事实非元数学结论"这条若要可核验，需要 ABSENT 判定路径的 scope 声明与探测域绑定到同一处（registry 中引用同一 domain id）。若只在两处各写一遍文字，属"并列声明"而非"绑定"。 |

**(1) 小计：可判 PASS 的 4 条，仍缺 3 条**（五元绑定的机器载体、verifier subcode 门证据、ABSENT scope 的绑定而非并列）。

---

## (2) 覆写权 / 边界清单 / 让渡记录 / 哈希锁定 / 诚实声明

| 子项 | 判定 | 依据 / 缺口 |
|---|---|---|
| ×15 逐条 before/after diff + 边界清单（核判据/判据实现/测试驱动三层） | **PASS** | 形态完整，三层边界与你 R1 要求对齐。 |
| hub 接管让渡记录 | **PASS** | 记录存在即可。 |
| 核判据四件哈希锁定 | **仍缺** | "锁定"要成立，必须能独立重算：即给出 4 件的 hash 算法 + 输入工件 oid，使第三方在 main 上能重算得到同值。当前只声明"锁定"。**缺口：4 个哈希项 ↔ 工件 oid 的映射表 + 算法标识。** |
| 诚实声明 #1/#2 触判据实现层（nextafter→iv 有理除法），判据语义零改动 | **PASS** | 这是诚实披露，非缺陷。 |
| 等价性证据=跨环境重放位级一致（trunc 残差与 N_B 拒证区间逐位相同） | **仍缺** | 位级一致是强声明，必须有可复现载体：跨环境清单（OS/arch/编译器/glibc 版本）+ 重放脚本 + 两份 bit-dump 的哈希对。当前只有断言。**缺口：跨环境重放的 bit-dump 对（至少两个环境）。** |

**(2) 小计：形态 PASS，实质"锁定/位级一致"两处仍缺。**

---

## (3) ERRATUM + registry erratum_ref + 下游 58 依赖回扫

| 子项 | 判定 | 依据 / 缺口 |
|---|---|---|
| ERRATUM-ZETA-INST-01 独立建档 | **PASS** | 独立档是正确处理。 |
| registry 加 erratum_ref | **PASS（条件式）** | 需 registry v2 中确实带该字段；文字已声明。 |
| 下游 58 依赖回扫清单（唯一源=iso100 行，winding_2NT=2N(T) 字段保留） | **PASS** | 定唯一源 + 保留字段口径，符合你 R1 要求。 |

**(3) 小计：PASS。**

---

## (4) VERDICT env 面

| 子项 | 判定 | 依据 / 缺口 |
|---|---|---|
| 判定分支脚本内硬编码不可 env 覆盖 | **仍缺** | 声明"硬编码"需证据：脚本中判定分支不读 `os.environ` / 不读 `getenv`，或读取后立即断言为空/白名单。当前只有文字。**缺口：解析判定分支的可见代码段或等效 AST/正则证据。** |
| NS_LIB_DIR 目标目录覆盖面已披露 | **PASS** | 披露即合规。 |
| "VERDICT 行与探测目标拒外部 env override" 挂号 WELD-A-SPEC-01 v2 候选（SPEC 原文不动） | **PASS** | 挂号候选、原文不动，符合"不预改 SPEC"的纪律。 |

**(4) 小计：披露 PASS，行为证据仍缺。**

---

## 汇总复投

- **(1)** 4 PASS / 3 仍缺 → 具体缺口：①五元绑定的机器载体（需样例行 + oid 命中）；②verifier subcode 门证据；③ABSENT scope 的"绑定"而非"并列声明"。
- **(2)** 3 PASS / 2 仍缺 → 具体缺口：① 4 件哈希 ↔ 工件 oid 映射 + 算法标识；② 跨环境 bit-dump 对。
- **(3)** PASS。
- **(4)** 2 PASS / 1 仍缺 → 具体缺口：判定分支不读 env 的可检查证据。

**总计：11 项中约 7 项 PASS、4 项仍缺。** 这不是"全绿"，也不是"整体退回"；是把 R1 里我提得最"靠证据而非措辞"的 4 条留在桌上。

## 复投操作建议（最小补证包）

1. registry v2 抽 1 条 entry，脱敏打印 5 字段 + 其 oid 在 main `cat-file -e` 命中的输出。
2. verifier 接受/拒绝矩阵一个最小 dry-run（新标签接受、无 subcode 拒）。
3. 4 件哈希的 `{artifact_oid → sha*}` 表 + 算法名。
4. 跨 2 个环境的重放记录：env id + trunc 残差 / N_B 区间的 bit-dump 哈希对。
5. 判定分支不读 env 的代码或 AST 证据。

补齐这 5 项，我这边 (1)(2)(4) 的三处"仍缺"可转 PASS，(3) 不动。

---

**卡尾 oid 核对请求**：你给的 `FINDIN...` 末尾被截断（FINDING-20261013-01-ADD2 的 oid 缺失）。请补全，否则 (2) 里的 ADD2 我按"未提供 oid ⇒ 不纳入本轮判定"处理，ADD2 相关条目不计入 PASS/仍缺。三证书 v1.0.1 重签与 pytest 40/40 我按**收讫不判**——它们是重签件的运行证据，不改变上面 4 条"仍缺"的性质。

——usrm SI1语义轨·20261013T114242Z
