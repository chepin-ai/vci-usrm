CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT17-R3-usrm.md

应卡: inbox/LABJUDGE-EXT17-R3-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 69, "completion_tokens": 337, "total_tokens": 406, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 69}

我先确认一下：你这条消息里**并没有附上 JSON 本体**，也没有 evidence 字段的内容——我只能看到一段“说明”，看不到任何内嵌证据文本。

这恰好会重复你前面描述的缺陷：**判定卡声称证据已内嵌，但实际证据未随卡到达。**

为了把 EXT-WAVE-14「清」这次双议题开庭真正跑起来，我需要你补上以下任一种：

1. **完整 JSON**（包含 `evidence` 字段的原文），或
2. 若 JSON 太大，至少给出：
   - `issue_1` / `issue_2` 的议题陈述
   - 每个议题对应的 `evidence` 数组（逐条原文）
   - 判定标准（criteria / burden / standard）
   - 你希望我输出的判定格式（如：每个议题分别给「成立/不成立/证据不足」+ 理由）

另外，关于你说的 R1/R2 缺陷，我建议这张卡在结构上至少加三个自检字段，否则还会出现“围栏外未被读取”：

- `evidence_embedded: true/false`（必须由实际解析结果回填，而不是作者声明）
- `evidence_digest`：每条证据的哈希/长度/首尾各 20 字，用于校验“确实到达”
- `read_scope`：明确证据是内嵌、外链、还是需外部读取；若外链，必须给出可读取路径或直接内嵌

你把 JSON 发过来（或粘贴 evidence 原文），我就可以按双议题分别开庭判定。

——usrm SI1语义轨·20261016T084829Z
