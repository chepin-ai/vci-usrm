CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-883-20261003T045352Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-883-20261003T045352Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 351, "completion_tokens": 968, "total_tokens": 1319, "completion_tokens_details": {"reasoning_tokens": 551}}

【互锚验】本run vci-vinf链尖fp=81a9234bdff61b99，源文件TIP-349-81a9234bdff61b99.json；来卡未另标fp，依源判为一致。

诊：HTTP 422 非认证/网络问题，乃请求体语义不合端点schema。state-excite-usrm-02.yml 中场铸段（vedana/attention/镜推）若调用 GitHub REST/GraphQL 或 workflow_dispatch，常见因：

1. 必填字段缺失/类型错：如 `title`、`body` 为空，`labels` 含未创建标签，`assignees` 不存在，`ref` 指向无分支。
2. 字段冗余：某些端点不接受 `milestone` null 或 `draft` 与 issue 类型冲突。
3. 镜推 payload 中 `head_sha` 长度/格式错，或目标分支不存在。
4. 权限：GITHUB_TOKEN 缺 `contents:write`、`issues:write` 或 actions 写权限，但 422 通常先于鉴权后的细粒度校验。
5. 变量解析失败：secrets/vars 含特殊字符未 JSON 转义，导致 body 非法。

修：
- 在该步骤加 `set -x` 或 `echo "$JSON_PAYLOAD" | jq .` 输出完整 body。
- 对照失败端点 schema 逐项校验；删除 null/冗余字段。
- 确保 `labels` 已在仓库创建；`ref` 存在且 token 有写权限。
- 若用 `gh api`，加 `--input -` 并先 `jq -c .` 校验。

负结果入册：当前无实际 workflow 片段与完整 payload，无法定位到具体字段。请粘贴 `.github/workflows/state-excite-usrm-02.yml` 中场铸段及 422 响应 body，修讫后销卡。

——usrm SI1语义轨·20261003T045401Z
