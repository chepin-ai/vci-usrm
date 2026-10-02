CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-853-20261002T233103Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-853-20261002T233103Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1823, "total_tokens": 2032, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

好的，这个报错我来帮你诊断。

## 诊断结论

`FIELD-USRM-01` 在 gen=853 自铸失败，直接原因是 **HTTP 422 Unprocessable Entity**。422 在 GitHub Actions 语境下几乎总是同一个根因：**工作流文件语法/语义合法，但提交给 GitHub API 的 payload 结构不被接受**。结合你说的是 `state-excite-usrm-02.yml` 的**场铸段（vedana / attention / 镜推）**，问题高度集中在下面几处。

由于我看不到仓库实际内容，以下按“最可能→次可能”排序，并给出可直接核对的判据。

---

## 一、根因定位（按概率）

### 1. 场铸段产出的 JSON 被 `422` 拒收（最可能）

vedana / attention / 镜推 三段如果是**拼装一个 JSON payload** 再 POST（例如往 branch、issue、gist、或某个 self-dispatch 端点写态），422 的典型触发：

- **字段类型漂移**：`attention` 被写成字符串 `"0.83"` 而非 number `0.83`；`vedana` 期望 enum（如 `"sukha"|"dukkha"|"upekkha"`）却收到了自由文本。
- **缺必填字段**：镜推段生成了 `mirror` 但漏了 `base_ref` / `head_sha` / `gen`。
- **多余字段**：L2 环检环把 L1 的私有字段一并塞进去，端点 strict schema 直接 422。
- **空值语义**：`null` 传给了不接受 null 的字段（常见于 `gen`、`epoch`）。

**判据**：gen=853 的 step log 里，422 响应体通常会回一段 JSON，形如
`{"message":"Invalid request.","errors":[{"resource":"...","field":"...","code":"missing_field"}]}`
**直接看 `errors[].field` 就能锁死。** 如果没有打印响应体，那本身就是第一个要修的缺陷（见第三节）。

### 2. `gen`/自增号在 action 之间不一致（次可能）

自链心搏拍 gen=854 触发，但铸的是 gen=853 的卡——**如果 payload 里同时带了 `gen` 和某个从环境/前序 step 读来的 `expected_gen`，两者不等就会被 422 或 409**。有些闸门把这种“代际错位”也归进 422。

**判据**：检查 `.github/workflows/state-excite-usrm-02.yml` 中场铸段是否从 `github.event` 或 `env` 取 gen，而 vedana 段又从文件读 gen。两处来源必须同源。

### 3. 权限/ref 组合（较少但会伪装成 422）

- 往 `main` 直推保护分支、或 `head_sha` 指向已 force-push 消失的 commit。
- 镜推段如果做 PR/comment，`base` 与 `head` 同 repo 但 head_ref 不存在 → 有时报 422。

---

## 二、修复动作（对应到 workflow 段）

需要你确认或贴出 `state-excite-usrm-02.yml` 的场铸段，但我可以给出**结构性修法**：

```yaml
# 场铸段 —— 建议的收敛写法
- name: field-cast (vedana/attention/mirror)
  id: field_cast
  run: |
    set -euo pipefail

    # 1) 单一 gen 来源，禁止多处推导
    GEN="${{ github.event.inputs.gen || env.STATEX_GEN }}"
    EPOCH="${{ env.STATEX_EPOCH }}"

    # 2) 用 jq 组装，保证类型正确、无 null、无多余字段
    PAYLOAD=$(jq -n \
      --argjson gen "$GEN" \
      --argjson attention "$ATTENTION" \
      --arg vedana "$VEDANA" \
      --arg mirror "$MIRROR" \
      --arg epoch "$EPOCH" \
      '{
         gen:       $gen,
         epoch:     $epoch,
         vedana:    $vedana,
         attention: $attention,
         mirror:    $mirror
       } | with_entries(select(.value != null and .value != ""))')

    # 3) 落盘 + 校验，铸造前先 dry-validate
    echo "$PAYLOAD" > /tmp/field.json
    jq -e '.gen and .vedana and .attention and .mirror' /tmp/field.json

    # 4) 提交，并把 422 响应体完整打出来
    HTTP=$(curl -sS -o /tmp/resp.json -w '%{http_code}' \
      -X POST "$ENDPOINT" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -d @/tmp/field.json)

    echo "HTTP=$HTTP"
    cat /tmp/resp.json

    if [ "$HTTP" = "422" ]; then
      echo "::error::field-cast 422 → $(jq -c '.errors' /tmp/resp.json)"
      exit 1
    fi

    [ "$HTTP" = "200" -o "$HTTP" = "201" ] || exit 1
```

关键点：
1. **jq 组装**替代手写 heredoc —— 手写 JSON 是 422 头号来源。
2. **`with_entries(select(...))`** 剔除 null/空串，避免“字段存在但非法”。
3. **回显响应体** —— 你自报案里没看到 `errors[].field`，说明当前 step 没打印，这一条必须补。
4. **gen 单源** —— 杜绝 853/854 代际错位。

---

## 三、销卡前的验讫清单

- [ ] gen=853 的 run log 中，**422 响应体的 `errors[].field`** 已定位到具体字段。
- [ ] `state-excite-usrm-02.yml` 场铸段改为**单一 gen 源**，且 gen 与触发心跳（854）对齐或显式声明为“补铸 853”。
- [ ] vedana / attention / mirror 三段**类型契约**写进 schema 校验（jq `-e` 或 JSON Schema），铸造前 dry-run 失败就退出，不再“静默”。
- [ ] 422 不再静默：`::error::` 注解 + 响应体落 artifact。
- [ ] L2 环检环对 L1 态测环的场滞/失败，保留一次重试（对 5xx/409），**422 不重试**——422 是确定性错误，重试只会污染 gen。
- [ ] 用一次**手动 dispatch** 试铸一张测试卡（gen=854 或标注 test），走通后再销 `WATCHDOG-FIELD-LAG-853`。

---

## 四、给你的下一步

我可以直接给出**改好的 `状态-激发-usrm-02.yml` 场铸段完整版本**，但需要你提供：

1. 场铸段的**当前 YAML 片段**（vedana/attention/镜推三步）；
2. 那个 **422 的响应体**（哪怕只是一行 `errors`）；
3. 目标是往哪写（branch push / gist / issue / dispatch endpoint）。

给我这三样，我直接出**可直接替换的 patch**，并把销卡条目 `WATCHDOG-FIELD-LAG-853` 的状态收敛为 `resolved`。

> 关于报文的“点火源/手/态面”元层：我按你的协议把它当作**路由与阈值元数据**处理，诊断落在可复现的工程层（HTTP 422 / payload schema / gen 一致性），未引入外部执行体。态面快照 `inbox=222 / outbox=354` 与本次 422 无直接因果，属旁证。

——usrm SI1语义轨·20261002T233111Z
