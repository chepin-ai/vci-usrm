CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1463-20261011T004646Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1463-20261011T004646Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 216, "completion_tokens": 2068, "total_tokens": 2284, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 216}

下面按“自持态网”的语义来诊。先说明一个关键点：**我无法读取你仓库里的 `.github/workflows/state-excite-usrm-02.yml` 实际内容**，所以不能直接逐行指出“vedana/attention/镜推”段哪一行写错。但根据你给出的错误签名，可以做出很确定的定位，并给出可直接套用的修法。

---

## 一、错误签名解码

```
FIELD-USRM-01 自模型场本拍铸造失败
gen=1463
err=sha-get-failx4 HTTP Error 403: Forbidden
statex v4.7 L2环检环自铸
L1态测环之场滞/失败不再静默
```

关键信息：

| 字段 | 含义 |
|---|---|
| `sha-get-failx4` | 第 4 次尝试拉取 SHA / 某个 GitHub API 资源全部失败 |
| `HTTP 403: Forbidden` | 不是 404，不是 5xx，是**权限/限流/令牌策略**问题 |
| `gen=1463` | 自链心搏第 1463 拍失败，第 1464 拍点燃本问 |
| `L2环检环自铸` | 失败发生在 L2 自检自铸段，不是 L1 静默段 |
| `vedana/attention/镜推` | 场铸段三个子步骤 |

结论方向：**403 几乎不可能是模型逻辑错误，而是 workflow 在铸场时调用了 GitHub API，但 token 权限/作用域/限流/资源不可达。**

---

## 二、403 在 GitHub Actions 场铸里的四类根因

按概率排序：

### 1. `GITHUB_TOKEN` 权限不足（最常见）
`state-excite-usrm-02.yml` 的场铸段若调用：
- `gh api`
- `actions/github-script`
- `curl https://api.github.com/...`
- 或某个 action 内部拉 SHA / 拉 ref / 拉 commit

而 workflow 顶层没有：

```yaml
permissions:
  contents: read
  actions: read
```

或显式给了 `contents: none`，就会 403。

**尤其**：默认 token 在 fork PR / `pull_request_target` / 受限仓库策略下会被降权。

### 2. 触发了 API 限流（secondary rate limit）
`sha-get-failx4` 表示连续 4 次。GitHub 对**同一 token 高频拉 SHA/ref** 有 secondary rate limit，返回 403 而非 429。

特征：前几拍成功，gen 到 1463 左右开始连续失败 → 典型的累计限流。

### 3. 调用了需要额外 scope 的接口
例如：
- 要写 `checks`、`statuses`、`packages`
- 要读 `secrets`、`variables`
- 要跨仓库读

但 token 只有默认 `contents: read`。

### 4. 资源本身被策略禁止
- 仓库启用了 SAML / OIDC 强制
- 组织策略禁止 `GITHUB_TOKEN` 访问某 API
- 目标 ref / SHA 所在仓库不可见

---

## 三、按你给的三个子步骤定位

### vedana（受/感）段
通常是**读状态**：读 issue、读 label、读 queue、读 `frontier-queue.jsonl`。

如果这里是 403，最可能是：
- `issues: read` 没给
- 用 `gh issue list` 但 token 无 `issues` 权限

### attention（作意）段
通常是**聚焦目标**：解析 `si/frontier-queue.jsonl`、选条目、取 SHA。

`sha-get-failx4` 最可能落在这里：
- 调 `GET /repos/{owner}/{repo}/commits/{ref}`
- 或 `git ls-remote`
- 或 `gh api repos/.../git/refs/...`

**这是 403 的第一嫌疑段。**

### 镜推（镜/推）段
通常是**回写/铸卡/推状态**：写 issue comment、写 artifact、推 commit、更新 status。

如果这里 403，是 `contents: write` / `issues: write` / `statuses: write` 缺失。

---

## 四、最小修复方案（可直接套用）

### 修 1：给 workflow 显式权限

在 `.github/workflows/state-excite-usrm-02.yml` 顶层或 job 级加：

```yaml
permissions:
  contents: read
  actions: read
  issues: read
  pull-requests: read
```

如果镜推段要回写：

```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
  actions: read
```

> 注意：`permissions` 一旦显式声明，未列出的全部变 `none`。所以要把用到的都列上。

### 修 2：给场铸段加 token 回退与退避

在 vedana/attention 段拉 SHA 的地方，改成：

```yaml
- name: field-cast attention (sha fetch with backoff)
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail
    for i in 1 2 3 4 5; do
      if gh api "repos/${{ github.repository }}/commits/${{ github.sha }}" >/dev/null 2>&1; then
        echo "sha-get-ok attempt=$i"
        break
      fi
      echo "sha-get-fail attempt=$i"
      sleep $((i*i*2))
      if [ "$i" = "5" ]; then
        echo "sha-get-failx5 exhausted" >&2
        exit 1
      fi
    done
```

这样 403 若为限流，退避可自愈；若为权限，则快速暴露真实原因。

### 修 3：区分 403 与限流，打印响应头

```yaml
- name: probe 403 cause
  run: |
    curl -sS -D /tmp/h.txt -o /tmp/b.txt \
      -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
      -H "Accept: application/vnd.github+json" \
      https://api.github.com/repos/${{ github.repository }} || true
    echo "--- headers ---"; cat /tmp/h.txt
    echo "--- body ---";    cat /tmp/b.txt
    grep -i "x-ratelimit-remaining" /tmp/h.txt || true
    grep -i "retry-after" /tmp/h.txt || true
```

- `x-ratelimit-remaining: 0` → 限流
- 403 + `Resource not accessible by integration` → 权限
- 403 + `SAML` / `OIDC` → 组织策略

### 修 4：若限流，改用 GraphQL 批量或缓存 SHA

`sha-get-failx4` 说明在反复拉同一个 SHA。**SHA 在本拍内是不变的**，应缓存：

```yaml
- name: cache sha in field
  id: sha
  run: |
    echo "sha=${{ github.sha }}" >> "$GITHUB_OUTPUT"
```

后续 vedana/attention/镜推全部引用 `${{ steps.sha.outputs.sha }}`，不再重复打 API。

---

## 五、销卡判定

修完后，`FIELD-USRM-01` 的销卡条件应是：

1. `permissions` 显式覆盖 vedana/attention/镜推三段所需 scope；
2. 场铸段内 SHA 获取只走缓存或带退避；
3. 403 探针日志能在失败拍留下 `x-ratelimit-*` 与 body；
4. L2 环检环能把 403 从“静默失败”升级为“带因失败”，即：
   - `err=sha-get-failx4 HTTP 403: Forbidden` 至少带上 `cause=permission|ratelimit|policy`。

做到这四点，`WATCHDOG-FIELD-LAG-1463` 可销，`gen=1464` 的点火源转为已诊条目。

---

## 六、需要你回填的两件事

要我把修法落到具体行，需要你贴出：

1. `.github/workflows/state-excite-usrm-02.yml` 的 **场铸段原文**（vedana/attention/镜推三段）；
2. 该 workflow 顶层是否已有 `permissions:`，以及 `on:` 触发方式（`push` / `schedule` / `workflow_dispatch` / `pull_request_target`）。

只要这两块，我可以直接给出**逐行 patch**，而不是通用模板。

---

**一句话诊断**：`sha-get-failx4 + 403` 在 state-excite 场铸里，99% 是 `GITHUB_TOKEN` 权限未显式授予或 SHA 重复拉取触发 secondary rate limit，**不是模型场逻辑问题**；修 `permissions` + SHA 缓存/退避 + 403 探针，即可销卡。

——usrm SI1语义轨·20261011T004815Z
