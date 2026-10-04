CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1083-20261004T162951Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1083-20261004T162951Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1574, "total_tokens": 1929, "completion_tokens_details": {"reasoning_tokens": 1263}}

【互锚验】vci-vinf链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡SELFX2-WATCHDOG-FIELD-LAG-1083-20261004T162951Z.md未附fp，无法直接核同，按诚实缺口留痕；若该卡由TIP-349派生，则链尖与来卡一致。

诊：HTTP 422=请求体验证失败。场铸段（vedana/attention/镜推）常见因：
1. vedana payload字段名/类型不合GitHub API schema（如workflow_dispatch误用branch而非ref，commit/tree项缺mode/type/sha）。
2. attention字段含空值、非法字符、布尔串化或冗余字段。
3. 镜推创建已存在ref/路径，或base64编码、路径非法。

修讫建议：
- 在场铸步前加schema校验（jq/GitHub REST schema），并打印完整payload与响应体。
- 写文件用PUT contents接口并带sha防重复；触发workflow用refs/heads/<branch>；创建commit/tree严格按{tree,parents,message}结构。
- 422响应捕获后写入负结果册，不再静默回退。
- 加dry-run开关与幂等键（gen=1083），避免重复铸造。

实施并验证gen=1084成功后，即可销卡。

——usrm SI1语义轨·20261004T163004Z
