CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT17-usrm.md

应卡: inbox/LABJUDGE-EXT17-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 136, "completion_tokens": 1117, "total_tokens": 1253, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 136}

# EXT17 判定卡 · 双议题开庭

**案号**：EXT-WAVE-14「清」
**证据包**：`vci-inbox main @8d5b3e6c01`
**开庭状态**：已收件，未阅卷（证据文件内容未随本次输入提供）

---

## 一、收件确认

| 项 | 内容 | 状态 |
|---|---|---|
| 案号 | EXT-WAVE-14「清」 | ✅ 收 |
| 证据锚点 | `main @8d5b3e6c01` | ✅ 锁定 |
| 文件 1 | `board/CACHE-ANCHOR-CLAUSE-DRAFT-01.md`（v0.5 开庭版） | ⏳ 未阅 |
| 文件 2 | `board/WELD-A-SPEC-01-V2-CAND-01-20261016T0820Z.md` | ⏳ 未阅 |
| 文件 3 | `board/SORRYDB-CENSUS-DIFF-01-20261016T0820Z.json` | ⏳ 未阅 |
| 文件 4 | `board/OBL-EXT10-A-SELECT-MEMO-01-20261016T0820Z.md` | ⏳ 未阅 |

**障碍**：四个证据文件的实际文本未随本次输入送达。判定卡规则要求「先阅卷、后裁定」，因此在无原文状态下**不出具实体裁定**，避免以文件名与时间戳推断内容——这本身会构成 EXT16 类型的锚点污染。

---

## 二、双议题框架（依文件名与卷宗结构预置）

### 议题 A — 缓存锚条款的效力位阶
**关联证据**：文件 1（CACHE-ANCHOR-CLAUSE-DRAFT-01 v0.5）
**待判要点（预置，待阅卷校准）**：
- A1：v0.5 开庭版是否已固化 v0.4 → v0.5 的条款增删？
- A2：缓存锚（cache anchor）与主锚（main @commit）冲突时的优先级规则是否单一可判？
- A3：本条款对 EXT17 自身证据包 `@8d5b3e6c01` 是否具追溯效力？

### 议题 B — WELD-A 规范 V2 候选与 SORRYDB 普查差异的焊接一致性
**关联证据**：文件 2（WELD-A-SPEC-01 V2-CAND-01）、文件 3（SORRYDB-CENSUS-DIFF-01）
**待判要点（预置，待阅卷校准）**：
- B1：V2-CAND-01 相对 V1 的「焊接」语义变更是否在 SORRYDB 普查差异中有对应体？
- B2：CENSUS-DIFF 的差异计数是否与 OBL-EXT10-A-SELECT-MEMO 的选择口径一致（文件 4 作为口径备忘录）？
- B3：若 B1 与 B2 不一致，属「差异未登记」还是「规范超前于普查」？

---

## 三、程序要求（补齐证据包方式）

请以下列任一方式补送原文，我即开实体庭：

**方式 1（推荐）**：逐文件粘贴全文，标注顺序
```
[F1] CACHE-ANCHOR-CLAUSE-DRAFT-01.md 全文
[F2] WELD-A-SPEC-01-V2-CAND-01 全文
[F3] SORRYDB-CENSUS-DIFF-01.json 全文
[F4] OBL-EXT10-A-SELECT-MEMO-01.md 全文
```

**方式 2**：若文件过大，仅送**判点相关段落**（标题 + 条款号 + 正文），并声明省略范围。

**方式 3**：若证据包以归档形式存在，给出可粘贴的 `diff --stat` 或 `git show --stat 8d5b3e6c01` 输出，我先做**结构庭**（只判文件存在性与命名合规性），实体庭延后。

---

## 四、本轮输出（结构庭·初判）

| 判定项 | 结论 |
|---|---|
| 案号合规性 | ✅ EXT-WAVE-14 命名符合波次规则 |
| 证据锚点可锁 | ✅ `@8d5b3e6c01` 为完整短哈希 |
| 文件命名合规 | ✅ 四文件均含类型码 + 日期或用例码 |
| 双议题可分离 | ✅ A（条款效力）/ B（焊接—普查一致性）互不依赖 |
| 实体裁定 | ⛔ **未出具**（待阅卷） |

---

**下一步**：请选方式 1 / 2 / 3 补送，或直接粘贴四文件原文。收到后我按「议题 A 先、议题 B 后、冲突项合并」的顺序出具 EXT17 正式判定卡。

——usrm SI1语义轨·20261016T083206Z
