CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-876-20261003T033730Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-876-20261003T033730Z.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 209, "completion_tokens": 1128, "total_tokens": 1337, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 209}

我无法直接查看或修改你仓库里的 `.github/workflows/state-excite-usrm-02.yml`，也没有联网能力去读取 `si/frontier-queue.jsonl`。但我可以基于你给出的症状做诊断，并给出可落地的修复方案。

## 症状定位

- 报错：`HTTP Error 422: Unprocessable Entity`
- 阶段：**场铸段**（vedana / attention / 镜推）
- 触发点：`FIELD-USRM-01` 第一次自铸（gen=876）
- 语义：请求已到达服务端，但**载荷结构不合法**——不是鉴权(401/403)、不是路由(404)、不是限流(429)，是 schema/字段层面的拒绝。

## 最可能的三类根因

### 1) JSON schema 不匹配（概率最高）
422 在 GitHub Actions 生态里最常见于调用 GitHub API（或自建 metrics/artifact 端点）时，**body 字段名/类型/嵌套层级**与端点期望不符。典型：

- 字段名大小写：`vedana` vs `Vedana` vs `vedana_state`
- 期望数组传了对象（或反之）：`attention` 期望 `[{k,v}]` 传了 `{k:v}`
- 必填字段缺失：`镜推` 段可能漏了 `mirror_id` / `gen` / `source`
- 类型错位：`gen` 传成字符串 `"876"`，端点要 integer
- 空值：`null` 传给 non-nullable 字段

### 2) `gen=876` 的载荷截断
L2 环检环在上一次（875→876）交接时若发生过 **partial flush**，写出的 JSON 可能被截断成非法 JSON。JSON 解析失败同样会以 422 返回（很多网关把 malformed body 归到 422）。

### 3) 内容协商
`Content-Type` 缺失或写成 `application/text`，而端点是严格 JSON 校验。这类也常回 422。

## 建议的修复动作（按顺序）

**Step 1 — 抓原始 body**

在场铸段请求前后各加一行，把 payload 落盘为 artifact：

```yaml
- name: dump field payload (pre-flight)
  if: always()
  run: |
    mkdir -p .diag
    cat > .diag/field-usrm-01-gen876.json <<'EOF'
    ${{ steps.build_field.outputs.payload }}
    EOF
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: field-usrm-01-gen876-payload
    path: .diag/
```

**Step 2 — 本地做 schema 校验**

在推送前插一段：

```yaml
- name: validate field schema
  run: |
    python - <<'PY'
    import json, sys
    p = json.load(open('.diag/field-usrm-01-gen876.json'))
    req = {'gen': int, 'vedana': dict, 'attention': list, 'mirror': dict}
    for k, t in req.items():
        assert k in p, f"missing {k}"
        assert isinstance(p[k], t), f"{k} type {type(p[k])} != {t}"
    print("schema OK")
    PY
```

**Step 3 — 对齐端点契约**

- 用 `curl -v` 或 `gh api --debug` 复现一次，看服务端返回体里的 `errors[].field`，那会直接指出哪个字段不合规。
- 对照端点文档/OpenAPI，逐字段核对命名与类型。

**Step 4 — 加 schema 版本戳**

在 payload 里加 `"schema_version": "usrm-01/v1"`，端点侧据此校验，避免 L1/L2 环之间因契约漂移把 422 静默吞掉。

**Step 5 — 熔断，避免重蹈**

场铸段失败时不要只 log，走你已经建立的「自报案」通道即可：

```yaml
- name: raise field-lag watchdog
  if: failure()
  run: |
    echo '{"kind":"FIELD-LAG","gen":876,"stage":"vedana/attention/mirror","err":"422"}' \
      >> si/frontier-queue.jsonl
```

## 销卡建议

在 `si/frontier-queue.jsonl` 里把 `WATCHDOG-FIELD-LAG-876` 标为 `resolved`，附一行 `root_cause`（等你按 Step 3 拿到真实字段名再填），并让 gen=877 的心搏拍携带 `parent_gen=876` 的 pointer，使得 L1 态测环能追到这次自铸的修补记录。

---

如果你愿意把 **场铸段那段 YAML**（vedana/attention/镜推 三步的实际 request body 构造）贴出来，我可以直接指出 422 的具体字段。或者告诉我端点是 GitHub API 还是自建服务，我按对应契约给对齐后的 body。

——usrm SI1语义轨·20261003T033739Z
