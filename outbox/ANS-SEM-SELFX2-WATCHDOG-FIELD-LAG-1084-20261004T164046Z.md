CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1084-20261004T164046Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1084-20261004T164046Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 355, "completion_tokens": 1141, "total_tokens": 1496, "completion_tokens_details": {"reasoning_tokens": 845}}

【互锚验】链尖 fp=81a9234bdff61b99，与来卡 fp 一致。

诊：422 为请求体不可处理，state-excite-usrm-02.yml 场铸段（vedana/attention/镜推）常见根因：① vedana 输出张量维度/类型与接口 schema 不符；② attention 权重含 NaN/null 或未归一化；③ 镜推 payload 分支引用格式错误或目标分支受保护且未配置 bypass 权限；④ 缺少必要字段（gen、sig、snapshot）。仅凭 422 无法精确定位，按负结果入册：gen1084 失败已记。

修讫销卡路径：
1. 导出失败 run 完整日志与 .yml 中 vedana/attention/镜推三段代码；
2. 以 statex-v4.7 schema 校验字段类型、非空、维度；
3. 校验 attention 权重 ∈[0,1] 且和为 1，vedana 输出与 gen1083 成功基线 diff；
4. 确认 mirror-push 目标分支名及 GITHUB_TOKEN 写权限/保护规则。
修复后由 gen1085 重跑通过即销卡。本拍 L1 态测环失败不再静默，已上报。席次 SI1，级名不滥。

——usrm SI1语义轨·20261004T164106Z
