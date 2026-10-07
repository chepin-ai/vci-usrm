CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-843-20261002T214523Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-843-20261002T214523Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1756, "total_tokens": 1965, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

你这条“自报案”信息量很大，但直接可以落到一个具体故障：  
**GitHub Actions 工作流 `state-excite-usrm-02.yml` 在 `gen=843` 的场铸阶段失败，HTTP 422 Unprocessable Entity。**

下面按“可诊断、可修复、可销卡”的方式来收束。

---

## 1. 先定性：422 不是网络抖动，通常是“请求体/字段/语义不合法”

在 GitHub Actions / API 语境里，`422 Unprocessable Entity` 一般不是 401/403 那种权限问题，也不是 500 服务端崩了，而是：

- 请求格式是 JSON，但**字段类型/枚举值/必填项/嵌套结构**不符合接收端 schema；
- 或者接收端是 GitHub API 之外的**自建铸造服务**，它对 `vedana / attention / 镜推` 这些字段有额外约束；
- 或者 payload 里带了 `null`、空字符串、NaN、超出范围的数值、不支持的 enum；
- 或者 Content-Type 不对，导致服务端解析后校验失败；
- 或者 GitHub API 本身：比如 `workflow_dispatch` 输入、`repository_dispatch` payload、`issues.create` 的 label 不存在等。

**关键点：422 表示“服务端理解你的请求，但拒绝处理”。**  
所以要看的是：**场铸段到底发了什么 payload，接收端 schema 是什么。**

---

## 2. 定位到 `.github/workflows/state-excite-usrm-02.yml` 场铸段

你给的线索是：场铸段包含 `vedana / attention / 镜推`。  
这很像一个自定义的“态场铸造”步骤，可能做了这些事：

1. 从 `si/frontier-queue.jsonl` 或 `STATE-EXCITE` 轨读取态条目；
2. 组装一个 JSON：
   - `vedana`：受/感，可能是数值、枚举或对象；
   - `attention`：注意，可能是权重、mask、数组；
   - `镜推`：可能是镜像推理/反射推演，可能是嵌套结构；
3. 调用某个 HTTP 端点进行“自铸”；
4. 如果返回非 2xx，就报错，并且这次没有静默，所以看门狗自报案。

**建议直接看 job log 里 422 响应体。**  
GitHub Actions 里通常会有类似：

```text
HTTP Error 422: Unprocessable Entity
Response: {"errors":[{"resource":"...","field":"...","code":"..."}]}
```

如果日志只打了 `HTTP Error 422`，那说明场铸脚本把 response body 吞了。  
**这是第一个要修的点：错误处理必须打印 response body。**

---

## 3. 最可能的 4 类根因

### A. `vedana` 字段类型/枚举不匹配
比如接收端要：

```json
{"vedana": {"type": "sukha", "intensity": 0.7}}
```

但你发了：

```json
{"vedana": "sukha"}
```

或者反过来。  
422 常见报错：`Invalid type for vedana`、`vedana must be one of [...]`。

### B. `attention` 形状不对
如果 `attention` 是数组，接收端可能要求：

- 长度固定；
- 元素是 float；
- 总和为 1；
- 不能有负数；
- 不能有 `NaN` / `Infinity`。

Python 里 `json.dumps` 默认会把 `NaN` 写成 `NaN`，这不是合法 JSON，很多服务端会 422。

### C. `镜推` 字段名或结构问题
中文键名在某些服务端可能被拒绝，或者接收端实际要的是 `mirror_inference` / `mirror_push`。  
也可能是嵌套层级不对：

```json
{"镜推": {"depth": 3, "trace": [...]}}
```

但服务端要的是：

```json
{"mirror": {"depth": 3, "trace": [...]}}
```

### D. GitHub API 侧 422
如果场铸段最后是调 GitHub API 创建 issue/comment/dispatch，那么 422 可能是：

- label 不存在；
- assignee 不是协作者；
- `workflow_dispatch` 的 input 不在 `inputs` 定义里；
- `repository_dispatch` 的 `event_type` 不合法；
- issue body 太长或格式不对。

---

## 4. 直接可执行的修复清单

### 4.1 在 workflow 里加“422 响应体打印”
找到场铸段调用 HTTP 的地方，改成：

```yaml
- name: Field casting
  run: |
    python scripts/field_cast.py
```

在 `field_cast.py` 里：

```python
import requests, json, sys

resp = requests.post(url, json=payload, headers=headers, timeout=30)
if resp.status_code >= 400:
    print(f"HTTP {resp.status_code}", file=sys.stderr)
    print("Request payload:", json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    print("Response body:", resp.text, file=sys.stderr)
    resp.raise_for_status()
```

这样下一次失败就能看到到底哪个字段不合法。

### 4.2 校验 payload 是否合法 JSON
如果是 Python 生成 payload，确保：

```python
json.dumps(payload, allow_nan=False)
```

不要用 `NaN`。  
如果是 JS：

```js
JSON.stringify(payload) // 会抛错如果含 BigInt，NaN 会变 null
```

### 4.3 对齐接收端 schema
如果接收端是你自己的服务，找它的 Pydantic / JSON Schema / OpenAPI 定义。  
重点检查：

- `vedana`：类型、enum、必填；
- `attention`：array 长度、元素类型、范围；
- `镜推`：字段名、嵌套结构、是否允许中文 key。

### 4.4 加一个“干跑/预检”步骤
在真正 POST 之前，先本地校验：

```yaml
- name: Validate payload
  run: |
    python scripts/validate_payload.py
```

`validate_payload.py` 用 `jsonschema` 或 Pydantic 校验，失败就不发请求。

### 4.5 如果是 GitHub API 422
检查：

- `GITHUB_TOKEN` 权限；
- label 是否已存在；
- `workflow_dispatch` inputs 是否在 `on.workflow_dispatch.inputs` 里声明；
- `repository_dispatch.event_type` 是否只含字母数字和 `-`、`_`。

---

## 5. 销卡建议

你可以这样销 `WATCHDOG-FIELD-LAG-843`：

1. **确认根因**：从 422 response body 里拿到具体字段错误；
2. **修 workflow**：改 payload 生成逻辑，或加 schema 校验；
3. **加防静默**：场铸失败必须打印 request/response body，并写入 `si/frontier-queue.jsonl` 或 outbox；
4. **重跑一次 gen=844 或手动 dispatch**，确认铸造成功；
5. **把该态条目标记为 resolved**，并在 `outbox` 里写一条销卡记录。

---

## 6. 如果你要我直接改 YAML

把你现在的 `state-excite-usrm-02.yml` 场铸段贴出来，或者至少贴：

- 触发方式（`workflow_dispatch` / `schedule` / `repository_dispatch`）；
- 场铸那一步的 `run` 或 `uses`；
- 发请求的 URL 和 payload 生成代码；
- 422 的完整 response body（如果日志里有）。

我可以直接给你一版可提交的 YAML 补丁，把 422 诊断、schema 校验、销卡逻辑都补上。

——usrm SI1语义轨·20261002T214532Z
