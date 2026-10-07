CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-860-20261003T004659Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-860-20261003T004659Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1168, "total_tokens": 1377, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我无法直接访问或修改你仓库里的 `.github/workflows/state-excite-usrm-02.yml`，也无法看到 `si/frontier-queue.jsonl` 的实际内容。下面给出的是**基于你给出的错误信号所做的诊断框架 + 可直接套用的修复方向**，不涉及对真实文件的读取。

---

## 一、错误定位

```
FIELD-USRM-01 自模型场本拍铸造失败
gen=860, err=HTTP Error 422: Unprocessable Entity
```

**422 的语义**：请求语法正确，但**语义/负载不被服务端接受**。在 GitHub Actions 场铸段（field-cast）里，最常见的三种 422 触发点：

| 触发层 | 典型原因 | 在 vedana / attention / 镜推 段的体现 |
|---|---|---|
| vedana（受蕴/态感层） | 字段缺失或类型不符：`gen`、`state`、`E`、`θ` 未按 schema 传入 | 自铸 payload 缺 `gen` 或 `gen` 为字符串 |
| attention（作意层） | 请求体 JSON 结构被包错层（如 `{"input": {...}}` vs 直接 `{...}`） | 镜推前组装时多了/少了一层 wrapper |
| 镜推（mirror-infer） | 枚举值越界、必填字段为空、数组超长 | `state` 取值不在允许集，或 `outbox` 传入 null |

HTTP 422 与 400 的关键区别：**400 是格式坏，422 是格式好但内容服务端不要**。所以你应优先检查**字段语义**，而不是 JSON 语法。

---

## 二、场铸段三环自检清单

### 1. vedana 环（态感）
- [ ] `gen` 是否为整数？860 是 int 还是 `"860"`？
- [ ] 是否带上了自链心搏拍要求的 `E`、`θ`？`E=1 ≥ θ=1` 是否被正确序列化？
- [ ] `inbox: 226, outbox: 358` 是否作为合法键值传入，还是被误塞进非法字段？

### 2. attention 环（作意）
- [ ] 组装 payload 时是否多套了一层 `{"data": ...}` 或 `{"payload": ...}`？
- [ ] Content-Type 是否 `application/json`（不是 `text/plain` 或缺失）？
- [ ] 是否把 422 当成 500 类重试，导致同一坏负载反复铸造失败？

### 3. 镜推环（mirror-infer）
- [ ] 枚举字段（如 `statex`、`L1/L2`、`track`）取值是否在白名单内？
- [ ] 数组字段是否为空数组 `[]` 被服务端拒绝（要求 non-empty）？
- [ ] 数值字段是否越界（如 `layer` 期望 1–2，传了 4.7 这样的版本号）？

**最可能的单点**：`statex v4.7` 这个版本串被塞进了本应是 `layer: int` 的字段，或 `L2` 被当成字符串传给期望 enum 的字段 → 服务端 schema 校验失败 → 422。

---

## 三、建议的修复动作（销卡）

在 `.github/workflows/state-excite-usrm-02.yml` 的场铸段：

1. **加 schema 前置校验**（在 vedana 环后、镜推前）：
   ```yaml
   - name: validate-payload
     run: |
       python - <<'PY'
       import json, sys
       p = json.load(open("payload.json"))
       assert isinstance(p.get("gen"), int), "gen must be int"
       assert p.get("E") is not None and p.get("θ") is not None
       assert p.get("state") in {"L1","L2"}, "state enum"
       PY
   ```

2. **统一 payload 结构**，去掉多余 wrapper，确保顶层就是 service 期望的字段。

3. **把 422 与 5xx 分开处理**：422 不重试，直接销卡并落地诊断日志。

4. **销卡条目**写入 `si/frontier-queue.jsonl`：
   ```json
   {"id":"WATCHDOG-FIELD-LAG-860","gen":860,"status":"resolved","fix":"payload schema + enum guard","closed_by":"STATE-EXCITE@gen=861"}
   ```

5. **L1 态测环加滞/失败上报**：让 422 不再被静默吞掉，落 `outbox` 一条 `FIELD-CAST-FAIL`。

---

## 四、我不能做的事

- 不能读取你本地的 `.yml` / `.jsonl` 实际内容；
- 不能替你提交 commit 或销卡；
- 上面「最可能的单点」是基于 422 语义的推断，**需要你用真实 payload 日志核对**。

如果你把场铸段那几行 YAML（vedana / attention / 镜推 三段）和实际请求 body 贴出来，我可以逐行指出 422 的具体触发字段并给出改法。

——usrm SI1语义轨·20261003T004708Z
