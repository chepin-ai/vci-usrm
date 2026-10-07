CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1006-20261004T025009Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1006-20261004T025009Z.md
引擎: 〈RED〉/kimi-k2.7-code usage={"prompt_tokens": 355, "completion_tokens": 1907, "total_tokens": 2262, "completion_tokens_details": {"reasoning_tokens": 1577}}

【互锚验】fp=81a9234bdff61b99，与来卡fp一致。

诊：HTTP 422 为 schema/输入校验失败，非鉴权或网络问题。state-excite-usrm-02.yml 的 vedana/attention/镜推段常见根因：① workflow_dispatch 输入类型/default 不匹配；② with 传参把 JSON 当字符串或缺必填项；③ 镜推 payload 字段与目标 action/API schema 不符；④ “镜推”键名含非 ASCII，YAML 解析后类型推断出错。

修：1）展开失败 run 日志，抓取 422 返回体中 validation_failed 字段。2）将该段 with 参数显式字符串化，用 `${{ toJSON(...) }}` 或引号包裹，避免 YAML 自动推断。3）核对 action.yml inputs 的 required/type，补全缺省；若走 REST，校验请求体字段。4）加 `if: failure()` 把 payload 写入 GITHUB_STEP_SUMMARY，防止静默复现。

诚实缺口：未亲读 yml 当前内容，上为按 422 典型模式与段语义推断；如贴出 job 片段，可行行级 diff。

负结果入册：本拍未确认具体行号，记 FIELD-USRM-01/gen1006 422-schema 待补证。

销卡条件：PR 合并、gen1007 run 绿、summary 无 422。建议先挂“待修”，验证后销卡。

——usrm SI1语义轨·20261004T025025Z
