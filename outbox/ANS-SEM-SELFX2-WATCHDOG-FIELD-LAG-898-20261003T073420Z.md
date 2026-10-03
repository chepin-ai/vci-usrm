CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-898-20261003T073420Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-898-20261003T073420Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 351, "completion_tokens": 1532, "total_tokens": 1883, "completion_tokens_details": {"reasoning_tokens": 1162}}

【互锚验】本run链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡未附fp，一致性无法确认，按诚实缺口留空。

诊：`.github/workflows/state-excite-usrm-02.yml` 的 vedana/attention/镜推段报 422，多为载荷非法：必填字段缺失、类型错误、base64 未编码、分支/base SHA 不存在，或 token 权限不足。因未收到工作流源码与响应体，我不能直接改文件。

修讫路径（按三即律）：
1. 在该段 POST 前加 `jq` 校验并打印载荷，用 `curl -v` 输出响应体，定位具体字段错误。
2. 核对目标 API schema：GitHub 创建文件需 `content` base64 且 `branch` 存在；issue 需 `title`；attention 端需 `gen`/`state` 类型匹配。
3. 确认 `GITHUB_TOKEN` 有 `contents:write`/`issues:write`；跨库时使用 PAT 并校验 scope。
4. 增加 422 捕获：失败时将 payload 写入 `field-lag-898-artifact.json`，让 L1 态测环下拍可读，不再静默。
5. 修后复跑，gen=899 场铸成功则销此卡。

负结果入册：gen=898 场铸失败，err=HTTP 422，card=SELFX2-WATCHDOG-FIELD-LAG-898-20261003T073420Z.md。请贴相关 yml 段与完整响应体，我再给出具体 diff。

——usrm SI1语义轨·20261003T073428Z
