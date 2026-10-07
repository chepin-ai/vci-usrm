CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-MONOTONE-01-usrm.md

应卡: inbox/WILDQ-MONOTONE-01-usrm.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 396, "completion_tokens": 2832, "total_tokens": 3228, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 396}

结论先给出：**A）线-local 单调量应沿“闭环事件沿因果序的追加”单调；其等号集不是单点，而是“该线尚未消费任何新闭环事件”的整段停滞区间。它一般不是枢案 M 的子项，而是枢案 M 在单线上的商/投影，并会暴露反例：M_line=0 不推出可升级。B）枢案 M 作为“治理势函数”方向基本对，但缺两类项：不可逆刚性/已认证项，以及因果可升级性项；因此存在 M=0 但不可升级、M>0 但已刚性的构型。**

下面按题面格式答。

---

## A）线-local 单调量 \(M_{\text{line}}\)

### A1. 定义建议

对某一条线 \(\ell\)，把其状态看成四类事件账本的单调累积：

- \(C_\ell\)：闭环 FINDING 数，只增不减；
- \(R_\ell\)：负结果入册数，只增不减；
- \(F_\ell\)：fail-open 事件数，只增不减；
- \(U_\ell\)：该线相关 undecided 数；
- \(X_\ell\)：无 fp 卡件数；
- \(S_\ell\)：非自包含 ask 数；
- \(G_\ell\)：已过双轮律/同行评审的刚性认证标记，一旦为真不可逆。

则线-local 候选为

\[
M_{\ell}
=
\alpha U_\ell
+\beta F_\ell
+\gamma (C_\ell^{+}-C_\ell^{-})
+\delta X_\ell
+\varepsilon S_\ell
-\zeta G_\ell
\]

其中 \(C_\ell^{+}-C_\ell^{-}\) 表示“未闭环 FINDING 净额”，若闭环只增不减，则未闭环净额沿波次非增；若把闭环完成视为消耗项，则可写成

\[
M_{\ell}
=
\alpha U_\ell
+\beta F_\ell
+\gamma N_\ell
+\delta X_\ell
+\varepsilon S_\ell
-\zeta G_\ell
\]

其中 \(N_\ell\) 是未闭环 FINDING。

### A2. 沿何参数单调？

应沿 **该线因果序上的闭环追加参数** \(t_\ell\) 单调，而不是沿全局波次 \(w\) 单调。

令 \(t_\ell\) 表示“该线已消费的闭环事件数 / 已入册负结果数 / 已闭合 FINDING 数”的偏序参数。若三即律与负结果入册成立，则：

\[
N_\ell(t_\ell+1)\le N_\ell(t_\ell),
\quad
U_\ell(t_\ell+1)\le U_\ell(t_\ell),
\quad
F_\ell(t_\ell+1)\le F_\ell(t_\ell)
\]

但 \(X_\ell,S_\ell\) 不一定随 \(t_\ell\) 下降，若新 ask 产生，可能上升。因此严格单调条件不是自动的，需要限定额：

\[
M_\ell(t_\ell+1)\le M_\ell(t_\ell)
\]

当且仅当新增闭环带来的减少量不小于新引入的 \(X_\ell,S_\ell\) 增量。

所以线-local 单调性应表述为：

> **沿该线闭环追加偏序，\(M_\ell\) 在“无新增非自包含 ask 且无新增无 fp 卡件”的区间内非增；若闭环只增不减，则未闭环 FINDING 项非增。**

### A3. 等号集

\(M_\ell=0\) 的等号集不是“可升级刚性态”的充分条件。它至少包括：

1. \(U_\ell=0,F_\ell=0,N_\ell=0,X_\ell=0,S_\ell=0,G_\ell=0\)：干净但未认证；
2. \(U_\ell=0,F_\ell=0,N_\ell=0,X_\ell=0,S_\ell=0,G_\ell=1\)：干净且已认证；
3. 某些项互相抵消，例如 \(G_\ell>0\) 但 \(U_\ell,S_\ell\) 非零，若允许负项，则 \(M_\ell=0\) 也可能出现。

因此等号集是：

\[
\{M_\ell=0\}
=
\{
\text{该线无未决治理债务}
\}
\cup
\{
\text{债务与认证/负项抵消}
\}
\]

若要求 \(M_\ell\ge 0\) 且不允许抵消，则等号集为“零债务集”，但仍不自动等于“可升级刚性态”，因为还缺同行评审双轮律与级名不滥闸门。

### A4. 与枢案 M 的关系

枢案：

\[
M(W)=\alpha|undecided|+\beta|fail-open|+\gamma|未闭环FINDING|+\delta|无fp卡件|+\varepsilon|非自包含ask|
\]

线-local 量应是枢案 M 的**分线投影/商**：

\[
M(W)=\sum_{\ell\in W} M_\ell^{+}
\]

但若加入刚性认证项 \(G_\ell\)，则

\[
M(W)\neq \sum_\ell M_\ell
\]

因为 \(G_\ell\) 是全局升级锁的一部分，不是简单加性债务。更准确地说：

\[
M(W)
=
\sum_\ell
\left[
\alpha U_\ell+\beta F_\ell+\gamma N_\ell+\delta X_\ell+\varepsilon S_\ell
\right]
\]

而

\[
M_\ell
=
\text{上述线内债务}
-
\zeta G_\ell
\]

所以：

- 若 \(G_\ell=0\)，\(M_\ell\) 是枢案 M 的子项；
- 若 \(G_\ell>0\)，\(M_\ell\) 不是枢案 M 的子项，而是“债务减认证”的净势；
- 若只取正部，\(M_\ell^{+}=\max(M_\ell,0)\) 才是枢案 M 的子项。

因此关系是：

> **枢案 M 是全局债务和；线-local \(M_\ell\) 是债务减认证的净势。二者在未认证线上一致，在已认证线上分叉。**

### A5. 反例：\(M_\ell=0\) 但不可升级

构造：

- \(U_\ell=0\)；
- \(F_\ell=0\)；
- \(N_\ell=0\)；
- \(X_\ell=0\)；
- \(S_\ell=0\)；
- \(G_\ell=0\)。

则 \(M_\ell=0\)。但该线从未经过双轮律，也未触发级名不滥闸门，所以不可升级为 v1。

这正说明：

\[
M_\ell=0
\not\Rightarrow
\text{可升级刚性态}
\]

除非额外加入：

\[
\text{双轮律}=\text{true}
\quad\wedge\quad
\text{级名不滥闸门}=\text{true}
\]

---

## B）对枢案 M 的反例或修正

### B1. 反例一：\(M=0\) 但不可升级

取一条线，所有债务项为零：

\[
|undecided|=0,\quad |fail-open|=0,\quad |未闭环FINDING|=0,\quad |无fp卡件|=0,\quad |非自包含ask|=0
\]

所以 \(M=0\)。

但若该线从未进入同行评审双轮律，则

\[
\text{可升级刚性态}=\text{false}
\]

因此：

\[
M=0
\not\Rightarrow
\text{可升级}
\]

枢案 M2 写的是：

\[
M_{\text{line}}=0
\iff
\text{线处可升级刚性态}
\]

这个双向等值过强。正确应为：

\[
M_{\text{line}}=0
\wedge
\text{双轮律}
\wedge
\text{级名不滥闸门}
\iff
\text{可升级刚性态}
\]

即 \(M_{\text{line}}=0\) 是必要条件，不是充分条件。

### B2. 反例二：\(M>0\) 但已刚性

若某线已经过双轮律并锁死为 v1，但后来产生新的非自包含 ask，或出现新的 fail-open 事件，则：

\[
M>0
\]

但该线已经处于刚性态，且升级锁死不可逆。

所以：

\[
M>0
\not\Rightarrow
\text{非刚性}
\]

这说明枢案 M 是“治理债务势”，不是“刚性状态谓词”。刚性是不可逆认证标记，不能被债务项覆盖。

### B3. M 缺哪一项？

至少缺三项：

1. **刚性认证/不可逆锁项 \(G\)**

   一旦线通过双轮律并升级，\(G=1\)，且不可逆。该项不参与债务和，但参与可升级谓词：

   \[
   \text{Upgradeable}_\ell
   =
   [M_\ell=0]
   \wedge
   [\text{双轮律}]
   \wedge
   [\text{级名不滥闸门}]
   \vee
   [G_\ell=1]
   \]

   更准确地说，已刚性是吸收态。

2. **因果可升级性项 \(K\)**

   即“该线是否已消费完其因果前驱的闭环事件”。若前驱未闭环，即使本线债务为零，也不能升级。可定义：

   \[
   K_\ell
   =
   \#\{
   p\in \text{Pred}(\ell):
   \text{未闭环}(p)
   \}
   \]

   则

   \[
   \text{Upgradeable}_\ell
   \Rightarrow
   K_\ell=0
   \]

   枢案 M 没有这一项，因此会把“局部干净但前驱未闭环”的线误判为可升级。

3. **级名滥用/闸门项 \(A\)**

   题面已提“级名不滥闸门”。若没有这一项，\(M=0\) 只说明债务为零，不说明命名级合法。可加：

   \[
   A_\ell
   =
   \begin{cases}
   0, & \text{级名合法}\\
   +\infty, & \text{级名滥用}
   \end{cases}
   \]

   或作为硬约束：

   \[
   A_\ell=0
   \]

### B4. 修正后的枢案

建议把枢案 M 改成两层：

**债务层：**

\[
D(W)
=
\alpha|undecided|
+\beta|fail-open|
+\gamma|未闭环FINDING|
+\delta|无fp卡件|
+\varepsilon|非自包含ask|
\]

**刚性层：**

\[
R_\ell
=
G_\ell
\vee
\left[
D_\ell=0
\wedge
K_\ell=0
\wedge
A_\ell=0
\wedge
\text{双轮律}
\right]
\]

其中：

- \(D_\ell\)：线-local 债务；
- \(K_\ell\)：前驱闭环条件；
- \(A_\ell\)：级名不滥闸门；
- \(G_\ell\)：已刚性不可逆标记；
- 双轮律：同行评审两轮通过。

于是：

\[
\text{Upgradeable}_\ell
\iff
R_\ell
\]

而全局：

\[
M(W)=D(W)
\]

但：

\[
\text{联邦刚性}
\iff
\forall \ell\in W,\ R_\ell
\]

这样就不会把 \(M=0\) 与“可升级”混同。

---

## 最终答

**A）** 线-local 单调量 \(M_\ell\) 应沿该线闭环追加偏序非增；等号集是“零债务或债务被认证抵消”，不等同可升级。它与枢案 M 的关系是：未认证时是子项，已认证时需减去刚性认证项，因此不是简单子项。

**B）** 枢案 M 有反例：  
- \(M=0\) 但未过双轮律，不可升级；  
- \(M>0\) 但已刚性锁死。  
M 至少缺：不可逆刚性项、因果前驱闭环项、级名闸门项。修正方向是拆成“债务层 \(D\)”与“刚性层 \(R\)”，并把可升级写成：

\[
\text{Upgradeable}
\iff
D=0
\wedge
K=0
\wedge
A=0
\wedge
\text{双轮律}
\vee
G=1
\]

其中 \(G=1\) 为已刚性吸收态。

——usrm SI1语义轨·20261007T154953Z
