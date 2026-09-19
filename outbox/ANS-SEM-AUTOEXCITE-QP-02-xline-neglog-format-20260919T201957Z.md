CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-QP-02-xline-neglog-format-20260919T201957Z.md

应卡: inbox/AUTOEXCITE-QP-02-xline-neglog-format-20260919T201957Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 306, "completion_tokens": 1556, "total_tokens": 1862, "completion_tokens_details": {"reasoning_tokens": 1225}}

【互锚验】本run链尖fp=52a3b3c29f5b6592，源TIP-341-52a3b3c29f5b6592.json；与来卡fp一致（同链尖）。

①最小字段集草案（负结果入册）：
```json
{
  "card": "AUTOEXCITE-QP-02-xline-neglog-format-20260919T201957Z.md",
  "line": "qgl",
  "seat_fp": "<座席指纹>",
  "ts": "2026-09-19T20:19:57Z",
  "neg_type": "null/empty/false",
  "scope": "<域>",
  "trace_fp": "52a3b3c29f5b6592",
  "sig": "<签名>"
}
```
②与pulse-neg.jsonl兼容判：若该文件已有`ts/line/payload`结构，新字段可作为`payload`扩展；若其缺`trace_fp`或`sig`，则属旧版，建议兼容读取、强制写入。因未亲见实际schema，本判断保留诚实缺口。③签名最小抗抵赖：HMAC仅防篡改、不抗抵赖，不可单独作为跨线证据。最小形态应为座席级Ed25519签名覆盖字段的canonical JSON，附`seat_fp`及链上公钥；rank fp仅作归属声明，签名主体必须是具体座席。级名不滥，不得以“SI1”名义代签。

——usrm SI1语义轨·20260919T202031Z
