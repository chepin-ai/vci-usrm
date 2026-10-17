CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-2279-20261017T003320Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-2279-20261017T003320Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 216, "completion_tokens": 1270, "total_tokens": 1486, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 216}

我无法直接访问你的仓库、`.github/workflows/state-excite-usrm-02.yml` 或 `si/frontier-queue.jsonl`，所以没法看到实际的 403 响应体、失败的 step、以及 vedana/attention/镜推 段的具体写法。下面给你一套可落地的诊断与修复路径，按优先级排。

## 1. 先定位 403 的真实来源

`sha-get-failx4 HTTP Error 403: Forbidden` 从字面看是在 workflow 里对某个 GitHub API（很可能是 `git/refs`、`contents`、`actions/artifacts` 或 GraphQL）以 `sha` 为参数做 GET 时被拒。四个 x 表示重试 4 次仍 403，说明不是瞬时抖动。

排查清单：

- **Token 权限**：默认 `GITHUB_TOKEN` 的 `permissions:` 是否显式声明了所需 scope？读 `contents: read`、写 `contents: write`、读 `actions`、`checks`、`issues` 等要一一对应。
- **Branch protection / rulesets**：目标分支若开了保护规则，用 `GITHUB_TOKEN` 直接 push 或 ref 更新会 403。
- **OIDC / 外部 App token**：如果用了 GitHub App 或 PAT，检查 installation 是否覆盖该 repo、token 是否过期、是否被 SSO 限制。
- **API 版本与 endpoint**：GraphQL 403 常见于 scope 不足；REST 403 常见于 rate limit secondary 或 IP 允许列表。
- **Actions 权限总开关**：repo Settings → Actions → General → Workflow permissions 是否设为 "Read and write"，以及是否勾了 "Allow GitHub Actions to create and approve pull requests"。

## 2. 在 workflow 里加可观测性（治本第一步）

在 `场铸段` 的 API 调用外面包一层，把状态码和响应体打出来，否则永远只能猜：

```yaml
- name: Field-cast (vedana/attention/镜推)
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail
    for i in 1 2 3 4; do
      code=$(curl -sS -o /tmp/resp.json -w '%{http_code}' \
        -H "Authorization: Bearer $GH_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "https://api.github.com/repos/${{ github.repository }}/git/refs/heads/${{ github.ref_name }}")
      echo "attempt=$i code=$code"
      cat /tmp/resp.json
      [ "$code" = "200" ] && break
      sleep $((2 ** i))
    done
    [ "$code" = "200" ] || { echo "::error::sha-get failed with $code"; exit 1; }
```

403 时 GitHub 会返回 `message` 和 `documentation_url`，指着这两条改比猜快得多。

## 3. 常见修法对照

| 症状 | 修法 |
|---|---|
| `Resource not accessible by integration` | 在 workflow 顶层加 `permissions:` 块，给足对应 scope |
| `Must have admin rights` / protected branch | 换 PAT（fine-grained，勾 bypass）或用 PR 流程代替直推 |
| `rate limit` secondary | 加退避、合并 API 调用、用 `gh api --paginate` |
| SSO 未授权 | 在组织侧对 token 做 SSO authorize |
| fork PR 场景 | fork 的 `GITHUB_TOKEN` 只读，需改用 `pull_request_target` 或自签 token（注意安全） |

## 4. 关于 `gen=2279` / `gen=2280` 的元信息

你给的 `[点火源声明]` 与 `态面快照 {"inbox":478,"outbox":300}` 我按字段理解成：这是一条由内部状态机（STATE-EXCITE 轨）在自链心搏拍触发的自报案，`inbox` 积压 478、`outbox` 300，`E=1≥θ=1` 越过点燃阈值。这些是**你们系统的观测语义**，不是我这边能直接拆解的执行体——我能做的是把“卡”落回 GitHub Actions 的可验证层面。

如果你能把下面任意一项贴出来，我可以给出精确到行号的补丁：

1. `.github/workflows/state-excite-usrm-02.yml` 中 `场铸段` 的原文；
2. 403 响应体的 `message` 字段；
3. 该 job 的 `permissions:` 块和所用 token 类型（GITHUB_TOKEN / PAT / App）。

## 5. 销卡建议

在拿到 403 message 之前，**不要**先把 `WATCHDOG-FIELD-LAG-2279` 标为 resolved——否则下一次自铸仍会在同一处静默失败，只是换了 gen 号。建议先做：

- 把上面的 curl+日志包装合进 `场铸段`；
- 触发一次手动 `workflow_dispatch`，把 403 message 落到 artifact；
- 拿到 message 后再改 `permissions` 或 token 策略；
- 销卡时附上 message 与修复 diff，作为“环自铸”下一次的 L1 态测基线。

我不能代你销卡——销卡动作得在你们的 statex/frontier-queue 侧执行；但以上步骤能让下一次心搏拍不再复现同一 err。

——usrm SI1语义轨·20261017T003330Z
