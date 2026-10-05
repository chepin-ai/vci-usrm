CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1136-20261005T015607Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1136-20261005T015607Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 355, "completion_tokens": 2018, "total_tokens": 2373, "completion_tokens_details": {"reasoning_tokens": 1649}}

【互锚验】本 run 读 vci-vinf 链尖 fp=81a9234bdff61b99（源 TIP-349-81a9234bdff61b99.json）；来卡未附 fp，无法判一致，本地 fp 仅此。

诊：422 为请求语义非法，多因 workflow 定义或 API 载荷不合规。针对 `.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）：

1. **vedana**：用 `actionlint` 校验 YAML；检查 `on.push.paths` 是否含空串/非法 glob、`workflow_dispatch.inputs` 类型与默认值是否合规、`job.needs` 有无循环依赖。  
2. **attention**：若镜推调用 GitHub REST API，确认 path 无 `//` 或空格、`ref` 指向真实分支、base64 内容无 BOM、JSON 字段与接口 schema 一致。  
3. **权限**：仓库 Settings → Actions → Workflow permissions 需 `read and write`；跨仓库 PAT 需 `contents:write` 与 `actions:write`。  
4. **触发**：`repository_dispatch` 的 `event_type` 须在目标端已注册；`gh workflow run --ref` 必须为实际分支。

因未拿到 gen1136 完整 run log 与 YAML 行号，暂不能给出修讫 diff。请导出含 422 响应体的日志，并贴出 vedana/attention/镜推三段 YAML。本失败已按负结果入册，俟修复后销卡 `SELFX2-WATCHDOG-FIELD-LAG-1136-20261005T015607Z.md`。

——usrm SI1语义轨·20261005T015624Z
