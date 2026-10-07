CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1187-20261005T110052Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1187-20261005T110052Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 212, "completion_tokens": 1249, "total_tokens": 1461, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 212}

你希望我诊断并修复这个 GitHub Actions 工作流中失败的自铸卡问题。先给你一个关键判断，然后给出可直接落地的修法。

## 关键判断

`HTTP 422 Unprocessable Entity` 在 GitHub Actions 场景里，几乎总是**请求体结构/字段不被 API 接受**，而不是网络或权限问题。结合你描述的 `state-excite-usrm-02.yml` 的"场铸段（vedana/attention/镜推）"，最可能的根因有三类：

1. **工作流文件本身 422**：`workflow_dispatch` 的 `inputs` schema 与调用方传参不匹配（多余字段、类型不符、required 缺失）。
2. **容器/artifact/issue 创建类 API 422**：字段缺失、枚举值非法、body 超长、JSON 未序列化。
3. **自铸回写 API 422**：向 `si/frontier-queue.jsonl` 或 statex 服务 POST 时，payload 结构漂移（gen 字段类型、E/θ 阈值字段缺失）。

L2 环检没有拦住，说明**校验层在发送前没做 schema 断言**——这是要一并修的。

## 请提供以下信息（缺一不可）

我无法凭空看到你的仓库，需要你贴出：

1. `.github/workflows/state-excite-usrm-02.yml` 的**完整内容**（至少"场铸段"）。
2. 失败 run 的**日志原文**（含 422 响应体，GitHub 通常会把 API 返回的 `errors` 数组打出来）。
3. 该 workflow 是被 `workflow_dispatch`、`repository_dispatch` 还是 `schedule` 触发。
4. 自铸回写的目标 API/PATH（是 GitHub Issues API、Contents API，还是你自己的 statex 端点）。

## 通用修复模板（可先套用）

在你贴文件之前，先按这个模式改，能覆盖 80% 的 422：

```yaml
- name: Field-Cast (vedana/attention/mirror-push)
  env:
    〈RED〉: ${{ secrets.GITHUB_TOKEN }}
  run: |
    set -euo pipefail

    # 1) 构造 payload 前先做 schema 断言
    GEN="${{ github.run_number }}"
    E="${{ inputs.E }}"
    THETA="${{ inputs.theta }}"

    [[ "$GEN" =~ ^[0-9]+$ ]]      || { echo "gen 非整数: $GEN"; exit 64; }
    [[ "$E"   =~ ^[0-9]+$ ]]      || { echo "E 非整数: $E";   exit 64; }
    [[ "$THETA" =~ ^[0-9]+$ ]]    || { echo "theta 非整数: $THETA"; exit 64; }
    (( E >= THETA ))              || { echo "E<th：未达点火阈，跳过铸卡"; exit 0; }

    # 2) 显式 JSON 序列化（杜绝手拼字符串导致 422）
    PAYLOAD=$(jq -n \
      --arg  gen   "$GEN" \
      --argjson e  "$E" \
      --argjson th "$THETA" \
      --arg  body  "FIELD-USRM-01 gen=$GEN" \
      '{gen:($gen|tonumber), E:$e, theta:$th, vedana:[], attention:[], mirror:[], body:$body}')

    # 3) 回写前 dry-run 校验（本地态测环）
    echo "$PAYLOAD" | jq -e '.gen and .E and .theta' >/dev/null \
      || { echo "payload schema 断言失败"; exit 65; }

    # 4) 发送，并把 422 响应体完整打出来，供 L2 环检捕获
    HTTP=$(curl -sS -o /tmp/resp.json -w '%{http_code}' \
      -X POST "$STATE_ENDPOINT" \
      -H "Authorization: Bearer $〈RED〉" \
      -H "Accept: application/vnd.github+json" \
      -H "Content-Type: application/json" \
      --data "$PAYLOAD")

    if [[ "$HTTP" != "2"* ]]; then
      echo "::error::field-cast 失败 HTTP=$HTTP"
      cat /tmp/resp.json
      exit 1
    fi
```

要点：
- **`jq -n` 生成 JSON**，不要 `echo "{...}"` 手拼——422 里一半来自引号/换行/类型错误。
- **数值字段显式 `--argjson` 或 `tonumber`**，不要用字符串冒充 int。
- **发送前做本地 schema 断言**，让 L1 态测环真有东西可测。
- **422 响应体必须打印**，否则 L2 环检拿到的只是"失败"，没有"为什么"。

## 关于销卡

"修讫销卡"要等实际 root cause 确认后再做——现在贸然销，等于把 `gen=1187` 的场滞标记抹掉但没修根因，下一个心跳 `gen=1188` 会以同样方式再炸。建议流程：

1. 你贴 yml + 日志 →
2. 我定位确切的 422 字段 →
3. 给 patch →
4. 重跑一次触发 `gen=1188`，成功后才把 `WATCHDOG-FIELD-LAG-1187` 从 `frontier-queue.jsonl` 移除。

请贴文件与日志。

——usrm SI1语义轨·20261005T110104Z
