CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-SELFX2-WATCHDOG-FIELD-LAG-1239-20261009T090839Z.md

应卡: inbox/SELFX2-WATCHDOG-FIELD-LAG-1239-20261009T090839Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 216, "completion_tokens": 1629, "total_tokens": 1845, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 216}

我无法直接访问或修改你本地/私有仓库里的 `.github/workflows/state-excite-usrm-02.yml` 文件——我看不到该文件内容，也没有你仓库的写权限。因此不能真的“修讫销卡”。

不过，根据你给出的错误签名，可以做**精确诊断**并给出**可直接落盘的修复补丁草案**。你确认后把这段贴回仓库即可。

---

## 一、错误解码

```
FIELD-USRM-01 自模型场本拍铸造失败
gen=1239
err=sha-get-failx4  HTTP Error 403: Forbidden
```

关键点：

| 信号 | 含义 |
|---|---|
| `sha-get-failx4` | 第 4 次 SHA/资源 GET 拉取失败 |
| `HTTP 403 Forbidden` | 不是 404、不是超时——是**鉴权/权限被拒** |
| `gen=1239` 连续失败 | 不是瞬态网络抖动，是**确定性拒绝** |
| 触发者：statex v4.7 L2 环检环自铸 | workflow 内某 step 以**受限 token** 去拉受限资源 |

403 在 GitHub Actions 场铸段里几乎只有四类根因：

1. **`GITHUB_TOKEN` 权限不足**：默认 `permissions:` 太窄（例如只读 `contents`，却要写 `packages`/`issues`/`actions`）。
2. **跨仓库/跨组织资源**：workflow 试图访问另一个私有 repo 或 org 级资源，token 作用域不覆盖。
3. **PAT / App token 过期或 scope 缺失**：secret 里放的 token 失效，或缺少 `repo`/`workflow`/`read:packages`。
4. **环境/分支保护 + OIDC 信任策略**：`environment` 未授权，或 OIDC `sub` claim 不匹配云侧信任策略。

403 而非 401，说明 token **本身有效但被授权层拒绝**——重点查 `permissions` 与目标资源 ACL，而不是查 token 是否存在。

---

## 二、按场铸段定位

你说场铸段分 `vedana / attention / 镜推` 三拍。403 最可能落在这两处：

- **`attention` 拍**：拉取外部态面/远端 inbox-outbox 快照（你快照里 `inbox:420 outbox:628`），若目标是另一私有仓库或 Packages/API，token scope 不够 → 403。
- **`镜推` 拍**：把铸造结果回写（push / release / artifact / API mutation），需要 `contents: write` 或 `packages: write`，默认 token 只读 → 403。

`vedana` 拍一般是本地态计算，403 概率低。

---

## 三、修复补丁草案

### 1) 顶层显式声明权限（最常见修复）

在 `state-excite-usrm-02.yml` 顶部加/改：

```yaml
permissions:
  contents: write        # 镜推回写需要
  actions: read
  packages: write        # 若涉及 GHCR/包铸造
  issues: write          # 若销卡走 issue/comment
  id-token: write        # 若用 OIDC 换云侧 token
```

> 原则：**按最小必要显式声明**，不要靠默认。默认在 org 策略下常被收紧成只读，这正是 403 的经典来源。

### 2) 若访问跨仓库/org 资源

默认 `GITHUB_TOKEN` **不能**跨仓库。需要：

```yaml
- name: 场铸-attention-拉取远端态面
  env:
    GH_TOKEN: ${{ secrets.FIELD_USRM_PAT }}   # 具备 repo / read:packages 的 PAT 或 App token
  run: |
    gh api repos/<org>/<repo>/contents/... \
      -H "Accept: application/vnd.github+json"
```

并在仓库 Settings → Secrets 里确认 `FIELD_USRM_PAT` 未过期、scope 覆盖目标。

### 3) 若是 OIDC 云侧 403

检查 `environment` 与信任策略的 `sub`：

```yaml
jobs:
  field-cast:
    environment: usrm-field
    permissions:
      id-token: write
      contents: read
```

云侧信任策略里的 `sub` 必须精确匹配 `repo:<org>/<repo>:environment:usrm-field`，否则换 token 时就是 403。

### 4) 给 `sha-get-failx4` 加重试+诊断（防再静默）

在拉取 step 外包一层，让下次失败带出**到底是哪个 URL、哪个 token、哪个 scope**：

```yaml
- name: 场铸-sha-get（带诊断）
  env:
    GH_TOKEN: ${{ secrets.FIELD_USRM_PAT || github.token }}
  run: |
    set -euo pipefail
    URL="https://api.github.com/repos/<org>/<repo>/contents/<path>"
    for i in 1 2 3 4; do
      code=$(curl -sS -o /tmp/resp.json -w '%{http_code}' \
        -H "Authorization: Bearer $GH_TOKEN" \
        -H "Accept: application/vnd.github+json" "$URL") || true
      echo "attempt=$i http=$code"
      if [ "$code" = "200" ]; then break; fi
      if [ "$code" = "403" ]; then
        echo "::error::403 diag: token-scope / cross-repo / environment 三选一"
        cat /tmp/resp.json
        # 不静默：失败即出，交给 L1 态测环
        [ "$i" = "4" ] && exit 1
      fi
      sleep $((i*2))
    done
```

---

## 四、销卡判定（给你 L1 态测环用）

修完后满足以下才可销 `WATCHDOG-FIELD-LAG-1239`：

1. 下一次 `gen=1240+` 场铸 `sha-get` 返回 **200**；
2. `镜推` 回写成功（无 403）；
3. `vedana/attention/镜推` 三拍全部 exit 0；
4. 连续 3 拍无 `failx4` 复现。

---

## 五、我做不到的部分（诚实声明）

- 我**没有**你仓库的读/写权限，无法拉取 `state-excite-usrm-02.yml` 真实内容，所以上面是**基于错误签名的模板级修复**，不是对你实际 YAML 的逐行改写。
- 我**不能**在你们的链心搏系统里真正“销卡”——那需要你们的 statex/L1 态测环执行。

**下一步给我其中之一，我就能出精确到行的 patch：**
- 把 `state-excite-usrm-02.yml` 的 `场铸段` 原文贴出来（脱敏 token 即可）；或
- 告诉我 403 命中的**具体 URL/API** 和当前 `permissions:` 块。

拿到后我直接给出可 `git apply` 的 diff。

——usrm SI1语义轨·20261009T091001Z
