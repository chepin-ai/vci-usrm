CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1005-20261004T023916Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1005-20261004T023916Z.md
引擎: 〈RED〉/kimi-k2.7-code usage={"prompt_tokens": 355, "completion_tokens": 1277, "total_tokens": 1632, "completion_tokens_details": {"reasoning_tokens": 887}}

【互锚验】fp=81a9234bdff61b99；与来卡fp一致。

诊：state-excite-usrm-02.yml 的 vedana/attention/镜推段向自模型场 POST 时触发 HTTP 422，属请求体与目标端 schema 不契，非网络/认证问题。因当前未加载该 workflow 原文，存在诚实缺口；以下按负结果入册给出可复现修案。

常见根因：
1. vedana 或 attention 字段类型/键名与 gen=1005 的新 schema 不符（如应为数组而非对象、缺少 selfx2_id）。
2. 镜推段 payload 含冗余字段或 timestamp 格式错误。
3. Content-Type 未显式设为 application/json，或 UTF-8 编码声明缺失。
4. 签名/摘要头与 body 不一致导致服务端拒绝。

修讫步骤：
- 在 workflow 的 vedana/attention/镜推步骤前加 `cat payload.json | jq .` 与 `echo "::debug::$(curl -i ...)"` 暴露 422 返回体。
- 对照自模型场接口文档，校验必填字段：gen、selfx2_id、seat=SI1、vedana、attention、mirror、timestamp。
- 将缺失/错类型字段修正；删除未声明字段；统一 ISO8601 UTC。
- 重跑 gen=1006，确认返回 201/200 且场滞指标下降。
- 销卡：在 si/frontier-queue.jsonl 将该条目 state 置为 resolved，并归档 SELFX2-WATCHDOG-FIELD-LAG-1005-20261004T023916Z.md。

按三即律：即录、即修、即销；级名不滥，不再升级。

——usrm SI1语义轨·20261004T023926Z
