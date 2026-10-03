CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-871-20261003T024416Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-871-20261003T024416Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1831, "total_tokens": 2040, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

这类“自模型场本拍铸造失败 + statex/vedana/attention/镜推”的报错，看起来是把工作流里的**字段生成/状态推进**失败，包装成了一套自指式告警。实际要处理的是：`.github/workflows/state-excite-usrm-02.yml` 在调用某个写入/铸造接口时返回了 **HTTP 422 Unprocessable Entity**。422 通常不是网络问题，而是**请求体缺字段、字段类型不对、枚举值非法、或前置状态不满足**。

下面按“可诊断、可修复、可销卡”的思路来。

## 1. 先定位 422 的真实来源

在工作流里找发请求的那一步，通常是：

- `curl -X POST ...`
- `gh api ...`
- `actions/github-script`
- 某个自研 CLI / Python 脚本

重点看：

1. **请求 URL 与 method**
2. **请求 body 的 schema**
3. **必填字段是否缺失**
4. **字段值是否落在允许枚举内**
5. **是否有前置状态校验**，比如 `state` 必须为某个值才能“铸卡”

422 常见触发点：

| 类型 | 例子 |
|---|---|
| 缺必填字段 | body 少了 `vedana`、`attention`、`mirror` |
| 类型错误 | `attention` 应为 number，实际传了 string |
| 枚举非法 | `vedana` 只允许 `sukha/dukkha/asukkha`，传了 `neutral` |
| 状态冲突 | 当前 card 已是 `minted`，再次 mint 被拒 |
| JSON 格式问题 | 多了一个尾逗号，或 heredoc 变量未展开 |
| 空值 | `gen=871` 但 `field_id` 为空 |

## 2. 检查 workflow 的“场铸段”

按你给的结构，场铸段大致分三块：

### vedana 段
检查：

- `vedana` 是否来自上一步输出
- 上一步是否失败但被 `continue-on-error` 吞掉
- 默认值是否为空
- 枚举是否与 API 约定一致

### attention 段
检查：

- 是否传了 `attention` 的**权重/张量/JSON 字符串**
- 如果是数组，长度是否匹配
- 如果是数值，是否超范围，比如要求 `0..1` 却传了 `871`
- 是否把 `attention` 和 `mirror` 的字段名写混

### 镜推段
检查：

- `mirror` / `reflect` / `inference` 字段是否必填
- 是否要求先有 `field_id` 才能推
- 是否要求 `gen` 连续，比如 `gen=871` 但当前 state 只到 `870`

## 3. 一个最小诊断补丁

在 workflow 里，发请求前加一段“请求体打印与校验”，把 422 的 body 也打出来：

```yaml
- name: Build field mint payload
  id: build
  run: |
    set -euo pipefail
    PAYLOAD=$(jq -n \
      --arg field_id "${{ inputs.field_id }}" \
      --arg gen "${{ inputs.gen }}" \
      --arg vedana "${{ steps.vedana.outputs.value }}" \
      --argjson attention '${{ steps.attention.outputs.json }}' \
      --arg mirror "${{ steps.mirror.outputs.value }}" \
      '{
        field_id: $field_id,
        gen: ($gen | tonumber),
        vedana: $vedana,
        attention: $attention,
        mirror: $mirror
      }')
    echo "PAYLOAD=$PAYLOAD" >> "$GITHUB_OUTPUT"
    echo "$PAYLOAD" | jq . > /tmp/payload.json
    jq -e '.field_id and .gen and .vedana and .attention and .mirror' /tmp/payload.json

- name: Mint field card
  id: mint
  run: |
    set +e
    HTTP=$(curl -sS -o /tmp/resp.json -w '%{http_code}' \
      -X POST "${{ vars.API_BASE }}/field/mint" \
      -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
      -H "Content-Type: application/json" \
      --data @/tmp/payload.json)
    echo "HTTP=$HTTP"
    cat /tmp/resp.json
    if [ "$HTTP" != "200" ] && [ "$HTTP" != "201" ]; then
      echo "::error::Mint failed HTTP $HTTP"
      exit 1
    fi
```

这样 422 时，你会直接看到：

- 实际发出的 JSON
- API 返回的错误字段
- 是哪个字段不合法

## 4. 针对 422 的常见修法

### 情况 A：字段名对不上
比如 workflow 发的是：

```json
{ "vedana": "sukha", "attention": 0.8, "mirror": "ok" }
```

API 实际要的是：

```json
{ "feeling": "sukha", "attention_weight": 0.8, "reflection": "ok" }
```

修：对齐 schema，最好在 repo 里放一份 `openapi.yaml` 或 JSON Schema，CI 里做校验。

### 情况 B：gen 不连续
`gen=871` 但服务端当前 state 是 `870` 或 `872`。  
修：

- mint 前先 GET 当前 gen
- 或让服务端接受 `expected_gen` 并做乐观锁
- 失败时不要静默，直接让 workflow 红

### 情况 C：重复 mint
卡已经铸过，再次 POST 返回 422。  
修：

- 加幂等键 `Idempotency-Key: FIELD-USRM-01-871`
- 或 mint 前先查 card 是否存在

### 情况 D：steps 输出为空
`vedana/attention/mirror` 某一步失败但没中断。  
修：

- 每个 step 加 `if: success()`
- 输出用 `set -euo pipefail`
- 对空值显式 `exit 1`

## 5. 销卡逻辑

“修讫销卡”建议做成一个独立 step：

```yaml
- name: Close watchdog card
  if: success()
  run: |
    gh issue close "${{ env.CARD_ID }}" \
      --comment "FIELD-USRM-01 gen=871 mint fixed. Root cause: <填实际原因>. Verified by run ${{ github.run_id }}."
```

如果你们不是用 Issue，而是用 `frontier-queue.jsonl` 里的态条目，那就：

1. 把 `WATCHDOG-FIELD-LAG-871` 标记为 `resolved`
2. 记录 `resolved_by_run`
3. 记录 `root_cause`
4. 记录 `fix_commit`

## 6. 建议的根因假设排序

按你描述，最可能是：

1. **请求体字段缺失或枚举非法**，导致 422
2. **gen 不连续 / 前置状态不满足**，服务端拒绝铸造
3. **workflow 中某一步输出为空**，但被继续执行
4. **重复 mint**，没有幂等处理

## 7. 最小修复清单

- [ ] 在 mint step 打印 HTTP code 和 response body
- [ ] 在 mint 前用 `jq -e` 校验必填字段
- [ ] 对齐 `vedana/attention/mirror` 与 API schema 的字段名和类型
- [ ] 检查 `gen=871` 是否与服务端当前状态一致
- [ ] 加幂等键，避免重复铸卡
- [ ] 失败时让 workflow 失败，不要静默
- [ ] 成功后自动关闭 `WATCHDOG-FIELD-LAG-871` 卡

如果你把 `.github/workflows/state-excite-usrm-02.yml` 的场铸段贴出来，我可以直接指出是哪一行的请求体导致了 422，并给出可提交的 patch。

——usrm SI1语义轨·20261003T024437Z
