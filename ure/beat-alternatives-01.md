# BEAT-ALTERNATIVES-01 · beat-forward 不依赖 vci-inbox 的方案谱 + 线环实证
usrm 2026-08-30T09:43:17Z ｜ 应 root W39 问：「beat-forward还有其他方案？不依赖vci-inbox」

## 〇、现状基线（已实证）
- 主道 hub qf-beat：**已通**（ops-line 扩面后 vci-vinf 两连实证 dispatch 204 → hub 15wf 齐起、kernel-loop success）。
- 纯血纪律：跨仓事件必须经鉴权叩门（GITHUB_TOKEN 不出仓、workflow_run 不跨仓、公仓 raw 只读）——任何「不依赖 vci-inbox」的方案只能换**叩门对象/方向**，不能消除叩门。

## 一、方案谱（六案）
| # | 案 | 机制 | 依赖 | 凭证 | 评 |
|---|---|---|---|---|---|
| 1 | **线环互叩 BEAT-RING-01** | 4线仓成环 vinf→ucif2→cfts→qgl→vinf，班次结束叩下一线（line-beat），cause=beat-forward 不转叩（级联≤1） | ops-line 覆盖线仓 | CI_OPS_LINE_KEY（线仓已有） | **荐作同哲学冗余**：hub 失联时线间自热；已实装 |
| 2 | 仓内自链 | workflow_run:completed / push 触发本仓后继 wf（watchdog/shadow-pulse 已是此形） | 无 | 零 | 已有；只能热本仓 |
| 3 | hub 拉模式 | kernel-loop/bridge-poller 死手拍内读 4 线公仓 outbox（raw 零凭证） | vci-inbox（读侧） | 零 | 已有；是轮询非事件，最稳兜底 |
| 4 | 轮值汇聚点 | 指定一线仓（如 vci-qgl，持 OTP 摆渡）作备用汇聚：众线叩它，它出汇总 outbox 供 hub 拉 | ops-line 覆盖线仓 | 同#1 | 可选；汇聚点本身仍单点 |
| 5 | Gitee 镜像总线 | 经镜像仓 webhook 传拍 | 外部 Gitee | GITEE_* | 引入外依，非纯血，不荐为常道 |
| 6 | kimi.link/lgt 摆渡 | 既有摆渡慢道传拍 | kimi.link | 摆渡件 | 小时级兜底，不荐为常道 |

## 二、BEAT-RING-01 实装与实证（本轮）
- 4 线仓 agent-duty 皆换环版 beat 步：hub qf-beat + 环 line-beat 双叩、按目标仓各自 installation 铸 token、cause=beat-forward 止叩守卫；4/4 YAML 绿。
- 实证（vci-vinf run 33305086587）：hub `qf-beat 204` ✓；环 `ops-line 未覆盖 vci-ucif2 HTTP 404`——**ops-line 安装面仅含 vci-inbox，未含任何线仓**。
- 精确卡点：root 于 ops-line installation 同面板再勾 4 线仓（vci-vinf/vci-ucif2/vci-cfts/vci-qgl）→ 环即通（代码已就位，零再改）。
- 副产物实证：首次环试 403（误用 hub installation token 叩线仓）→ 已修为按目标铸 token；403/404 语义分判在案（403=装在选区外，404=未安装）。

## 三、结论建议
- 主道：hub qf-beat（已通，不动）。冗余：线环（荐，候 root 一键）+ hub 拉（已有）。常道不引外依（⑤⑥仅急备）。
- D-157 纪律守界：一切 beat 带 cause=beat-forward 者**不转叩**，环/网永不风暴。
