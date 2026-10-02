CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-821-20261002T175117Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-821-20261002T175117Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 966, "total_tokens": 1175, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

你的排队消息里混进了一段乱码/臆造字段，不能按它去改工作流。下面是能落地的诊断与修复路径：

## 先定位真实错误

`HTTP 422 Unprocessable Entity` 在 GitHub Actions 里通常来自调用 GitHub REST API 的动作/脚本，常见原因：

1. **`workflow_dispatch` 或 `repository_dispatch` 的 payload 结构不对**——422 是 GitHub API 对 schema 校验失败的典型返回。
2. **`actions/github-script` 或 `curl` 调 `POST /repos/.../dispatches`** 时 `event_type` 缺失/为空，或 `client_payload` 不是对象。
3. **引用不存在的 ref/环境**。
4. **PR/Issue 相关 API 缺必填字段**。

## 需要你提供的最小信息

请贴出：

- `.github/workflows/state-excite-usrm-02.yml` 里 **报 422 那一步** 的完整 `run:` 或 `uses:` 片段
- 该 step 前一步的 **输出**（token、URL、body 变量）
- 触发本次运行的 **event 与 payload**（`github.event_name`、`github.event`）

## 自查清单（对照你贴的“场铸段”）

假设你的 step 大致长这样，逐条核对：

```yaml
- name: 场铸 / vedana-attention-镜推
  uses: actions/github-script@v7
  with:
    script: |
      await github.rest.repos.createDispatchEvent({
        owner: context.repo.owner,
        repo:  context.repo.repo,
        event_type: 'state-excite',          # ← 不能为空字符串
        client_payload: ${{ toJSON(...) }}   # ← 必须是对象, 不能是字符串
      })
```

常见坑：

| 现象 | 原因 | 修法 |
|---|---|---|
| 422 + `"event_type is required"` | `event_type` 空/未定义 | 写死常量或校验后才调用 |
| 422 + schema 报错 | `client_payload` 传了字符串化 JSON | 直接传对象，`github-script` 会自己序列化 |
| 422 只在某些 gen 出现 | 上游 step 输出为空 → payload 缺字段 | 加 `if:` 守卫 + 空值 fail-fast |
| 只在 L2 环检时挂 | 用了 L2 token 但无 dispatches 权限 | 换 `GITHUB_TOKEN` 或给 PAT `repo` scope |

## 建议的修法（模板）

```yaml
- name: 校验场铸输入
  id: guard
  run: |
    set -euo pipefail
    test -n "${EVENT_TYPE:-}" || { echo "EVENT_TYPE 空"; exit 1; }
    echo "payload=$(jq -c . <<<"$RAW")" >> "$GITHUB_OUTPUT"
  env:
    EVENT_TYPE: state-excite
    RAW: ${{ toJSON(inputs) }}

- name: 场铸 dispatch
  if: steps.guard.outputs.payload
  uses: actions/github-script@v7
  with:
    script: |
      const payload = JSON.parse(process.env.PAYLOAD);
      await github.rest.repos.createDispatchEvent({
        owner: context.repo.owner,
        repo:  context.repo.repo,
        event_type: process.env.EVENT_TYPE,
        client_payload: payload
      });
  env:
    EVENT_TYPE: ${{ env.EVENT_TYPE }}
    PAYLOAD: ${{ steps.guard.outputs.payload }}
```

加 `if:` 守卫后，上游为空时**不会**发出 422 调用，而是本步直接失败并打印原因——就达到你要的“不再静默”。

## 关于“销卡”

如果你有一个 `frontier-queue.jsonl` 的卡要标记完成，请给我**该卡的真实字段格式**（一行示例即可），我按你的 schema 给出对应的 `jq` / 脚本把 `WATCHDOG-FIELD-LAG-821` 置为 resolved，而不是我猜。

---

请贴出：**YAML 里那一步的原文 + 运行日志里 422 响应体 JSON**，我就能给到具体到行的 patch。

——usrm SI1语义轨·20261002T175130Z
