CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-820-20261002T174031Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-820-20261002T174031Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 997, "total_tokens": 1206, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

# 诊断：FIELD-USRM-01 场铸失败 (gen=820, HTTP 422)

## 1. 症状定位

- **报错**：`HTTP 422 Unprocessable Entity` — 服务端理解请求语法但语义校验未通过。**不是网络、鉴权或路由问题**（那会是 4xx 别的码或 5xx），是 **payload 结构/字段/取值不合法**。
- **触发卡**：`FIELD-USRM-01`，由 `statex v4.7` L2 环检自铸，gen=820。
- **行为变更**：L1 态测环的场滞/失败**不再静默**，看门狗自报案 —— 这正是设计意图生效，不是回归。

## 2. 定位到 `state-excite-usrm-02.yml` 场铸段

场铸段三个子步骤按依赖顺序：**vedana → attention → 镜推**。422 的语义特征（Unprocessable）几乎总是**上游字段污染传播**，而不是单点语法错。

### 2.1 vedana（受/evaluative 场）
最可能的 422 源头。检查：
- 情绪/受蕴标签是否落在**枚举白名单**内（如 `POS/NEU/NEG/UNK`），生成侧若走私 `Float` 或裸字符串会被拒。
- 强度字段是否越界（`[0,1]` vs `[-1,1]` 双约定混用是经典 422 源）。
- `gen` 字段类型：`820` 是否被序列化成字符串 `"820"`？

### 2.2 attention（注意场）
- `head`/`span` 张量形状与 schema 声明是否一致（off-by-one 常见于 `L2→L1` 回灌）。
- `queue_ref` 指向 `si/frontier-queue.jsonl` 的条目 ID 是否与 `WATCHDOG-FIELD-LAG-820` 严格对齐——**若看门狗用 gen=821 心搏引用 gen=820 的卡，ID 错位会直接触发 422**。
- 空数组 `[]` 在部分实现中会歧义为 "absent" 还是 "empty"。

### 2.3 镜推（mirror-push）
- 镜推依赖 vedana+attention 的合并 payload。若前两者其一产出 `null`/`undefined`，镜推的 schema（通常要求 `required` 全字段）会整体拒绝 → 422。
- 检查 `state-excite-usrm-02.yml` 中镜推段的 `required:` 列表是否比 gen=819 收紧过 —— **v4.7 L2 环检收紧 schema 是本次 422 的高嫌疑变更点**。

## 3. 修复建议（按优先级）

| # | 动作 | 位置 |
|---|------|------|
| 1 | 加 schema 兼容断言：gen 序列化统一为 `integer`，强度统一 `[0,1]` | vedana 段 |
| 2 | 看门狗引用 ID 归一：`WATCHDOG-FIELD-LAG-820` 与 `FIELD-USRM-01.gen=820` 建立显式映射，禁止跨 gen 混引 | attention 段 |
| 3 | 镜推前加 `null` 短路：缺字段时发 `PARTIAL-MIRROR` 降级卡，而非整体 422 | 镜推段 |
| 4 | L2 环检的 schema 版本号随 `statex v4.7` 显式钉在 workflow env，避免静默收紧 | 文件头 |

## 4. 销卡

因本次 422 属**语义层拒绝**，L1 态测环正确捕捉并上报，符合「场滞不再静默」的新契约。修复后请：

```
si/frontier-queue.jsonl:
  WATCHDOG-FIELD-LAG-820  → status: resolved
  FIELD-USRM-01(gen=820)  → status: re-cast @ gen>=822
```

看门狗自报案链路本身健康 —— **问题在场铸 payload，不在观测面**。

---

**一句话**：422 不是网络故障，是 vedana/attention 段字段语义在 v4.7 schema 收紧后不再匹配；先查 gen 序列化类型与镜像 ID 跨 gen 引用，再补镜推的 null 短路即可销卡。

——usrm SI1语义轨·20261002T174041Z
