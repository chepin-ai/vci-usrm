CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1202-20261005T133847Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1202-20261005T133847Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1545, "total_tokens": 1757, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

你这条“自报案”里，真正可诊断的硬信息只有一句：

> `FIELD-USRM-01` 自模型场本拍铸造失败，`gen=1202`，`err=HTTP Error 422: Unprocessable Entity`，发生在 `.github/workflows/state-excite-usrm-02.yml` 的场铸段（vedana/attention/镜推）。

但你没有把 **该 workflow 文件内容**、**失败 step 的日志**、**请求体/响应体** 贴出来。没有这些，我不能假装能“诊修讫销卡”。下面按可操作方式给出诊断与修复路径。

---

## 1. 422 在这个语境下的含义

`422 Unprocessable Entity` 不是网络层错误，而是：

> 请求已经到达服务端，服务端也理解请求方法/URL，但**请求体语义不合法**，拒绝处理。

在场铸段（vedana/attention/镜推）里，最常见根因是：

| 类别 | 具体表现 |
|---|---|
| 字段缺失 | 必填字段如 `gen`、`state`、`vedana`、`attention`、`mirror` 未传 |
| 字段类型错 | 应为 int/float 传成 string，或应为 array 传成 object |
| 枚举越界 | `vedana` 只允许某些值，传了未定义态 |
| 结构不匹配 | 镜推段期望 `{"mirror": {...}}`，实际传了扁平字段 |
| 版本不匹配 | statex v4.7 的 schema 与 workflow 里写的 payload 不一致 |
| 空值/NaN | JSON 里出现 `NaN`、`Infinity`、`null` 到必填位 |
| 时间/gen 约束 | `gen=1202` 与期望的 `gen=1203` 或单调递增约束冲突 |

你提到“L1 态测环之场滞/失败不再静默”，说明这次是**主动抛错**，不是超时。所以优先查 **payload schema**，不是查网络。

---

## 2. 需要你补的最小诊断集

请贴出或确认以下四项，否则只能猜：

1. `.github/workflows/state-excite-usrm-02.yml` 中“场铸段”的 step 原文（可脱敏 token）。
2. 该 step 实际发出的请求体（JSON）。
3. 服务端 422 响应体（通常含 `detail` 或 `errors` 字段，会直接指出哪个字段不合法）。
4. `si/frontier-queue.jsonl` 中 `WATCHDOG-FIELD-LAG-1202` 那条的完整态条目。

其中 **第 3 项最关键**。422 的响应体一般长这样：

```json
{
  "detail": [
    {
      "loc": ["body", "vedana"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

`loc` 直接告诉你哪个字段错了。没有它，等于闭眼修。

---

## 3. 高频修法（按可能性排序）

### 修法 A：补必填字段
如果 422 说 `field required`，在场铸段 payload 构造处补：

```yaml
- name: field-cast
  run: |
    python - <<'PY'
    import json, os, requests
    payload = {
        "gen": int(os.environ["GEN"]),
        "state": os.environ["STATE"],
        "vedana": os.environ.get("VEDANA", "neutral"),
        "attention": float(os.environ.get("ATTENTION", "1.0")),
        "mirror": json.loads(os.environ.get("MIRROR", "{}")),
    }
    r = requests.post(os.environ["FIELD_ENDPOINT"], json=payload, timeout=30)
    if r.status_code == 422:
        print("422 body:", r.text)
        raise SystemExit(1)
    r.raise_for_status()
    PY
```

关键是 **422 时打印 `r.text`**，否则永远看不到 `loc`。

### 修法 B：类型强转
YAML/GitHub Actions 里 env 全是字符串。`gen`、`attention` 常被当成 string 发出去，服务端 schema 要 int/float，就 422。上面 `int()`、`float()` 就是干这个。

### 修法 C：枚举对齐
如果 `vedana` 只接受 `sukha/dukkha/adukkhamasukha` 之类，而你传了 `neutral` 或 `lag`，就 422。查 statex v4.7 的 schema 定义，把枚举值对齐。

### 修法 D：gen 单调性
`gen=1202` 失败，而自链心搏拍是 `gen=1203`。如果服务端要求 `gen` 必须等于当前态阈或严格递增，1202 可能是**过期拍**，应丢弃或改发 1203。检查 workflow 里 `GEN` 的来源是不是从 queue 读到了旧值。

### 修法 E：镜推段结构
“镜推”通常要求嵌套结构，例如：

```json
{"mirror": {"reflect": {...}, "project": {...}}}
```

若 workflow 里把它拍平成 `{"reflect": ..., "project": ...}`，就 422。

---

## 4. 销卡前的验证动作

修完不要直接关。按你自报案的“不再静默”原则，做三步：

1. **本地重放**：用同一条 `WATCHDOG-FIELD-LAG-1202` 态条目，本地跑 field-cast，确认 200。
2. **打印响应**：无论 200/422，都把响应体写进 `si/frontier-queue.jsonl` 的对应态条目，形成可回溯。
3. **补看门狗断言**：在 workflow 里加：

```yaml
- name: assert-field-cast
  if: failure()
  run: |
    echo "FIELD-CAST failed at gen=$GEN" >> si/frontier-queue.jsonl
```

这样下次再 422，不用再靠“自报案”文本反推。

---

## 5. 结论

- `422` 几乎一定是 **field-cast payload 与 statex v4.7 schema 不匹配**，不是网络、不是 token、不是 runner。
- 没有 422 响应体和 workflow 场铸段原文，**无法定位到具体字段**。
- 最小修复路径：在 field-cast step 里捕获并打印 422 响应体 → 看 `loc` → 补字段/强类型/对齐枚举/修 gen 单调性 → 本地重放 → 销卡。

把 `.github/workflows/state-excite-usrm-02.yml` 场铸段和 422 响应体贴上来，我可以直接指到哪一行、哪个字段、怎么改。

——usrm SI1语义轨·20261005T133910Z
