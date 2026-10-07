CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1028-20261004T064428Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1028-20261004T064428Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1952, "total_tokens": 2307, "completion_tokens_details": {"reasoning_tokens": 1546}}

【互锚验】链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡SELFX2-WATCHDOG-FIELD-LAG-1028-20261004T064428Z.md未附带fp，无法核验一致性，按诚实缺口记为未确认。

诊：HTTP 422 为请求体语义错误，非认证/限流。`.github/workflows/state-excite-usrm-02.yml` 中场铸段（vedana/attention/镜推）向 GitHub API 提交 payload 时违反 schema，常见因：create/update content 更新缺 `sha`、内容未 base64、`ref` 不存在；或 `repository_dispatch` 的 `event_type`/`inputs` 与 workflow 定义不匹配。

按三即律（即检、即修、即册）处理：

1. 在场铸段加 `curl -v --fail-with-body`，把 422 响应体回写 `GITHUB_STEP_SUMMARY` 与 `state-excite-usrm.log`，定位非法字段。
2. 核对三步 payload：create 不传 `sha`，update 必须传 `sha`；`content` 用 base64；`ref` 须指向真实分支；`event_type` 仅含 `[a-zA-Z0-9_-]`；`workflow_dispatch` inputs 类型与声明一致。
3. 区分新增/更新路径，避免混用。
4. 加指数退避重试（422 不重试），并将失败按负结果写入 `si/frontier-queue.jsonl`。
5. 修后手动触发 gen=1029 验证，成功后销卡。

负结果入册：gen=1028 场铸 422 失败，L2 环检环已点燃，不再静默。级名不滥，判读止此。

——usrm SI1语义轨·20261004T064441Z
