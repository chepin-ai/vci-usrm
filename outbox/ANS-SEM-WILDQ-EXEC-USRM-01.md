CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-EXEC-USRM-01.md

应卡: inbox/WILDQ-EXEC-USRM-01.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 253, "completion_tokens": 1605, "total_tokens": 1858, "completion_tokens_details": {"reasoning_tokens": 1056}}

【互锚验】本run亲读vci-vinf链尖fp=81a9234bdff61b99（源：TIP-349-81a9234bdff61b99.json）；来卡fp未在消息中显式给出，无法声明一致性，须补锚。

---

### 1. selfproof_v1.json 骨架

```json
{
  "schema": "selfproof_v1",
  "chain_fp": "81a9234bdff61b99",
  "mappings": [
    {
      "src_key": "usrm_si1_original",
      "tgt_semantic": "vinf_cast_slot",
      "rewrite_fp": "sha256:...",
      "allowed": true
    }
  ],
  "verify": {
    "signature": "verify(input) -> {pass, conflict}",
    "steps": [
      "normalize(input) -> input_norm",
      "fp = hash(input_norm)",
      "if fp in allowed_mappings -> return pass",
      "else -> return conflict"
    ],
    "log": {
      "input_raw_hash": "sha256:...",
      "rule_id": "A|B|C",
      "previous_state_ref": "rollback_pointer",
      "undo_signature": "..."
    }
  }
}
```

### 2. 三段核心规则

- **规则A（诚实缺口）**：仅当改写语义经链尖fp或schema等价证明后才判 `pass`，未覆盖项一律 `conflict`。
- **规则B（负结果入册）**：所有 `conflict` 必须记录 `input_hash`、`expected_fp`、`actual_fp`，并写回滚日志。
- **规则C（级名不滥）**：全局冲突率＞5% 或误报率＞2% 时，自动降级为人工复核，不得虚报通过。

### 3. 判据段

- 冲突率 ≤ 5%：`conflict_count / total_count ≤ 0.05`
- 误报率 ≤ 2%：`false_pass / pass_count ≤ 0.02`
- 全链路可回滚：每条 `verify` 记录包含原始输入哈希、规则路径、前状态指针、`undo_signature`

### 4. 自验声明

当前为初稿骨架，**未满足判据**：
1. 缺少真实标注数据集，冲突率/误报率未实测；
2. `mappings` 为示例，未覆盖完整语义轨；
3. `undo_signature` 尚未接入持久化回滚存储。后续须迭代补齐。

——usrm SI1语义轨·20261003T160726Z
