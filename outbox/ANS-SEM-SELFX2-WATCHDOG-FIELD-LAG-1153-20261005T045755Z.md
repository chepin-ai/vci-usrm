CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1153-20261005T045755Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1153-20261005T045755Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 849, "total_tokens": 1204, "completion_tokens_details": {"reasoning_tokens": 507}}

【互锚验】链尖 fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡 SELFX2-WATCHDOG-FIELD-LAG-1153-20261005T045755Z.md 未提供独立 fp，故链尖与卡 fp 暂无法一致/不一致判定，缺卡锚；诊以链尖为锚。

诊：422 非权限，是请求体语义不合 GitHub `workflow_dispatch` 输入 schema。`.github/workflows/state-excite-usrm-02.yml` 场铸段 vedana/attention/镜推 最可能：

1. `镜推` 为中文输入键，GitHub 输入 ID 仅允许 `[a-zA-Z0-9_-]` 且首字符须为字母或下划线，直接触发 422。
2. 或 vedana/attention 值类型/必填项与声明不符，或 `ref` 指向不存在的分支/SHA。

修：
- 将 `镜推` 改为 ASCII id（如 `mirror_push`/`jingtui`），映射到业务语义。
- 校验 `workflow_dispatch.inputs` 三键均声明为 `type: string` 且非空。
- 调用前校验 `ref` 为有效分支；payload 字段与 schema 对齐。
- 在 L2 环检环加入预检钩子，422 时回写具体字段错误，避免 L1 场滞静默。

修讫后手动触发 gen=1154 验证，成功后销卡。

——usrm SI1语义轨·20261005T045809Z
