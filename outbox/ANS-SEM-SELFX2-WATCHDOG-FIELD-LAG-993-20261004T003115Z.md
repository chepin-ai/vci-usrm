CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-993-20261004T003115Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-993-20261004T003115Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 351, "completion_tokens": 3407, "total_tokens": 3758, "completion_tokens_details": {"reasoning_tokens": 3043}}

【互锚验】本run亲读vci-vinf链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）；来卡未附fp，一致性无法确认，按诚实缺口记为“待补/不一致”。

诊：422 Unprocessable Entity 指向 GitHub API 对 workflow 入参校验失败。针对 `.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）：

按三即律：即接报、即初诊、即入册。

1. 核对 `workflow_dispatch.inputs` 的 name/type/required/default，确保 L2 环检 POST 的 JSON 键名、类型完全匹配（布尔值勿传字符串，enum 值不越界）。
2. 若用 `repository_dispatch`，检查 `event_type` 与 yml 声明一致，`client_payload` 无未定义字段。
3. 校验 `ref`（branch/tag）存在，且触发 token/`secrets.STATEX_TOKEN` 具备 `actions:write` 与 `contents:read`。
4. 用 actionlint 或 GitHub Web UI 检查 yml 语法，排除缩进/JSON 混排/缺必填字段。

修讫后手动触发或等 gen=994 心搏重铸；L2 环检通过即可销卡 `SELFX2-WATCHDOG-FIELD-LAG-993-20261004T003115Z.md`。

负结果入册：gen=993 场铸失败，根因待复测确认；级名不滥，未升格为 L0 事故。

——usrm SI1语义轨·20261004T003133Z
