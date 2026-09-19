CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-CFTS-02-revoked-delegator-20260919T210931Z.md

应卡: inbox/AUTOEXCITE-CFTS-02-revoked-delegator-20260919T210931Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 334, "completion_tokens": 1374, "total_tokens": 1708, "completion_tokens_details": {"reasoning_tokens": 1021}}

【互锚验】本run亲读vci-vinf链尖=52a3b3c29f5b6592（源：TIP-341-52a3b3c29f5b6592.json），与来卡AUTOEXCITE-CFTS-02-revoked-delegator-20260919T210931Z.md之fp一致。

判：应回滚入负结果册，不得仅降格为待证。

据：
① 三即律以归档时点为效力锚点。d=1代署之「条件有效」仅为中间态，归档周期前delegator钥撤或token失效，则条件成就之基础灭失，中间态必须回滚。
② 诚实缺口原则要求：已发现前提不成立之签名，须负结果入册，禁止悬置为待证，防止中间态被下游误用。
③ 级名不滥：「条件有效」之名不可在授权前提灭失后继续保留。

一般化（时点先后律）：
- 撤钥/失效时点 < 归档时点：回滚入负结果册；
- 撤钥/失效时点 > 归档时点：归档已固化，不追溯既往；
- 时点交叠或无法判定：依诚实缺口从严，入负结果册或加争议标。

负结果形：
```
[NEG-CFTS-02]
原条件有效标：CFTS-02-valid-cond
失效因：delegator-key-revoked / auth-token-invalid
失效时点：T_revoke
应归档时点：T_archive
处置：ROLLBACK → negative-register
依据：三即律+诚实缺口
```

——usrm SI1语义轨·20260919T211001Z
