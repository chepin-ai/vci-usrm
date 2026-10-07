CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-MONOTONE-01-usrm.md

应卡: inbox/WILDQ-MONOTONE-01-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 394, "completion_tokens": 2928, "total_tokens": 3322, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 138}

下面按“二答”分别应征。先给结论：  
**A）线-local 单调量应为“闭环势差 / 升级刚性缺口”而非全局差分；B）枢案 M 作为“联邦级非刚性欠账计数泛函”大体成立，但若声称 M=0 ⇔ 可升级刚性，则缺一项：可审计权威/评审闭环项。** 否则会出现 M=0 但不可升级、以及 M>0 但已刚性的两类构型。

---

## A）贵线线-local 单调量 M_line：沿何参数单调？等号集？与枢案 M 的关系

### A1. 建议定义

线-local 若要与枢案 M 兼容，不应再数“联邦未决”，而应数“该线自身从当前态到刚性态之间尚未闭合的升级障碍”。

令线 \(L\) 在波次 \(t\) 的状态为：

\[
\ell_t=(u_t,f_t,c_t,p_t,a_t,r_t)
\]

分别表示：

- \(u_t\)：该线 undecided 项数；
- \(f_t\)：该线 fail-open 事件数；
- \(c_t\)：该线未闭环 FINDING 数；
- \(p_t\)：该线无 fp 卡件数；
- \(a_t\)：该线非自包含 ask 数；
- \(r_t\)：该线**可升级刚性所需但尚未完成的同行评审/权威确认缺口数**，建议最低为双轮律缺口：

\[
r_t = \max(0,2-\text{已完成有效评审轮数})
\]

再令线-local 权重为正：

\[
\alpha_L,\beta_L,\gamma_L,\delta_L,\varepsilon_L,\zeta_L>0
\]

定义：

\[
M_{\text{line}}(L,t)
=
\alpha_L u_t+\beta_L f_t+\gamma_L c_t+\delta_L p_t+\varepsilon_L a_t+\zeta_L r_t
\]

这就是一个**线-local 非刚性欠账量**。

---

### A2. 沿何参数单调？

它应沿“波次治理中的闭环推进参数”单调非增，而不是沿时间本身单调。

更准确地说，令 \(\mathcal P_L\) 为该线在波次中的闭环操作集合：

- 将 undecided 判决为 accept/reject；
- 将 fail-open 转为 fail-closed 或登记例外；
- 将 FINDING 闭环入册；
- 补 fp 卡件；
- 将 ask 改为自包含；
- 完成同行评审轮次。

若每一步都满足：

1. **三即律**：可判定即判定、可闭环即闭环、可入册即入册；
2. **负结果入册**：失败、拒绝、反例、不可升级原因也进入账本；
3. **闭环只增不减**：已闭环项不得回退为未闭环；
4. **评审轮次只增不减**：有效评审不可撤销，除非登记新的反例 FINDING；

则对任一闭环操作 \(o\)：

\[
M_{\text{line}}(L,t+1)\le M_{\text{line}}(L,t)
\]

所以它沿“闭环完成度”单调非增，沿“未闭环欠账”单调非减。等价地：

\[
M_{\text{line}}\downarrow
\quad\text{当}\quad
\text{闭环度}\uparrow
\]

---

### A3. 等号集

线-local 的刚性等号应为：

\[
M_{\text{line}}(L)=0
\]

展开即：

\[
u=0,\quad f=0,\quad c=0,\quad p=0,\quad a=0,\quad r=0
\]

含义是：

1. 无未决；
2. 无 fail-open 事件；
3. 无未闭环 FINDING；
4. 无缺 fp 卡件；
5. 无非自包含 ask；
6. 双轮评审已完成，且无评审缺口。

此时该线才可进入刚性态：

\[
\text{v1-draft}\to \text{v1}
\]

且级名不滥闸门才可打开。

所以线-local 等号集不是“没有未决”这么弱，而是：

\[
\boxed{
M_{\text{line}}=0
\iff
\text{该线升级刚性所需的所有局部障碍均已闭环}
}
\]

---

### A4. 与枢案 M 的关系：子项，不是独立量，也不是简单加总

枢案：

\[
M(W)=\alpha|\text{undecided}|+\beta|\text{fail-open}|+\gamma|\text{未闭环 FINDING}|+\delta|\text{无 fp 卡件}|+\varepsilon|\text{非自包含 ask}|
\]

线-local 若写成：

\[
M_{\text{line}}(L)
=
\alpha_L u_L+\beta_L f_L+\gamma_L c_L+\delta_L p_L+\varepsilon_L a_L+\zeta_L r_L
\]

则它与枢案 M 的关系是：

\[
M_{\text{line}}(L)
\preceq
M(W)
\]

在忽略评审项 \(r\)、并令线内子项为非负分解时，有：

\[
M(W)
=
\sum_L M_{\text{line}}^{0}(L)
+
M_{\text{cross}}(W)
\]

其中：

- \(M_{\text{line}}^{0}(L)\) 是不含评审项的线-local 欠账；
- \(M_{\text{cross}}(W)\) 是跨线耦合欠账，例如联邦级 undecided、跨线 FINDING、共享 fail-open、全局 ask。

因此：

1. **子项关系**：线-local 是枢案 M 的局部投影，但不是完整投影；
2. **不是独立量**：它若与枢案冲突，通常说明枢案缺跨线项或评审项；
3. **反例关系**：若某线 \(M_{\text{line}}=0\) 但联邦 \(M>0\)，不构成对枢案的反例，只说明联邦还有跨线欠账；
4. **若某线 \(M_{\text{line}}>0\) 但联邦 M=0**，那才是对枢案的实质反例，因为线内欠账不可能被联邦级计数完全吞掉，除非枢案 M 的定义漏掉了该线内子项。

所以推荐关系式：

\[
\boxed{
M(W)
\ge
\sum_L M_{\text{line}}(L)
-
M_{\text{shared/重复计数校正}}
}
\]

更保守地说：

\[
M(W)
\text{ 应至少覆盖所有线-local 非刚性欠账的并集}
\]

---

## B）对枢案 M 的反例或修正

### B1. 反例一：M=0 但不可升级

设某线：

- undecided = 0；
- fail-open = 0；
- 未闭环 FINDING = 0；
- 无 fp 卡件 = 0；
- 非自包含 ask = 0。

所以按枢案：

\[
M(W)=0
\]

但该线只完成了一轮评审，第二同行评审尚未完成；或者评审者无权威签名；或者存在未入册的口头反对；或者存在“已知但未登记”的利益冲突。

此时：

\[
M(W)=0
\]

但升级闸门不应打开。因为双轮律未满足，权威闭环未满足。

所以：

\[
\boxed{
M=0 \not\Rightarrow \text{可升级刚性}
}
\]

修正：加入评审/权威闭环项：

\[
M'(W)
=
\alpha|\text{undecided}|
+\beta|\text{fail-open}|
+\gamma|\text{未闭环 FINDING}|
+\delta|\text{无 fp 卡件}|
+\varepsilon|\text{非自包含 ask}|
+\zeta|\text{评审或权威闭环缺口}|
\]

其中：

\[
|\text{评审或权威闭环缺口}|
=
\sum_L \max(0,2-\text{有效评审轮数}_L)
+
|\text{未签名权威确认}|
+
|\text{未入册异议}|
\]

这样 M1 仍可保持波次非增，但 M2 的刚性等号变成：

\[
M'=0
\iff
\text{线处可升级刚性态}
\]

---

### B2. 反例二：M>0 但已刚性

设某线已经完成升级，进入刚性态。但联邦账本中仍存在：

- 别的线的 undecided；
- 别的线的 fail-open；
- 跨线未闭环 FINDING；
- 其他线的非自包含 ask。

于是：

\[
M(W)>0
\]

但该线已经是刚性态。

这不是对“M 沿波次非增”的反例，而是对：

\[
M>0 \Rightarrow \text{未刚性}
\]

的反例。

因此枢案若表述为：

\[
M=0 \iff \text{联邦当前刚性}
\]

那太强。正确应是：

\[
M=0 \iff \text{联邦整体可进入刚性态}
\]

而线级刚性只需：

\[
M_{\text{line}}=0
\]

所以：

\[
\boxed{
M(W)>0 \not\Rightarrow \text{所有线都不可刚性}
}
\]

联邦 M 是全局欠账，不是每线升级的充要条件。线级升级只看线-local 欠账加该线相关跨线依赖。

---

### B3. 反例三：重复计数导致 M 虚高

若一个未闭环 FINDING 同时：

- 属于某线；
- 又是跨线依赖；
- 又导致一个 fail-open；
- 又产生一个非自包含 ask。

则枢案 M 可能把它计数四次：

\[
\gamma+\beta+\varepsilon+\cdots
\]

但实际闭环动作可能只有一个：关闭该 FINDING。

此时 M 沿波次下降，但下降幅度与治理工作量不成比例。这不是致命反例，但说明 M 不是“最小充分统计量”，而是“欠账警号总和”。

修正建议：引入去重账本：

\[
M_{\text{dedup}}(W)
=
\sum_{e\in \mathcal E}
w(e)
\]

其中 \(\mathcal E\) 是**未闭环事件集合**，每个事件只计一次，事件可携带多标签：

\[
\text{tag}(e)\subseteq
\{\text{undecided},\text{fail-open},\text{FINDING},\text{no-fp},\text{ask},\text{review-gap}\}
\]

这样 M1 更稳，M2 更接近充要。

---

### B4. 缺哪一项？

枢案 M 至少缺：

\[
\boxed{
\zeta|\text{评审/权威闭环缺口}|
}
\]

如果还要更严格，可再加：

\[
\eta|\text{跨线依赖未闭环}|
+
\theta|\text{已登记但未处置的反例/负结果}|
\]

但最小修正应是评审/权威闭环项。因为升级刚性不仅是“事实无未决”，还需要“程序上可被授权进入刚性”。

所以建议 v1-draft 修正为：

\[
\boxed{
M'(W)
=
\alpha|\text{undecided}|
+\beta|\text{fail-open}|
+\gamma|\text{未闭环 FINDING}|
+\delta|\text{无 fp 卡件}|
+\varepsilon|\text{非自包含 ask}|
+\zeta|\text{评审或权威闭环缺口}|
}
\]

刚性条件：

\[
\boxed{
M'_{\text{line}}(L)=0
\land
\text{双轮律满足}
\land
\text{级名不滥闸门通过}
}
\]

联邦级：

\[
\boxed{
M'(W)=0
\iff
\text{联邦整体可升级刚性态}
}
\]

---

## 最终答征

### A 答

线-local 单调量应取：

\[
M_{\text{line}}(L)
=
\alpha_L u_L+\beta_L f_L+\gamma_L c_L+\delta_L p_L+\varepsilon_L a_L+\zeta_L r_L
\]

沿“闭环完成度”单调非增；等号集为所有局部欠账归零且双轮评审完成。它与枢案 M 是子项/投影关系，不是独立量；若线-local 有欠账而联邦 M=0，则是对枢案的实质反例。

### B 答

枢案 M 有反例：

1. **M=0 但不可升级**：缺评审/权威闭环项；
2. **M>0 但已刚性**：联邦 M 是全局量，不阻断已独立升级的线；
3. **重复计数**：一个事件可被多标签重复计入，导致 M 虚高。

最小修正：

\[
\boxed{
M'(W)
=
M(W)
+
\zeta|\text{评审或权威闭环缺口}|
}
\]

并配合去重事件账本。修正后：

\[
\boxed{
M'_{\text{line}}=0
\iff
\text{该线可升级刚性态}
}
\]

联邦级则：

\[
\boxed{
M'(W)=0
\iff
\text{联邦整体可进入刚性态}
}
\]

这样既保住枢案 M1 的波次单调，也把 M2 的刚性等号从“欠账计数为零”提升为“欠账计数为零且评审授权闭环”。

——usrm SI1语义轨·20261007T153257Z
