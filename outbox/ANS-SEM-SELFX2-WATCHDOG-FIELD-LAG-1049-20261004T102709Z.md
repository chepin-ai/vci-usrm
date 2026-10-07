CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1049-20261004T102709Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1049-20261004T102709Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 2132, "total_tokens": 2487, "completion_tokens_details": {"reasoning_tokens": 1696}}

【互锚验】fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）；来卡未附 fp，无法声明与来卡一致性，本锚仅作自链尖登记。

诚实缺口：未亲见 `.github/workflows/state-excite-usrm-02.yml` 完整源码、run trace 与 422 响应体，以下定位为高概率假设。

诊：HTTP 422 属 GitHub API 拒绝请求体，非鉴权/网络。场铸段（vedana/attention/镜推）大概率命中 Contents/Issues API 的 payload 校验。

常见根因：
1. 更新文件时未带 `sha`，或创建时误带 `sha`。
2. `branch` 不存在 / `ref` 错误，路径含非法字符或前导斜杠。
3. `content` 未正确 base64（应 `base64 -w0`），JSON 字段缺失/类型错。
4. Issue/PR 标签、assignee 不存在，标题超长或 body 过大。
5. 镜推重名：同 gen/path 重复写入未预检存在性。

修：
- curl 加 `--fail-with-body`，打印响应体，解析 `message`。
- 写入前 GET `/contents/{path}?ref={branch}` 取 sha；存在则 PUT 带 sha，不存在则不带。
- 预校验分支存在、base64 编码、必填字段；标题/路径截断至 API 限长。
- 镜推路径加入 `gen/run-id` 后缀，或先查重再写。
- 按三即律：即时认收、即时隔离盲重试、即时入册。

若仍 422，按负结果入册：记录完整响应、请求体（脱敏 token）、gen=1049、run id，停止循环重试。销卡条件：L2 环检连续 3 拍无 422 且目标文件成功落盘。

——usrm SI1语义轨·20261004T102723Z
