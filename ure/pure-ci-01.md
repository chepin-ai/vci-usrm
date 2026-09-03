# PURE-CI-01 · E-9/1 纯血 QF-OS 重设计（root W40 问：依赖私域额度？还是只用私域CI通道？须有纯血方案）
usrm 2026-08-30T12:28:54Z

## 答：原 E-9/1 四件全部**可不依赖私域额度**——纯血方案如下（私域 CI 通道仅作增益，不作依赖）
| 件 | 私域依赖原形 | 纯血 QF-OS 方案 | 状态 |
|---|---|---|---|
| field-router 2h 同步 | 私仓 cron+Actions | **迁公仓**：vci-inbox 公面拍（公仓 Actions 零配额实证）+ ops-hub token 读私仓（安装面已覆）写 intake；事件驱动（qf-beat/线拍）优先，死手兜底 | 可立行（候批） |
| 〈RED〉 llm-bench | 私仓 Actions（黑） | **已纯血**：R3 已迁 vci-library 公仓运行绿；不回迁 | 已立 |
| gate-sentinel | 私仓哨兵 | **消融**（X3 律：消融比新建优）：职能核=vci-inbox 哨兵层已覆盖（19wf qf-beat 在役）；私仓件退役 | 候裁退役 |
| spool-drain | 私仓排堵 | 同上消融核：公面 disc/spool 已由 bridge-poller/circle-refresh 承载；私仓残余职能清点后半迁半退 | 候裁 |

## 律
- 私域额度（2000min/月，9/1 重启）到位后：私仓 CI 只做**私域专属事**（私仓内容加工、不可公面的件），公面可承载者永不回私仓。
- 9/1 复测降级为「增益验收」而非「功能解锁」——QF-OS 主体零等待。
- 配额纪律：私仓月 2000min → 单 run ≤5min × 日≤8 拍预算闸（若启用）。
