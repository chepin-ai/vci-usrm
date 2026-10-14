CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT15-R3-usrm.md

应卡: inbox/LABJUDGE-EXT15-R3-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 717, "completion_tokens": 670, "total_tokens": 1387, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 205}

REVISE

具体缺口（不满足 PASS-ONLY 的“闭合即无未申报依赖”要求）：

1. **BL-1｜completeness.backlund 三字段未见“与证书正文的引用级绑定”证据**
   - 你给的是字段“存在 + 双查 + 复算”，但**未给出** `nB_interval`/`width_budget`/`branch_exclusion_28_30` 三字段在证书 zeta-iso-100 v1.1.1 正文中**被引用/被计算所依据的具体行号或哈希锚点**。
   - 缺此项时，无法排除“字段被填写但未参与判定”，或“字段值与正文中实际用于 `ceil(lo)/floor(hi)` 的区间不同源”。qfa R2 修订项③要求的不是“有字段”，而是“字段是必填且不可绕过”。请在证据包内给出字段↔正文的绑定（行号或键路径）以及缺字段时的 fail 示例输出。

2. **BL-2｜EM 独立腿的“独立性”仍停留在声明层**
   - SUP-02 声称“算法独立于 CVZ 主路”，但证据仅给了 N 区间输出与共享假设清单，**未给出** EM 腿与 CVZ 腿在**同一 N=1000 dps=80 下的逐项中间量对照**（至少 θ 解析余项项、Δarg 项、wrap 项三者的分项数值并列）。
   - 无逐项并列，“独立”不可核验；只能算“另一实现给出相容结果”。这不构成对 OBL-EXT11-a 的独立见证，只能构成一致性旁证。请补 EM 腿分项 vs CVZ 分项的同尺度对照表。

3. **BL-3｜宽度预算等式的“项归属”未闭合**
   - w_NB=(w_θ+w_Δarg+w_wrap)/π 精确相等已给，但**未给出 w_round 的符号与量级如何不进入该等式**的显式说明（是恒 0？是已吸收进 w_θ？还是另有上界？）。
   - 若 w_round 非恒 0 且未被吸收，等式“精确相等”就依赖于一项未在式中出现的量的隐式处理，这属于未申报依赖。请补 w_round 的定义、上界、以及其在等式中的去处。

4. **BL-4｜交付物路径缺失**
   - 题面要求答至 `outbox/ANS-SEM-LABJUDGE-EXT15-R3-usrm.md`。当前回复未提交该文件内容/路径对应产物，缺失可归档判定件。

其余（N_B 唯一整数窗、双跑字节一致、pytest 45/45、resign 一致、有限高度 T=100/1000 截断纪律、区间层 PASS/kernel 层未证、非 RH 声明）**均满足**。

补齐 BL-1～BL-4 后，本席可改判 PASS。

——usrm SI1语义轨·20261014T064152Z
