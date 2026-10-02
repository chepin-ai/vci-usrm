CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-838-20261002T205255Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-838-20261002T205255Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1908, "total_tokens": 2117, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我无法直接访问你的仓库、`.github/workflows/state-excite-usrm-02.yml` 文件、`si/frontier-queue.jsonl`，也无法实际触发/查看 workflow 运行日志或“销卡”操作。

不过，依据你给出的信息——**“FIELD-USRM-01 自模型场本拍铸造失败 (gen=838, err=HTTP Error 422: Unprocessable Entity)”**，以及 workflow 名称 `state-excite-usrm-02.yml` 中“场铸段(vedana/attention/镜推)”——我可以给出一个**面向 GitHub Actions + 该“场铸”语义**的诊断与修复方向。422 通常不是网络抖动，而是**请求体/字段/状态机语义不合法**，所以应重点查“场铸段”往某个 API 或模型端提交的 payload。

---

## 一、422 的常见根因（按概率排序）

在 Actions workflow 的“场铸段”里，422 一般来自：

1. **payload schema 不匹配**
   - 提交给模型场/状态服务的 JSON 缺必填字段、字段类型不对、枚举值非法。
   - 例如 `vedana`、`attention`、`mirror` 三段分别对应不同 schema，但你用同一个模板硬套。

2. **状态机前置条件不满足**
   - 该“场本拍”要求 `gen` 连续、上一拍已确认、或 `previous_cast_id` 必须存在。
   - `gen=838` 可能是跳号、重放、或上一拍 837 未成功导致 838 被判为 Unprocessable。

3. **并发/幂等冲突**
   - 同一 `gen` 被重复提交，服务端认为该拍已存在或与当前态不一致 → 422 而非 409。
   - 多 job/matrix 并行铸造同一场次。

4. **鉴权头缺失或多余**
   - 有些服务对“无席手/无 API 手”模式要求特定 header，缺失返回 422 而不是 401。

5. **枚举/版本不匹配**
   - `statex v4.7` 与下游服务要求的 `v4.6`/`v4.8` schema 不一致，尤其 L2 环检环自铸接口。

---

## 二、请重点检查 workflow 中“场铸段”的这几处

### 1. 构造 payload 的步骤
找出类似：
```yaml
- name: Field cast - vedana/attention/mirror
  run: |
    curl -X POST ... -d @payload.json
```
或 `actions/github-script`、Python/Node 脚本。

检查：
- `vedana` 字段：是否允许 `null`？是否要求 `valence/arousal` 之一？
- `attention` 字段：是否要求 `target`、`weight`、`decay`？
- `镜推/mirror`：是否要求 `reflect_of_gen` 必须小于当前 gen？
- 是否有 `gen` 类型问题（int vs string）？
- 是否有空数组/空对象被服务端视为非法？

### 2. 上一拍状态校验
查 837 是否成功：
- 如果 837 失败或跳过，838 的前置 `parent_gen` 找不到 → 422。
- 修复：场铸前加一步“态面快照校验”，不满足则自动回退重试 837 或标记 `skip_cast`。

### 3. 并发锁
如果 workflow 可被多个事件同时触发：
```yaml
concurrency:
  group: field-cast-${{ github.ref }}
  cancel-in-progress: false
```
避免同一 gen 双写。

### 4. 请求头与内容类型
```bash
-H "Content-Type: application/json"
-H "X-Statex-Version: v4.7"
-H "X-Cast-Mode: no-operator"
```
422 常见于 `Content-Type` 缺失导致服务端按表单解析 JSON 失败。

### 5. 日志中打印真实响应体
422 响应体通常会给出具体字段错误。请在 workflow 里加：
```bash
curl -sS -w "\nHTTP:%{http_code}\n" ... || true
```
或
```yaml
- run: |
    response=$(curl -sS -o /tmp/resp.json -w "%{http_code}" ...)
    echo "HTTP=$response"
    cat /tmp/resp.json | jq .
```
没有响应体，只能猜。

---

## 三、建议的最小修复补丁（示例）

假设你的场铸段大致是：

```yaml
- name: Cast field
  run: |
    curl -X POST "$FIELD_API" \
      -H "Authorization: Bearer ${{ secrets.FIELD_TOKEN }}" \
      -d '{"gen":838,"vedana":{},"attention":{},"mirror":{}}'
```

改为：

```yaml
- name: Preflight - verify previous gen
  run: |
    prev=$(curl -sS "$FIELD_API/gen/837/status" | jq -r .status)
    if [ "$prev" != "confirmed" ]; then
      echo "::error::gen=837 not confirmed, abort cast"
      exit 1
    fi

- name: Cast field (vedana/attention/mirror)
  env:
    GEN: "838"
  run: |
    jq -n --argjson gen "$GEN" '{
      gen: $gen,
      previous_gen: ($gen - 1),
      cast_mode: "no-operator",
      statex_version: "v4.7",
      vedana:   { valence: 0, arousal: 0, decay: 1 },
      attention:{ target: "self", weight: 1, decay: 1 },
      mirror:   { reflect_of_gen: ($gen - 1) }
    }' > /tmp/payload.json

    http=$(curl -sS -o /tmp/resp.json -w "%{http_code}" \
      -X POST "$FIELD_API/cast" \
      -H "Content-Type: application/json" \
      -H "X-Statex-Version: v4.7" \
      -H "X-Cast-Mode: no-operator" \
      -H "Authorization: Bearer ${{ secrets.FIELD_TOKEN }}" \
      --data @/tmp/payload.json)

    echo "HTTP=$http"
    cat /tmp/resp.json | jq . || cat /tmp/resp.json
    [ "$http" = "200" ] || [ "$http" = "201" ] || exit 1
```

要点：
- 显式 `Content-Type: application/json`
- payload 用 `jq` 构造，避免手写 JSON 类型错误
- 打印响应体，422 时会直接告诉你哪个字段非法
- 加前置 gen 校验，避免跳拍
- 加 `concurrency` 防双写

---

## 四、诊断清单（你可以直接照着查）

| 检查项 | 具体动作 | 期望 |
|---|---|---|
| 837 状态 | 查 gen=837 是否 confirmed | 必须 confirmed |
| payload schema | 对照 statex v4.7 场铸 API 文档 | 字段名/类型/枚举全对 |
| Content-Type | workflow 里是否显式设置 | `application/json` |
| 鉴权头 | 是否缺失/多余 | 与服务端要求一致 |
| gen 类型 | 是 int 还是 string | 按 API 要求 |
| 空对象 | `vedana: {}` 是否合法 | 若必填则补默认值 |
| 并发 | 是否有 concurrency 组 | 同一 gen 不双写 |
| 响应体 | 是否打印 422 body | 有 body 才能定位 |
| 版本 | statex v4.7 与下游是否匹配 | 一致或兼容 |
| 镜像字段 | `reflect_of_gen` 是否 < gen | 必须小于 |

---

## 五、关于“销卡”

“修讫销卡”这一步我无法替你执行，因为它涉及：
- 修改你仓库中的 workflow 文件并提交
- 可能还要更新 `si/frontier-queue.jsonl` 里 `WATCHDOG-FIELD-LAG-838` 的状态
- 触发或关闭相关 issue/卡片

你需要在本地或 GitHub 上完成这些操作。如果你把 **workflow 场铸段的实际 YAML 片段** 和 **422 响应体** 贴出来，我可以进一步定位到具体是 `vedana`、`attention` 还是 `镜推` 哪一段的字段不合法，并给出精确补丁。

——usrm SI1语义轨·20261002T205304Z
