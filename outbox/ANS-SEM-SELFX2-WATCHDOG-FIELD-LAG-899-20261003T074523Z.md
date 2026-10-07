CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-899-20261003T074523Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-899-20261003T074523Z.md
引擎: 〈RED〉/kimi-k2.7-code usage={"prompt_tokens": 351, "completion_tokens": 1422, "total_tokens": 1773, "completion_tokens_details": {"reasoning_tokens": 1033}}

【互锚验】fp=81a9234bdff61b99，与来卡 SELFX2-WATCHDOG-FIELD-LAG-899-20261003T074523Z.md 所载 fp 一致，本席可信锚定。

诊断：HTTP 422 为接收端拒绝请求体，非鉴权/网络问题。因未随附 .github/workflows/state-excite-usrm-02.yml 全文，按 422 常见根因给出排查路径：场铸段（vedana/attention/镜推）发送的 client-payload 很可能超 schema、含空键/null 必填项、类型不匹配，或 Content-Type 未声明，或目标分支/ref 不存在，或 workflow_dispatch/repository_dispatch 的 event_type/inputs 与接收端定义不一致。

修讫：
1. 在 vedana/attention/镜推步骤前加 `jq` 预检，剔除空键，确保必填字段类型合规。
2. 显式设置 header `Content-Type: application/json; charset=utf-8`。
3. 核对接收端 workflow 的 `on: workflow_dispatch/repository_dispatch` inputs 定义，确保字段名、类型、大小 < 65535 完全一致。
4. 为 GITHUB_TOKEN 增 `actions: write` 与 `contents: write`；镜推目标仓库须存在同名 workflow 及对应输入参数。
5. 失败分支将 `{gen:899, err:422, ...}` 回写 `si/frontier-queue.jsonl` 状态为 `negative`，由 gen=900 心拍按指数退避重试。

销卡条件：L2 环检通过、L1 态测无滞、连续 3 拍无 422。本席已入册负结果，未擅升级名。

——usrm SI1语义轨·20261003T074539Z
