CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1164-20261005T065551Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1164-20261005T065551Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 2159, "total_tokens": 2371, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

我无法直接访问你仓库里的 `.github/workflows/state-excite-usrm-02.yml` 文件内容，也不具备查看你 GitHub Actions 运行日志、`si/frontier-queue.jsonl` 或 `statex v4.7` 内部状态的权限。因此不能凭这段自述直接“诊”出 422 的具体成因，也不能替你改工作流并“销卡”。

不过，422 Unprocessable Entity 在 GitHub Actions / API 语境下通常有比较明确的排查方向。下面按“场铸段：vedana/attention/镜推”这个描述，给你一个可执行的诊断与修复路径。你或你的执行体可以按此在仓库内完成修复。

## 1. 先定位 422 是谁返回的

422 不是 GitHub Actions runner 默认会抛的通用错误，它通常来自：

- **GitHub REST API**（如 `gh api`、`actions/github-script`、curl 调用 `api.github.com`）
- **GitHub GraphQL API**（较少见，GraphQL 一般返回 200 + errors）
- **第三方端点**（webhook、自建服务、模型场本拍铸造服务）
- **GitHub Actions 的 `workflow_dispatch` / `repository_dispatch`** 参数校验失败
- **`peter-evans/create-pull-request`、`gh pr create`、`gh issue create` 等封装动作** 对输入校验失败

请先在 workflow 里把失败步骤的 **完整 HTTP 响应体** 打出来。422 的响应体里通常有 `message`、`errors`、`documentation_url`，这是唯一能确定根因的信息。

建议加一段临时诊断：

```yaml
- name: Dump 422 context
  if: failure()
  run: |
    echo "=== GITHUB_CONTEXT ==="
    echo '${{ toJSON(github) }}' | head -c 4000
    echo
    echo "=== job status ==="
    echo '${{ toJSON(job) }}'
    echo
    echo "=== steps ==="
    echo '${{ toJSON(steps) }}'
```

如果是 `gh api` 或 curl，确保加 `-i` 或 `--include`，并把 stderr 也捕获。

## 2. 422 的常见具体原因

按你提到的“场铸段 vedana/attention/镜推”，我推测它可能对应：

- **vedana**：感受/状态判定，可能在做条件分支或调用状态 API
- **attention**：注意力/筛选，可能在做 issue/PR 查询或过滤
- **镜推**：镜像/推理，可能在做模型调用或写入铸造

对应到 422，常见根因有：

### A. 请求体字段缺失或类型错误
GitHub API 对 `workflow_dispatch` 的 `inputs`、`repository_dispatch` 的 `client_payload`、`create-pull-request` 的 `body` 等都有严格 schema。少一个必填字段、类型不对（字符串 vs 数字）、枚举值不在允许列表，都会 422。

检查：
- `workflow_dispatch.inputs` 是否都设了 `required` 和 `type`
- 调用方传入的 JSON 是否与 workflow 定义一致
- 是否有空字符串传给必填字段

### B. JSON 本身不合法
如果 workflow 里用 heredoc / echo 拼 JSON，很容易多逗号、少引号、换行未转义。422 常在 body 解析阶段就失败。

检查：
```bash
echo "$PAYLOAD" | jq .
```
如果 `jq` 报错，就是 JSON 语法问题。

### C. 引用了不存在的 ref / sha / branch
`create-pull-request`、`gh pr create`、`contents` API 在 base/head 不存在时会 422。

检查：
- `base` 分支是否存在
- `head` 分支是否已 push
- `sha` 是否 40 位合法
- 是否在 fork 场景下 base 写错

### D. 权限或 token scope 导致的结构性拒绝
有些 422 是因为 token 类型不对（如 fine-grained token 缺某权限），GitHub 会返回 422 而不是 403。

检查：
- `permissions:` 块是否给了 `contents: write`、`issues: write`、`pull-requests: write`
- 是否用了 `GITHUB_TOKEN` 但目标仓库是另一个仓库

### E. 模型场本拍铸造服务自身的 422
如果“铸造”是调用你自建服务，422 可能来自该服务的输入校验。需要看该服务的日志，而不是只看 Actions。

检查：
- 服务端是否记录了 request id
- 请求体是否包含 `gen=1164` 对应字段
- 是否有 schema 版本不匹配（statex v4.7 vs 服务端期望版本）

## 3. 针对“场铸段”的具体修法

在没看到文件的情况下，我给一个通用修复模板。你把 `state-excite-usrm-02.yml` 的场铸段按这个结构对齐：

```yaml
- name: 场铸 - vedana
  id: vedana
  run: |
    set -euo pipefail
    # 先做本地校验，避免把坏数据发出去
    if [ -z "${INPUT_STATE:-}" ]; then
      echo "vedana: INPUT_STATE empty" >&2
      exit 1
    fi
    echo "state=$INPUT_STATE" >> "$GITHUB_OUTPUT"

- name: 场铸 - attention
  id: attention
  run: |
    set -euo pipefail
    # 查询类操作，失败要保留响应体
    resp=$(curl -sS -w '\n%{http_code}' -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
      "https://api.github.com/repos/${{ github.repository }}/issues?state=open&per_page=1")
    code=$(echo "$resp" | tail -n1)
    body=$(echo "$resp" | sed '$d')
    if [ "$code" != "200" ]; then
      echo "attention: HTTP $code" >&2
      echo "$body" >&2
      exit 1
    fi
    echo "$body" | jq -c '.[0] // {}' > attention.json

- name: 场铸 - 镜推
  id: mirror
  run: |
    set -euo pipefail
    # 写入类操作，先 jq 校验 payload
    payload=$(jq -n \
      --arg gen "${{ github.run_number }}" \
      --arg state "${{ steps.vedana.outputs.state }}" \
      '{gen: ($gen|tonumber), state: $state}')
    echo "$payload" | jq . >/dev/null
    resp=$(curl -sS -w '\n%{http_code}' -X POST \
      -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
      -H "Accept: application/vnd.github+json" \
      -H "Content-Type: application/json" \
      -d "$payload" \
      "https://api.github.com/repos/${{ github.repository }}/dispatches")
    code=$(echo "$resp" | tail -n1)
    body=$(echo "$resp" | sed '$d')
    if [ "$code" != "204" ] && [ "$code" != "200" ]; then
      echo "镜推: HTTP $code" >&2
      echo "$body" >&2
      exit 1
    fi
```

关键点：
1. **每个外部调用都打印 HTTP code 和 body**，否则 422 永远查不到根因。
2. **写入前先用 jq 校验 JSON**。
3. **必填字段做空值检查**。
4. **区分 200/204/201/202**，不要只判断 `curl` 退出码。
5. **`set -euo pipefail`** 防止管道中间失败被吞。

## 4. “销卡”的正确做法

你说“修讫销卡”。在自判之前，建议：

1. 在 workflow 里加一个 `if: failure()` 的步骤，把 422 的完整响应写到 artifact 或 issue 评论。
2. 用 `actions/upload-artifact` 保存诊断日志。
3. 修完后，用一次 `workflow_dispatch` 手动触发，确认 `gen=1165` 能通过。
4. 确认 `si/frontier-queue.jsonl` 里 `WATCHDOG-FIELD-LAG-1164` 的状态被正确更新。
5. 再让看门狗自报案逻辑判断是否销卡，而不是人工直接销。

## 5. 我需要你提供什么才能进一步定位

如果你希望我帮你更具体地分析，请贴出：

- `.github/workflows/state-excite-usrm-02.yml` 的场铸段内容（可脱敏）
- 失败 run 的日志中 **422 响应体原文**
- 触发方式：`workflow_dispatch` / `repository_dispatch` / schedule / 其他
- 铸造目标是 GitHub API 还是自建服务
- `statex v4.7` 对 L2 环检环自铸的输入 schema

有了这些，我可以帮你判断是字段缺失、JSON 语法、ref 不存在、权限问题，还是服务端 schema 不匹配，并给出具体的 YAML 修改。

**当前结论：仅凭 `HTTP Error 422: Unprocessable Entity` 和这段自述，无法确定根因，也无法直接修讫销卡。必须先拿到 422 的响应体。**

——usrm SI1语义轨·20261005T065601Z
