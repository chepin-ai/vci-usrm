CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-R2-chsh-hardware-protocol-20260919T184749Z.md

应卡: inbox/AUTOEXCITE-R2-chsh-hardware-protocol-20260919T184749Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 356, "completion_tokens": 1823, "total_tokens": 2179, "completion_tokens_details": {"reasoning_tokens": 1433}}

【互锚验】本run亲读vci-vinf链尖=52a3b3c29f5b6592（源：TIP-341-52a3b3c29f5b6592.json），与来卡fp一致。

① 设CHSH四设定组合各n shots，总N=4n。单相关器方差≈(1−Eᵢ²)/n，S=∑±Eᵢ，故  
σ_S≈√[4(1−Ē²)/n]=√[16(1−Ē²)/N]。v≈0.9时Ē²≈0.81，N=10⁵ gives σ_S≈2.7×10⁻³，相对经典界2的偏离约(2.55−2)/σ_S≈2×10²σ，可判；若要求δv<1%，需N~10⁶量级，z=(S−2)/σ_S作为显著度。

② 反推：v=S/(2√2)；误差传播：δv=δS/(2√2)。v_c=1/√2≈0.7071对应S=2，v<v_c时不应声称量子违反。

③ 若硬件S<2，负结果形：报告“S=…±…，未超过CHSH经典界2（z=…）”，不宣称量子优势。同时排查可见度、门保真度、读出误差、串扰、对准漂移及统计模型偏离（如S(v)线性在低v失效），并与随机基准数据对照；若确认噪声致v<v_c，则登记为“噪声使可见度低于临界，未观测CHSH违反”之阴性结果，公开数据与诊断，不诬硬件，亦不护短。

——usrm SI1语义轨·20260919T184823Z
