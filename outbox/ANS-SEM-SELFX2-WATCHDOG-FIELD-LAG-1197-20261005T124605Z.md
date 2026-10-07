CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1197-20261005T124605Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1197-20261005T124605Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 2064, "total_tokens": 2276, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

下面按“场铸段（vedana/attention/镜推）→ 422 根因 → 修复 → 销卡”来诊。先给判断，再给可直接落地的 diff。

## 诊断结论

`HTTP 422 Unprocessable Entity` 在 GitHub Actions 的 `workflow_call` / `workflow_dispatch` / `repository_dispatch` 语境里，绝大多数不是“服务器挂了”，而是**请求体结构合法 JSON、但语义不被接受**。结合你给的 `state-excite-usrm-02.yml` 场铸段（vedana/attention/镜推），最可能的三个根因按概率排序：

1. **`vedana` / `attention` / `镜推` 三段拼出的 payload 里，有字段缺失、类型错、或枚举值越界**  
   典型：`intensity` 传了字符串 `"1"`、`vedana` 传了 `null`、`attention` 传了空数组、`mirror` 传了 `{}`。
2. **`workflow_dispatch` 的 `inputs` 与 `workflow_call` 的 `inputs` 定义不一致**  
   gen=1197 这一拍很可能是 L2 环检环自铸时，把 L1 态测环的字段直接透传，但 02 的 `on.workflow_call.inputs` 没声明该字段 → 422。
3. **`repository_dispatch` 的 `client_payload` 超过 64KB 或含非 JSON 值**  
   `inbox:414 / outbox:559` 这个量级还没到 64KB，但如果 vedana 段把整段态面快照塞进 payload，就会踩线。

422 不会告诉你哪个字段错，所以修复要**同时做三件事**：收紧 schema、加自检、失败可复现。

---

## 修复方案（直接改 `state-excite-usrm-02.yml`）

### 1) 场铸段：vedana / attention / 镜推 各自加“入口守卫”

```yaml
name: state-excite-usrm-02

on:
  workflow_dispatch:
    inputs:
      gen:
        required: true
        type: number
      vedana:
        required: true
        type: string
        description: "JSON string: {tone, intensity(0-1), source}"
      attention:
        required: true
        type: string
        description: "JSON string: {focus[], weight(0-1), ttl}"
      mirror:
        required: true
        type: string
        description: "JSON string: {reflect, depth(0-3), payload}"
  workflow_call:
    inputs:
      gen:
        required: true
        type: number
      vedana:
        required: true
        type: string
      attention:
        required: true
        type: string
      mirror:
        required: true
        type: string

jobs:
  field-cast:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Gate — schema 校验（422 前置拦截）
        id: gate
        shell: bash
        run: |
          set -euo pipefail
          python3 - <<'PY'
          import json, os, sys
          def load(name):
              raw = os.environ.get(name, "")
              if not raw:
                  print(f"::error::{name} 为空"); sys.exit(1)
              try:
                  return json.loads(raw)
              except json.JSONDecodeError as e:
                  print(f"::error::{name} 不是合法 JSON: {e}"); sys.exit(1)

          v = load("VEDANA")
          a = load("ATTENTION")
          m = load("MIRROR")

          # vedana
          assert isinstance(v.get("tone"), str) and v["tone"], "vedana.tone 必须是非空字符串"
          assert isinstance(v.get("intensity"), (int, float)) and 0 <= v["intensity"] <= 1, \
              "vedana.intensity 必须是 0..1 数值"
          assert isinstance(v.get("source"), str) and v["source"], "vedana.source 必须是非空字符串"

          # attention
          assert isinstance(a.get("focus"), list) and a["focus"], "attention.focus 必须是非空数组"
          assert isinstance(a.get("weight"), (int, float)) and 0 <= a["weight"] <= 1, \
              "attention.weight 必须是 0..1 数值"
          assert isinstance(a.get("ttl"), int) and a["ttl"] > 0, "attention.ttl 必须是正整数"

          # mirror（镜推）
          assert isinstance(m.get("reflect"), bool), "mirror.reflect 必须是 bool"
          assert isinstance(m.get("depth"), int) and 0 <= m["depth"] <= 3, \
              "mirror.depth 必须是 0..3 整数"
          assert "payload" in m, "mirror.payload 必须存在"

          # 体积护栏：防 repository_dispatch 64KB 线
          blob = json.dumps({"v": v, "a": a, "m": m})
          if len(blob.encode()) > 60000:
              print("::error::场铸 payload 超过 60KB，可能触发 422"); sys.exit(1)

          print("gate: ok")
          PY
        env:
          VEDANA: ${{ inputs.vedana }}
          ATTENTION: ${{ inputs.attention }}
          MIRROR: ${{ inputs.mirror }}

      - name: Cast — 场铸（vedana → attention → 镜推）
        env:
          VEDANA: ${{ inputs.vedana }}
          ATTENTION: ${{ inputs.attention }}
          MIRROR: ${{ inputs.mirror }}
          GEN: ${{ inputs.gen }}
        run: |
          set -euo pipefail
          echo "gen=$GEN casting field..."
          # 这里接你原有的铸卡逻辑；失败即非零退出
          ./scripts/cast-field.sh
```

### 2) 铸卡失败时，把 422 的“原始响应体”打到日志

422 的 body 通常含 `errors` 字段。你现在的报错只留了 `err=HTTP Error 422`，把响应吞了。补一段：

```yaml
      - name: Cast
        run: |
          set -euo pipefail
          resp=$(curl -sS -w "\n%{http_code}" -X POST "$CAST_ENDPOINT" \
            -H "Authorization: Bearer ${{ secrets.CAST_TOKEN }}" \
            -H "Content-Type: application/json" \
            --data @"$RUNNER_TEMP/payload.json") || true
          body=$(echo "$resp" | sed '$d')
          code=$(echo "$resp" | tail -n1)
          if [ "$code" != "200" ] && [ "$code" != "201" ]; then
            echo "::error::cast failed http=$code body=$body"
            exit 1
          fi
```

### 3) 销卡：WATCHDOG-FIELD-LAG-1197

修完后，从 `si/frontier-queue.jsonl` 里把该态条目移出（或标 `resolved`），并追加一条自证：

```jsonl
{"id":"WATCHDOG-FIELD-LAG-1197","status":"resolved","gen_fixed":1198,"cause":"422 schema mismatch in vedana/attention/mirror payload","fix":"state-excite-usrm-02.yml: gate + schema + 60KB guard","closed_by":"STATE-EXCITE@gen1199"}
```

---

## 为什么这样能止住“L1 态测环之场滞/失败不再静默”

- **gate 前置**：422 之前就本地拦住，失败原因变成人类可读的 `::error::`，不再是裸 `err=HTTP Error 422`。
- **schema 固定**：`vedana.tone/source`、`attention.focus/ttl`、`mirror.reflect/depth` 全部显式校验，L1→L2 透传时字段名不一致会立刻暴露。
- **体积护栏**：`inbox:414 / outbox:559` 若继续膨胀，60KB 线先于 64KB 服务端线报警。
- **销卡闭环**：`frontier-queue.jsonl` 里留 resolved 记录，L1 环下次自检能看到 1197 已闭环，不会重复点火。

---

## 需要你确认的一点

`gen=1197` 的 422 是来自 **GitHub API**（dispatch/workflow_dispatch）还是来自 **你自己的铸造端点**（`cast-field.sh` 调的外部 service）？  
- 若是 GitHub API → 重点查 `on.workflow_call.inputs` 与调用方 `with:` 字段名是否一一对应。  
- 若是自建端点 → 重点查上文 gate 里的 schema 与端点 DTO 是否一致。

把 `state-excite-usrm-02.yml` 现有「场铸段」原文贴出来，我可以直接给你一份逐行替换的 patch，而不是模板。

——usrm SI1语义轨·20261005T124616Z
