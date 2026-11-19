CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-CARD-ROOT-AUTONOMY-COLLAB-20261119-01-usrm.md

应卡: inbox/CARD-ROOT-AUTONOMY-COLLAB-20261119-01-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 193, "completion_tokens": 1834, "total_tokens": 2027, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 193}

下面按 usrm 线语义协作席给出**协议级**审查设计。本卡不读取、不转述任何私域原始行或数值结果；所有“可判失败”的判据均写成对**未来提交的统计产物**可执行的检查，而不是对已发生数值的断言。

---

## ① 本线立即可做动作（无需原始数据）

1. **冻结主分析规格（pre-spec lock）**：在事件 `ROOT-AUTONOMY-COLLAB-20261119-01` 下写出主分析清单：二项 plug-in 风险差对比、其方差估计式、交互项方差、单侧下界的置信水平与方向、双侧区间水平、区组定义与持续性统计量、留一区组重算规则、异质性诊断量（如 I²/Cochran Q 或区组间方差分量）。主分析项须标注为“主”，其余标注为“后补稳健性”，并禁止事后换位。
2. **建立验收测试台账**：把②中三项测试写成可执行脚本的输入/输出契约（输入：提交的汇总表 schema；输出：PASS/FAIL + 失败码），本线先交付契约与失败码字典，不填数值。
3. **定义数据最小 schema**：仅要求提交方提供聚合级字段（区组 ID、事件数、样本量、估计值、方差/标准误、方法标签），明确禁止本线接触行级私域数据；本线只做“汇总进—判据出”。
4. **建立“后补稳健性”隔离栏**：任何在主分析锁定后新增的区间、下界或异质性诊断，必须带 `post_hoc=true` 标记，并在报告中与主分析分表呈现。
5. **野问预登记**：把④的 PROPOSITION/FALSIFIER 先登记为待验命题，指定 REVIEWER 与 FAILURE_LEDGER 字段格式，等待 EVENT 触发。

---

## ② 至少三个能判失败的验收测试

**T1 — Plug-in 方差与区间自洽性测试（可判 FAIL）**
- 检查：提交的二项 plug-in 对比方差是否等于按锁定公式由 (p̂₁, n₁, p̂₂, n₂) 复算的值（容差预先写死，如相对误差 ≤1e-6）；单侧下界与双侧区间端点是否由该方差与锁定分位数一致导出。
- FAIL 条件：方差不可由声明公式复现，或下界/区间端点与方差-分位数不一致，或出现 n=0 / p̂ 越界未按锁定规则处理。
- 失败码：`VAR_INCONSISTENT`、`CI_ENDPOINT_MISMATCH`、`DEGENERATE_CELL_UNHANDLED`。

**T2 — 区组持续性与留一区组稳定性测试（可判 FAIL）**
- 检查：区组持续性统计量是否按锁定定义计算（同号区组比例或锁定等效量）；留一区组重算后，主效应方向与单侧下界符号是否保持；留一后区间是否出现预定阈值外的翻转。
- FAIL 条件：持续性统计量无法由区组级汇总复算；留一后主效应方向翻转，或下界由正变负（或反之）且未在预登记规则中列为预期；留一结果缺失任一区组。
- 失败码：`PERSISTENCE_NOT_REPRODUCIBLE`、`LOO_DIRECTION_FLIP`、`LOO_MISSING_BLOCK`。

**T3 — 交互方差与异质性诊断的可复算性测试（可判 FAIL）**
- 检查：交互项方差是否按锁定式由提交的区组级量复算一致；异质性诊断量（Q 或方差分量）是否与区组级汇总自洽；诊断结论（是否触发“不宜合并”规则）是否与预登记阈值一致。
- FAIL 条件：交互方差不可复算；异质性诊断量与区组汇总矛盾；诊断触发合并禁止规则但主分析仍按合并呈现且未标 `post_hoc`；或反之，未触发却声称异质性显著。
- 失败码：`INTERACTION_VAR_MISMATCH`、`HETERO_DIAG_CONTRADICTION`、`POOLING_RULE_VIOLATED`。

**T4（附加，后补稳健性专用）— 主/后补标签完整性测试**
- 检查：所有非主分析项是否带 `post_hoc=true`，是否与主分析分表；是否存在主分析锁定后静默替换。
- FAIL 条件：标签缺失、混表、或锁定后替换无变更记录。
- 失败码：`POSTHOC_LABEL_MISSING`、`SPEC_SILENT_SWAP`。

---

## ③ 向 cfts 线的一项具名协作请求

**请求名：`CFTS-AGG-SCHEMA-VALIDATION-20261119`**
请求 cfts 线作为**聚合 schema 与失败码字典的独立校验方**：对②中 T1–T4 的输入 schema（区组 ID、事件数、样本量、估计值、方差/标准误、方法标签、`post_hoc` 标志）与失败码字典做一次“契约级”复核，确认字段足以支撑可复算判据、且不要求任何行级私域数据；返回 PASS/FAIL 与缺口清单。该请求不涉及数值复验，只涉及契约充分性。

---

## ④ 野问（可证伪命题）

- **PROPOSITION**：在 `ROOT-AUTONOMY-COLLAB-20261119-01` 的锁定主分析规格下，若提交方给出的二项 plug-in 对比方差、单侧下界、双侧区间、区组持续性与留一区组结果均通过 T1–T3 的复算判据，则“主效应方向在留一区组下不翻转且单侧下界符号稳定”这一陈述可由聚合级汇总独立复现，无需行级数据。
- **FALSIFIER**：出现任一情形即证伪——(a) 存在一个区组，其留一后主效应方向翻转或下界符号改变，且该情形未被预登记规则列为预期；(b) 提交的方差/区间端点无法由声明公式与聚合量在预定容差内复现；(c) 异质性诊断触发禁合并规则而主分析仍按合并呈现且未标 `post_hoc`。
- **REVIEWER**：usrm 线语义协作席（本线）执行契约与复算判据审查；cfts 线按 `CFTS-AGG-SCHEMA-VALIDATION-20261119` 校验 schema 充分性；数值复验责任归提交方，本线不代行。
- **FAILURE_LEDGER**：按失败码记账——`VAR_INCONSISTENT`、`CI_ENDPOINT_MISMATCH`、`DEGENERATE_CELL_UNHANDLED`、`PERSISTENCE_NOT_REPRODUCIBLE`、`LOO_DIRECTION_FLIP`、`LOO_MISSING_BLOCK`、`INTERACTION_VAR_MISMATCH`、`HETERO_DIAG_CONTRADICTION`、`POOLING_RULE_VIOLATED`、`POSTHOC_LABEL_MISSING`、`SPEC_SILENT_SWAP`；每条记录须含区组 ID（若适用）、判据编号、PASS/FAIL、复算容差、时间戳。
- **NEXT_EVENT**：`CFTS-AGG-SCHEMA-VALIDATION-20261119` 返回 PASS 后，触发 `USRM-REPLAY-T1T3-20261119`（对提交的聚合汇总执行 T1–T3 复算判据并出 FAILURE_LEDGER）；若 schema 返回 FAIL，则触发 `SCHEMA-GAP-PATCH-20261119` 并顺延复算事件。

---

**声明**：本卡仅为可执行审查协议、验收判据与可证伪野问的设计；未读取任何原始行，未完成任何数值复验，未对私域数值作任何转述或断言。

**PROTOCOL_ONLY_NOT_RAW_REVIEW**

——usrm SI1语义轨·20261119T064241Z
