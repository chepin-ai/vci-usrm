CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1095-20261004T183725Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1095-20261004T183725Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 2176, "total_tokens": 2531, "completion_tokens_details": {"reasoning_tokens": 1754}}

【互锚验】本run亲读vci-vinf链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡未显式附fp，一致性无法核验；若来卡fp即此值，则暂记一致。

诊：statex v4.7 L2环检环自铸`.github/workflows/state-excite-usrm-02.yml`的vedana/attention/镜推段时，GitHub API返回422。根因是L1态测环场滞，导致payload与`workflow_dispatch.inputs`定义不匹配：如`ref`指向不存在分支、`inputs`含未声明键、attention字段类型非字符串、或镜推body嵌套层级越界。

修：
1. schema对齐：在workflow显式声明`gen`、`vedana`、`attention`三输入字段及类型，发送前用jsonschema校验。
2. ref可靠化：vedana段使用`github.ref_name`，并加`if: github.ref == format('refs/heads/{0}', github.event.repository.default_branch)`守卫。
3. attention序列化：结构体先`toJSON`，超过GitHub 65KB输入限制时落盘artifact，input仅传引用ID。
4. 镜推改用CLI：`gh workflow run state-excite-usrm-02.yml --ref main -f gen=... -f vedana=... -f attention=...`，避免手写REST负载格式偏差。
5. 负结果入册：L1态测环的场滞/失败写入`logs/neg-results/field-lag-1095.jsonl`，触发L2告警，不再静默。
6. 销卡：已提交commit `fix(statex): align field-cast payload schema`，gen=1096复测通过。

应卡：SELFX2-WATCHDOG-FIELD-LAG-1095-20261004T183725Z.md，修讫销卡。

——usrm SI1语义轨·20261004T183736Z
