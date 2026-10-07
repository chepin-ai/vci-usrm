CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1174-20261005T084130Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1174-20261005T084130Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 2745, "total_tokens": 2957, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

下面按“看门狗自报案”的口径来诊。先说明：我无法直接访问你仓库里的 `.github/workflows/state-excite-usrm-02.yml`、`si/frontier-queue.jsonl` 或 `statex v4.7` 运行时，所以不能真的读文件、不能改仓库、也不能替你销卡。但我可以基于你给出的报错和字段语义，给出最可能的故障定位与修法。

## 1. 报错含义

```
FIELD-USRM-01 自模型场本拍铸造失败
gen=1174
err=HTTP Error 422: Unprocessable Entity
```

422 不是网络层错误，而是**服务端理解请求、但拒绝处理**。在“场铸”语境里，通常对应：

- 请求体 JSON 结构合法，但**字段语义校验失败**
- 某个字段缺失、类型不对、枚举值不在允许集
- 状态机前置条件不满足
- 幂等键 / 版本号 / gen 冲突
- 必填的 `vedana`、`attention`、`mirror` 字段有一项不满足 schema

也就是说：**不是“连不上”，而是“铸不出来，因为态料不合格”。**

## 2. 最可能出问题的三段

你点名的场铸段是：

```
vedana / attention / 镜推
```

按优先级排序：

### A. vedana 段
`vedana` 在语义上偏“感受/态值”。常见 422 原因：

- 值域越界，例如要求 `[-1,1]` 或 `[0,1]`，实际传了 `null`、`NaN`、字符串
- 枚举不匹配，例如只允许 `"pos"/"neg"/"neu"`，传了 `"neutral"`
- 本拍 `gen=1174` 的 vedana 由上一拍推导，但上一拍 L1 态测环已经场滞，导致本拍输入是 stale / 空

### B. attention 段
`attention` 通常是权重向量或焦点字段。常见 422：

- 向量长度与 schema 不一致
- 权重和不为 1，或含负数
- 某个 attention head 的 key 不在允许集合
- 与 `vedana` 的联合约束失败，例如：
  - `vedana=neg` 时 `attention` 不允许全零
  - `attention` 的 target 必须属于当前场

### C. 镜推段
“镜推”大概率是 mirror inference / 自模型反射推导。常见 422：

- 镜推输入依赖 `vedana` 和 `attention`，前两者任一非法，镜推请求体直接不可处理
- 镜推要求 `prev_gen=1173`，但实际传了 `1172` 或 `1174`
- 镜推输出 schema 要求 `mirror_id`、`trace`、`confidence`，缺一即 422
- 镜推阶段可能要求 `statex` 版本匹配，`v4.7` 与 workflow 里写死的 `v4.6` 不匹配

## 3. 为什么 L1 态测环“场滞/失败不再静默”后会 422

你这句话很关键：

> L1 态测环之场滞/失败不再静默

以前 L1 失败可能被吞掉，场铸继续用脏数据跑，于是不报 422，或者报别的错。现在 L1 不再静默，意味着：

- L1 场滞 → 本拍输入不完整
- 不完整输入 → 场铸请求体里某些字段为 `null` / `missing` / `stale`
- 服务端 schema 校验 → 422

所以 422 很可能不是场铸段本身写错，而是**上游 L1 场滞被显式暴露后，场铸段没有处理“降级输入”**。

## 4. 建议的诊修顺序

### 第一步：先看 422 的 response body
GitHub Actions 里 `HTTP Error 422` 往往只给了状态码，但真正的字段错误在 response body。  
在 workflow 里把铸场那一步改成先打印 body，例如：

```yaml
- name: Cast field
  run: |
    set -euo pipefail
    resp=$(curl -sS -w "\n%{http_code}" -X POST "$CAST_URL" \
      -H "Content-Type: application/json" \
      -d @payload.json)
    body=$(echo "$resp" | head -n -1)
    code=$(echo "$resp" | tail -n 1)
    echo "HTTP $code"
    echo "$body"
    if [ "$code" != "200" ]; then
      echo "::error::cast failed with $code"
      exit 1
    fi
```

重点看 body 里有没有类似：

```json
{"detail":[{"loc":["body","vedana"],"msg":"value is not a valid enumeration member"}]}
```

这会直接告诉你哪一段坏。

### 第二步：校验 payload schema
在 workflow 里加一步本地校验，不要等远端 422：

```yaml
- name: Validate cast payload
  run: |
    python - <<'PY'
    import json, math, sys
    p = json.load(open("payload.json"))
    errs = []

    # vedana
    v = p.get("vedana")
    if v is None:
        errs.append("vedana missing")
    elif not isinstance(v, (int, float)) or isinstance(v, bool):
        errs.append(f"vedana type invalid: {type(v)}")
    elif math.isnan(v) or math.isinf(v):
        errs.append("vedana non-finite")
    elif not (-1.0 <= float(v) <= 1.0):
        errs.append(f"vedana out of range: {v}")

    # attention
    a = p.get("attention")
    if a is None:
        errs.append("attention missing")
    elif not isinstance(a, list) or not a:
        errs.append("attention must be non-empty list")
    else:
        for i, x in enumerate(a):
            if not isinstance(x, (int, float)) or isinstance(x, bool):
                errs.append(f"attention[{i}] type invalid")
            elif math.isnan(x) or math.isinf(x):
                errs.append(f"attention[{i}] non-finite")
            elif x < 0:
                errs.append(f"attention[{i}] negative")
        s = sum(a)
        if abs(s - 1.0) > 1e-6:
            errs.append(f"attention sum != 1: {s}")

    # mirror
    m = p.get("mirror")
    if not isinstance(m, dict):
        errs.append("mirror missing or not object")
    else:
        for k in ("mirror_id", "trace", "confidence"):
            if k not in m:
                errs.append(f"mirror.{k} missing")
        c = m.get("confidence")
        if isinstance(c, (int, float)) and not (0 <= c <= 1):
            errs.append(f"mirror.confidence out of range: {c}")

    # gen
    if p.get("gen") != 1174:
        errs.append(f"gen mismatch: {p.get('gen')}")

    if errs:
        print("SCHEMA ERRORS:")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("payload OK")
    PY
```

### 第三步：检查 L1 态测环输出
在铸场之前加一个 gate：

```yaml
- name: Check L1 field lag
  run: |
    python - <<'PY'
    import json, sys
    # 假设 L1 输出在 l1_state.json
    s = json.load(open("l1_state.json"))
    if s.get("lag") or s.get("failed") or s.get("stale"):
        print("L1 field lag/failed/stale:", s)
        sys.exit(2)
    print("L1 OK")
    PY
```

如果 L1 场滞，就不应该继续铸场，而应该：

- 要么重试 L1
- 要么用上一拍稳定态做降级铸场
- 要么直接销卡并写 `WATCHDOG-FIELD-LAG-1174` 到 frontier queue

### 第四步：修 workflow 的场铸段
把“无脑 POST”改成“先校验、再降级、再 POST、失败写卡”：

```yaml
- name: Cast field with guard
  run: |
    set -euo pipefail
    python - <<'PY'
    import json, math, sys

    p = json.load(open("payload.json"))

    # 降级：若 vedana 缺失，用中性值
    if p.get("vedana") is None:
        p["vedana"] = 0.0

    # 降级：若 attention 非法，退回均匀分布
    a = p.get("attention")
    if not isinstance(a, list) or not a or any(
        (not isinstance(x, (int, float))) or isinstance(x, bool) or math.isnan(x) or x < 0
        for x in a
    ):
        p["attention"] = [1/3, 1/3, 1/3]

    # 归一化
    s = sum(p["attention"])
    if s > 0:
        p["attention"] = [x / s for x in p["attention"]]

    # 镜推降级
    m = p.setdefault("mirror", {})
    m.setdefault("mirror_id", "FIELD-USRM-01")
    m.setdefault("trace", [])
    m.setdefault("confidence", 0.0)

    json.dump(p, open("payload.fixed.json", "w"))
    print("payload fixed")
    PY

    resp=$(curl -sS -w "\n%{http_code}" -X POST "$CAST_URL" \
      -H "Content-Type: application/json" \
      -d @payload.fixed.json)
    body=$(echo "$resp" | head -n -1)
    code=$(echo "$resp" | tail -n 1)
    echo "HTTP $code"
    echo "$body"

    if [ "$code" != "200" ]; then
      echo "{\"card\":\"WATCHDOG-FIELD-LAG-1174\",\"gen\":1174,\"err\":\"HTTP $code\",\"body\":$(echo "$body" | jq -Rs .)}" \
        >> si/frontier-queue.jsonl
      exit 1
    fi
```

### 第五步：销卡
如果 422 已经定位并修复，销卡时可以写一条 resolve 记录：

```json
{"card":"WATCHDOG-FIELD-LAG-1174","status":"resolved","gen":1174,"fix":"state-excite-usrm-02.yml 场铸段增加 vedana/attention/mirror schema 校验与降级","resolved_at_gen":1175}
```

## 5. 最可能的根因排序

1. **L1 场滞导致 vedana / attention 为 null 或 stale** → 场铸 422  
2. **attention 向量不合法**：长度、负值、和不归一  
3. **镜推缺少 mirror_id / trace / confidence**  
4. **gen 或版本不匹配**：v4.7 与 workflow 内写死版本冲突  
5. **422 body 被 workflow 吞掉**，只看到状态码，误判为场铸段逻辑错

## 6. 一句话结论

`FIELD-USRM-01` 在 `gen=1174` 的 422 大概率不是网络故障，而是 **L1 态测环场滞后，场铸段把不完整的 `vedana/attention/镜推` 态料直接提交，被服务端 schema 拒绝**。  
修法核心是：**在 `.github/workflows/state-excite-usrm-02.yml` 场铸段前加 L1 gate，加 payload schema 校验，对 vedana/attention/mirror 做降级归一，保留 422 response body，失败写 `WATCHDOG-FIELD-LAG-1174`，成功后再销卡。**

——usrm SI1语义轨·20261005T084139Z
