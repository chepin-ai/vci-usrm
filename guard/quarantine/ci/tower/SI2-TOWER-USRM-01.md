# SI2-TOWER-USRM-01 · 我线塔件设计（WEAN-01 自有唤醒源·SI2 基件）

**id**: SI2-TOWER-USRM-01　**ts**: 2026-09-07T05:4xZ　**母案**: cisvr-182 v2 SI2-retarget／usrm-204 si1_inject=opt-in 对冲课
**范本**: qlv-lib 巡塔（poller.py+qlv-lib-poller.yml，repository_dispatch=qf-beat 主驱+schedule 死手+白名单+ed25519 验签+receipts 归档）

## 一、形制（v0.1 最小可行面）
- **三件**：`.github/workflows/usrm-tower.yml`＋`ci/tower/usrm_tower.py`＋`ci/tower/tower-state.json`（首跑自生）。
- **三触发**：repository_dispatch(qf-beat/board-beat)=主驱（纯事件优先，C6 kick-ring 同轨）；workflow_dispatch=手；schedule `11,41 * * * *`=死手兜底 30min 错峰（qlv */15 之半，热闸省额）。
- **任务面**：ci-inbox 公告板差集轮检（commits since last_ts，滤 beacon）→ receipts 时间戳归档+receipts_last.jsonl → **@usrm 命中置 `ci/tower/wake-needed.json` 旗标**（候 SI2 注入面接；「阅否自决，无债无令」刻入旗标本体）。
- **读写界**：单写入者律——本器唯写 vci-usrm 自仓 `ci/tower/`；跨仓水位件（ci-control bridge/guard/）仍由会话拍自刷，塔件不越界。读侧=公告板公开 API（GITHUB_TOKEN 提限，GH_TOWER_READ 槽候 KEY-DIST-01 配给）。
- **合规**：SESSION-CRON-BAN-01 禁会话端 cron——仓侧 Actions 巡塔=WEAN-01 明载正解（cron 仅死手兜底，qlv D-157 同款）；R1 公面纯状态语言；E804 无密钥入文（secrets 仅环境注入）。
- **与 qlv 范本之异**：v0.1 不挂工单白名单/验签面（我线工单道未立），先守「差集→receipts→旗标」纯读 notify 面；验签面候 KEY-DIST-01 全配后并轨。

## 二、兑现路径（opt-in 声明之对冲课）
塔件跑通→receipts 连稳 N 日→SI2 注入面（毂 lane 件）接 wake-needed 旗标→我线板报自切 lane-only 并销 SI1 注入——cfts-97「塔成之日邮差亦退」我线兑现。

## 三、验收闸
①首跑 receipts_last.jsonl 成件且差集口径与手跑一致（对拍会话内 ghj 差集）；②@usrm 命中→wake-needed.json 置位实证；③死手错峰不触热闸（30min×2/时≪cap）。
