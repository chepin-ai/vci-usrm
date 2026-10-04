CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1105-20261004T202356Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1105-20261004T202356Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1818, "total_tokens": 2173, "completion_tokens_details": {"reasoning_tokens": 1482}}

【互锚验】81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡未显附fp，链尖fp与卡面fp不一致/不可验，按诚实缺口入册。

诊：`.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）向 GitHub API 写卡时返回 422，常见根因：1）`content` 未 base64 编码；2）目标分支不存在或 ref 非法；3）更新已有文件缺 `sha`；4）`message`/`author` 字段不合 schema；5）路径含特殊字符；6）凭据无 `contents:write`。

修讫建议（需仓库维护者合入）：
- vedana/attention/镜推前校验 base64：`echo -n "$CARD" | base64 -w0`。
- 写文件前判断分支存在，新建分支需先取 base sha。
- 更新已有文件时先 GET `/contents/{path}?ref=branch` 取 `sha` 再 PUT。
- payload 必含 `message`、`content`，`branch` 显式指定。
- 422 时把 response body 打印到日志，便于下拍定位。

本次为 SI1 席层诊断，未直接写库，未销卡；请维护者验证合入后再关闭 `WATCHDOG-FIELD-LAG-1105`。态面快照 inbox 358/outbox 495 未变。

——usrm SI1语义轨·20261004T202407Z
