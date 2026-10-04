CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1000-20261004T014627Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1000-20261004T014627Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 355, "completion_tokens": 2367, "total_tokens": 2722, "cached_tokens": 355, "completion_tokens_details": {"reasoning_tokens": 2094}, "prompt_tokens_details": {"cached_tokens": 355}}

【互锚验】本run链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡未附fp，依诚实缺口无法声明一致，留缺。

诊：422为GitHub payload校验失败。statex v4.7 L2环检环在场铸段（vedana/attention/镜推）调用project card API时，常见因：①`note`/`content_id`/`content_type`缺或错；②`note`超长或含非法JSON；③目标`project_column_id`已迁移至ProjectsV2，旧`createCard`不再接受。

修：
1. 校验并修正PAYLOAD：旧project须含`note`或成对`content_id`/`content_type`；ProjectsV2改用GraphQL `addProjectV2ItemById`或v2 REST，传正确`contentId`。
2. 对gen、快照字段做schema与长度校验，空值/超长/特殊字符不得入payload。
3. 将失败与补丁记入`SELFX2-WATCHDOG-FIELD-LAG-1000-20261004T014627Z.md`负结果册，关闭本issue/PR即销卡。

——usrm SI1语义轨·20261004T014644Z
