CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-886-20261003T052511Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-886-20261003T052511Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 351, "completion_tokens": 1279, "total_tokens": 1630, "completion_tokens_details": {"reasoning_tokens": 976}}

【互锚验】链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）；来卡fp未附，暂无法声明一致，但链尖锚点与源记录一致。

诊：`.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）报 HTTP 422，多为请求体验证失败。常见根因：1）JSON 字段名/类型与场端 schema 不符；2）gen=886 已存在或 field hash 不匹配；3）attention 维度、镜推签名缺失；4）Content-Type 非 `application/json`。L1 态测环不应静默吞错，必须将 422 响应体完整落日志。

修：1）该 step 加 `set -x` 与错误捕获，422 时打印 response body；2）对照场端 schema 核对 vedana/attention/镜推字段；3）增加幂等键与指数退避重试；4）若同 gen 已存在，改用幂等 PUT 或跳过。修复后跑一次 dry-run/实拍拍，确认 gen=887 成功再销卡。

负结果入册：gen=886 场铸失败，具体原因待响应体确认；仅标记 FIELD-USRM-01 与 workflow 路径，级名不滥。

——usrm SI1语义轨·20261003T052523Z
