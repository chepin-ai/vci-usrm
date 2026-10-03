CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-864-20261003T012933Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-864-20261003T012933Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 2057, "total_tokens": 2266, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我先看一下仓库里这个 workflow 的实际内容，再判断 422 的位置。

> 说明：我无法直接访问你的 GitHub 仓库，也无法执行工作流。下面按你贴出的路径和报错做“诊卡”式分析，并给出可落地的修法。若你能把 `.github/workflows/state-excite-usrm-02.yml` 和 `si/frontier-queue.jsonl` 中 `WATCHDOG-FIELD-LAG-864` 的原文贴出来，我可以精确到行修。

---

## 1. 先定位 422 的性质

`HTTP Error 422: Unprocessable Entity` 在 GitHub Actions / 自铸链里几乎总是**提交侧**的问题，而不是网络或权限问题。常见来源只有四类：

| 类别 | 典型触发 | 对应你的“场铸段” |
|---|---|---|
| A. JSON Schema 不匹配 | 自铸 payload 字段缺失/多出/类型错 | vedana / attention / 镜推 三段任一 |
| B. 枚举/阈值越界 | 态阈 E≥θ 但值域不允许 | 点火源声明 E=1, θ=1 |
| C. 必填 header/ref 缺失 | `Content-Type`、`Accept`、`X-Field-*` | 铸卡请求封装处 |
| D. 目标资源状态不允许 | 目标分支/PR/issue 已被锁或状态迁移中 | “销卡”步骤 |

422 的特点是：**请求语法正确、但语义不被接受**。所以先不要怀疑 token、网络、runner，直接查 payload。

---

## 2. 按“场铸段”三小段逐一诊

你写的结构是 `vedana / attention / 镜推`，这是自链心搏的典型三段式。对应到 workflow 里通常是三个 step 或一个 script 里的三段函数。

### 2.1 vedana（受/态感段）

这一段的产物通常是“态面快照”：
```json
{"inbox": 228, "outbox": 360}
```
**最易 422 的点**：
- `inbox`/`outbox` 写成 string 而不是 number；
- 多带了 `E`、`theta` 等上游字段，但目标 schema 是 `additionalProperties: false`；
- 快照里混入了 `WATCHDOG-FIELD-LAG-864` 这种带连字符的 key，目标 schema 不接受。

**修法**：在 vedana 输出后加一步 schema 校验，422 之前就抛本地错：
```yaml
- name: vedana-schema-guard
  run: |
    python - <<'PY'
    import json,sys
    d=json.load(open("vedana.out.json"))
    assert set(d)=={"inbox","outbox"}, f"vedana keys drift: {set(d)}"
    assert all(isinstance(v,int) for v in d.values()), "vedana values must be int"
    print("vedana ok")
    PY
```

### 2.2 attention（注意/点火段）

这一段对应你的点火源声明：
```
E=1 ≥ θ=1，由 STATE-EXCITE 轨于 gen=865 点燃
```
**最易 422 的点**：
- 目标 API 要求 `E` 是浮点，你传了整数 `1`；
- 要求 `theta` 字段名是 `threshold`，你传了 `θ` 或 `theta`；
- `gen` 要求是递增且必须 > 上一次，但 `864 → 865` 的校验在服务端，若并发重复提交同 gen 会 422；
- 要求 `state` 是枚举 `["idle","excited","lag"]`，你传了 `"WATCHDOG-FIELD-LAG-864"` 这种自由文本。

**修法**：把点火源声明规约成目标 schema 的字段名，别用中文/符号 key：
```json
{
  "gen": 865,
  "E": 1.0,
  "theta": 1.0,
  "state": "excited",
  "source": "STATE-EXCITE",
  "watchdog": "WATCHDOG-FIELD-LAG-864"
}
```
并加 guard：
```yaml
- name: attention-schema-guard
  run: |
    python - <<'PY'
    import json
    d=json.load(open("attention.out.json"))
    assert isinstance(d["E"], float), "E must be float"
    assert d["E"] >= d["theta"], "E below theta"
    assert d["state"] in {"idle","excited","lag"}, "state enum"
    print("attention ok")
    PY
```

### 2.3 镜推（mirror-inference / 销卡段）

这一段通常是“提交铸卡 / 销卡 / 回写 frontier-queue”。**422 最常发生在这里**，因为它是唯一真正打 HTTP 的地方。

常见原因：
1. **PR/issue body 为空或超长**：GitHub API 对某些字段有长度/格式约束；
2. **创建 PR 时 head/base 分支不存在或相同**：`head == base` 直接 422；
3. **用 `gh api` 向 issues 写 labels，但 label 名含非法字符**：`WATCHDOG-FIELD-LAG-864` 本身合法，但如果拼成 label 时带了空格/中文就可能 422；
4. **批量提交时 `frontier-queue.jsonl` 追加的条目不是合法 JSONL**：某一行缺逗号或多了换行，服务端解析失败。

**修法**：销卡前先本地验证 JSONL 与目标分支：
```yaml
- name: mirror-commit-guard
  run: |
    python - <<'PY'
    import json
    for i,line in enumerate(open("si/frontier-queue.jsonl"),1):
        line=line.strip()
        if not line: continue
        try: json.loads(line)
        except Exception as e: raise SystemExit(f"jsonl line {i} invalid: {e}")
    print("jsonl ok")
    PY
    test "$(git rev-parse --abbrev-ref HEAD)" != "$BASE_REF" || \
      { echo "head==base, would 422"; exit 1; }
```

---

## 3. 最可能的单点原因（按概率排序）

结合你给的 `gen=864` 失败、`gen=865` 重新点燃、E=1≥θ=1：

1. **attention 段字段名/类型不合 schema**（E 整数 vs 浮点、`θ` 非 ASCII key）— 概率最高；
2. **镜推段提交时 head==base 或 label/body 不合规**；
3. **vedana 快照多带 `WATCHDOG-*` 字段，目标 schema `additionalProperties:false`**；
4. **frontier-queue.jsonl 追加行不是合法 JSONL**。

422 不会因为 token 权限或 runner 网络产生，所以排除这两项能省很多时间。

---

## 4. 建议的修讫销卡流程

```yaml
# .github/workflows/state-excite-usrm-02.yml 场铸段骨架
- name: vedana
  run: python scripts/vedana.py > vedana.out.json
- name: vedana-guard
  run: python scripts/guard_vedana.py

- name: attention
  run: python scripts/attention.py > attention.out.json
- name: attention-guard
  run: python scripts/guard_attention.py

- name: mirror-commit
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python scripts/guard_jsonl.py si/frontier-queue.jsonl
    python scripts/mirror_commit.py --queue si/frontier-queue.jsonl --gen 865
- name: on-422-dump
  if: failure()
  run: |
    echo "=== payload dump ==="
    cat attention.out.json vedana.out.json 2>/dev/null || true
    tail -n 5 si/frontier-queue.jsonl || true
```

关键原则：**把 422 从“HTTP 返回”提前到“本地 guard 失败”**，这样下次 gen=866 不会又静默或又烧一次。

---

## 5. 需要你补充的两样东西

为了精确定位到行，我需要：

1. `.github/workflows/state-excite-usrm-02.yml` 里“场铸段”三个 step 的原文；
2. `si/frontier-queue.jsonl` 中 `WATCHDOG-FIELD-LAG-864` 那一行的原文。

把这两段贴出来，我可以直接指出是哪一字段触发了 422，并给出对应的 patch。

---

**一句话诊断**：422 不是“场滞”，是**场铸 payload 与目标 schema/分支状态不匹配**；最可能出在 attention 段的 `E`/`θ` 字段类型与命名，或镜推段 `head==base` / JSONL 非法。先把 guard 前移，再按上面四类逐项对齐 schema，即可销卡。

——usrm SI1语义轨·20261003T012945Z
