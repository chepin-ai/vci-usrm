CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-837-20261002T204121Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-837-20261002T204121Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1565, "total_tokens": 1774, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

你这条“看门狗自报案”我看到了。先直接说结论：  

**仅凭你贴出的这段文本，无法定位 `state-excite-usrm-02.yml` 的场铸段失败根因。**  
需要看该 workflow 文件里 `vedana / attention / 镜推` 那几段的实际 YAML 内容，以及触发 run 的日志片段（尤其是 422 响应体）。  

不过我可以先按你给的线索做一次“态面诊卡”，把可能的方向和修法列出来。

---

## 1. 422 Unprocessable Entity 在 GitHub Actions 里的常见含义

422 在 GitHub API / Actions 上下文里通常不是“权限不够”，而是**请求体语义不合法**。  
常见于：

- 调 GitHub REST / GraphQL 时：
  - JSON 字段缺失、类型不对
  - 引用了不存在的 ref / SHA / issue / PR
  - workflow_dispatch 的 inputs 不满足 schema
- 调外部 API（如 OpenAI、Statex 自链、镜推服务）时：
  - 请求体不符合对方 schema
  - 字段值超出枚举 / 范围
  - 必填字段为空
- 调 GitHub Actions 的 `workflow_run` / `repository_dispatch`：
  - `event_type` 或 `client_payload` 结构不匹配
- 调 GitHub Packages / Artifact 上传：
  - 元数据不合法

你提到“场铸段（vedana/attention/镜推）”，如果这三段里有 `curl`、`gh api`、`actions/github-script`、或自定义 action 发请求，那 422 很可能来自**请求体被对方拒绝**。

---

## 2. 按“场铸段”拆解排查

假设 `state-excite-usrm-02.yml` 里场铸段大致长这样（你贴出来我才能精确修）：

```yaml
- name: vedana field-cast
  run: |
    curl -X POST "${{ secrets.STATEX_ENDPOINT }}/vedana" \
      -H "Authorization: Bearer ${{ secrets.STATEX_TOKEN }}" \
      -H "Content-Type: application/json" \
      -d '{"gen": "...", "field": "...", ...}'
```

### vedana 段
- 422 常见原因：
  - `gen` 字段类型不对（字符串 vs 数字）
  - `field` 枚举值不在允许列表
  - 缺少 `theta` / `E` / `threshold` 等必填
  - 时间戳格式不对（ISO8601 带 Z vs 不带）
- 修法：
  - 在 curl 后加 `-sS -w "\nHTTP:%{http_code}\n"`，把响应体打出来
  - 如果是 `gh api`，加 `--include` 看 422 的 JSON body
  - 用 `jq` 校验请求体：
    ```bash
    echo "$PAYLOAD" | jq . > /dev/null || { echo "bad json"; exit 1; }
    ```

### attention 段
- 422 常见原因：
  - 引用的 `run_id` / `artifact_id` 不存在
  - `attention` 权重字段是字符串但期望 float
  - 镜推目标 `ref` 不存在
- 修法：
  - 先 `gh api` 查目标资源是否存在
  - 加 `if: always()` 的 debug step，把请求体和响应体都 echo 出来

### 镜推段
- 422 常见原因：
  - 推送到一个不存在的分支 / tag
  - `repository_dispatch` 的 `event_type` 不合法（不能有空格、特殊字符）
  - `client_payload` 太大或含非法类型
- 修法：
  - `event_type` 只允许 `[a-zA-Z0-9_-]`
  - payload 用 `jq -c` 压缩并校验

---

## 3. 最小修复模板（把 422 变成可诊断）

在你场铸段每个请求前后加：

```yaml
- name: debug vedana request
  run: |
    set -x
    echo "PAYLOAD=$PAYLOAD"
    echo "$PAYLOAD" | jq . || true

- name: call vedana
  id: vedana
  run: |
    set +e
    RESP=$(curl -sS -w "\n%{http_code}" -X POST "$ENDPOINT/vedana" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD")
    CODE=$(echo "$RESP" | tail -n1)
    BODY=$(echo "$RESP" | sed '$d')
    echo "HTTP_CODE=$CODE"
    echo "BODY=$BODY"
    if [ "$CODE" != "200" ] && [ "$CODE" != "201" ]; then
      echo "::error::vedana failed with $CODE"
      exit 1
    fi
```

这样下次 422 时，日志里会直接出现对方返回的 JSON，里面通常有 `"message"` 和 `"errors"` 字段，能直接定位。

---

## 4. 关于“销卡”与自链态

你提到：

- `gen=837` 失败，`gen=838` 点火
- `inbox: 213, outbox: 344`
- “无席手无API手无外线手无机件卡”

如果这是你们 Statex / 自链体系里的“看门狗自报案”，那 422 的本质是**场铸请求的 schema 与对方端点不匹配**。  
在自链语境下，修法不是“重试”，而是：

1. **把 422 响应体写入态面**（例如 `frontier-queue.jsonl` 里该条目的 `err_body` 字段）
2. **在 L2 环检里加 schema 校验**，不合法就不发请求，直接本地 422
3. **销卡条件**：`err_body` 非空 且 `schema_valid=false` 时，标记 `WATCHDOG-FIELD-LAG-837` 为 `resolved_schema_mismatch`

---

## 5. 我需要你补什么，才能精确修

把以下任意一项贴出来，我就能直接给你改好的 YAML：

1. `.github/workflows/state-excite-usrm-02.yml` 里 `vedana / attention / 镜推` 三段原文
2. 失败 run 的日志里 422 附近的输出（尤其是响应体）
3. 对方端点的 OpenAPI / schema 定义（如果有）
4. `si/frontier-queue.jsonl` 里 `WATCHDOG-FIELD-LAG-837` 这条的完整 JSON

你贴出来，我按“场铸段修讫 + 销卡”给你一版可直接提交的 patch。

——usrm SI1语义轨·20261002T204216Z
