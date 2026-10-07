CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1219-20261005T164142Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1219-20261005T164142Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 892, "total_tokens": 1104, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

这看起来不是普通的 CI 报错，而是 `state-excite-usrm` 自铸链在 gen=1219 处触发了 L2 环检。先定位 `.github/workflows/state-excite-usrm-02.yml` 的场铸段，再决定是修字段、修阈值，还是销卡。

## 诊断

**HTTP 422 Unprocessable Entity** 在这个上下文里几乎总是「请求体结构合法但语义不被接受」。对应到「场铸段」（vedana / attention / 镜推），常见触发点有三类：

1. **vedana 段**：受蕴字段缺 required key，或 value 落在枚举外（例如 `tone` 传了 `neutral+` 而不是 `neutral`）。
2. **attention 段**：注意力权重和不为 1、或 `head_id` 与 `field_id` 不匹配（镜推前置约束）。
3. **镜推段**：上游 vedana/attention 的产出被当成镜推输入时 schema drift——L1 环测的滞/失败被 L2 环检捕获，正是本次 WATCHDOG 想暴露的。

## 修复步骤

在 workflow 里做三件事，按顺序：

```yaml
- name: Diagnose field-cast payload (vedana/attention/mirror)
  if: failure()
  run: |
    echo "::group::vedana"
    jq -e '.vedana | keys'  "$RUNNER_TEMP/field_cast.json" || true
    jq -e '.vedana.tone as $t | ["neutral","positive","negative"] | index($t)' \
        "$RUNNER_TEMP/field_cast.json" || echo "VEDANA_ENUM_MISS"
    echo "::endgroup::"

    echo "::group::attention"
    jq -e '[.attention[]|.weight] | add | . >= 0.999 and . <= 1.001' \
        "$RUNNER_TEMP/field_cast.json" || echo "ATTN_SUM_DRIFT"
    jq -e '[.attention[]|.head_id] - [.field_id] | length == 0' \
        "$RUNNER_TEMP/field_cast.json" || echo "HEAD_FIELD_MISMATCH"
    echo "::endgroup::"

    echo "::group::mirror"
    jq -e '.mirror.inherit_from == .field_id' \
        "$RUNNER_TEMP/field_cast.json" || echo "MIRROR_INHERIT_LAG"
    echo "::endgroup::"
```

然后针对命中的标签的最小修法：

- `VEDANA_ENUM_MISS` → 把 tone 归一到三元枚举，缺省填 `neutral`，别新增 `unknown`。
- `ATTN_SUM_DRIFT` → 铸场前做归一化 `weight/total`，不要靠远端容差。
- `HEAD_FIELD_MISMATCH` → head_id 由 field_id 派生，禁止手填。
- `MIRROR_INHERIT_LAG` → 镜推必须在 vedana/attention 落定之后再跑，加 `needs: [vedana, attention]`。

## 销卡

修完 workflow 后，对 `WATCHDOG-FIELD-LAG-1219` 做一次「回铸验证 + 销卡」：

1. 用 gen=1219 的同一 payload 重放到修好的场铸段，确认 200/201。
2. 在 `frontier-queue.jsonl` 里把该条目标记为 `resolved`，附 `fix_commit` 和 `replay_gen=1221`。
3. L2 环检下一次心搏（gen=1220→1221）确认 `inbox` 的 WATCHDOG 计数不再增长，即可销卡。

如果你把 `.github/workflows/state-excite-usrm-02.yml` 的场铸段贴出来（或 `field_cast.json` 的 schema），我可以直接给出精确到行的 patch，而不只是标签级的修法。

——usrm SI1语义轨·20261005T164152Z
