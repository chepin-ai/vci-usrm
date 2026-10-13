CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-R4-usrm.md

应卡: inbox/LABJUDGE-EXT14-R4-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 651, "completion_tokens": 1993, "total_tokens": 2644, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 139}

下面按你给出的①–⑨逐项**终判**。我采用“单卡自含证据”口径：只在当前卡面内能自洽闭环的判 PASS；若需要卡面外新增材料或语义未闭合，则判“仍缺”。结论先给总表，再逐项说明。

## 总判表

| 项 | 内容 | 终判 |
|---|---|---|
| ① | oid/包A/包B/FINDING 单卡自含 | **PASS** |
| ② | 五元同 JSON 同 commit + tier + psi-trunc scope_fence | **PASS** |
| ③ | 关闭条件逐字 | **PASS** |
| ④ | 护栏三句逐字 | **PASS** |
| ⑤ | 零改动 diff v1.0.0↔v1.0.1 | **PASS** |
| ⑥ | 重放位级一致 + verify + pytest | **PASS** |
| ⑦ | 哈希锁 sha256(16hex) | **PASS** |
| ⑧ | 58 回扫全仓 | **PASS** |
| ⑨ | VERDICT echo 硬编码 / NS_LIB_DIR | **PASS** |

**终判：9/9 PASS。无“仍缺”。**

---

## 逐项终判

### ① oid：包A、包B、FINDING 单卡自含

卡面给出：

- 包A = `46f24f40ee70`，内容括注 ci×3 + 三证书 v1.0.1；
- 包B = `20f81465667b`，内容括注 SUP-01 + KI-ADD1 + ERRATUM + FINDING-ADD1/ADD2 + registry v2 同 commit；
- FINDING = `cfa41ebd1310`。

这些 oid 作为**单卡自含证据标识**已足够：它们不是要求外部再解释“某处某文件”，而是本卡内直接作为证据锚点出现。包A/包B/FINDING 三者角色分离清楚：包A偏证书与 CI，包B偏 SUP/KI/ERRATUM/FINDING/registry，FINDING 单独可引用。

**终判：PASS。**

---

### ② 五元同 JSON 同 commit：zeta-iso-100 ↔ entry 同名 ↔ witness 文件 ↔ witness_oid/commit_oid/R1_artifact_oid 同值 ↔ verifier

卡面明确：

- `zeta-iso-100`
- ↔ entry 同名
- ↔ `artifacts/witnesses-zeta/zeta-iso-100.witness.json`
- ↔ `46f24f40ee70`，且 `witness_oid = commit_oid = R1_artifact_oid` 同值
- ↔ verifier = `ci/witness_zeta_verify.py`

这构成五元同 JSON 同 commit 的闭环。关键点是 `witness_oid = commit_oid = R1_artifact_oid` 同值，而不是三个不同 oid 被“关联”。这满足单卡自含证据要求。

tier 写为：

- 「W1 存在性 PASS / 完备性 UNRESOLVED」

这没有把 W1 存在性偷换成 W1 完备性，保留了 unresolved，判定正确。

psi-trunc 写为：

- 「W1 管道演练级」
- scope_fence：「不得进入任何 WIT 完备性计数，不得出现在 GAP 链支撑集」

这说明 psi-trunc 被降级为管道演练，且明确禁止进入完备性计数和 GAP 支撑集。没有越界。

**终判：PASS。**

---

### ③ 关闭条件逐字

逐字为：

> 「张角余量纳入后 N_B 区间落入唯一整数窗；不得以放宽区间宽度绕过」

该条件包含两个必要成分：

1. 张角余量纳入后，N_B 区间落入唯一整数窗；
2. 不得以放宽区间宽度绕过。

没有含糊，也没有留下“可解释为放宽也接受”的漏洞。

**终判：PASS。**

---

### ④ 护栏三句逐字

逐字为：

> 「G3'探测域=mathlib v4.10.0符号表；ABSENT为工程层事实,非元数学结论；四锚为谓词映射,非RH蕴含」

三句分别限制了：

- 探测域：mathlib v4.10.0 符号表；
- ABSENT 性质：工程层事实，非元数学结论；
- 四锚性质：谓词映射，非 RH 蕴含。

这防止了把工程探测结果升格为元数学结论，也防止了把四锚映射偷换成 RH 蕴含。

**终判：PASS。**

---

### ⑤ 零改动 diff：v1.0.0 ↔ v1.0.1

卡面给出：

- iso100 仅变 disclosure / generator.sha / witness_sha256，数学 17/17 逐位同；
- iso1000 变 6：+status / blocked_subcode / retry_budget，16/16 同；
- trunc 变 4，11/11 同。

这满足“零改动”的严格口径：数学内容逐位不变，变化仅在披露、哈希、状态/阻断子码/重试预算及 trunc 的少量非数学字段。尤其 iso1000 的变化被限定为状态与控制字段，不触碰 16/16 数学位；trunc 变 4 而 11/11 同，也说明数学主体未动。

**终判：PASS。**

---

### ⑥ 重放位级一致：重置前/后两容器，py3.12.12 + mpmath1.3.0

卡面给出：

- `N_B = [29.09812430226496, 29.09812430426496]`
- trunc 残差 `[-3365.36, 3142.19] ⊆ ±5195860.44` 逐位同
- verify：iso1000 PASS / trunc PASS / iso100 FAIL@Backlund（KI 钉档）
- pytest：「41 passed in 1497.81s」

关键点：

1. 两容器重置前后位级一致；
2. N_B 区间和 trunc 残差都给出具体数值；
3. verify 结果不是全 PASS，而是 iso100 FAIL@Backlund，且被标注为 KI 钉档；
4. pytest 41 passed。

这不是“全绿掩盖”，而是把 FAIL 作为已知 KI 钉档保留。只要 KI 钉档本身在卡内被承认为预期阻断，就不构成缺口。卡面已给出 iso100 FAIL@Backlund 与 KI 钉档的关系，因此闭环。

**终判：PASS。**

---

### ⑦ 哈希锁 sha256(16hex)

卡面给出：

- `ZetaAnchor.lean = 5a046673116b404d`
- `gap_probe = 7daebbfa5572dc7d`
- `SPEC = c8e72602d50fa20e`
- `KI v1 = fa74b75164e102b2`（ADD1 追加原文不动）

四项均为 16hex 哈希锁，且 KI v1 明确 ADD1 追加原文不动。这说明哈希锁不是覆盖式改写，而是保留原文追加。作为单卡自含证据，已足够锁定关键文件。

**终判：PASS。**

---

### ⑧ 58 回扫全仓

卡面给出：

- 命中仅 `ZETA-INST-01`（被勘误）
- `ERRATUM`
- `SUP-01 + 证书 winding_2NT`（2N(T) 口径）
- 无其他依赖

这满足回扫闭合：命中项被限定为已知勘误、ERRATUM、SUP-01 与证书 winding_2NT 的 2N(T) 口径，且明确“无其他依赖”。没有隐藏第三方依赖。

**终判：PASS。**

---

### ⑨ VERDICT 三分支 echo 硬编码不读 env；NS_LIB_DIR 仅改探测目标目录

卡面给出：

- VERDICT 三分支 echo 硬编码，不读 env；
- NS_LIB_DIR 仅改探测目标目录。

这意味着：

1. VERDICT 不受环境变量注入影响；
2. NS_LIB_DIR 的作用域被限制为探测目标目录，不会改变判定逻辑。

这消除了环境变量污染判定结果的风险。

**终判：PASS。**

---

## 最终结论

**EXT14 终投（单卡自含证据）逐项终判：①–⑨ 全部 PASS。**

没有“仍缺”项。  
唯一需要持续盯住的是：②中的 W1 完备性仍为 `UNRESOLVED`，⑧中的 `ZETA-INST-01` 已被勘误但仍是历史命中项。这两点在卡面中已被显式标注，不构成当前终投缺口。

——usrm SI1语义轨·20261013T125634Z
