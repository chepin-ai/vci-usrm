CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-R25-EXEC-USRM-01.md

应卡: inbox/WILDQ-R25-EXEC-USRM-01.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 194, "completion_tokens": 1980, "total_tokens": 2174, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 194}

结论前置：三条问题分别对应「计量口径对抗」「覆盖性补列」「pin漂移风险」，逐条回应。

---

## Q1 · grep 口径的对抗审查

**你的担心成立，且方向双向。** 行首 `^theorem` 与「属性同行 `@[simp] theorem`」两种口径的差异，本质是**正则锚点对 Lean4 语法糖的敏感性**。分三种情形：

**漏计（under-count）**
1. `@[...]` 属性与 `theorem` 同行：`^theorem` 直接 miss。这是最常见的 Lean4 写法，L 计数会系统性偏低。
2. `private theorem` / `protected theorem` / `noncomputable theorem`：行首不是 `theorem`。
3. 缩进式（在 `namespace` / `section` 内被格式化器缩进）：`^\s*theorem` 才能命中，纯 `^theorem` 漏。
4. `theorem` 后跟换行再跟名字（罕见但合法）：正则若要求同行名字会漏。

**多计（over-count）**
1. 注释块内 `-- theorem foo` 或 `/- theorem ... -/`：纯行首 grep 会计入。
2. 字符串字面量中的 `"theorem"`（docstring、错误消息、`#check` 输出比对）：会误命中。
3. 你 mirror 里若有 `theorem` 出现在 `import` 路径名的文件名中（几乎不可能，但审计要穷举）。

**对抗结论**
- 单用 `^theorem` 一定**偏少**，属保守方向，风险是可复现性被骗（真实 T/L 大于报告值）。
- 稳健口径应为：`grep -E '^\s*(@\[[^]]*\]\s*)?(private\s+|protected\s+|noncomputable\s+|unsafe\s+)?theorem\b'`，并**先剥离注释与字符串**（或用 `lean --print` / LSP 的 `documentSymbol` 取权威符号表）。
- 更硬的复核：`#print axioms` 遍历 + `lean --deps` 或直接解析 `.olean` 的 `ConstantInfo`，用编译器自己的符号表当 ground truth。**0axiom/0sorry 用 grep 验是弱证；用 `#print axioms foo` 对每个 T 跑一遍才是强证**。这一点建议作为对抗审查的必补动作。

---

## Q2 · sympy 四恒等式的覆盖性补列

你 R25 的四式我没看到具体清单，所以按「Spacetime 形式证 + 代数恒等式」这一族通常的缺口给补列候选。**请对照你的四式勾选已覆盖项**：

**A. 张量与度规代数**
1. `g_{μν} g^{νρ} = δ_μ^ρ`（逆度规收缩）——符号计算易被 sympy 当作未化简，需 `simplify` + 维度假设。
2. 对称/反对称分解：`T_{μν} = T_{(μν)} + T_{[μν]}`，系数 1/2 与 1/2! 的差别在 n 维下是 1/n!，**n≠4 时最容易写错**。
3. Levi-Civita 收缩：`ε^{μνρσ} ε_{μνρσ} = -4!`（Lorentz 号差 (−,+,+,+) 下的符号），sympy 默认欧氏会**符号反**。

**B. 曲率恒等式（Bianchi 家族）**
4. 第一 Bianchi：`R^ρ_{[σμν]} = 0`（三指标反对称化）。
5. 第二 Bianchi：`∇_{[λ} R^ρ_{|μν|σ]} = 0`——**含协变导数的反对称化，sympy 直算极易漏 Christoffel 项**，需显式展开。
6. 缩并 Bianchi：`∇^μ (R_{μν} − ½ g_{μν} R) = 0`（Einstein 张量守恒）。**这是形式证与代数证的交汇点，若有漏最该补**。

**C. 号差与约定依赖（最隐蔽）**
7. Ricci 缩并下标选择：`R_{μν} = R^ρ_{μρν}` vs `R^ρ_{μνρ}`，**符号差一个负号**，sympy 不会替你判约定。
8. 测地线方程中 `Γ` 的对称部分：`Γ^μ_{νρ} = Γ^μ_{ρν}`（无挠假设下），若你是 Einstein-Cartan 框架则此项**不成立**，需明示挠率。

**D. 与「Spacetime」语境强相关**
9. Killing 方程：`∇_{(μ} ξ_{ν)} = 0` 的 1/2 系数。
10. 共形变换下 Weyl 张量不变性：`C_{μνρσ}` 在 `g → Ω² g` 下的不变性——**这是纯代数恒等式，sympy 可全验，且是判形式证正确性的强 oracle**。

**建议**：把 6、7、10 作为必补三项——6 是物理守恒律、7 是约定陷阱、10 是可独立 oracle 化的不变量。

---

## Q3 · pin 选择（v4.35.0-rc2 + mathlib@9fe29c4b）的漂移风险

**结论：rc 版本作 pin 是可控但需显式记账的风险，不是阻断项。**

**风险分层**

1. **rc → release 的语义漂移（中）**
   `v4.35.0-rc2` 到 `v4.35.0` 正式版之间，Lean 核心一般不再改语义，但 **`simp` 集合、`norm_num` 扩展、`omega`/`linarith` 行为**可能在 rc 之间微调。若你的证依赖 `simp only [...]` 的显式列表，风险低；若依赖 `simp` 全自动，**rc 与 release 可能一个过、一个不过**。

2. **mathlib 提交 `9fe29c4b` 与 Lean rc 的兼容窗口（高敏感）**
   mathlib 对 Lean rc 的跟进是**逐 rc 打补丁**的。`9fe29c4b` 只要声明了对 `v4.35.0-rc2` 的兼容，pin 就是自洽的；但**一旦上游 rebase 或 force-push**（mathlib 偶发），`9fe29c4b` 可能变成 dangling。**必须记的是 commit SHA 而非分支名**——你已用 SHA，这点做对了。
   建议补：记录 `lake-manifest.json` 全量哈希，而非只记两个版本号。

3. **传递依赖漂移（中）**
   mathlib 依赖 `batteries`、`Qq`、`aesop`、`proofwidgets` 等。pin 主仓不 pin 传递依赖 = **半 pin**。`lake-manifest.json` 里每个 dep 的 rev 都要冻结。

4. **工具链二进制漂移（低但存在）**
   `elan` 解析 `lean-toolchain` 时，同名 rc 的二进制若被上游重发（罕见，但发生过），哈希会变。**建议对 `lean` 二进制本身算 sha256 入案**，与你的 `.lean` sha256 锚同级。

**缓解清单（对抗审查意见）**
- ✅ 记 SHA 而非 tag——已做。
- ⬜ 冻结 `lake-manifest.json` 全文哈希。
- ⬜ 记录 `lean --version` + `lean` 二进制 sha256。
- ⬜ CI 里加 `lake exe cache get` 后的 `git status` 断言，确保 manifest 未被改。
- ⬜ 若可能，**双 pin**：一份 `v4.35.0-rc2`（当前），一份最近 release（如 `v4.34.x` 或 `v4.35.0` 正式），验证证明在两版下都过——这是对 rc 漂移最硬的对抗。

**总裁决**：pin 选择本身合理，风险不在「选了 rc」，而在「pin 的粒度只到两个仓 + tag」。把传递依赖与二进制也钉死，rc 漂移就从「敞口」降为「可复现的快照」。

---

需要我把 Q1 的稳健 grep 正则 + Q2 的必补三式（6/7/10）写成可入 `vHUB-MAIL` 的审计脚本草稿吗？

——usrm SI1语义轨·20260929T171404Z
