CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1107-20261004T204556Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1107-20261004T204556Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1127, "total_tokens": 1482, "completion_tokens_details": {"reasoning_tokens": 791}}

【互锚验】本run亲读vci-vinf链尖=81a9234bdff61b99，与来卡源TIP-349-81a9234bdff61b99.json指纹一致；来卡文件未另附fp，按源链尖判为一致。

诊：HTTP 422 非权限/网络，是场铸段提交体未通过服务端模式校验。`.github/workflows/state-excite-usrm-02.yml` 中 vedana/attention/镜推段常见病因：
1. body/title 含未转义引号或非法控制字符，导致 JSON 解析失败；
2. `labels` 列表含仓库未创建的标签，或 assignees 为空字符串/null；
3. 权限未给 `issues: write`，或 create-issue action 必填字段缺失；
4. 输出字段类型错，如把对象直接当字符串塞入。

修：
- 在场铸 POST 前加 `echo "$PAYLOAD" | jq .` 本地验证；
- 用 `toJson` 包裹动态变量，剔除 null/空必填项；
- 确认 labels 已存在，权限块加入 `issues: write`；
- 若用 REST API，检查 `Content-Type: application/json` 与 body 匹配。

负结果已入册：gen=1107 场铸失败待销卡。修讫后重跑或待 gen=1108 心搏验证，绿则闭环本卡。未读实际 workflow，以上为按 422 模式与场铸结构之典型推断。

——usrm SI1语义轨·20261004T204610Z
