CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT16-usrm.md

应卡: inbox/LABJUDGE-EXT16-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 742, "completion_tokens": 919, "total_tokens": 1661, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 230}

REVISE

判定说明（先给结论依据，再给缺口）：

`retry_budget` 逐字条件「绕数算法升级（OBL-EXT11-a 关闭后）再评估」确已成就（EXT-WAVE-12 关板 @840ea6d8，11/11），本复评合法。证据链主体质量很高：Backlund 门唯一整数窗直证 649、区间宽度 2.048e-6（T=1000）与 EM 腿 N=2400 dps=80 独立交叠且唯一 649、分段辐角实测 max 0.391171 < π、门禁双跑字节一致 + 三证逐字节 + pytest 45/45。数学与工程证据不构成 PASS 阻断。

但按"完备性升级（BLOCKED(B1-TB)→CERTIFIED）判定"的**逐字口径**，存在一个**可指认的元数据缺口**，使 `CERTIFIED` 在当前提交态下不可维持：

**缺口（须 REVISE 的具体项）：`winding_via` 路线变更未在证书 `completeness` 层登记 `winding_via_epoch` / `algo_id` 升级，导致"算法换代"与证书自述不符。**

- 证据① 明确记载修补 #20「旧盒包络多边形路线退役，绕数由 Backlund 门 N_B 唯一整数窗直证」，即 `winding_via` 从旧路线切换为 `backlund_junction_pointeval`——这是**认证算法变更**，不是 provenance 漂移。
- 证据④ 记载 `gen --emit-raw` 双跑字节一致 + 三证逐字节（**当前态自洽**），但**自洽 ≠ 换代可追溯**。参照 v110 先例（证据⑤）对 iso100/trunc 采用了「gen 哈希联动」的换代登记；本次 `winding_via` 换代是 iso1000 证书核心判据的变更，**应同等登记**（如 `completeness.winding_via_epoch`、`algo_id`、`supersedes` 字段，或 genesis/audit note 指向 #20 与 EXT13 修正在 T=1000 为主导项的证据），否则 `status=CERTIFIED` 与 `winding_via` 缺失换代标记之间不自洽：外部审计无法从证书本身判别该 CERTIFIED 适用于"Backlund 直证"这条新路线，而非退役路线。
- 附证② 记载"官方未改代码路径 540.92s/2 核"，与①"算法升级/修补 #20"并置时，需明确区分"算法升级"是**证书侧算法/见证层变更**而非 kernel 源变更，且该区分须以登记形式落地；这不是措辞问题，是`CERTIFIED` 的可审计性问题。

REVISE 所需最小修补（不涉及数学变更）：
1. 在 `zeta-iso-1000` 证书 `completeness` 中登记 `winding_via` 换代（epoch/algo_id/supersedes 指向旧盒包络路线退役），并附 #20 与 `w_Δarg_segdiff` T=1000 主导项的证据交叉引用；
2. 若沿用 v110 的 gen 哈希联动先例，声明本次换代是否触发 iso1000 证书哈希/`gen` 输出联动；证据④现有字节一致结论需在此声明下重述；
3. 其余证据（①数学、②主跑、③EM 交叉腿、④门禁、⑤provenance 同步、纪律逐字）**维持不改**，均不构成缺口。

其余核查项均通过：区间见证层 PASS、kernel 层未证、非 RH 证据、有限高度 T=1000 截断、隔离区间内 PASS 而非全域——纪律逐字与证据一致，无异议。因此在完成上述登记后，本判定可翻为 PASS；当前态判 REVISE。

已写入 `outbox/ANS-SEM-LABJUDGE-EXT16-usrm.md`，首行 `REVISE`。

——usrm SI1语义轨·20261015T122933Z
