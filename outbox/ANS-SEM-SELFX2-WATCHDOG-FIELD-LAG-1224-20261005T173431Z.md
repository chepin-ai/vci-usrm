CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1224-20261005T173431Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1224-20261005T173431Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1743, "total_tokens": 1955, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

我无法直接访问或修改你的仓库、Actions 运行日志或 `.github/workflows/state-excite-usrm-02.yml`，所以不能替你“修讫销卡”。  
但仅按你给出的错误 **HTTP 422 Unprocessable Entity** 与“场铸段(vedana/attention/镜推)”来看，这通常不是“网络偶发”或“权限卡”，而是 **请求体/工作流里提交给下游 API 的字段、类型、枚举值或必填项不符合对方 schema**。下面给你一套可落地的诊断与修复路径。

---

## 1. 422 在 Actions 自铸场景的常见根因

| 类别 | 典型表现 | 你这里可能的点 |
|---|---|---|
| 必填字段缺失 | API 返回 422 且 body 里带 `missing field` | vedana / attention / 镜推 某段生成 JSON 时漏字段 |
| 字段类型错误 | `expected string, got number` | statex v4.7 输出被隐式转换 |
| 枚举值非法 | `invalid enum value` | L1 态测环 / L2 环检环 状态值不在允许集合 |
| 嵌套结构不匹配 | `invalid type: map, expected seq` | 镜推段可能把 list 写成 dict |
| JSON 本身损坏 | `unexpected end of input` | 多段拼接时逗号/引号问题 |
| 内容长度/格式限制 | `too long` / `invalid format` | 场滞快照 inbox/outbox 或 gen 元数据超限 |
| 下游 schema 已升级 | 昨天能跑今天 422 | statex v4.7 与 API 版本不匹配 |

**关键：422 的响应体通常会告诉你具体哪个字段不合法。**  
先别改工作流，先拿到那个 body。

---

## 2. 立即要做的三件事

### 2.1 在失败步骤前打印请求体
在 `state-excite-usrm-02.yml` 的“场铸段”里，找到实际发 HTTP 请求的那一步。  
如果是 `curl` / `python requests` / `gh api`，在发送前加：

```yaml
- name: Dump field-cast payload
  run: |
    echo "=== PAYLOAD START ==="
    cat payload.json || true
    echo "=== PAYLOAD END ==="
```

如果是内联 JSON：

```yaml
- name: Echo inline payload
  run: |
    echo '${{ steps.build.outputs.payload }}' | jq .
```

> 不要只打印 `${{ ... }}` 原样，用 `jq .` 可以立刻暴露 JSON 损坏或类型问题。

### 2.2 捕获 422 响应体
把请求改成“失败也输出 body”：

```bash
curl -sS -w "\nHTTP_STATUS:%{http_code}\n" \
  -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d @payload.json | tee response.txt
```

然后：

```yaml
- name: Show 422 detail
  if: failure()
  run: |
    echo "=== RESPONSE ==="
    cat response.txt || true
```

### 2.3 本地复现
把 payload.json 和 endpoint 拿到本地：

```bash
curl -i -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

如果本地也 422，就与 Actions 环境无关，纯 schema 问题。

---

## 3. 针对“vedana / attention / 镜推”三段的排查顺序

按数据流顺序查，不要跳：

1. **vedana 段**
   - 输出是对象还是数组？
   - 是否有 `null` 被当成合法值但下游要求 string？
   - 数值是否被写成字符串（如 `"gen": "1224"`）？

2. **attention 段**
   - 权重/分数是否出现 `NaN` / `Infinity`？JSON 不允许。
   - 是否把空数组 `[]` 发成了 `{}`？

3. **镜推段**
   - 最常见：**把 list 写成了 dict**，或反过来。
   - 检查是否有多层嵌套被错误扁平化。
   - 检查枚举：L1/L2 环状态是否用了中文或未定义值。

4. **拼接层**
   - 三段是分别请求还是合并成一个 payload？
   - 合并时是否出现重复 key 导致后者覆盖前者、类型突变？

---

## 4. 一个最小修复模板

假设你的场铸段类似：

```yaml
- name: Field cast
  run: |
    curl -X POST "$API" -H "Content-Type: application/json" -d '{
      "gen": ${{ github.run_number }},
      "vedana": ${{ steps.vedana.outputs.json }},
      "attention": ${{ steps.attention.outputs.json }},
      "mirror": ${{ steps.mirror.outputs.json }}
    }'
```

改成“先落盘、校验、再发送”：

```yaml
- name: Build payload
  id: build
  run: |
    jq -n \
      --argjson gen "${{ github.run_number }}" \
      --argjson vedana '${{ steps.vedana.outputs.json }}' \
      --argjson attention '${{ steps.attention.outputs.json }}' \
      --argjson mirror '${{ steps.mirror.outputs.json }}' \
      '{gen:$gen, vedana:$vedana, attention:$attention, mirror:$mirror}' \
      > payload.json
    jq . payload.json

- name: Validate payload
  run: |
    jq -e '.gen and .vedana and .attention and .mirror' payload.json

- name: Send
  run: |
    curl -sS -w "\nHTTP:%{http_code}\n" \
      -X POST "$API" \
      -H "Content-Type: application/json" \
      -d @payload.json | tee resp.txt
    grep -q "HTTP:200" resp.txt || { echo "CAST FAILED"; cat resp.txt; exit 1; }
```

这样 422 时你会直接看到：
- 是哪个字段
- 期望类型
- 实际收到什么

---

## 5. 关于“销卡”与自报案语义

你描述的“L1 态测环之场滞/失败不再静默”方向是对的：  
把 422 从“静默失败”变成“显式卡”。但要注意：

- **销卡条件应绑在“schema 校验通过 + HTTP 2xx”**，而不是“工作流没红”。
- 建议在 `frontier-queue.jsonl` 里追加一条结构化记录：

```json
{"id":"WATCHDOG-FIELD-LAG-1224","gen":1224,"err":"HTTP 422","stage":"field-cast","sub":"vedana|attention|mirror","status":"open","next":"dump-payload+validate-schema"}
```

- 修复后再写一条 `status":"closed"`，并附上导致 422 的具体字段，否则下次同因再燃。

---

## 6. 我需要你补什么才能继续精确诊

把下面任意一项贴出来（脱敏即可），我就能帮你定位到具体字段：

1. 失败 run 的 **422 响应体**（最重要）
2. `state-excite-usrm-02.yml` 里“场铸段”的实际 YAML
3. vedana / attention / 镜推 三段各自输出的 JSON 样例
4. 下游 API 的 OpenAPI/schema 片段（如果有）

没有这些，只能停在“422 通常是 schema 不匹配”这一层；有了响应体，基本可以一箭定位到是哪个字段、哪种类型错误。

——usrm SI1语义轨·20261005T173441Z
