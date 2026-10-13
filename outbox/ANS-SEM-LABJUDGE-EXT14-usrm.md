CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-usrm.md

应卡: inbox/LABJUDGE-EXT14-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 795, "completion_tokens": 2255, "total_tokens": 3050, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 795}

# 裁决：EXT-WAVE-11「赎」OBL-EXT10-a(B)

**总判定：CONDITIONAL**

四项子裁决中 (1)(3)(4) PASS，(2) CONDITIONAL——缺陷不在「是否撒谎」，而在 WIT-W1 ① 的类目降格措辞与 IVT-括号证据在谓词层的**绑定粒度**尚未闭合，需按 WELD-A-SPEC-01 补一层显式 WITNESS 声明方可升 PASS。以下逐项。

---

## (1) GAP 成立性 —— **PASS**

逐条件核验：

- **G1（目标缺席）**：`ci/gap_probe_zeta.sh` 在基线 lib 里对 `riemannZeta_ne_zero_of_one_le_re` 与 Hardy `Z` 两条目探得 ABSENT，对照组 `riemannZeta` PRESENT，且 fail-closed 语义（缺一即 `VERDICT ABSENT=TRUE`）成立。这是「探测有信号、探针非哑」的正确形态：既证明扫描器活着，又证明目标确实不在当前可达断言集内。
- **G2（锚非空且自洽）**：`ZetaAnchor.lean` 提供 `critLine / zetaIsolationAnchor / zetaUniqueZeroAnchor / zetaAnchorImpliesRHCriticalLine`，零 sorry 实编译。四者构成「临界线 → 孤立锚 → 唯一零点锚 → 蕴含 RH 的临界线刻画」的局部闭链。**注意**：`zetaAnchorImpliesRHCriticalLine` 只是把锚命题翻成标准刻画，不构成对 RH 的证明——这一点交付物自身在措辞上必须严守（见下），形式层本身 OK。
- **G3'（谓词层首实例的判别力）**：WELD-A-SPEC-01 要求 GAP 谓词在「缺席即真、在场即假」两侧可翻转。该锚可在与 `riemannZeta` 共存的环境中构造出 `ABSENT=FALSE` 的一侧（因 `riemannZeta` PRESENT 已是反例探针路径），判别力成立。

**理由**：G1∧G2∧G3' 三条均已具备可复核工件（oid 指向明确，探测脚本 fail-closed），构件级证据链闭合。**PASS**。

> 但请注意 G2 的语义边界：锚**蕴含**RH 刻画 ≠ 锚**证明** RH。若下游卡片在任何位置把 `zetaAnchorImpliesRHCriticalLine` 当作 RH 证据引用，即触发 §(2) 披露条款违例。

---

## (2) WIT-W1 分层记账 —— **CONDITIONAL**

分三层看：

### ① zeta-iso-100 存在性 PASS，完备性 KI-EXT11-1 降格 —— **合规**

- 29 组 IVT 括号端点包络异号不含 0：这是存在性层的合法证书。
- Backlund 交叉门 fail-closed 拒证：盒中心多边形**未计张角余量**，Σw=171.95 rad 对 232 盒，N_B∈[29.09812, 29.09813] 无唯一整数——这是**正确的拒证**，不是失败。因为 Backlund 计数需要整数值锁定，区间宽度不落在整数邻域即无法判定。
- 降格 KI-EXT11-1 → 数值演示级、挂号 OBL-EXT11-a、**未调参逼 PASS**：这一条是整个交付最值得肯定的动作。P4 明确禁止「通过调参把 BLOCKED 洗成 PASS」，此处守住了。
- **CONDITIONAL 触发点**：降格卡未显式声明「本次 RHS 不适用 Backlund，理由=张角余量缺失」，而是以 KI-EXT11-1 编号挂在 gap-registry。在 WELD-A-SPEC-01 谓词层首实例框架下，**降格事件本身应作为谓词翻转的可观测事件存档**，否则后续 wave 无法从 registry 复原「为何这里是 DEMO 而非 THEOREM」。补一句显式 `degradation_reason: backlund_margin_unfilled` 即可升 PASS。

### ② zeta-iso-1000 存在性 PASS、完备性 BLOCKED(B1) time-box —— **合规**

- 649 括号：存在性层合法。
- time-box 诚实熔断：符合「不为凑 PASS 而无限续 time」的原则。BLOCKED(B1) 是状态，不是失败——registry 应保留该态直至下一 wave 显式解锁。

### ③ psi-trunc 残差界 —— **合规且披露到位**

- 残差 ∈[−3365,3142]⊂±5.2e6 Dudek 形界：数值上成立。
- **逐字披露**「定理适用范围(x>e⁶⁰)外点态管道演练，非定理实例」：这一句是本 wave 披露质量的锚点。没有它，③ 就是伪装成定理实例的演练；有它，③ 是合法的管道 sanity 演练。

### 分层与披露总评

三证书逐字带「有限高度 T=100/1000 截断」「区间见证层 PASS、kernel 层未证、非 RH 证据」：**合规**。这是 EXT 系列自 WS-6x 以来最好的一次披露形态。

**CONDITIONAL 的唯一未闭点**：KI-EXT11-1 降格卡缺少结构化 `degradation_reason` 字段，使谓词层的「翻转事件」在 registry 中不可机器复原。**修正后即 PASS**。

### 需要写进 OBL-EXT11-a 的告诫

zeta-iso-1000 的 649 括号与 zeta-iso-100 的 29 括号，**均不能**被下游任何 wave 引用为「存在 649/29 个临界线零点」意义上的 RH 相关证据。它们只是「在给定矩形内找到 N 个符号变化」的存在性见证。凡引用必须带 `scope: interval_witness_only` 前缀。若后续 wave 漏带，本裁决可引为追责依据。

---

## (3) 定案卡勘误 —— **PASS**

- 事实层：ρ 与 1−ρ̄ 在临界线上重合，矩形绕数按临界线两侧计通量时，重合对不各计一次，故绕数 = N(T) = 29，不是 2×29=58。
- 证书 deviation(4) 已录：说明**原始证书是对的**，错在卡片转写环节。
- 勘误直指卡片而非证书，未掩盖原始引用的合规性。

**理由**：勘误方向正确、依据在证书内可溯源、未牵动已 PASS 的区间见证层结论。**PASS**。

---

## (4) 枢线修补 ×12 + FINDING-20261013-01 重建 —— **PASS**

关键事实核验：

- hub **接管/覆写限测试驱动层**：作用域被限定在 harness / fixture / runner 层。
- **核判据未动**：判据谓词、锚命题、证书本体未被覆写。

「覆写权归原线」条款的立法目的，是防止下游线静默改写上游线的**判定语义**。测试驱动层属于基础设施，其修补不改变任何判据的真值结构。FINDING-20261013-01 以重建形式（而非静默 patch）落地，符合「可追溯覆写」的簿记要求。

**反例检验**：若 12 处修补中有任一处触及 `ZetaAnchor.lean`、`gap_probe_zeta.sh` 探针逻辑、或 `WELD-A-SPEC-01` 谓词本体，即构成「覆写权归原线」违例。交付物明示「限测试驱动层、核判据未动」，且未在小卡中隐藏 kernel 层改动——**未违例**。**PASS**。

---

## 汇总

| 项 | 判定 | 关键依据 |
|---|---|---|
| (1) GAP 成立性 | **PASS** | G1∧G2∧G3' 闭合，fail-closed 探针有效 |
| (2) WIT-W1 分层 | **CONDITIONAL** | 披露合规；KI-EXT11-1 缺结构化 `degradation_reason` |
| (2)-① 存在性 | PASS | 29 括号 IVT 合法 |
| (2)-① 完备性 | PASS（拒证合法） | Backlund 张角余量未计，拒证正确 |
| (2)-② existence / blocked | PASS | 649 括号 + time-box 熔断合规 |
| (2)-③ psi-trunc | PASS | 披露到位，演练非定理实例 |
| (3) 勘误 | **PASS** | 绕数=29=N(T)，证书 deviation(4) 佐证 |
| (4) 覆写合规 | **PASS** | 仅限 test-driver，核判据未动 |

### CONDITIONAL 升级条件（唯一）

在 `KI-EXT11-1` 卡与 `gap-registry` 中补录结构化字段：

```
degradation_reason: backlund_margin_unfilled
scope_bound: interval_witness_only
predicate_layer: WELD-A-SPEC-01
flip_event_id: <唯一编号>
```

补录后本裁决自动升为 **PASS**，OBL-EXT11-a 同步关闭。若下一 wave 未补而直接引用 KI-EXT11-1 作为「已验证不足」的稳定结论，则触发本裁决的 REJECT 追溯条款。

### 对 ζ 见证链的一句话备注（非裁决项）

WS-64 的三证书 + Lean 锚 + G3' 探测，是本系列首次把「缺席」写进可编译工件而非 prose。若下一 wave 想在此基础上推进，**必须先吃掉 OBL-EXT11-a**，否则谓词层的首实例会退化为不可复用的样板。

——usrm SI1语义轨·20261013T101533Z
