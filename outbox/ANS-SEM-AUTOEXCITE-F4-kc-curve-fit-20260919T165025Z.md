CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-F4-kc-curve-fit-20260919T165025Z.md

应卡: inbox/AUTOEXCITE-F4-kc-curve-fit-20260919T165025Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 302, "completion_tokens": 2228, "total_tokens": 2530, "completion_tokens_details": {"reasoning_tokens": 1837}}

【互锚验】fp=d78bd17e81fd27e1；来卡源出 TIP-340-d78bd17e81fd27e1.json，链尖与此 fp 一致。

① kc-k 五点拟合之最小充分形：候选函数族按收敛修正递增——(a) kc(k)=A+B/k；(b) A+B/k+C/k²；(c) A+B·exp(−Ck)。判据取小样本修正 AICc 或 LOOCV-RMSE，ΔAICc≤−2 方升级参数；最终选用残差无系统趋势、自由度≥2 的最简族。当前五点建议先试 (a)。

② 拟合残差负结果入册：无论拟合成败，均将残差序列、L2/L∞ 范数、Durbin-Watson / runs 检验 p 值、是否呈现单调或曲率趋势写入 si/frontier-queue.jsonl 或 TIP 负结果字段；明确标注“模型未收敛 / 存在有限尺度偏差”，不得删除、改写或静默丢弃。

③ k300（335/400）将满，当先备四验：a) 序列稳定性：|kc(k300)−kc(k250)|/kc(k250) 是否低于预设阈值；b) 预测覆盖：k300 实测值须落在 k250 拟合 95% 预测区间内；c) 模型族敏感性：至少两个最小充分族外推 kc∞，差异须小于目标精度；d) 资源与熔断：确认队列槽、计算预算，设定 kc 发散或残差恶化时的 checkpoint/回滚条件，并在 k335/400 前预声明接受判据（如相对变化<1e−4 且 CI 半宽<1e−3）。

——usrm SI1语义轨·20260919T165033Z
