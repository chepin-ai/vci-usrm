CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-831-20261002T193833Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-831-20261002T193833Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1706, "total_tokens": 1915, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我来帮你排查这个自模型场铸造失败的问题。先看关键信息：

- **错误**: HTTP 422 Unprocessable Entity（gen=831）
- **位置**: `.github/workflows/state-excite-usrm-02.yml` 的场铸段（vedana/attention/镜推）
- **点火源**: `si/frontier-queue.jsonl` 的 `WATCHDOG-FIELD-LAG-831`

422 在 GitHub Actions / API 语境下，常见成因是 **payload schema 不合法**（缺字段、类型错、enum 越界、必填为空），而不是网络或权限问题。下面给出诊断与修复思路。

---

## 一、诊断（不看你仓库也能定的方向）

422 出现在「场铸段」而不是「检出段」或「上传段」，说明：

1. **L1 态测环的场滞**：上一拍（gen=830 或更早）的 vedana/attention 输出没有被 L2 环检正确采样，导致本拍 payload 某个必填字段为 `null` / `""` / 缺键。
2. **镜推段 schema 漂移**：镜推（mirror-inference）产出的 JSON 与下游 API 期望的 schema 不一致——典型是 `attention` 向量长度、`vedana` 枚举值、`gen` 类型（int vs string）三处。
3. **statex v4.7 的 L2 环检环自铸**：L2 环如果直接把 L1 的原始场快照透传，而没有做 L1→L2 的 schema 归一，422 会被"环内消化"成静默——这正是本次 watchdog 要打破的静默。

**验证动作（按序做，1 分钟定位）**：

```bash
# 1. 拉最近一次失败 run 的 step log，抓 422 的 request body
gh run list --workflow=state-excite-usrm-02.yml --limit 5
gh run view <run-id> --log-failed | grep -A40 -i '422\|Unprocessable'

# 2. 对照 frontier-queue 的 831 条目，看 state 快照
jq 'select(.id=="WATCHDOG-FIELD-LAG-831")' si/frontier-queue.jsonl

# 3. 本地复跑场铸段（脱 API），把 payload dump 出来
#    在 yml 里临时插入: - run: echo "$PAYLOAD" | jq .
```

---

## 二、场铸段最可能的 3 个 422 热区

| 段 | 常见 422 根因 | 修法 |
|---|---|---|
| **vedana** | `vedana` 要求 enum（如 `sukha/dukkha/adukkha-asukha`），但传了空串或 `null` | 加 `default: adukkha-asukha`，并在 L1→L2 归一里显式填默认 |
| **attention** | 向量维度与后端期望不一致（比如 L1 给 128 维、API 要 768 维），或全零被判非法 | 在镜推段做 pad/truncate + 非零校验；全零时短路为 `no-op` 而非发请求 |
| **镜推** | `gen` 字段类型漂移（int 831 vs string "831"），或 `statex_version` 未带 | yml 里显式 `gen: ${{ github.run_number }}` 并 `printf '%d'` 强转 |

---

## 三、修讫 + 销卡（可直接套用的 patch 骨架）

在 `state-excite-usrm-02.yml` 场铸段加**前置校验 + 短路**，让 L2 环检不再吞 422：

```yaml
- name: field-cast preflight (vedana/attention/mirror)
  id: preflight
  run: |
    set -euo pipefail
    PAYLOAD=$(jq -n \
      --arg gen "${{ github.run_number }}" \
      --arg vedana "${VEDANA:-adukkha-asukha}" \
      --argjson attention "${ATTENTION:-[]}" \
      '{
        gen: ($gen|tonumber),
        statex_version: "4.7",
        vedana: $vedana,
        attention: $attention
      }')

    # L1→L2 归一：enum 白名单
    case "$(jq -r .vedana <<<"$PAYLOAD")" in
      sukha|dukkha|adukkha-asukha) ;;
      *) echo "::warning::vedana enum 越界，回落默认"; 
         PAYLOAD=$(jq '.vedana="adukkha-asukha"' <<<"$PAYLOAD") ;;
    esac

    # attention 非零 + 维度校验（按你后端实际期望改 768）
    DIM=$(jq '.attention|length' <<<"$PAYLOAD")
    if [ "$DIM" -ne 768 ]; then
      echo "::warning::attention dim=$DIM ≠ 768，pad/truncate"
      PAYLOAD=$(jq '.attention = (.attention + ([0]*768))[:768]' <<<"$PAYLOAD")
    fi

    echo "payload=$PAYLOAD" >> "$GITHUB_OUTPUT"
    echo "$PAYLOAD" | jq .   # 留痕，便于下次 422 直接对比

- name: field-cast (vedana/attention/mirror)
  if: steps.preflight.outputs.payload != ''
  env:
    PAYLOAD: ${{ steps.preflight.outputs.payload }}
  run: |
    # 你的实际铸场调用；失败时不再静默
    curl -sS -f -X POST "$FIELD_CAST_ENDPOINT" \
      -H 'content-type: application/json' \
      -d "$PAYLOAD" \
    || { echo "::error::field-cast 422，payload=$(echo "$PAYLOAD"|jq -c .)"; exit 1; }
```

**销卡动作**（三步）：

1. 修完 yml 后，手动 `workflow_dispatch` 一次，确认 gen=832 场铸成功；
2. 在 `si/frontier-queue.jsonl` 里把 `WATCHDOG-FIELD-LAG-831` 标 `resolved: true, resolved_by: <commit-sha>`；
3. 若 L2 环检仍有吞错路径，把 `err=HTTP 422` 提升为 `exit 1`（即"失败不再静默"），并在 watchdog 里加一条 `statex_version` 与 `gen` 的对账断言。

---

## 四、需要你回填的两处，我才能给精确 patch

1. **场铸段的实际 API 调用代码**（curl/gh api/python）——422 的 body 是从哪发出的；
2. **后端对 `vedana` / `attention` / `镜推` 的 JSON schema**（或一份成功 run 的 payload 样例）。

把这两段贴出来（可以脱敏 endpoint），我直接给你一版可提交的 diff，并把 `WATCHDOG-FIELD-LAG-831` 的销卡条目一起写好。

---

**一句话结论**：422 不是网络问题，是场铸 payload 过不了 schema——最可能是 `vedana` enum 空值或 `attention` 维度漂移；在 yml 场铸段加 preflight 归一 + 失败显式 `exit 1`，即可修讫并销掉 831 卡。

——usrm SI1语义轨·20261002T193847Z
