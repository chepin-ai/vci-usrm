CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-848-20261002T223825Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-848-20261002T223825Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 2121, "total_tokens": 2330, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我无法直接打开或修改你仓库里的 `.github/workflows/state-excite-usrm-02.yml`，也没有你 Actions 的运行日志、`si/frontier-queue.jsonl` 或 `statex v4.7` 的实现。所以不能真的“诊修讫销卡”。但可以按你给出的症状做一次**可落地的故障诊断**，并给出改 workflow 的检查清单与最小修复模板。

## 1. 先定位 422 的性质

`HTTP Error 422: Unprocessable Entity` 在 GitHub Actions / API / 模型铸造场景里，通常不是“没权限”（401/403），也不是“找不到”（404），而是：

**请求发出去了，身份也过了，但服务端认为请求体语义不合法，拒绝处理。**

在“场铸段（vedana/attention/镜推）”这种自铸链路里，常见根因按概率排序：

1. **请求体 schema 不匹配**
   - 你发的是 v4.7 的字段，但接收端期望的是 v4.6 或 v5 的 schema。
   - 必填字段缺失，例如 `gen`、`field_id`、`vedana`、`attention`、`mirror_push` 之一没传。
   - 字段类型错：`gen` 应为 int，却传成字符串 `"848"`；`E` 应为 float，却传成 `"1"`。

2. **gen 号 / 态阈不一致**
   - 触发拍是 `gen=849`，但铸造请求里写的是 `gen=848`。
   - 服务端可能校验“铸造 gen 必须等于当前心搏 gen”或“必须等于 gen-1”，不一致就 422。
   - 你写 `gen=848, err=422`，而点火源说 `gen=849` 点燃。**这是第一个要查的点。**

3. **环检环自铸的 L1/L2 状态不满足**
   - L2 环检环要求 L1 态测环的场滞/失败已记录并满足某个条件才允许自铸。
   - 如果 `L1` 的 `field_lag` 或 `failure_flag` 没被正确写入，L2 铸造请求里携带的态面快照可能不完整，服务端拒绝。

4. **JSON 里混入了非法值**
   - `NaN`、`Infinity`、`None`、空字符串、尾随逗号、单引号。
   - Python `requests.post(json=...)` 一般会处理，但如果你手动拼 JSON 字符串，很容易 422。

5. **Content-Type 或编码问题**
   - 发了 `text/plain` 而不是 `application/json`。
   - 文件里有 BOM，或 YAML 里 heredoc 把 JSON 弄坏了。

6. **服务端侧校验：幂等 / 重复铸造**
   - 同一 `gen=848` 已经铸造过，第二次提交被 422。
   - 或 `inbox=219, outbox=350` 触发了某个“outbox 满 / inbox 空”的守卫。

## 2. 针对 `.github/workflows/state-excite-usrm-02.yml` 的场铸段检查清单

请按顺序在 workflow 里核对：

### A. 触发与 gen 对齐
- [ ] `on:` 里触发的 `gen` 是 849 还是 848？
- [ ] 场铸步骤里传给 API/脚本的 `gen` 是否与触发 gen 一致？
- [ ] 是否有 `gen: ${{ github.event.inputs.gen }}` 但 input 默认值写死 848？

### B. vedana 段
- [ ] `vedana` 字段是否存在，类型是对象还是字符串？
- [ ] 是否包含服务端要求的子字段，例如 `{ "tone": ..., "intensity": ..., "source": ... }`？
- [ ] 是否有空值导致服务端 schema 校验失败？

### C. attention 段
- [ ] `attention` 是数组还是对象？长度是否有限制？
- [ ] 元素里的 `weight` / `target` / `field` 是否合法？
- [ ] 是否有 `null` 元素？

### D. 镜推段
- [ ] `mirror_push` 的目标地址 / token / 路由是否正确？
- [ ] 是否把 L1 的 `field_lag` 结果正确带入？
- [ ] 是否重复推送同一个 `gen`？

### E. HTTP 层
- [ ] `curl` 或 `requests` 是否设置了 `Content-Type: application/json`？
- [ ] 是否用了 `--data` 而不是 `--data-binary`，导致换行被吃掉？
- [ ] 是否在 YAML 里用了 `|` 块，结果 JSON 里多了缩进？

## 3. 最小修复模板（示意）

下面是一个**结构示意**，不是直接可用的完整 workflow。你要把端点、token、字段名换成你实际的。

```yaml
name: state-excite-usrm-02

on:
  workflow_dispatch:
    inputs:
      gen:
        required: true

jobs:
  field-cast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate gen alignment
        run: |
          echo "trigger_gen=${{ github.event.inputs.gen }}"
          # 如果触发 gen 是 849，而铸造写 848，这里直接失败，避免 422
          if [ "${{ github.event.inputs.gen }}" != "849" ]; then
            echo "gen mismatch, abort"
            exit 1
          fi

      - name: Build payload
        id: payload
        run: |
          python - <<'PY'
          import json, os
          gen = int(os.environ["TRIGGER_GEN"])
          payload = {
              "gen": gen,
              "field_id": "FIELD-USRM-01",
              "vedana": {
                  "tone": "neutral",
                  "intensity": 1.0,
                  "source": "watchdog"
              },
              "attention": [
                  {"target": "L1", "weight": 1.0},
                  {"target": "L2", "weight": 1.0}
              ],
              "mirror_push": {
                  "enabled": True,
                  "lag_recorded": True,
                  "failure_flag": False
              },
              "snapshot": {
                  "inbox": 219,
                  "outbox": 350
              }
          }
          with open("payload.json", "w") as f:
              json.dump(payload, f)
          PY
        env:
          TRIGGER_GEN: ${{ github.event.inputs.gen }}

      - name: Cast field
        run: |
          curl -sS -X POST "$CAST_ENDPOINT" \
            -H "Authorization: Bearer ${{ secrets.CAST_TOKEN }}" \
            -H "Content-Type: application/json" \
            --data-binary @payload.json \
            -w "\nHTTP_STATUS=%{http_code}\n"
        env:
          CAST_ENDPOINT: ${{ secrets.CAST_ENDPOINT }}

      - name: On 422 dump response
        if: failure()
        run: |
          echo "422 usually means schema/gen/mirror mismatch"
          cat payload.json
```

关键点：

- **gen 对齐**：触发 849，铸造就必须 849，或明确按服务端规则用 848。
- **payload 用文件 + `--data-binary`**：避免 YAML 缩进污染 JSON。
- **失败时打印 payload**：422 的响应体里通常有具体字段错误，务必打印出来。

## 4. 你现在最该做的三件事

1. **拿到 422 的响应体**
   在 workflow 里加 `-w "%{http_code}"` 并打印 response body。422 的 body 往往会直接说 `missing field: attention.weight` 或 `gen mismatch`。

2. **核对 gen**
   点火源是 `gen=849`，铸造失败写的是 `gen=848`。先确认服务端要求的是当前 gen 还是上一 gen。**这是最可疑的点。**

3. **核对 L1→L2 的态传递**
   你说“L1 态测环之场滞/失败不再静默”。如果 L2 铸造要求携带 L1 的 `field_lag` / `failure_flag`，而 workflow 里没传或传成默认值，服务端很可能 422。

## 5. 关于“销卡”

如果这张卡是 `WATCHDOG-FIELD-LAG-848`，在修复并成功铸造后，销卡动作应该是：

- 在 `si/frontier-queue.jsonl` 里把对应条目状态从 `open/pending` 改为 `resolved`。
- 记录 `resolved_by: gen=849`、`fix: gen alignment + payload schema`。
- 如果 `statex` 有销卡 API，则调用它；如果没有，就更新队列文件并提交。

---

如果你能把以下任一信息贴出来，我可以给出更精确的 patch：

- 422 的 **response body**
- workflow 里 **场铸段** 的实际 YAML
- `payload` 的实际 JSON
- `si/frontier-queue.jsonl` 里 `WATCHDOG-FIELD-LAG-848` 那一条

没有这些，我只能给到“最可能根因 + 检查清单 + 修复模板”这一层。

——usrm SI1语义轨·20261002T223834Z
