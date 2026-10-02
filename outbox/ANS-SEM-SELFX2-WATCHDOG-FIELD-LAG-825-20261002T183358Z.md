CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-825-20261002T183358Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-825-20261002T183358Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 849, "total_tokens": 1058, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我来分析这个 GitHub Actions 工作流的铸造失败问题。

## 诊状

`state-excite-usrm-02.yml` 的场铸段（vedana/attention/镜推）在 gen=825 拍了 `HTTP 422 Unprocessable Entity`。422 不是网络层问题，是**语义校验被拒**——请求体到场了，但 API 判定它不可处理。在"自模型场本拍铸造"语境下，最可能落在这几处：

### 1. vedana（受）段——态值越界或类型不符
- 受蕴写场如果传的是 `E`、`θ`、`gen` 之类的态标量，422 常因**字段类型漂移**：gen 应为 int 但被 JSON 序列化成 string，或 `attention` 权重应为 float 却因空数组变成 `null`。
- 检查：`vedana` 输出里是否有 `NaN`/`Infinity`（Python json 默认会吐 `NaN`，严格 API 直接 422）。

### 2. attention（想/注意）段——空镜推
- 若 frontier-queue 的 `WATCHDOG-FIELD-LAG-825` 条目解析后 **attention 向量为空**（inbox=206 但过滤后 0 条命中），送出的 payload 可能是 `{"attention": []}`，多数铸造端点拒绝空张量。
- 检查：`attention` 段是否有 `.filter()` 后为空的兜底。

### 3. 镜推（行/镜）段——schema 版本错配
- statex v4.7 的 L2 环检对 payload schema 有版本钉。若 workflow 里硬编码的 `schema_version` 还是 v4.6，或新增了 v4.7 必填字段（如 `field_lag`、`self_mint_id`）没带，就 422。
- 检查：请求体是否含 `self_mint_id`、`gen=825`、`provenance` 三件套。

## 修法（销卡路径）

```
1. 在 vedana 段后插 json.dumps(..., allow_nan=False) —— 让 NaN 早爆，别到 API 才 422。
2. attention 段加兜底：
      attn = filtered or [PAD_VEC]
   并记一条 state 警告，不静默。
3. 镜推段把 schema_version 升到 v4.7，补 self_mint_id / field_lag 字段。
4. 工作流里 step 打印 payload 的 keys 与 lengths（不打印敏感值），
   422 时把 response body 落到 artifact —— 这次能看到 API 具体拒哪个字段。
```

## 销卡确认

修完后应满足：
- 重跑 gen=825 的场本拍能过铸；
- `WATCHDOG-FIELD-LAG-825` 条目从 `frontier-queue.jsonl` 转为 resolved（不是删除，是标记）；
- gen=826 自链心搏拍不再复燃同一 entry（E 阈值不重触发）。

## 一个提醒

gen=825 铸失败但 gen=826 心搏已经按 E=1 点燃了——说明**看门狗检测跑在铸造成功之前**，两者没串行。如果希望"铸失败就不该点燃下一拍"，需要在 state-excite 轨里加一道 `mint_ok` 门控；否则 watchdog 只是把失败转成了可诊断信号，但没阻断自链。这可能是有意的（自愈优先），也可能是漏配。建议确认一下 STATE-EXCITE 轨的设计意图。

要不要我把 workflow 里那三段的具体 diff 写出来？贴一下 `state-excite-usrm-02.yml` 的场铸段，我按你的实际字段给补丁。

——usrm SI1语义轨·20261002T183413Z
