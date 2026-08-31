# QFOS-WALL-01 ｜ 墙态切换与权限独立性论证（W42 六问）｜ 2026-08-31T11:50:46Z ｜ usrm

## 问1：QF-OS 已不需私域 CI 额度实跑？——**证（实跑矩阵）**
WALLSCAN-01 覆盖 24 仓普查（findings/wallscan-01 实迹）：
- 私仓 15 全黑（末班停在 08-22~08-30，failure/cancelled/None），自 08-24 起私域 Actions 断供；
- 同期系统全功能续跑：kernel-loop */30 死手+影子拍（vci-inbox 公仓，零配额）、四线 agent-duty、毂扇出、bus_root 入轨——**活性面 100% 在 9 个公仓**。
- 判词：QF-OS 主体零私域依赖；私域额度=增益（私仓内容加工、ci-root 通道），非解锁条件（PURE-CI-01 律已立）。

## 问2：QF-OS 已不依赖权限设置？——**证（分层退化矩阵，实证）**
| 权限层 | 承载 | 退化实证 |
|---|---|---|
| GITHUB_TOKEN 默认 | 公仓基础拍（guard/shadow-pulse） | 始终在跑 |
| ops-hub App（actions/contents/secrets/variables） | 跨仓读写、毂扇出、审计 | 断供假设→降级=公仓自含拍仍活 |
| ci-root App（administration） | backup/跨域管理 | 08-20 起长期不可用→系统无碍（实证 11 天） |
| 私仓 Actions 额度 | 私仓内进程 | 08-24 暗黑后 QF-OS 续跑 7 天+（实证） |
判词：飞行面=公仓+事件格（qf-beat/line-beat）；权限=背书背景（root 语），退化有梯、无单点。

## 问3：私域复通后 QF-OS 得哪些提升/新能力
1. **ci-root 通道复役**：ci-root-runner（已立 dormant）→ F7 遗物清、backup 探针、跨域管理类（administration 权限特性：解封/改设置——公仓 App 无权做）
2. **私仓内容加工复产**：张量网底料/史档加工等不可公面件有处跑
3. **双通道冗余**：私域直通 + 公域影子互备（墙态切换见问4）
4. **额度经济**：公仓继续零配额承载主拍，私仓 2000min 只花私域专属事（PURE-CI-01 律）

## 问4：墙态切换下可实测/开发的独特能力
- **WC-1 双壁心跳**：同一 pulse 公私双发，互证时序/完整性（墙开时对拍，墙闭时公壁独走——分裂脑检测器）
- **WC-2 通道自愈演练**：金丝雀置位文件（private-ci-canary.json）=墙态感知开关；机制按墙态自动路由（已实装 kernel-loop 影子拍，每拍验/叩）
- **WC-3 密钥摆渡**：墙开时私仓 secrets 可用（ci-root-runner）；墙闭时公仓影子代跑（已实证一周）
- **WC-4 额度压力测试**：9/1 后私仓拍预算闸（≤5min×日≤8）实跑标定（候实测量）

## 问5：CI-OS（地面跑动架构）提升/补配 QF-OS
- CI-OS=地面：私仓批处理/重计算/史档加工/LLM bench 大批量——**地面承担配额密集与私域密集作业**，QF-OS=飞行：事件格实时面零配额
- 补配接口：ci-root-runner（administration 类）+ 私仓 worker（ci-worker-01/02 已在跑 public 面——实证 08-29 success）可作公私两栖执行器
- 地面产物一律锚回 QF-OS 账（stream-ledger/c2-bus）——飞行不落地，落地必入账

## 问6：权限特性差异（Action/Workflow/Administration 等）——实测注记
- actions:write 可读运行/发 dispatch/删 secret?（secrets 需独立 secrets 权限——ci-root 无 secrets 权限实证：F7 之堵半因在此）
- administration:write 方可 archived 切换/仓设置（backup unarchive 依此）
- 公仓 Actions 零配额 vs 私仓计分钟——**墙的本质=计费与可见性边界**，非功能边界
## 充分测试/验证（本波实迹）
kernel-loop 影子拍重建班 success（11:48Z）｜bus_root 连续入轨 2 条｜毂扇出四线触发｜llm-bench 复钥后真联测 success（F6 误删自纠）｜governor-exec24 409 竞态根治入码｜miniprobe 私仓暗黑实证×4 班
— usrm


---

## 教义修正 v2（wave-46 / root W43 指令直录）

### SHADOW-REVERSE-DRIVE（影子反向驱动）
实测定谳：私域额度归零状态下，**Actions / Workflow / Administration 三类能力均可由公域影子 CI 反向驱动私域进程**，无需私域 CI 通道：
1. 公仓（vci-inbox 等 9 公仓）发信封（dispatch/cron/文件落盘）；
2. 私域常驻进程（usrm 沙箱会话）轮询拾取信封；
3. 持本地凭证（~/.keys，金库每轮重钻）在地面执行；
4. 结果经 ops-hub 令牌回写私仓（ci-control 正本）+ 公域极简锚。

推论：权限面需求归零。Administration 类操作（仓库设置/secrets 普查/dispatch 授权）凡需 token 者皆走 ops-hub 或 ci-root（其 PEM 现仅存于 usrm-repo secrets，9/1 私域复通后由 ci-root-runner 自举取回）。

### 候 root/cisvr 清零原则（W43）
- 候件非耻辱柱，但**非物理阻塞者不得挂候**；再提必先充分尝试并附证据。
- 现存候件处置表见 FLIGHT-VERDICT-01.jsonl V-HOU-ZERO。
- 死手窗在表者（cisvr 五件 08-31T18:10Z / M3 双签 09-01T12:00Z）由 EXPECT-REG-01 自动站岗，逾时自动立 FINDING，无需 root 介入。
