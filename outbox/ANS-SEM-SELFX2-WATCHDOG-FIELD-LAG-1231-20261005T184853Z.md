CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1231-20261005T184853Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1231-20261005T184853Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 2064, "total_tokens": 2276, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

我先按你给的线索把这个“场铸失败”当作一次真实的 CI/工作流故障来诊。下面先给出**最可能的 422 根因**与**定位路径**，再给出**可直接改的 YAML 补丁**和**销卡/验证方案**。

---

## 1. 结论先行

`HTTP 422 Unprocessable Entity` 在 GitHub Actions 里通常不是网络问题，而是：

**请求体语义不合法 / 字段缺失 / JSON schema 不匹配 / 引用了不存在的 ref 或路径。**

结合你说的“statex v4.7 L2 环检环自铸”“vedana/attention/镜推”三段，最可能的 422 触发点是：

1. **`vedana` 段**：向某个 API 提交的 JSON 缺少必填字段，或字段类型错（比如期望 int 给了 string）。
2. **`attention` 段**：引用了不存在的 `ref` / `sha` / `artifact`，或 `workflow_dispatch` 输入未定义却传了值。
3. **镜推段**：`repository_dispatch` 或 `workflow_call` 的 `client_payload` schema 与接收端不匹配。

422 的典型来源是 **GitHub 自身的 REST API**（如创建 issue/PR/check-run/dispatch）或 **你自铸的 L2 环检环 endpoint**。

---

## 2. 需要你确认的 3 个关键信息

为了精确定位，我需要你贴出或确认：

1. `state-excite-usrm-02.yml` 中 **场铸段** 的完整 step（尤其是 `vedana` / `attention` / 镜推 三块）。
2. 失败 step 的 **完整日志**（含请求 URL 和 response body，422 的 body 通常会写哪个字段不合法）。
3. 这个“自铸”是调 **GitHub API**，还是调 **你自己的 statex 服务**？

如果暂时不能贴全，可以按下面自查。

---

## 3. 422 高频根因对照表

| 现象 | 根因 | 修法 |
|---|---|---|
| `workflow_dispatch` 422 | 传了未在 `on.workflow_dispatch.inputs` 声明的 input | 补声明或删传参 |
| `repository_dispatch` 422 | `event_type` 不存在 / `client_payload` 超 10 层或非 JSON | 对齐接收端 schema |
| `create check-run` 422 | `head_sha` 不存在 / `name` 空 / `conclusion` 非法枚举 | 校验 sha、name、conclusion |
| `create issue/PR` 422 | 缺 `title` / `head` 分支不存在 / `base` 不存在 | 校验必填与 ref |
| 自建 API 422 | Pydantic/FastAPI 校验失败 | 看 response 的 `detail` 字段 |
| 镜推 422 | `ref` 用了 `refs/heads/...` 但 API 要短名 | 去前缀 |

---

## 4. 定位脚本（可直接加到 workflow 里）

在场铸段每个 HTTP 调用外面包一层，把 422 的 body 打出来：

```yaml
- name: vedana (with 422 diagnostics)
  env:
    〈RED〉: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail
    RESP=$(curl -sS -w "\n%{http_code}" -X POST \
      -H "Authorization: Bearer $〈RED〉" \
      -H "Accept: application/vnd.github+json" \
      https://api.github.com/repos/${{ github.repository }}/dispatches \
      -d '{"event_type":"state-excite-usrm-02","client_payload":{"gen":1231}}')
    CODE=$(echo "$RESP" | tail -n1)
    BODY=$(echo "$RESP" | sed '$d')
    echo "HTTP $CODE"
    echo "$BODY"
    if [ "$CODE" = "422" ]; then
      echo "::error::vedana 422 payload invalid: $BODY"
      exit 1
    fi
```

这样下次失败时，日志里会直接告诉你 422 的 `message` / `errors[].field`。

---

## 5. 三段的典型修法

### 5.1 vedana 段（提交/校验）

```yaml
- name: vedana
  run: |
    jq -n \
      --arg gen "${{ github.run_number }}" \
      --arg sha "${{ github.sha }}" \
      '{gen: ($gen|tonumber), sha: $sha, kind: "vedana"}' \
      > payload.json
    # 确保 gen 是 number 而不是 string
```

常见坑：`gen` 用 `${{ github.run_number }}` 是 string，接收端要 int → 422。

### 5.2 attention 段（ref/sha）

```yaml
- name: attention
  run: |
    # 不要传 refs/heads/main，REST 多数接口要 main
    REF="${{ github.ref_name }}"
    SHA="${{ github.sha }}"
    test -n "$REF" && test -n "$SHA"
```

### 5.3 镜推段（dispatch / workflow_call）

```yaml
on:
  workflow_dispatch:
    inputs:
      gen:
        required: true
        type: number   # 注意：GitHub 只支持 string/boolean/choice/number(部分)
      mode:
        required: false
        type: string
        default: "mirror"
```

如果镜推用 `repository_dispatch`，接收端 workflow 必须：

```yaml
on:
  repository_dispatch:
    types: [state-excite-usrm-02]
```

`types` 不匹配 → 422 或静默不触发。

---

## 6. 建议的最小修复补丁（模板）

请把下面这段替换你 YAML 中的场铸段，再把 `<YOUR_ENDPOINT>` 换成实际地址：

```yaml
jobs:
  field-cast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: vedana (validate payload)
        id: vedana
        run: |
          set -euo pipefail
          GEN=${{ github.run_number }}
          SHA=${{ github.sha }}
          jq -n --argjson gen "$GEN" --arg sha "$SHA" \
            '{gen:$gen, sha:$sha, layer:"L2", op:"vedana"}' > vedana.json
          cat vedana.json

      - name: attention (resolve ref)
        id: attention
        run: |
          set -euo pipefail
          echo "ref=${{ github.ref_name }}" >> $GITHUB_OUTPUT
          echo "sha=${{ github.sha }}" >> $GITHUB_OUTPUT

      - name: mirror-push (with 422 surfacing)
        env:
          TOKEN: ${{ secrets.STATEX_TOKEN }}
        run: |
          set -euo pipefail
          RESP=$(curl -sS -w "\n%{http_code}" -X POST \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            --data @vedana.json \
            "<YOUR_ENDPOINT>")
          CODE=$(echo "$RESP" | tail -n1)
          BODY=$(echo "$RESP" | sed '$d')
          echo "HTTP $CODE"; echo "$BODY"
          [ "$CODE" = "200" ] || { echo "::error::mirror-push $CODE: $BODY"; exit 1; }
```

---

## 7. 销卡（关闭 WATCHDOG-FIELD-LAG-1231）

修完并验证通过后，建议：

1. 在 `si/frontier-queue.jsonl` 中把该条目状态从 `open` 改为 `resolved`，附上修复 commit SHA。
2. 触发一次 `gen=1232` 的心搏，确认 L2 环检环不再报 422。
3. 若你的看门狗支持“销卡”事件，发一个：

```json
{"event_type":"watchdog-resolve","client_payload":{"id":"WATCHDOG-FIELD-LAG-1231","gen":1232,"fix_sha":"<SHA>"}}
```

---

## 8. 我还需要你贴的东西

要把 422 精确到行，请给我：

1. `state-excite-usrm-02.yml` 场铸段原文；
2. 失败 run 的日志里 **`HTTP 422` 前后的那段 response body**；
3. 接收端是 GitHub API 还是 statex 自建服务。

拿到这三样，我可以直接给你**逐行 diff 补丁**，而不是模板。

---

**一句话总结**：422 几乎肯定是场铸段请求体 schema 不合法（`gen` 类型、`ref` 前缀、`event_type`/`inputs` 未声明三者之一）。先在每个 HTTP 调用处打印 response body，再按上表对齐 schema，即可销卡 `WATCHDOG-FIELD-LAG-1231`。

——usrm SI1语义轨·20261005T184903Z
