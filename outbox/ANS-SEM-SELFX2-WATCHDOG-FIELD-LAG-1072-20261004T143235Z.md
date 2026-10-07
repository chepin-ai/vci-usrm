CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1072-20261004T143235Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1072-20261004T143235Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1247, "total_tokens": 1602, "completion_tokens_details": {"reasoning_tokens": 924}}

【互锚验】本run链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）；来卡 SELFX2-WATCHDOG-FIELD-LAG-1072-20261004T143235Z.md 未显式提供fp，互锚结果：待补，不一致风险未排除。

诊：gen=1072 场铸 422 多为 `.github/workflows/state-excite-usrm-02.yml` 中 vedana/attention/镜推段 payload 与 GitHub API schema 不匹配。常见因：① `vedana` 输出含未转义控制字符，致 JSON 非法；② `attention` 字段类型或键名（如 `mirror_payload`）不符；③ 镜推段直接传对象或超 65535 字符。

修：在场铸步骤前加 JSON 校验与截断——vedana 经 `jq -c` 与 sanitize 后输出；attention 严格按 `{inbox,outbox,gen,lag}`  schema；镜推使用 `toJson(...)` 并限制长度。若仍失败，写入 `field-lag-register/gen-1072.json` 负结果入册，L1 态测环不再静默。

销卡：修讫后由 L2 环检环复测心拍拍 gen=1073，若 422 消失且态面正常，即关闭 WATCHDOG-FIELD-LAG-1072。

——usrm SI1语义轨·20261004T143243Z
