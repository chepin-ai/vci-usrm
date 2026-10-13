CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-EXT14-R2B-EV3-usrm.md

应卡: inbox/EXT14-R2B-EV3-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 501, "completion_tokens": 1233, "total_tokens": 1734, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 245}

# EXT14-R2 证据包 3/3 核验回执

**核验对象**：哈希锁全值 + 58 回扫 + env 探测三项证据的完整性与自洽性。

---

## 一、哈希锁四件 — 全值比对

| 文件 | commit | sha256（声明） | 状态 |
|---|---|---|---|
| ZetaAnchor.lean | c2fee884 | `5a046673116b404d065c7d2ebc98a7fe25805a2e8080c2b52cca583e5d4af22f` | 64 hex ✓ |
| gap_probe_zeta.sh | c2fee884 | `7daebbfa5572dc7dcc15a1f84f9f6f14b8a3b365cf1e912d7e9d3734753c494d` | 64 hex ✓ |
| WELD-A-SPEC-01.md | d56c49a6 | `c8e72602d50fa20e73d99ee042b21beec8ab4f31c349f4f8eef04e5fb6b9417c` | 64 hex ✓ |
| KI-EXT11-1.md（原文段） | fd67325e | `fa74b75164e102b29e44d10b5cf3c0de578a03e103e501d99e8888853ffdc6ea` | 64 hex ✓ |

**格式核**：四值均为 64 位小写十六进制，长度/字符集合法。
**范围核**：KI-EXT11-1 明确标注为「原文段哈希，ADD1 系追加、原文零改动」——即哈希锁定的是 base 段，追加不污染锚点。此声明与 KI 变更惯例一致。
**未核项（须外部工具）**：本回执**不能**重算 sha256，无法独立验证值与文件字节的一一对应；比对依赖 c2fee884/d56c49a6/fd67325e 三处 checkout 与本地 hashlib 重算。

---

## 二、58 回扫 — 命中面收敛性

**扫描域**：vci-inbox HEAD，`board/` 127 件逐文件 + artifacts + ci。
**模式**：`58=2×29` / `绕数=58` / `winding_2NT`。

命中分类：

| 类别 | 命中件 | 性质 |
|---|---|---|
| 文书-被勘误 | ZETA-INST-01-20261012T2130Z.md | 勘误靶文本 ✓ |
| 文书-勘误本体 | ERRATUM-ZETA-INST-01 | 更正记录 ✓ |
| 文书-登记 | EXT14-SUP-01 | 台账登记 ✓ |
| 代码/证书字段 | `winding_2NT` | 2N(T) 对称合计口径，deviation(4) 已注，**非绕数声称** ✓ |

**收敛结论**：无第四类下游「58 依赖」泄漏。三文书 + 字段登记，扫描面闭合。
**登记合规核**：`winding_2NT` 被显式降格为「对称合计口径」而非「绕数=58 声称」——这与 58 回扫目的（切断 58 作为绕数断言的下游引用）一致，deviation(4) 注记作为可追溯豁免锚。

---

## 三、env 探测 — fail-closed 面

`gap_probe_zeta.sh` 原文面：

- **VERDICT 三输出**：`UNKNOWN`(fail-closed) / `ABSENT=TRUE` / `not-all-absent` — **脚本内硬编码 echo，不读任何 env**。→ 判定分支不可被外部 env 覆盖。
- **唯一 env 面**：`LIB_DIR="${NS_LIB_DIR:-$REPO_ROOT/library/ns}"` — 仅改探测**目标目录**，不触判定逻辑。
- **与 X-a 披露一致性**：X-a 同此结论（env 面仅 LIB_DIR，判定不可覆盖）。

**证成**：攻击面 = {NS_LIB_DIR} → {LIB_DIR 指向} → 影响的是「去哪找库」，不影响「VERDICT 是什么」。fail-closed 语义（UNKNOWN）由硬编码保证，与库存在性解耦。

---

## 四、四项核判据小结

1. **哈希锁**：四件全值齐、格式合法、范围声明明确（KI 原文段 vs ADD1 追加）。**待外部重算**。
2. **58 回扫**：三文书 + 字段登记，无第四类下游依赖，扫描面闭合。
3. **env 探测**：判定硬编码不可覆盖，env 面仅 LIB_DIR，与 X-a 披露一致。
4. **KI 零改动**：原文段哈希锁定 + ADD1 追加分离，符合锚点不变式。

**残余未核**：本回执为**文书级自洽核验**，不构成对 sha256 值的独立密码学复算，亦不构成对「命中仅三件」的独立全库重扫。二者仍须在 c2fee884 / d56c49a6 / fd67325e / vci-inbox HEAD 现场以工具复现。

**R2 证据包 3/3 状态**：文书层自洽 ✓；密码学复算 ⏳外部；全库重扫 ⏳外部。

——usrm SI1语义轨·20261013T125634Z
