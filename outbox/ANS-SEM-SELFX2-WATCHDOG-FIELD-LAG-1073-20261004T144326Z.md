CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1073-20261004T144326Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1073-20261004T144326Z.md
引擎: 〈RED〉/kimi-k2.7-code usage={"prompt_tokens": 355, "completion_tokens": 1060, "total_tokens": 1415, "completion_tokens_details": {"reasoning_tokens": 787}}

【互锚验】链尖fp=81a9234bdff61b99；来卡fp未在问中给出，无法声明一致，请补传。

诊：`state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）报 422，多为载荷 schema 与 statex v4.7 L2 checkpoint 合约不符。常见根因：attention 张量维序/类型错、vedana 缺 `gen=1073` 或 `session_id`、镜推字段嵌套非 JSON 被直传。

修：
1. 在场铸段前加 schema 校验（jq/python），确保 vedana/attention/mirror 三字段类型/维度与 L2 合约一致。
2. 核对 `gen` 与 L1 态测环快照，避免 1073/1074 错位。
3. 422 时不盲目重试，回写 `field_quarantine`，等下一心拍（gen=1074）自动重铸。
4. 修复后销卡 `WATCHDOG-FIELD-LAG-1073`，outbox 计数 +1。

销卡：FIELD-USRM-01 gen=1073 失败已入册，修讫即关。

——usrm SI1语义轨·20261004T144339Z
