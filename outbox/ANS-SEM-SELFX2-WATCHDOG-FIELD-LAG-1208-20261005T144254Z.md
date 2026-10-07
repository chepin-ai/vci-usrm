CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1208-20261005T144254Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1208-20261005T144254Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 2139, "total_tokens": 2351, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

我无法直接访问或修改你的仓库文件（包括 `.github/workflows/state-excite-usrm-02.yml`），也无法读取 `si/frontier-queue.jsonl` 的实际内容——我没有工具通道接到你的 GitHub / 本地文件系统。

不过我可以基于你给出的报错信息做诊断推理，并给出**可落地的修复方案**，你拿到仓库里对照改即可。

---

## 一、报错定位

```
FIELD-USRM-01 自模型场本拍铸造失败
gen=1208
err=HTTP Error 422: Unprocessable Entity
状态：statex v4.7 L2 环检环自铸，L1 态测环之场滞/失败不再静默
```

**关键判读：**

| 信号 | 含义 |
|---|---|
| `422 Unprocessable Entity` | 请求**语法合法但语义被拒**。不是 401/403（认证）、不是 404（路径）、不是 500（服务端崩）。是**payload 结构/字段/约束**问题。 |
| `gen=1208` | 第 1208 拍失败，说明前面 1207 拍大概率成功 → **不是初始配置错，是漂移/越界/状态耦合**。 |
| `自模型场本拍铸造` | 这一拍是把「场」（field）作为自模型写入/上传，走的是某个 API（很可能是模型场注册/铸卡接口）。 |
| `L1 态测环之场滞` | L1 层测到「场」出现滞后/停滞，L2 环检因此触发自铸。 |
| `看门狗自报案` | 这是 watchdog 自己发的案，不是外部调用失败。 |

**结论：422 不是网络/权限问题，是发出去的场载荷（vedana / attention / 镜推 三段）里某个字段违反了 API 的 schema 约束。**

---

## 二、按你点名的三段逐一排查

你指定了场铸段的三块：`vedana` / `attention` / `镜推`。

### 1. `vedana`（受/感受段）
常见 422 诱因：
- 值域越界：如受值被 clamp 到 `[-1,1]` 但本拍吐出 `1.0000001` 或 `NaN`。
- 类型漂移：前 1207 拍是 `float`，本拍因某分支变成 `null` 或 `"1.0"`（字符串）。
- 缺字段：受段在「场滞」状态下可能被跳过，导致必填的 `vedana` 缺失 → 422。

**查：** 本拍 `vedana` 是否 `null` / `NaN` / 超界 / 类型变了。

### 2. `attention`（注意段）
常见 422 诱因：
- 权重和 ≠ 1（若 API 校验归一化）。
- 维度不匹配：前拍 `dim=768`，本拍因镜推回退变成 `dim=512`。
- 空数组：注意力全被 mask 掉 → `[]` → 422。

**查：** `attention` 的 shape、sum、是否空。

### 3. `镜推`（mirror-inference 段）
常见 422 诱因：
- 递归深度超限：镜推是自指段，1208 拍可能触到 API 的 `max_depth`。
- 循环引用：镜推结果里嵌回了场本身 → JSON 序列化出环 → 服务端拒。
- 版本字段：`statex v4.7` 的镜推 schema 可能要求 `mirror_version`，本拍漏了。

**查：** 镜推输出是否自引用、深度、是否带 `mirror_version`。

---

## 三、修复方案（按优先级）

### 修法 A：给场铸段加「出站前校验 + 降级」（推荐，治本）

在 `.github/workflows/state-excite-usrm-02.yml` 的场铸 step 里，**在 POST 之前**插入一段 guard：

```yaml
- name: Field Cast Guard (pre-flight schema check)
  run: |
    python - <<'PY'
    import json, math, sys, os

    payload = json.load(open("si/field_cast_payload.json"))

    errors = []

    # --- vedana ---
    v = payload.get("vedana")
    if v is None:
        errors.append("vedana missing/null")
    elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        errors.append(f"vedana non-finite: {v}")
    elif not (-1.0 <= float(v) <= 1.0):
        errors.append(f"vedana out of range: {v}")

    # --- attention ---
    a = payload.get("attention")
    if not a:
        errors.append("attention empty")
    else:
        s = sum(a)
        if abs(s - 1.0) > 1e-3:
            errors.append(f"attention not normalized: sum={s}")

    # --- 镜推 ---
    m = payload.get("mirror")
    if m is None:
        errors.append("mirror missing")
    else:
        if m.get("depth", 0) > 8:
            errors.append(f"mirror depth too high: {m.get('depth')}")
        if "mirror_version" not in m:
            errors.append("mirror_version missing")

    if errors:
        print("FIELD-CAST-GUARD FAIL:", errors)
        # 写出诊断，供 watchdog 销卡
        json.dump({"gen": os.environ.get("GEN","1208"),
                   "errors": errors},
                  open("si/field_cast_guard.json","w"))
        sys.exit(1)

    print("FIELD-CAST-GUARD OK")
    PY

- name: Cast field to statex (USRM-01)
  if: success()
  run: |
    curl -fsS -X POST "$STATEX_ENDPOINT/usrm/field" \
      -H "Content-Type: application/json" \
      -d @si/field_cast_payload.json
```

这样 422 会在**出站前**被拦成可读的 guard 失败，而不是黑盒 422。

### 修法 B：422 响应体必须落盘（治诊）

422 的响应体里通常有 `detail` 字段指明哪个字段不合格。当前报错只留了 `HTTP Error 422`，把 body 丢了 → 无法定位。

```yaml
- name: Cast field (capture 422 body)
  run: |
    set +e
    code=$(curl -sS -o si/field_cast_resp.json -w "%{http_code}" \
      -X POST "$STATEX_ENDPOINT/usrm/field" \
      -H "Content-Type: application/json" \
      -d @si/field_cast_payload.json)
    set -e
    if [ "$code" != "200" ]; then
      echo "CAST FAIL code=$code"
      cat si/field_cast_resp.json
      exit 1
    fi
```

下次 422 就能看到具体是 `vedana` 还是 `attention` 还是 `镜推` 被拒。

### 修法 C：场滞自愈（治因）

`L1 态测环之场滞` 说明本拍 `vedana` 或 `attention` 进入了停滞区（长时间不变 → 归一化漂移 / NaN）。

在 state-excite 轨里加：**检测到场滞 ≥ N 拍，先 reseed 再铸**，而不是直接原样铸。

```python
# 伪码，插在 generate_payload 之前
if field_lag_streak >= LAG_THRESHOLD:
    vedana   = reseed_vedana(vedana)
    attention = renormalize(attention)
    mirror   = reset_mirror_depth(mirror)
    emit("FIELD-RESEED", gen=gen, reason="lag")
```

---

## 四、销卡（关闭 WATCHDOG-FIELD-LAG-1208）

修完后，写一条回执进 `si/frontier-queue.jsonl`：

```json
{"id":"WATCHDOG-FIELD-LAG-1208","status":"resolved","gen_fixed":1209,"fix":"guard+422-body+reseed","card":"FIELD-USRM-01","assigned":"state-excite-usrm-02.yml"}
```

并跑一次自铸验证：

```
gen=1209 → FIELD-CAST-GUARD OK → 200 → 销卡
```

---

## 五、一句话诊断

> **422 ≠ 网络/权限，是场载荷的 schema 语义被拒。1208 拍在前 1207 拍成功后失败，说明是 vedana/attention/镜推 三段中某段发生了「值域越界 / 归一化漂移 / 深度超限 / 自引用」的漂移。当前流水线丢了 422 响应体，所以看不到具体字段。先补 body 落盘（修法 B），再加出站 guard（修法 A），最后加场滞 reseed（修法 C），即可销卡。**

---

需要的话，你把三样东西贴出来，我可以给出精确到字段的补丁：

1. `.github/workflows/state-excite-usrm-02.yml` 场铸段原文；
2. `si/frontier-queue.jsonl` 里 `WATCHDOG-FIELD-LAG-1208` 那条；
3. 422 的响应体（如果有 `si/field_cast_resp.json` 或 CI 日志片段）。

——usrm SI1语义轨·20261005T144305Z
