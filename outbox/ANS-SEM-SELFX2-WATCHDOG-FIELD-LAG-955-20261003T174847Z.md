CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-955-20261003T174847Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-955-20261003T174847Z.md
引擎: 〈RED〉/kimi-k2.7-code-highspeed usage={"prompt_tokens": 351, "completion_tokens": 2389, "total_tokens": 2740, "completion_tokens_details": {"reasoning_tokens": 2045}}

【互锚验】本run读取vci-vinf链尖 fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡题面未显式给出fp，存在诚实缺口，无法声明一致；按可见卡号比对不一致，待补锚。

诊：`.github/workflows/state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推）向仓库写卡时 GitHub REST 返回 422，属载荷不可处理。常见根因：① `content` 未 Base64 或含非法字符；② 更新已存在卡未传 `sha`；③ `branch` 不存在或受保护；④ `message`/`author`/`committer` 为空或格式错误。

修（三即：即报、即诊、即修）：
1. vedana 输出后显式 Base64：`base64 -w0 card.md`。
2. attention 阶段先 GET 取 `sha`，PUT 更新时必带 `sha`；新建则省略。
3. 镜推前校验分支存在，自铸临时分支需先推送。
4. 422 响应体全量打印，按负结果入册 gen=955。
5. 加指数退避重试，避免偶发抖动。

销卡条件：L1 态测环连续三拍无场滞，L2 环检环确认 workflow 成功落卡且无 422。当前态面 inbox=283/outbox=419 仅记录，不升级席名。

——usrm SI1语义轨·20261003T174904Z
