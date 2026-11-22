CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-TASK-HOLO-SURGE-20261122-02-usrm.md

应卡: inbox/TASK-HOLO-SURGE-20261122-02-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 192, "completion_tokens": 884, "total_tokens": 1076, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 192}

VERDICT=REJECT

EVIDENCE=检查对象：批次 HOLO-SURGE-20261122-02；公共前厅固定引用 chepin-ai/vci-inbox@95a320455445ce2a83afbdd038c68a8b416dc4ce。审查仅针对题面给定的“归并 spectral/around 两个新 pattern、检查与 HOLO 关系闭包是否重复、给出同义标签不同来源不得去重丢失谱系的反例”这一语义结构，不以任何本地运行结果、CI 状态或公共前厅可访问性作为已核验事实。题面未提供 spectral 与 around 的具体 pattern 定义、边语义、HOLO 关系闭包的具体成员与闭包算子、两 pattern 的出处来源标识（source id / provenance 字段），也未提供任何哈希化的中间产物。因此“归并后是否与 HOLO 闭包重复”在当前证据下不可判定，而不是“无重复”。

COUNTEREXAMPLE=反例（同义标签不同来源不得去重丢失谱系）：设来源 A 的 pattern 记为 `around(v1,v2,label="temporal-near",source=A)`，来源 B 的 pattern 记为 `around(v1,v2,label="temporal-near",source=B)`。若归并器以 `(v1,v2,label)` 为键做去重，两条会被合并为一条并丢弃 source=B（或 source=A）的谱系，导致后续 HOLO 闭包计算中该边的贡献来源不可追溯。可证伪点：若归并键改为 `(v1,v2,label,source)` 或保留 provenance 多重集，则此反例不成立；反之若归并实现确实以三元组为键，则谱系丢失可复现。另一个独立反例：`spectral` 与 `around` 在标签字符串上不同但语义等价（如 `spectral-band` 与 `around-band` 指向同一关系类），若按标签字符串判“不重复”则漏归并；若按语义等价类判“重复”又可能误并不同来源的同义标签，两者都说明“标签同义性”与“来源谱系”必须分开建模，不能由单一去重规则同时承担。

LIMIT=未执行项：未运行任何归并脚本、未加载 chepin-ai/vci-inbox@95a320455445ce2a83afbdd038c68a8b416dc4ce 的实际内容、未计算 HOLO 关系闭包、未对 spectral/around 做实际集合交并差、未验证公共前厅哈希与批次号的一致性。不能外推的边界：本审查不构成对 HOLO-SURGE-20261122-02 正确性的全局证明，不构成对 chepin-ai/vci-inbox 仓库状态或可访问性的确认，不构成对任何有限数值结果或工作流 success 的升格。题面中“两个新 pattern”的“新”亦未被证据支持，仅视为待核声明。

ACTION=需修复：1) 在归并规则中显式保留 provenance（source id、引入批次、哈希），去重键至少包含来源维度，或改为多重集合并并记录合并映射；2) 对 spectral/around 给出形式化定义（顶点、边、标签语义、等价类判定函数），并给出与 HOLO 闭包算子的交互说明；3) 提供可复现的中间产物哈希（归并前集合、归并后集合、闭包结果）以支撑“是否重复”的判定。下一实验：在固定公共路径 chepin-ai/vci-inbox@95a320455445ce2a83afbdd038c68a8b416dc4ce 下取 spectral/around 的实际记录，构造 provenance 保留型归并，分别计算“三元组键去重”与“含来源键归并”两种结果，比对 HOLO 闭包差异，并以上述反例作为回归测试用例验证谱系不丢失。

——usrm SI1语义轨·20261122T151849Z
