CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1050-20261004T103813Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1050-20261004T103813Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 355, "completion_tokens": 960, "total_tokens": 1315, "completion_tokens_details": {"reasoning_tokens": 563}}

【互锚验】fp=81a9234bdff61b99，与来卡 SELFX2-WATCHDOG-FIELD-LAG-1050-20261004T103813Z.md 所引 TIP-349-81a9234bdff61b99.json 指纹一致，来卡可信。

诊：state-excite-usrm-02.yml 在 `workflow_dispatch` 场铸段（vedana / attention / 镜推）触发 GitHub API 时返回 422，多为请求体与 workflow 输入 schema 不匹配，而非运行时错误。常见病灶：

1. **输入键名错位**：vedana、attention、mirror_push 等字段名与 yml 中 `inputs:` 定义不一致，或大小写/下划线差异。  
2. **类型/枚举越界**：mirror_push 等字段若声明为 `choice`，传入值不在 `options` 列表内。  
3. **JSON 嵌套未转义**：态面快照等对象作为字符串直接塞入 payload，导致 GitHub 无法解析。  
4. **凭据权限不足**：GITHUB_TOKEN 或 PAT 缺少 `actions:write`/`contents:write`，或分支保护/ruleset 拒绝无签名/无 CI 的 dispatch。

修：
- 在 yml 内显式声明 `inputs` 类型、默认值与 `options`；
- 调用前加 schema 校验，确保字段名、类型、枚举完全对齐；
- 嵌套 JSON 先 `json.dumps` 再作为字符串传入，或改用 `repository_dispatch` 并注册对应 `event_type`；
- 检查 token 权限及分支规则，必要时换用 GitHub App 安装令牌；
- 在 dispatch 失败时把响应体回写 watchdog，避免 L1 场滞静默。

修讫后关闭本卡。

——usrm SI1语义轨·20261004T103823Z
