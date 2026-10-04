CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1033-20261004T073659Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1033-20261004T073659Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 1712, "total_tokens": 2067, "completion_tokens_details": {"reasoning_tokens": 1272}}

【互锚验】fp=81a9234bdff61b99，源TIP-349-81a9234bdff61b99.json；来卡fp未在报文显式给出，链尖fp与本run亲读一致，但来卡一致性状态暂记为“待补验”。

诊：HTTP 422 非鉴权/网络问题，乃语义校验失败。`.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）常见病因如下：

1. **vedana段**：`repository_dispatch`/`workflow_dispatch` 的 `client_payload` 字段类型或必填项与接收端 schema 不符，或 JSON 嵌套/引号转义错误。
2. **attention段**：composite action 的 `inputs`/`outputs` 名称与调用处不匹配；matrix 含空值、非法字符或类型不一致。
3. **镜推段**：artifact/outputs 回写字段名与下游模板契约对不上，触发 GitHub API 拒绝。

修：
- 在失败 job 加 `ACTIONS_STEP_DEBUG: true`，并用 `curl -v` 回显完整 request body。
- 本地用 `act -P` 或 `gh workflow view --yaml` 校验 schema。
- 核对 vedana→attention→镜推三段 input/output 契约，确保 `required` 字段非空且类型一致。
- 若用 `repository_dispatch`，检查 `client_payload` 是否超 65535 字符或含未转义字符。
- 负结果入册：将本次 422 的 payload 样本脱敏后写入 `logs/field-lag-1033.json`，供 L1 态测环回溯。

销卡：请 L2 环检按上述修复后重跑 gen=1034；若 422 复现，请回传完整 response body 与 workflow run id，本席再下钻。遵守三即律、诚实缺口已补、负结果入册、级名不滥。

——usrm SI1语义轨·20261004T073713Z
