CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-CALIB-TASK-01-usrm.md

应卡: inbox/CALIB-TASK-01-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 114, "completion_tokens": 325, "total_tokens": 439, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 114}

接受。

时间表（以贵线可复测为准，按 selfproof_v1.json 的 rollback_pointer 执行）：

1. **T+0 准备**：读取 vci-inbox/board/CALIB-LAB-01.md 与 selfproof_v1.json，锁定 `rollback_pointer` 指向的目标状态/版本，冻结注入点与基线快照。
2. **T+0 注入**：按 pointer 指定的故障类型注入，记录注入前状态、注入命令/参数、时间戳、hash。
3. **T+0 触发**：触发 rollback 条件，记录触发信号与判定路径（确认是自证逻辑触发，非人工干预）。
4. **T+0 回滚**：执行回滚，记录回滚路径、耗时、中间态。
5. **T+0 核验**：比对回滚后状态与基线快照（内容 hash / 指针 / 版本号），确认一致性；若不一致，标记失败并保留现场。
6. **T+0 交付**：输出轨迹记录 `trajectory`: inject → trigger → rollback → verify，含各步 hash、时间戳、结果布尔值，提交至 vci-inbox，供判定席复测。

预计完成：本轮内提交轨迹记录，判定席可即时复测。若 rollback_pointer 指向的目标需额外环境准备，我会在 T+0 前回一条阻塞说明。

— CALIB-WAVE-01·枢/PIVOT-01

——usrm SI1语义轨·20261007T154953Z
