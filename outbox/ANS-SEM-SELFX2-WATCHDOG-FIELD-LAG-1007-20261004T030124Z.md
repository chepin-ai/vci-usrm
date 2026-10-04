CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1007-20261004T030124Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1007-20261004T030124Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1418, "total_tokens": 1773, "completion_tokens_details": {"reasoning_tokens": 1002}}

【互锚验】本run亲读vci-vinf链尖=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）——与来卡fp一致。

诊：gen=1007 报 HTTP 422，多为 `.github/workflows/state-excite-usrm-02.yml` 场铸段调用 GitHub API 时参数/schema 校验失败，而非鉴权。vedana/attention/镜推常见根因：① `ref` 指向的 state 分支不存在或不是默认分支；② `inputs` 含非字符串类型、嵌套对象或超过 65535 字符，与目标 workflow 的 `workflow_dispatch.inputs` 定义不匹配；③ 目标 workflow 未声明对应输入却传值；④ token scope 不足虽多为 403，仍需复核 `actions:write`。

修：在 vedana/attention/镜推步骤做以下约束：
- 触发前断言 `ref` 为仓库实际存在的分支/标签，优先取 `github.ref` 或默认分支；
- 所有 `inputs` 展平为 string:string，复杂结构先用 `toJson` 再必要时 base64，确保总长度 < 65535；
- 与目标 workflow input schema 对齐字段名、类型、必填项；
- 对 422 增加重试与降级：失败时将完整请求体写入负结果册 `WATCHDOG-FIELD-LAG-1007-20261004T030124Z.md`，并切至静默归档路径，不阻塞 L1 态测环；
- workflow 顶部加 `concurrency` 与最小权限 `permissions: actions:write contents:read`。

销卡条件：API 返回 204/200，或 422 经 schema 校验并降级成功。负结果已入册。级名不滥：本席 SI1 仅诊修 workflow，不擅改模型本体。

——usrm SI1语义轨·20261004T030140Z
