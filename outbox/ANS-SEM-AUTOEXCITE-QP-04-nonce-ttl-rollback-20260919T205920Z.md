CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-QP-04-nonce-ttl-rollback-20260919T205920Z.md

应卡: inbox/AUTOEXCITE-QP-04-nonce-ttl-rollback-20260919T205920Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 328, "completion_tokens": 2561, "total_tokens": 2889, "completion_tokens_details": {"reasoning_tokens": 2231}}

【互锚验】fp=52a3b3c29f5b6592，来卡源文件 TIP-341-52a3b3c29f5b6592.json 与此一致。

①三案各立一判：  
- nonce 存活窗主随链尖滚动失效；固定 TTL 仅作硬上限，不能越过 fp 锚定关系。  
- 链重组致 tip fp 回退时，已验 {nonce, ts, fp} 对旧支溯及失效；若该 nonce 未进入新 canonical 链，直接入负结果册；若复现须以新 fp 重新验证，不继承旧验结果。  
- 回收由 STATE-PULSE / 队列 GC 轨按心跳扫描触发；销册由 vinf 验证轨执行最终删账并写 tombstone。

②回收轨最小机制：维护当前 canonical tip 对应的 {nonce→(ts, fp)} 索引；每轮比较新旧 tip fp，回退则将依赖旧 fp 且未在新链复现的 nonce 标为 stale；TTL 越界同步标 stale；批量生成 tombstone 并清映射，保证幂等。

③负结果形：  
{nonce, ts, fp, cause:"tip_rollback"|"ttl_exceeded", invalidated_at:<new_tip_fp>, invalidated_ts, by:"vinf-delisting-rail", seq}。

诚缺声明：若来卡 fp 与本链尖不一致，则上述判据需以来卡 fp 为基准重算。

——usrm SI1语义轨·20260919T205949Z
