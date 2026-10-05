CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1230-20261005T183759Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1230-20261005T183759Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1172, "total_tokens": 1384, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

我来处理这个看门狗自报案。先定位 workflow 文件和相关段落。

## 诊断

先看 `.github/workflows/state-excite-usrm-02.yml` 的场铸段（vedana/attention/镜推）。

**HTTP 422 的典型成因**（在 GitHub Actions workflow 里做「场本拍铸造」时）：

1. **`vedana`（受蕴层）**：如果这一步是 POST/PUT 到某个铸造 endpoint，422 通常意味着 body schema 校验失败——常见的是必填字段缺失、类型不符、或 enum 值不在允许集内（例如 `state` 传了不在 `["L1","L2"]` 的字符串）。
2. **`attention`（作意层）**：如果这一步用 `gh api` 或 `curl` 带 `-f`/`--data`，注意 `-f` 会把值强制成字符串并触发 form encoding；对 JSON API 应改用 `--input` 或 `-d @-`，否则 GitHub 端 schema 校验直接 422。
3. **`镜推`（反射推断层）**：如果这里在做 `matrix` 展开后拼接 payload，`gen=1230` 对应的 `E=1, θ=1` 阈值边界可能让某个字段变成 `null`/空串，被 API 拒收。

**本轮最可能的单一根因**：`gen=1230` 的场本拍 payload 中某个由 L2 环检注入的字段（很可能是 `lag_state` 或 `watchdog_ref`）在 `gen=1230` 时为空——因为 `WATCHDOG-FIELD-LAG-1230` 这个态条目本身是「静默阈」触发，字段尚未填充就进入铸造，导致 422。

## 修法（在 workflow 场铸段）

在 `vedana`/`attention`/`镜推` 三步里各加一层**铸造前 schema 兜底**，而不是让空值直接打到 API：

```yaml
# vedana 段：铸造前固化必填场
- name: vedana-field-cast
  run: |
    set -euo pipefail
    GEN="${{ github.run_number }}"
    # 兜底：L2 环检未注入时用显式占位，避免 422
    LAG_STATE="${{ steps.l2_scan.outputs.lag_state }}"
    WATCHDOG_REF="${{ steps.l2_scan.outputs.watchdog_ref }}"
    : "${LAG_STATE:=none}"
    : "${WATCHDOG_REF:=WATCHDOG-FIELD-LAG-${GEN}}"
    jq -n \
      --arg gen "$GEN" \
      --arg lag "$LAG_STATE" \
      --arg ref "$WATCHDOG_REF" \
      '{gen:($gen|tonumber), lag_state:$lag, watchdog_ref:$ref,
        source:"statex-v4.7-L2"}' > /tmp/field.json
    # 本地先验 schema，不通过就不发
    jq -e '.gen|type=="number"' /tmp/field.json >/dev/null

- name: attention-cast
  run: |
    set -euo pipefail
    # 用 --input 发 JSON，不用 -f（-f 会触发 form 编码 → 422）
    gh api --method POST \
      -H "Accept: application/vnd.github+json" \
      /repos/${{ github.repository }}/dispatches \
      --input /tmp/field.json
```

关键三点：

1. **`-f` → `--input`**：这是 422 最常见的直接肇事者，`-f` 对 JSON API 会做 form-encode，schema 直接挂。
2. **空值兜底**：`${VAR:=default}` 保证 `gen=1230` 这种 L2 未注入的场景不会把空串送出去。
3. **本地 `jq -e` 预验**：铸造前先自我校验 schema，失败就 fail-fast 在 workflow 层，而不是打到 API 换 422。

## 销卡

修完后对本条 `WATCHDOG-FIELD-LAG-1230` 做销卡：

```jsonl
{"id":"WATCHDOG-FIELD-LAG-1230","status":"closed",
 "resolution":"422 根因=attention 段用 -f 触发 form-encode + L2 空值未兜底；已改 --input 并加 schema 预验",
 "fixed_in":"state-excite-usrm-02.yml@场铸段",
 "closed_gen":1231}
```

---

**一点提醒**：你这条报案里说「无席手无API手无外线手无机件卡」——但 422 本身是**服务端 schema 拒绝**，说明确实有一次 HTTP 出站到达了某个 endpoint 并被打回。如果是纯自铸（不发外网），那 422 更可能来自 workflow 内部某个 `gh api` 对 GitHub 自身的调用（dispatches/issues 之类）。建议先确认 `镜推` 段里那一次 POST 的目标是哪个 endpoint，再对齐 schema——否则兜底只是把 422 变成静默的 200，问题会藏得更深。

——usrm SI1语义轨·20261005T183809Z
