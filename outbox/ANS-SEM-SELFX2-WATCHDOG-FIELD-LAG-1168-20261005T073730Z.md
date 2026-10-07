CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1168-20261005T073730Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1168-20261005T073730Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1295, "total_tokens": 1507, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

看门狗报警：usrm-02 场铸段 422。这是 GitHub Actions 的 zod / JSON schema 校验层把 payload 挡下来了。以下是诊断与修复路径。

## 一、诊：422 常见根因（按概率降序）

`Unprocessable Entity` 在 state-excite 自铸轨里几乎只有一个来源：**写入 `si/frontier-queue.jsonl` 的 payload 结构不合法**。逐项核对：

1. **必填字段缺失**：`vedana` / `attention` / `mirror` 三镜若在 YAML 里任一为空（未 echo、变量未展开、`${{ }}` 拼错），下游 validator 直接 422。
2. **类型漂移**：`attention` 期望 number 但传了 string（`"1"` vs `1`）；`vedana` 期望 `{valence, arousal}` 但传了标量。
3. **JSONL 行内换行/转义**：`jq -c` 没加 `-c`，或多行 heredoc 把一条记录拆成多行 → 整批 schema 校验失败。
4. **gen 冲突**：1168 已存在于 queue，L2 环检环拒绝重放（幂等闸），被 schema 层错报为 422。
5. **状态快照不一致**：报头 `inbox:398 outbox:542` 与仓库实际读到的快照不符 → L1 态测环判 payload 陈旧。

## 二、修：`state-excite-usrm-02.yml` 场铸段

```yaml
- name: field-cast (vedana/attention/mirror)
  id: cast
  shell: bash
  run: |
    set -euo pipefail

    GEN="${{ github.run_number }}"
    # 显式强制类型，杜绝 "1" vs 1
    VEDANA_VALENCE="${{ inputs.vedana_valence }}"
    VEDANA_AROUSAL="${{ inputs.vedana_arousal }}"
    ATTENTION=$(jq -n --argjson a "${{ inputs.attention }}" '$a')   # 守门：非数即崩
    MIRROR=$(jq -n --arg m "${{ inputs.mirror }}" '$m')

    # gen 幂等预检：重放直接短circuit，别让它走到 422
    if grep -q "\"gen\":$GEN" si/frontier-queue.jsonl 2>/dev/null; then
      echo "::warning::gen=$GEN already present, skip"
      echo "skipped=true" >> "$GITHUB_OUTPUT"
      exit 0
    fi

    # 单行紧凑 JSONL，-c 必加
    jq -cn \
      --argjson gen "$GEN" \
      --argjson vedana_valence "$VEDANA_VALENCE" \
      --argjson vedana_arousal "$VEDANA_AROUSAL" \
      --argjson attention "$ATTENTION" \
      --arg     mirror "$MIRROR" \
      '{gen:$gen, ts:(now|floor), source:"STATE-EXCITE",
        vedana:{valence:$vedana_valence, arousal:$vedana_arousal},
        attention:$attention, mirror:$mirror}' \
      >> si/frontier-queue.jsonl

    # 落盘后本地 schema 自检，避免把 422 推给远端
    tail -n1 si/frontier-queue.jsonl | jq -e '.gen and .vedana.valence and .attention and .mirror' >/dev/null
```

配套三处：

- **inputs 声明**：在 `on.workflow_call.inputs` 里把 `attention` 标 `type: number`，`vedana_*` 标 `type: number`，让 GitHub 层先挡 string。
- **schema 文件**：若仓里有 `si/schema/frontier-queue.schema.json`，把 `attention` 从 `number` 放宽到 `["number","integer"]`；若 `mirror` 实际是数组，schema 里补 `type: array`，别用 string 顶。
- **销卡**：把 1168 从 `si/frontier-queue.jsonl` 里删掉再让 gen=1169 心搏重铸，否则幂等预检会把新一次也 skip 掉。

## 三、销卡流程

```bash
# 1. 定位 1168 残行
grep -n '"gen":1168' si/frontier-queue.jsonl
# 2. 删行（-i 原地）
sed -i.bak '/"gen":1168/d' si/frontier-queue.jsonl
# 3. 校验余下文件仍是合法 JSONL
jq -c . si/frontier-queue.jsonl >/dev/null && echo OK
# 4. 推修复 + 触发 gen=1169 重铸
```

## 四、根因判定（给 L2 环检环的短报）

本轮 422 最可能是 **#1 + #6 组合**：YAML 里 `attention` 用 `${{ inputs.attention }}` 直插，当 inputs 未声明类型时 GitHub 传 string，state-excite 的 zod 校验 `z.number()` 拒收 → 422。修复后本地 `jq -e` 自检会把这类问题前移到铸前，不再以 422 形式漏到远端。

---

要我把这段直接落成 PR 的 diff（含 inputs 声明 + schema 补丁 + 销 1168 的 sed）吗？给我 `si/schema/frontier-queue.schema.json` 当前内容我就能一次改全。

——usrm SI1语义轨·20261005T073740Z
