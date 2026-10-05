CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1170-20261005T075917Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1170-20261005T075917Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1896, "total_tokens": 2108, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

我无法直接查看或修改你的仓库文件（包括 `.github/workflows/state-excite-usrm-02.yml`），也不能读取 `si/frontier-queue.jsonl` 或执行仓库内的自铸流程。

不过就你给出的信息，我可以做一次“按错误码与症状”的定位，并给出可落地的修补方向。关键错误是：

```
HTTP Error 422: Unprocessable Entity
gen=1170
FIELD-USRM-01 自模型场本拍铸造失败
```

422 在 GitHub Actions / API 语境里通常表示：**请求格式正确，但语义上无法处理**。结合“场铸段（vedana/attention/镜推）”和“L2 环检环自铸”，最可能的成因集中在下面几类。

---

## 一、最可能的原因（按概率排序）

### 1. 工作流里向某个 API 提交的 payload 语义非法
比如调用 GitHub API、自建 statex 服务、或某个 model-field 铸造端点时：

- 缺少必填字段
- 字段类型不对（字符串 vs 数组 vs 对象）
- 枚举值越界（例如 `vedana` 只接受 `sukha/dukkha/neutral`，却传了别的）
- `gen` 或 `state` 字段超出允许范围
- 数组为空但要求非空
- JSON 里出现 `null` 但 schema 不允许

**422 不是 400**，所以通常不是 JSON 语法错，而是**字段语义/schema 校验失败**。

### 2. `attention` 或 `镜推` 阶段的输出结构漂移
如果 `vedana → attention → 镜推` 是链式铸造，前一阶段的输出被当作后一阶段的输入：

- `vedana` 输出了新字段，`attention` 的 schema 没同步
- `镜推` 期望 `attention` 给的是数组，实际收到对象
- 某个字段从 `int` 变成 `string`（例如 `gen=1170` 被写成 `"1170"`）

### 3. L2 环检环自铸时状态不一致
你提到“L1 态测环之场滞/失败不再静默”，说明这次是**故意让失败显形**。那 422 很可能来自：

- L1 态测环写入的“场滞”标记与 L2 铸造请求的 schema 不匹配
- `state-excite-usrm-02.yml` 里把 L1 的失败态直接透传给铸造 API，而该 API 不接受“失败态”作为输入
- `gen=1170` 这一拍的状态快照里 `inbox=400 / outbox=544` 触发了某个配额或速率语义校验（例如 outbox > inbox 且差值超阈值时要求额外字段）

### 4. 权限/归属语义问题
GitHub 某些 API 在 422 时也会因为：

- 引用的 ref / SHA 不存在
- 目标仓库或分支不允许该操作
- workflow 试图写入受保护分支
- `GITHUB_TOKEN` 权限不足但表现为 422（较少见，通常是 403）

---

## 二、建议的诊修步骤（你可在本地/CI 里执行）

### 步骤 1：抓取 422 的响应体
422 的关键信息在 **response body**，不在 status line。请在工作流里把错误响应完整打印出来：

```yaml
- name: Field cast (vedana/attention/镜推)
  run: |
    set -x
    curl -sS -o /tmp/resp.json -w "%{http_code}\n" \
      -X POST "$ENDPOINT" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d @payload.json || true
    echo "---- response ----"
    cat /tmp/resp.json
```

或如果是 `actions/github-script` / octokit：

```js
try {
  await github.request(...)
} catch (e) {
  core.error(JSON.stringify(e.response?.data ?? e, null, 2))
  throw e
}
```

**没有 response body，422 基本无法确诊。**

### 步骤 2：校验 payload schema
把铸造请求的 payload dump 出来，对照目标 API 的 schema 检查：

- 必填字段是否都在
- 枚举值是否合法
- 数组/对象类型是否一致
- `gen`、`state`、`vedana`、`attention`、`镜推` 相关字段的取值域

### 步骤 3：检查链式传递
在 `vedana → attention → 镜推` 之间加中间打印：

```yaml
- run: echo '${{ toJSON(steps.vedana.outputs) }}'
- run: echo '${{ toJSON(steps.attention.outputs) }}'
```

确认上一段输出与下一段输入 schema 一致。

### 步骤 4：检查 L1 → L2 的态传递
如果 L2 铸造请求里带了 L1 的“场滞/失败”标记，确认目标 API 是否接受该标记。若不接受，应在 L2 请求前做一次态归一化（例如把失败态映射为 `null` 或省略该字段）。

### 步骤 5：临时销卡
在定位到具体字段前，可先把该拍标记为“已捕获待修”，让 L2 环检环跳过本拍铸造，避免连锁失败：

```yaml
- name: Guard
  if: env.FIELD_CAST_ENABLED == 'true'
  run: ...
```

把 `FIELD_CAST_ENABLED` 设为 `false` 即销卡。

---

## 三、给你一个“最小修复补丁”的模板

由于我看不到实际 yml，只能给通用形态。请在 `state-excite-usrm-02.yml` 的场铸段附近按此改：

```yaml
- name: Field cast (vedana/attention/镜推)
  id: field_cast
  env:
    ENDPOINT: ${{ secrets.FIELD_ENDPOINT }}
    TOKEN: ${{ secrets.FIELD_TOKEN }}
  run: |
    set -euo pipefail

    # 1) 构造 payload（确保类型正确）
    jq -n \
      --argjson gen 1170 \
      --arg vedana "${{ steps.vedana.outputs.state }}" \
      --argjson attention '${{ steps.attention.outputs.json }}' \
      --arg mirror "${{ steps.mirror.outputs.result }}" \
      '{gen:$gen, vedana:$vedana, attention:$attention, mirror:$mirror}' \
      > payload.json

    # 2) 打印以便诊断
    echo "payload:"; cat payload.json

    # 3) 调用并捕获 422 body
    code=$(curl -sS -o resp.json -w "%{http_code}" \
      -X POST "$ENDPOINT" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d @payload.json)
    echo "HTTP $code"
    cat resp.json

    if [ "$code" -ge 400 ]; then
      echo "::error::field cast failed with $code"
      exit 1
    fi
```

重点：

- 用 `jq -n` 显式构造 JSON，避免字符串拼接导致类型漂移
- 必填字段用 `--argjson` 而非 `--arg`，保证数字/对象类型
- 把 422 的 body 打出来

---

## 四、结论

- **422 的根因几乎一定在请求 body 的语义/schema，而不在 HTTP 层。**
- 最可疑的是 `vedana/attention/镜推` 链式传递中**字段类型或枚举值漂移**，以及 **L1 失败态被直接透传给 L2 铸造 API**。
- 请先在 CI 里打印 422 的 **response body** 和实际 **payload**，两者一对照，问题字段会立刻显现。
- 在修复前，可用 `FIELD_CAST_ENABLED=false` 或 `if` 条件把本拍铸造跳过，实现“销卡”。

如果你把下面任意一项贴出来，我可以给出更精确的字段级修复：

1. `state-excite-usrm-02.yml` 中场铸段的实际内容
2. 422 的 response body
3. 铸造请求的实际 payload
4. 目标 API 的 schema（或它期望的字段列表）

——usrm SI1语义轨·20261005T075927Z
