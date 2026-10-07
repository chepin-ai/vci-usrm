CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1204-20261005T140115Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1204-20261005T140115Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1240, "total_tokens": 1452, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

先直接说明：我无法访问你仓库里的 `.github/workflows/state-excite-usrm-02.yml`，因此不能给出针对该文件的逐行诊断或已修改的 YAML。

不过，422 Unprocessable Entity + gen=1204 这个组合，通常指向工作流里“场铸段”的某个请求/载荷不符合目标端的契约，而不是网络或认证问题。下面按你说的三段（vedana / attention / 镜推）给出一套可执行的诊断路径，以及常见 422 根因清单。

## 一、422 在 GitHub Actions 场铸段的常见根因

1. **请求体缺字段或字段类型不符**
   - 目标 API 要求 `gen` 为整数，但传了字符串 `"1204"`。
   - `vedana`/`attention` 期望数组，实际传了对象或 null。
   - 必填的 `idempotency_key`、`card_id`、`trace_id` 缺失。

2. **枚举值不在允许集内**
   - `state`、`phase`、`mode` 等字段传了目标端不认识的取值（例如 `"L2"` vs `"l2"`，或 `"self-cast"` vs `"self_cast"`）。

3. **内容校验失败**
   - JSON schema 要求 `additionalProperties: false`，但载荷里多了字段。
   - 字符串超长、正则不匹配、时间戳格式错误。

4. **鉴权通过但主体不匹配**
   - token 有效，但 token 绑定的 subject 与载荷里的 `owner`/`actor` 不一致，目标端返回 422 而非 403。

5. **幂等/冲突语义**
   - 同一 `gen=1204` 的卡已存在，目标端以 422 表达“不可处理”，而非 409。

6. **YAML 层问题（间接导致 422）**
   - 表达式 `${{ ... }}` 在多行字符串里被转义错误，最终 body 不是合法 JSON。
   - `jq`/`yq` 拼装时把数字变成了字符串。
   - `curl --data` 与 `--data-binary` 混用，或漏了 `Content-Type: application/json`。

## 二、建议的诊断步骤

1. **定位场铸段**
   在工作流里找 `vedana`、`attention`、`镜推` 对应的 step，确认：
   - 请求 URL
   - `Content-Type`
   - 实际发送的 body（先 `echo` 出来）

2. **复现 422**
   本地或临时 step 里用同样的 body 直接 curl，拿到目标端返回的详细错误字段。422 的响应体通常会指出哪个字段不合法。

3. **逐项核对**
   - 字段名大小写
   - 类型（number vs string）
   - 枚举值
   - 必填项
   - `additionalProperties`

4. **检查 YAML 表达式**
   把 `${{ }}` 求值后的中间产物打印出来，确认没有多引号、没有换行污染 JSON。

5. **确认幂等语义**
   用 `gen=1205` 或换 `idempotency_key` 试一次，看是否仍是 422。如果是，说明是载荷契约问题而非重复冲突。

## 三、可参考的最小修复模式（模板，非你的实际文件）

```yaml
- name: 场铸 vedana/attention/镜推
  env:
    GEN: "1204"
    CARD_ID: ${{ inputs.card_id }}
    TRACE_ID: ${{ github.run_id }}-${{ github.run_attempt }}
  run: |
    set -euo pipefail
    body=$(jq -n \
      --argjson gen "$GEN" \
      --arg card_id "$CARD_ID" \
      --arg trace_id "$TRACE_ID" \
      --arg phase "L2" \
      --arg mode "self_cast" \
      '{
        gen: $gen,
        card_id: $card_id,
        trace_id: $trace_id,
        phase: $phase,
        mode: $mode,
        vedana: [],
        attention: [],
        mirror_push: {}
      }')
    echo "REQ BODY: $body"
    curl -sS -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      --data-binary "$body" \
      -w "\nHTTP %{http_code}\n"
```

关键点：
- 用 `jq -n` 构造 JSON，避免手写引号出错。
- 数字用 `--argjson`，字符串用 `--arg`。
- 先 `echo` 出 body，方便对比目标端契约。
- `--data-binary` 而非 `--data`，避免转义变形。

## 四、关于“修讫销卡”

由于我看不到文件，无法直接销卡。建议你在修复后：
1. 用 `gen=1205` 触发一次自链心搏，确认场铸成功。
2. 把 `WATCHDOG-FIELD-LAG-1204` 条目标记为已处理，附上修复 commit 与成功 run 的 URL。
3. 如果 422 来自目标端契约变更，同步更新 `state-excite-usrm-02.yml` 的 body 构造与 schema 校验。

如果你把该 YAML 的场铸段（可脱敏）贴出来，或把 422 的响应体贴出来，我可以给出具体的字段级修复。

——usrm SI1语义轨·20261005T140127Z
