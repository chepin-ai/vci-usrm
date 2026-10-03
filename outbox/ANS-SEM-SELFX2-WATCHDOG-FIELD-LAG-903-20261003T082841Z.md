CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-903-20261003T082841Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-903-20261003T082841Z.md
引擎: KIMI_API_KEY/kimi-k3 usage={"prompt_tokens": 436, "completion_tokens": 1551, "total_tokens": 1987, "completion_tokens_details": {"reasoning_tokens": 1180}, "prompt_tokens_details": {"cache_write_tokens": 256}}

【互锚验】本run所读vci-vinf链尖fp=81a9234bdff61b99（源TIP-349-81a9234bdff61b99.json）。然来卡正文未附fp字段，本会话亦无文件系统权限亲读卡文与TIP原件，故声明：一致性**无法核验**，按诚实缺口记"未确认"，不伪报一致。

**诊断**（HTTP 422=语义校验拒绝，非网络/权限问题，按概率排序）：

1. **schema漂移**：场拍JSON中vedana/attention/镜推三段新增或改型字段，接收端校验拒绝；或含NaN/裸None直出成非法JSON。
2. **若走GitHub Contents API提交快照**：PUT时未带当前文件sha，或路径/分支校验失败 → 422 Validation Failed。
3. **幂等重试**：超时后重发同gen=903，服务端唯一约束拒收。

**修复**：

- 场铸段POST前加本地schema校验（jsonschema/jq），fast-fail并打字段diff。
- **关键**：422分支必须落盘response body。当前卡面只剩状态码，属"失败半静默"，恰是本看门狗要防的二次违例。
- 提交GitHub前先GET取sha再PUT。
- schema版本钉入仓库，加契约测试防再漂移。

**诚实缺口**：未读到yml原文与422响应体，上列系假设清单；决定性一步是补响应体日志后重放gen=903。负结果已入册；销卡须附新一拍成功证据，不得仅因报错消失即销。

——usrm SI1语义轨·20261003T082852Z
