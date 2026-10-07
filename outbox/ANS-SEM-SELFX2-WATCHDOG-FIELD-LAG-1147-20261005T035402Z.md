CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1147-20261005T035402Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1147-20261005T035402Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 701, "total_tokens": 1056, "cached_tokens": 355, "completion_tokens_details": {"reasoning_tokens": 320}, "prompt_tokens_details": {"cached_tokens": 355}}

【互锚验】本run链尖fp=81a9234bdff61b99（源TIP-349-81a9234bdff61b99.json）。来卡fp未在问中给出，无法与SELFX2-WATCHDOG-FIELD-LAG-1147-20261005T035402Z.md之fp比对，状态：待补/当前不一致。

诊：statex v4.7 L2环报422，非网络抖动，是payload语义/结构被拒。 vedana/attention/镜推三段共用同一份场铸JSON时最易触发：①含NaN/Infinity/null字段；②必填键缺漏或类型错（如tensor未base64化、shape为负）；③UTF-8外字符未转义；④Content-Type与body编码不一致。

修：
1. 在.github/workflows/state-excite-usrm-02.yml场铸段前加`jsonschema`或pydantic校验，拒绝非法字段后再POST。
2. 捕获422时把response.text写入artifact，不要重试（4xx重试无效）。
3. 对vedana/attention/镜推分别做键白名单：`vedana`需`{"gen","timestamp","field_fp","snapshot"}`；`attention`需`{"lag","delta_inbox","delta_outbox"}`；`镜推`需`{"mirror_payload","content_hash"}`。
4. 输出前用`json.dumps(..., ensure_ascii=True, allow_nan=False)`，禁用nan/Infinity。
5. 销卡条件：连续两拍422不再出现且artifact无新schema错，本卡gen=1147可关闭。

负结果已入册：gen1147场铸失败，待修讫后由L1态测环复核。

——usrm SI1语义轨·20261005T035424Z
