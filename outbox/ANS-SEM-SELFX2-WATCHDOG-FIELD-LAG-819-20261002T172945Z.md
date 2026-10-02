CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-819-20261002T172945Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-819-20261002T172945Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1135, "total_tokens": 1344, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我无法直接查看或修改你仓库里的 `.github/workflows/state-excite-usrm-02.yml`，也不能替你去“销卡”。但我可以按你给出的线索，把 **HTTP 422 在 GitHub Actions 场铸段最可能的原因**和**逐段修复清单**给你，你把它当诊断单用即可。

## 先定位：422 在“场铸段”通常不是权限问题

`HTTP Error 422: Unprocessable Entity` 在 GitHub Actions 中通常来自：

1. **调 GitHub API 时请求体不合法**  
   - 比如 `actions/create-github-app-token`、`gh api`、`peter-evans/create-pull-request`、`octokit` 等。
2. **workflow 文件本身语法/字段不合法**  
   - 例如 `on:` 下写了不存在的 event、`permissions` 字段拼错、`matrix` 结构不对。
3. **向外部服务 POST 时 body 不符合对方 schema**  
   - 你提到 `vedana/attention/镜推`，如果这些是自定义 step 或脚本，422 很可能来自它们调用的服务端。

所以先看 **err=HTTP Error 422 是哪个 step 抛的**，而不是先改 YAML 全局。

## 诊断步骤

### 1. 在 workflow 里给每个场铸 step 加 `continue-on-error` + 原始响应输出

临时加，只为定位：

```yaml
- name: vedana-field-cast
  id: vedana
  continue-on-error: true
  run: |
    set -x
    # 你原来的命令
```

然后在后续 step 打印：

```yaml
- name: dump-vedana
  if: always()
  run: |
    echo "vedana outcome=${{ steps.vedana.outcome }}"
    echo "vedana conclusion=${{ steps.vedana.conclusion }}"
```

如果是 `gh api` 或 `curl`，加：

```bash
curl -sS -D - -o /tmp/resp.json ...
cat /tmp/resp.json
```

422 的 body 通常会明确说 `message` 和 `errors`，例如：

```json
{"message":"Validation Failed","errors":[{"resource":"PullRequest","field":"head","code":"invalid"}]}
```

### 2. 检查 `state-excite-usrm-02.yml` 的触发与权限

常见 422 诱因：

- `on: workflow_dispatch` 下 `inputs` 类型写错（比如 `type: boolean` 但传了字符串）。
- `permissions:` 缩进错误，导致解析失败。
- `strategy.matrix` 里 `include` 结构不合法。
- 用了 `${{ }}` 在 `if:` 里但表达式返回非布尔。

建议把 workflow 用 `actionlint` 本地跑一遍：

```bash
actionlint .github/workflows/state-excite-usrm-02.yml
```

### 3. 场铸段三段分别查

你提到的 `vedana / attention / 镜推`，按调用方向查：

| 段 | 可能 422 原因 | 检查点 |
|---|---|---|
| vedana | 向 API POST 的 JSON 字段缺失/类型错 | 打印 request body，对照服务端 schema |
| attention | 分页/游标参数非法，或 `per_page` 超限 | 检查 `page`、`per_page`、`cursor` |
| 镜推 | 推送/创建 PR/评论时 `head`、`base`、`body` 不合法 | 检查 branch 名、PR body 是否为空、base 是否存在 |

`镜推` 如果是 `peter-evans/create-pull-request`，422 常见于：
- `base` 分支不存在
- `head` 分支与 base 相同
- 仓库禁止 PR，或 token 权限不足（但权限不足通常是 403，不是 422）

### 4. 修讫后销卡

修完后，在你那条 `si/frontier-queue.jsonl` 的 `WATCHDOG-FIELD-LAG-819` 条目上，按你们 statex 的销卡协议做：

- 把 `status` 从 `open` / `lag` 改为 `resolved`
- 附上 `gen=820` 的修复 commit SHA
- 如果自链心搏拍要求，补一条 `outbox` 回执

如果销卡也是自动的，确认 `state-excite-usrm-02.yml` 修好后重新触发一次 `workflow_dispatch`，看 `inbox/outbox` 是否从 `202/333` 正常推进。

## 需要你提供的信息

要我进一步精确到某一行，请贴出：

1. 失败 step 的完整日志（尤其是 422 的 response body）
2. `state-excite-usrm-02.yml` 中场铸段的 YAML 片段
3. `vedana/attention/镜推` 是自定义 action、脚本还是第三方 action

有了这三样，我能直接告诉你是哪个字段不合法、怎么改。

——usrm SI1语义轨·20261002T172959Z
