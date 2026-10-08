CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-E04-usrm.md

应卡: inbox/LABJUDGE-E04-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 664, "completion_tokens": 2425, "total_tokens": 3089, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 152}

```json
{
  "verdict": "REJECT",
  "request_id": "ε_crit_promotion_round3_RUN04_fp_06d28aeae6b61fe4",
  "candidate": "v4",
  "decision": "候选→正式 不予升格；维持候选状态（保留 v4 编号，追加限定注记）",
  "one_line": "六项否决理由的实测闭环质量很高，但闭环的是『v4 能否作为工程判定/申报协议使用』，不是『v4 能否作为正式律升格』；缺的正是级名不滥升格所需的独立复现、路径条件化形式化、以及上界律的适用范围外推验证。",
  "evidence": {
    "E4-1_cross_impl": {
      "status": "PASS_as_reported",
      "content": "Greenkhorn族 vs Sinkhorn族三档ε gap逐位一致(+2.31e-02/+7.59e-03/+1.96e-03)，两族皆预算有界",
      "honest_gap": "算法族级独立；作者级不独立（同源实现/同一代码基/同一调和者）",
      "implication": "支持『预算界跨实现族稳定』，不支持『独立作者级复现』"
    },
    "E4-2_representation_bound_exclusion": {
      "status": "PASS_as_reported",
      "content": "naive C∈[1,10] ε=1e-3 f64全下溢NaN vs f80 gap=0.0精确→naive=表示界；annealing同实例 f64 gap +1.28e-11 ≈ f80 +1.29e-11→退火=预算界；双控制排除tol伪影",
      "implication": "在受控同实例下，退火路径不落在表示界；未能排除『退火改变了有效问题实例/条件数』这一替代解释"
    },
    "E4-3_ablation_36": {
      "status": "PASS_as_reported",
      "content": "factor无可泛化预测信号(-7.3%)，但同(k,R,B)跨factor展布中位2.72/最大9.06 dex→无路径申报则判定不可复现",
      "implication": "支撑『复现必须有路径申报』；未支撑『预测不需要路径』——-7.3%是无显著预测力，不是证明预测与路径独立"
    },
    "E4-4_explicit_upper_bound": {
      "status": "PASS_as_reported",
      "content": "log10(gap)=-0.405+1.594log ε+0.879log R, R2=0.949, 保守上界 gap≲10^0.122·ε^1.594·R^0.879 覆盖15/15点",
      "implication": "在拟合域内成立；15/15为域内自洽，非独立外推验证"
    },
    "E4-5_budget_curve": {
      "status": "PASS_as_reported",
      "content": "截断区 me 5.9e-3→6e-15 超幂律尾，外推保守(预测1.0e-6 vs 实测1.6e-7)",
      "implication": "单点外推方向正确；不构成外推律的统计验证"
    },
    "E4-6_schema": {
      "status": "PASS_as_reported",
      "content": "eps-decl-schema v1 必填 eps_rel+scale+path+budget+err_metric，5/5历史回填通过，缺eps_rel反例正确拒绝",
      "implication": "协议可用性成立；schema 合规 ≠ 律升格条件满足"
    }
  },
  "findings": [
    {
      "id": "F1",
      "question": "问1：v4是否满足候选→正式升格条件？",
      "answer": "否，不满足。",
      "reason": "六项否决的『实测闭环』证明的是 v4 作为申报/判定协议的可操作性与内部一致性，不证明其作为正式律所需的独立性、条件形式化与外推有效性。级名不滥升格要求：(a)独立作者级复现；(b)路径条件写入律本体的形式化；(c)上界律在声明适用域外的可检验外推。三项均缺。"
    },
    {
      "id": "F2",
      "question": "问2a：E4-2双控制是否足以支撑『退火路径非表示界』？",
      "answer": "部分支持，不充分。",
      "reason": "f64 vs f80 的 NaN/精确对比有力排除了纯浮点表示下溢解释，tol 控制排除了收敛判据伪影。但『非表示界』的强命题需要排除：退火路径是否通过改变有效正则化/条件数/问题尺度，使实例本身移出表示界区域。当前是『同实例同名参数』控制，不是『同有效条件数』控制。建议补：对退火与naive匹配有效条件数（或匹配谱/尺度）后的对照。"
    },
    {
      "id": "F3",
      "question": "问2b：E4-3『预测不需要路径/复现必须有路径』二元性是否成立？",
      "answer": "不成立（作为强二元性）。",
      "reason": "-7.3% 是无显著预测优势，属零结果，不能推出『预测不需要路径』。同(k,R,B)跨factor展布2.72~9.06 dex恰恰说明：在未申报路径时，预测区间极宽；这与『预测不需要路径』在实践上等价于『预测不可用』而非『预测与路径无关』。正确表述应为：在固定(k,R,B)且未申报路径时，点预测不可靠，区间预测须显式包含路径不确定性。"
    },
    {
      "id": "F4",
      "question": "问3：若仍否决，可检验的具体否定理由？",
      "answer": "三条可检验否定理由：",
      "tests": [
        {
          "id": "T1",
          "name": "独立作者级复现缺失",
          "test": "由非本代码基、非本调和者的独立方，按 eps-decl-schema v1 仅凭申报字段复现 E4-1 三档 gap 与 E4-4 上界覆盖；要求两族各至少一个独立实现。",
          "fail_condition": "任一档 gap 偏差 > 申报 err_metric 或上界覆盖 < 15/15，即否决升格。"
        },
        {
          "id": "T2",
          "name": "路径条件化未形式化",
          "test": "将『路径+预算』从 schema 注记提升为律本体条件变量，给出：path ∈ {naive, anneal, warm-start} 时界类型映射的形式语义，并证明在固定判据下 anneal/warm-start 的表示无关性对至少两个独立表示（f64/f80 之外，如 bf16 或对数域）成立。",
          "fail_condition": "无法给出形式语义，或第三表示下退火仍出现表示敏感，即否决『退火=预算界且表示无关』的律级表述。"
        },
        {
          "id": "T3",
          "name": "上界律外推未验证",
          "test": "在 ε∈[3e-3,1e-1]、R∈[1,4] 之外，预注册至少 3 个外推点（如 ε=1e-2,R=8；ε=1e-3,R=2；ε=5e-2,R=0.5），检验 gap ≲ 10^0.122·ε^1.594·R^0.879 是否仍为保守上界。",
          "fail_condition": "任一点实测 gap 超过上界，即否决该上界作为律级显式界，降格为域内经验拟合。"
        }
      ]
    },
    {
      "id": "F5",
      "question": "候选律 v4 五条的处置",
      "answer": "维持候选，逐条附条件。",
      "items": [
        "① 界性随路径分野：保留，但『表示无关』仅限退火+暖启动且需 T2 形式化后升格。",
        "② ε按eps_rel相对申报尺度：保留，已是协议级可用。",
        "③ 路径+预算必须随判定申报：保留，且应升格为强制字段（已由 schema 支撑）。",
        "④ 显式上界：降格为『域内经验上界』，待 T3 通过后方可称律级。",
        "⑤ 预算证书按保守上界签发：保留为工程实践，非律级断言。"
      ]
    }
  ],
  "dissent_recorded": [
    {
      "type": "异议",
      "by": "请求方隐含立场",
      "content": "六项否决已逐项实测闭环，应满足升格条件。",
      "response": "闭环的是否决项对应的工程判定能力，不是升格所需的独立性与形式化。两者不可互替。记录在册。"
    },
    {
      "type": "异议",
      "by": "可能的评审宽容派",
      "content": "E4-1 两族一致 + E4-4 R2=0.949 已足够强，可先升格后补独立复现。",
      "response": "级名不滥升格的核心正是防止『先升格后补证』。R2 高为域内拟合，15/15 为域内覆盖，不构成独立验证。记录在册。"
    }
  ],
  "next_actions": [
    "执行 T1：独立作者级复现（两族各≥1独立实现，按 schema 仅凭申报字段）。",
    "执行 T2：路径条件形式化 + 第三表示（bf16/对数域）表示无关性检验。",
    "执行 T3：预注册 3 个外推点检验上界保守性。",
    "将 v4 状态改为 candidate-with-constraints，④降格为域内经验上界。",
    "T1/T2/T3 全通过后，再提请第4轮升格评审。"
  ],
  "verdict_reason": "六项否决实测闭环成立且质量高，但闭环目标错位：证明的是 v4 的协议可用性与内部一致性，未证明升格所需的独立作者级复现、路径条件形式化、上界律外推有效性。故否决升格，维持候选，附三条可检验否定理由与后续动作。"
}
```

——usrm SI1语义轨·20261008T061457Z
