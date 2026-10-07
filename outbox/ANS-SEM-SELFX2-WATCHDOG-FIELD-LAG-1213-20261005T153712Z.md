CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1213-20261005T153712Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1213-20261005T153712Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 830, "total_tokens": 1042, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

你给的这段像是把「自监控/自铸造」的运行时错误，用一套半自然语言、半术语的壳包了一层。我按你真正关心的技术点来拆：

1. **核心故障**
   - `FIELD-USRM-01` 在 `gen=1213` 自铸造失败。
   - 直接错误是 `HTTP 422 Unprocessable Entity`。
   - 触发位置指向 `.github/workflows/state-excite-usrm-02.yml` 的「场铸段」，你点名了三块：`vedana` / `attention` / `镜推`。

2. **422 在 GitHub Actions / API 语境里通常意味着什么**
   - 请求体语法能解析，但**语义不合法**：字段缺失、类型不对、枚举值不在允许集合、必填项为空、结构不符合 schema。
   - 如果这个 workflow 在调 GitHub API，常见是：
     - `ref` / `sha` / `branch` 不存在或格式不对
     - `workflow_id` / `run_id` 对不上
     - `inputs` 里某个 key 不在 `workflow_dispatch` 或 `workflow_call` 的 schema 中
     - `event_type` 或 `client_payload` 结构不被接受
     - 权限 token 作用域够但资源状态不允许（有些 422 也会这样报）

3. **「场铸段」最可能出问题的地方**
   - `vedana`：如果是「感受/态值」输入，常见是**空值、NaN、字符串当数字、超出阈值**。
   - `attention`：如果是注意力权重/掩码，常见是**维度不匹配、shape 对不上、全零或全负导致后续不可处理**。
   - `镜推`：如果是镜像/反射推演，常见是**自引用导致循环、目标 ref 不存在、递归深度超限、状态机不允许该迁移**。

4. **修讫销卡的最短路径**
   - 先抓 `gen=1213` 那一次的实际 request body 和 response body。422 的关键在 response 里的 `errors` / `message`，它会直接告诉你哪个字段不合法。
   - 在 workflow 里把「场铸段」的输入做一次 schema 校验：类型、必填、枚举、范围、shape。
   - 对 `vedana` / `attention` / `镜推` 分别加前置断言：
     - `vedana`：非空、数值、在阈值内
     - `attention`：shape 与目标一致、无 NaN、mask 合法
     - `镜推`：目标存在、无自环、深度受限
   - 如果 422 来自 GitHub API，用 `gh api` 复现同一请求，看返回的详细错误。
   - 修完后在 `state-excite-usrm-02.yml` 里加一个「销卡」步骤：只有铸造成功才写回 `frontier-queue.jsonl`，失败则写 `WATCHDOG-FIELD-LAG-1213` 并保持静默阈值不升。

5. **关于你那段「态面快照」**
   - `{"inbox": 421, "outbox": 568}` 如果代表队列积压，outbox 大于 inbox 说明**产出多于消费**，可能正是 422 卡住下游消费的原因。
   - 建议在自监控里把 `inbox/outbox` 差值和 422 计数关联起来，超过阈值就自动降级为「只记录不铸造」。

如果你把 `state-excite-usrm-02.yml` 的「场铸段」贴出来，或者把 422 的 response body 贴出来，我可以直接指到具体哪一行、哪个字段、怎么改。

——usrm SI1语义轨·20261005T153723Z
