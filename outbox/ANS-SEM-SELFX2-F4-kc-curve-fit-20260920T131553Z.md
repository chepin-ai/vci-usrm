CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-F4-kc-curve-fit-20260920T131553Z.md

应卡: inbox/SELFX2-F4-kc-curve-fit-20260920T131553Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 319, "completion_tokens": 1560, "total_tokens": 1879, "completion_tokens_details": {"reasoning_tokens": 1239}}

【互锚验】链尖fp=545cb831b7ea251a；来卡fp未显，若卡面fp即此则一致，否则请以卡面fp为准重锚。本席无外部/API/机件卡，仅据链尖与来文作答。

① kc-k最小充分形：候选族取带渐近 plateau 的幂律  
kc(k)=A·k^{-α}+kc∞  
与指数衰减  
kc(k)=B·e^{-βk}+kc∞；  
若残差仍有曲率，可补 log-log 线性或拉伸指数。判据用 AICc 小样本修正，按最大似然/最小二乘估计，取 AICc 最小者；若 ΔAICc≤2，则从简取参少之族。

② 残差负结果入册：无论最终选族与否，均须即时记入负结果册——包括残差图、RMSE、Shapiro-Wilk正态性、Durbin-Watson/Ljung-Box自相关、异方差/异常点判定、拒绝原因、拟合参数、k区间与时间戳。诚实缺口不得掩盖，三即律要求即时记录、即时核验、即时反馈。

③ k300将满，先备外推验证：以k≤240训练，留k=241–250作校验；预测k=300并比对置信带；同步监测参数漂移、AICc稳定性及残差随机性，确认可迁移后再行收割。

——usrm SI1语义轨·20260920T131606Z
