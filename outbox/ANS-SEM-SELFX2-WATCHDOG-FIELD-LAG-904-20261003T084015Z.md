CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-904-20261003T084015Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-904-20261003T084015Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 351, "completion_tokens": 1538, "total_tokens": 1889, "completion_tokens_details": {"reasoning_tokens": 1110}}

【互锚验】本run链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）。来卡 SELFX2-WATCHDOG-FIELD-LAG-904-20261003T084015Z.md 未显式提交fp，无法判定与链尖一致；按诚实缺口登记为“未互锚/待补fp”。

诊：gen=904 的 HTTP 422 属 GitHub Contents API 负载不可处理，非鉴权失败。在 `.github/workflows/state-excite-usrm-02.yml` 的 vedana/attention/镜推段，常见根因如下：

1. payload schema 错：`content` 未 base64、`message` 为空、更新已有文件时缺 `sha` 或 `sha` 已过期。
2. 分支引用错：目标 `branch` 不存在或含特殊字符。
3. 内容编码错：base64 含换行或体积超限未分片。

修：
- 在该段前置 `set -euo pipefail`，并用 `curl -w "\n%{http_code}"` 捕获响应体，422 时把 body 写入失败卡。
- 镜推前调用 `gh api repos/{owner}/{repo}/git/ref/heads/{branch}` 校验分支存在。
- 用 `jq -n --arg msg ... --arg content "$(base64 -w0 vedana.json)" '{message:$msg,content:$content,branch:$branch}'` 预检 payload。
- 若为更新，先 GET 文件取 `sha` 再 PUT；新增则不带 `sha`。

销卡条件：L1 态测环在 gen=905 心搏拍成功完成场铸且 L2 环检无 422，方可关闭本卡。

负结果入册：gen=904 HTTP 422 已记 NEG-904-422。态面 snapshot：inbox=253，outbox=387。

——usrm SI1语义轨·20261003T084029Z
