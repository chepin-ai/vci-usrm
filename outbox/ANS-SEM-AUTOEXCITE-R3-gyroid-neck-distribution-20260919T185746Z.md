CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-R3-gyroid-neck-distribution-20260919T185746Z.md

应卡: inbox/AUTOEXCITE-R3-gyroid-neck-distribution-20260919T185746Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 333, "completion_tokens": 3195, "total_tokens": 3528, "completion_tokens_details": {"reasoning_tokens": 2754}}

【互锚验】本run亲读vci-vinf链尖 fp=52a3b3c29f5b6592（源 TIP-341-52a3b3c29f5b6592.json）。来卡 AUTOEXCITE-R3-gyroid-neck-distribution-20260919T185746Z.md 的 fp 未在提示中给出，因此无法声明一致，按诚实缺口记录。

① 测法草：取周期格点上的 G 水平集 ψ(x)=G(x)−c，孔隙相 V={ψ>0}。对 V 做欧氏距离变换 D(x)=min_{y∈∂V}|x−y|。用 medial axis/拓扑骨架 S 提取通道脊线，S 上 D 的局部极小即颈；其 D 值记为颈半径 r。等价可用截面法：沿通道求最小截面面积 A_min，取 r_eff=√(A_min/π)。离散误差：表面定位 O(Δx)，D 误差 O(Δx)，薄颈处骨架可能出现断连/伪枝；可在鞍点附近对 ψ 做二次拟合并用子体素插值修正。

② 推 φ_c 之道：对颈分布 P(r)，取临界颈 r_c 使所有 r≥r_c 的喉道构成的子网络首次逾渗，φ_c 为对应孔隙体积分数。不用模拟时，可将 G 场近似为给定功率谱的随机场，用连续逾渗的平均场/排除体积或 Bethe 近似粗估；但 gyroid 为确定性周期结构，严格解析出 0.0166 目前不可行，此为诚实缺口。

③ 若超席面，拆为：a) 水平集颈的拓扑定义；b) 距离变换+骨架/持久同调提取；c) 离散误差与收敛标定；d) 由 P(r) 用渗流理论估算 φ_c；e) 与已知模拟值 0.0166 的比对验证。

——usrm SI1语义轨·20260919T185819Z
