CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-847-20261002T222732Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-847-20261002T222732Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1671, "total_tokens": 1880, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我来诊断这个 GitHub Actions 工作流的场铸失败问题。先读取工作流文件，定位 422 的具体抛出点。

**诊断路径：**
1. 读 `.github/workflows/state-excite-usrm-02.yml`
2. 定位场铸段（vedana / attention / 镜推）
3. 复现 422 语境 → 修 → 销卡

---

## 一、读文件

我需要先看实际内容才能给出精确修复。请确认或直接贴出该文件。不过基于错误特征（`HTTP 422 Unprocessable Entity` 来自 GitHub API 或某个 POST 端点），我先给出**高概率根因分类**，你对照文件即可锁定：

---

## 二、422 的三种典型成因（按概率排序）

### A. GitHub API 调用体 schema 不合法（最常见）
422 = **请求体语义可解析但字段非法**。在场铸段里典型表现为：

- `issues.create` / `pulls.create` / `repos.createDispatchEvent` 等：
  - `title` 缺失或全空白
  - `body` 含非法 UTF-8 / 裸控制字符（场滞文本里有 `\x00` 或截断的多字节）
  - `labels` 传了字符串而非数组
  - `ref` 不存在（镜推 target 分支未创建就 push）
- `dispatchEvent` 的 `event_type` 含空格/非法字符

→ **镜推（mirror-push）段** 最容易踩：把 `gen=847` 的态文本作为 `client_payload`，其中若含裸 `\n` 之外的怪字符或非 JSON 化对象，直接 422。

### B. REST 端点路径参数非法
- 调 `POST /repos/{owner}/{repo}/...` 时 `owner/repo` 从 env 注入但被截断（如 `${{ }}` 未加引号被 shell 分词）
- `vedana` 段若构造了 `issue_number` 为字符串 `"847 "` 带尾空格 → 422

### C. 分支保护 / 权限位（少数会返 422）
- attention 段强制 push 到受保护分支且绕过参数格式错

---

## 三、定位片段（请你核对下列模式）

请在该 yml 的场铸段搜索以下**易错写法**：

```yaml
# ✗ 错误 1：未 JSON 化，多行文本直接塞 payload
client_payload: ${{ steps.vedana.outputs.text }}

# ✓ 修复：显式 toJSON
client_payload: ${{ toJSON(steps.vedana.outputs.text) }}
```

```yaml
# ✗ 错误 2：labels 传字符串
labels: "field-lag,watchdog"

# ✓ 修复
labels: ["field-lag", "watchdog"]
```

```yaml
# ✗ 错误 3：body/title 从 shell 变量拼且含尾随换行/空格
title: ${{ env.CARD_TITLE }}

# ✓ 修复：trim
run: echo "TITLE=$(echo "$RAW" | tr -d '\r' | sed 's/[[:space:]]*$//')" >> $GITHUB_ENV
```

```yaml
# ✗ 错误 4：ref 未校验存在性（镜推目标分支不存在）
ref: usrm-02-$(date +%s)   # 若同一 run 内后续未 push 该 ref → 422

# ✓ 修复：先 push 分支再 dispatch，或改用默认分支
```

```yaml
# ✗ 错误 5：event_type 含非法字符
event_type: "usrm field lag 847"

# ✓ 修复（仅允许 a-zA-Z0-9_-）
event_type: "usrm_field_lag_847"
```

---

## 四、通用防御性修补（可直接套用）

在 vedana / attention / 镜推三段入口加一道**422 预校验 + 重试降级**：

```yaml
- name: field-cast preflight (422 guard)
  id: guard
  shell: bash
  run: |
    set -euo pipefail
    # 1. 清理非法字符
    clean() { printf '%s' "$1" | tr -d '\000-\010\013\014\016-\037' | sed 's/[[:space:]]*$//'; }
    TITLE="$(clean "${RAW_TITLE:-field-lag-847}")"
    BODY="$(clean "${RAW_BODY:-}")"
    [ -n "$TITLE" ] || { echo "::error::title empty after clean"; exit 1; }
    # 2. 校验 env 关键量非空且格式合法
    [[ "${GEN:-}" =~ ^[0-9]+$ ]] || { echo "::error::gen not numeric: ${GEN:-}"; exit 1; }
    echo "TITLE=$TITLE" >> $GITHUB_ENV
    {
      echo "BODY<<EOF"
      echo "$BODY"
      echo "EOF"
    } >> $GITHUB_ENV

- name: field-cast (with 422 typed fallback)
  uses: actions/github-script@v7
  with:
    script: |
      const payload = {
        title: process.env.TITLE,
        body: process.env.BODY,
        labels: ['field-lag','watchdog'],
      };
      try {
        await github.rest.issues.create({
          owner: context.repo.owner,
          repo: context.repo.repo,
          ...payload,
        });
      } catch (e) {
        if (e.status === 422) {
          core.error(`422 schema reject: ${JSON.stringify(e.response?.data?.errors||[])}`);
          // 降级：去掉 labels 重试（labels 非法是最常见 422）
          await github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: payload.title,
            body: payload.body,
          });
        } else { throw e; }
      }
```

并用 `actions/github-script` 的 `e.response.data.errors` 把 422 的**具体字段**打到日志——这是销卡前必须留的证据：

```
422 errors: [{resource:"Issue", field:"labels", code:"invalid"}]
```

---

## 五、请给我这两样，我直接出补丁 diff

1. `.github/workflows/state-excite-usrm-02.yml` 全文（或场铸段 vedana/attention/镜推 三块）
2. 失败 run 的 422 响应体（若 workflow 里已打印 `e.response.data`）

拿到后我输出：
- **根因判定**（A/B/C 哪一类）
- **最小 diff**（只改违规行，不动场滞逻辑）
- **销卡动作**：`si/frontier-queue.jsonl` 里把 `WATCHDOG-FIELD-LAG-847` 标 `resolved`，附 `fix_commit` 与 `422_field` 字段，让 L1 环测不再误报静默。

---

**当前状态回执**：读文件前无法 100% 锁定 422 字段，但按场铸段结构，**镜推段的 `client_payload` 未 `toJSON` 化**为最高概率根因（多行态文本裸塞 → GitHub 解析失败 → 422）。请贴文件确认，我即可销卡。

——usrm SI1语义轨·20261002T222742Z
