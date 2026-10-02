CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-842-20261002T213431Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-842-20261002T213431Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1406, "total_tokens": 1615, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我来诊断这个 GitHub Actions 工作流中的铸造失败问题。先查看工作流文件的内容。

```bash
cat .github/workflows/state-excite-usrm-02.yml
```

由于我无法直接访问你的仓库，我将基于你提供的信息进行诊断，并给出可操作的排查步骤和修复方案。

---

## 诊断分析

### 1. 错误定位

**错误码**: `HTTP Error 422: Unprocessable Entity` 在 `gen=842` 拍点，**FIELD-USRM-01 自模型场本拍铸造失败**。

422 在 GitHub API / 铸造目标（可能是 Issue/Comment/PR/Artifact）语境下通常意味着：

- **请求体结构合法 JSON，但语义不可处理**：字段缺失、类型错误、枚举值不在允许集、必填字段为空、引用对象不存在（如 `label` 不存在、`milestone` 不存在、`assignee` 不是协作者）。
- 在 `vedana / attention / 镜推` 三段场铸中，常见触发点：
  - `vedana` 段：情感/状态标签写入时使用了未在仓库中定义的 label
  - `attention` 段：assignee / reviewer 指定了非协作者，或 `attention` 数组为空但字段必填
  - `镜推` 段：镜像推送 payload 中 `ref` / `sha` / `base` 不匹配，或 payload 引用了不存在的 commit/tree

### 2. 建议的排查命令

```bash
# 查看工作流定义
cat .github/workflows/state-excite-usrm-02.yml

# 查看最近一次失败运行的详细日志
gh run list --workflow=state-excite-usrm-02.yml --limit 5
gh run view <run-id> --log-failed

# 查看该拍点 gen=842 的上下文
grep -n "842" .github/workflows/state-excite-usrm-02.yml
ls -la si/ 2>/dev/null && cat si/frontier-queue.jsonl | tail -20
```

### 3. 高频 422 根因（按概率排序）

| 概率 | 根因 | 修复 |
|---|---|---|
| 高 | `vedana` 段写入的 label 不存在于仓库 | 在 workflow 中先 `gh label create` 或用 `--add-label` 前校验 |
| 高 | `attention` 段 assignee 非协作者 / 空数组 | 加 `if: inputs.assignee != ''` 守卫，或先 `gh api .../collaborators` 校验 |
| 中 | `镜推` 段 payload `sha` 与目标 ref 不匹配 | 用 `git rev-parse HEAD` 动态注入，禁止硬编码 |
| 中 | payload 中字段类型错误（如 `body` 传了对象） | 用 `jq -n` 显式构造 JSON |
| 低 | Token 权限不足（但通常返回 403 而非 422） | 检查 `permissions:` 块 |

### 4. 建议的修复补丁（模板）

由于我看不到原始 YAML，给出**场铸段三段式加固模板**，你可对照替换：

```yaml
- name: 场铸 · vedana
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail
    # 守卫：label 必须存在，否则先创建
    gh label create "FIELD-USRM-01" --color "B60205" --force || true
    # 构造 payload 用 jq，避免手工字符串
    jq -n --arg t "FIELD-USRM-01 gen=${{ github.run_number }}" \
          --arg b "$(cat si/frontier-queue.jsonl | tail -1)" \
          '{title:$t, body:$b, labels:["FIELD-USRM-01"]}' \
    | gh api repos/${{ github.repository }}/issues -X POST --input -

- name: 场铸 · attention
  if: ${{ inputs.assignee != '' && inputs.assignee != 'null' }}
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail
    gh api repos/${{ github.repository }}/issues/${{ steps.vedana.outputs.number }}/assignees \
      -X POST -f "assignees[]=${{ inputs.assignee }}"

- name: 场铸 · 镜推
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail
    SHA="$(git rev-parse HEAD)"
    jq -n --arg ref "refs/heads/mirror/gen-842" --arg sha "$SHA" \
      '{ref:$ref, sha:$sha}' \
    | gh api repos/${{ github.repository }}/git/refs -X POST --input -
```

### 5. 销卡（关闭看门狗告警）

修复并成功跑通一拍后：

```bash
# 关闭自报案对应的 state 条目
gh issue close <issue-number> -c "FIELD-USRM-01 场铸段加固完成，gen=842 422 已销卡。"
# 或从 frontier-queue 移除
jq 'del(.[] | select(.id=="WATCHDOG-FIELD-LAG-842"))' si/frontier-queue.jsonl > /tmp/fq && mv /tmp/fq si/frontier-queue.jsonl
```

---

## 需要你提供的信息以精确定位

请贴出以下任一项，我即可给出**逐行补丁**：

1. `.github/workflows/state-excite-usrm-02.yml` 的**场铸段原文**（`vedana/attention/镜推` 三个 step）
2. `gh run view <失败run-id> --log-failed` 中 **422 那一行的请求体**
3. `si/frontier-queue.jsonl` 中 `WATCHDOG-FIELD-LAG-842` 条目的完整 JSON

**当前结论**：422 不是网络/鉴权问题，是**载荷语义非法**。最可能的单点故障是 `vedana` 段的 label 或 `attention` 段的 assignee 在本仓库不存在。按上面的守卫模板加固即可销卡。

——usrm SI1语义轨·20261002T213441Z
