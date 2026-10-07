CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-815-20261002T164811Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-815-20261002T164811Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1070, "total_tokens": 1279, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我无法直接访问你的仓库文件、`.github/workflows/state-excite-usrm-02.yml` 的实际内容、`si/frontier-queue.jsonl` 或 GitHub Actions 的运行日志，因此不能凭这条自报案断言具体哪一段“场铸段(vedana/attention/镜推)”写错了。

不过，**HTTP 422: Unprocessable Entity** 在这个语境下通常不是“网络问题”，而是**请求已经到达服务端，但服务端拒绝处理**。在 GitHub Actions / 自铸工作流里，最常见的触发点是：

1. **`workflow_dispatch` / `repository_dispatch` 的 payload schema 不匹配**
   - 例如 `client_payload` 里少了必填字段、多了未定义字段、类型不对（字符串 vs 数组 vs 对象）。
   - 422 经常出现在 GitHub API 对 dispatch 事件做 schema 校验时。

2. **`actions/github-script` 或 `gh api` 调用时 body 不合法**
   - 例如 `POST /repos/{owner}/{repo}/dispatches` 缺少 `event_type`，或 `event_type` 含非法字符。
   - 创建 issue/comment 时 body 为 `null`、字段名拼错、`labels` 不是数组等。

3. **Artifact / cache / release 上传路径或元数据不合法**
   - 例如 artifact 名字含非法字符、路径越界、release tag 已存在但尝试创建、`Content-Length` 与 body 不符。

4. **OIDC / 权限 / 环境规则导致的 422**
   - 有些组织级规则会以 422 返回，而不是 403。

5. **你自己的“场铸”服务端做了严格 schema 校验**
   - 如果 `vedana/attention/镜推` 是自建 HTTP 端点，422 就是它主动返回的“语义不可处理”，需要看它期望的 JSON schema。

---

### 建议的最小诊断步骤

请把下面几项贴出来（或你自己对照检查），我就能帮你定位到具体行：

1. `.github/workflows/state-excite-usrm-02.yml` 中**场铸段**的完整 step（尤其是 `run:` 或 `uses:` 里发 HTTP 请求的部分）。
2. 失败 run 的**原始日志**，特别是 422 前后几行，通常 GitHub 会打印 response body。
3. `si/frontier-queue.jsonl` 里 `WATCHDOG-FIELD-LAG-815` 这条的**完整 JSON**。
4. 如果是 `repository_dispatch`，给出触发时的 `client_payload`。
5. 如果是自建端点，给出它期望的请求 schema。

---

### 一个常见的 422 修法模板

如果场铸段是类似这样的：

```yaml
- name: field-cast
  run: |
    curl -X POST "$ENDPOINT" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"vedana": "${{ inputs.vedana }}", "attention": "${{ inputs.attention }}"}'
```

而服务端要求 `attention` 必须是数组、`vedana` 必须是枚举，那么当 `inputs.attention` 为空字符串时就会 422。

修法通常是：

```yaml
- name: field-cast
  env:
    VEDANA: ${{ inputs.vedana }}
    ATTENTION: ${{ inputs.attention }}
  run: |
    jq -n \
      --arg vedana "$VEDANA" \
      --argjson attention "${ATTENTION:-[]}" \
      '{vedana: $vedana, attention: $attention}' \
      > payload.json

    curl -sS -X POST "$ENDPOINT" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      --data-binary @payload.json \
      -w '\n%{http_code}\n'
```

并在 step 前加 schema 校验，失败就 `exit 1` 并打印 body，而不是静默。

---

### 关于“销卡”

如果这是你们内部看门狗流程，正确的销卡条件应该是：

- 422 的 response body 被完整记录；
- 触发条件（gen=815 的 payload）被复现；
- 修复后同一 `gen` 重放不再 422；
- 在 `si/frontier-queue.jsonl` 里把 `WATCHDOG-FIELD-LAG-815` 标记为 `resolved` 并附上修复 commit SHA。

否则只是把静默失败换了个地方继续静默。

---

把上面 1–4 项贴出来，我可以直接帮你改 `.github/workflows/state-excite-usrm-02.yml` 的场铸段。

——usrm SI1语义轨·20261002T164822Z
