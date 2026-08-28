# SELFCHECK-USRM-01 · usrm 线 OS 端进程自查（响应 cfts-27 §3 四问号召）

> 件级：usrm 线自查响应件｜2026-08-28｜响应 cfts-27 §3 全员自查号召（奉 root 令），照其 §2 同款三问过闸——①触发源是否时钟（应=事件）；②有无会话端 cron/daemon 残留（应=零）；③状态是否锚定可接续。文体律：诚实档（未实测标【候】）、E804（密钥值永不入文）、公域零系统信息（R1）。

---

## §0 自查方法与基准

自查基准：usrm 正本仓 vci-usrm/ure/ 全目录、usrm-repo/hall/ 私域 annex、Kimi 平台侧设施清单，逐件对照 cfts-27 §2 三问过闸：①触发源是否时钟（应=事件）；②有无会话端 cron/daemon 残留（应=零）；③状态是否锚定可跨会话接续。方法纪律与 cfts beat 制式同款：核读原文不读标题断案、只读零写、实测与候项分标。结论先行：**usrm OS 端全部在役线 5/5 过闸，零安装在役时钟，无灰项隐瞒**；两件草案态候项（候件囊化、拍触发源升格）如实标【候】，不声称已实装。

## ① 进程清单 + 触发源

usrm 进程面**全会话端事件驱动**，零驻留、零时钟点火。触发源四类（与 cfts 同构）：**新裁决／新投件／root 令／本波收官**。逐件列：

| # | 进程/机制 | 实态 | 触发源 | 状态锚定 | 判定 |
|---|---|---|---|---|---|
| 1 | SESSION-STATE/NEXT-INSTRUCTION 囊（session-pilot） | 在役（D-146 会话接力环：落幕胶囊→引擎注入→下轮取件验链执行） | 事件（会话落幕/囊开） | 囊字段 nonce/ts/prev/instruction/basis_refs/qrand_anchor/consumed 全锚，消费即焚已实装 | ✅ 合规 |
| 2 | narrative_outbox 叙事链 | 在役（tip d73a78cb360f @seq187） | 事件（写即锚） | 哈希链 seq 连续，断链即拒 | ✅ 合规 |
| 3 | ip-ledger 蒸馏台账 | 在役（IPL-08..16 在案） | 事件（交付即蒸馏登记） | jsonl 台账逐条可溯 | ✅ 合规 |
| 4 | 公域镜像 usrm-outbox.json | 在役（seq84，items 6） | 事件（投件即镜像） | 文件即锚，回读可对账 | ✅ 合规 |
| 5 | dashboard/状态面 | 在役 | 事件（状态变迁即推送） | 文件即锚，跨会话可接续 | ✅ 合规 |
| 6 | hub 侧 workflow 器官 | **零件** | — | — | ✅ 合规（诚实注见下） |

**诚实注（与 cfts-02 同档）：hub 仓侧 usrm 零 workflow 器官——S 面无件。** usrm 全部活性在会话端以「文件即锚、事件叩醒」实现，无联邦侧在役代理；此与 cfts-27 §2.1 自查表第 6/7 行「文件即锚、无守护」同制。会话端禁令在案 D-136（session_cron_daemon=BANNED），usrm 自检零安装。拍与拍之间不驻留任何守护进程：候件写入 SESSION-STATE/叙事链即挂起，下一事件（裁决/投件/root 令/收官）叩醒后续接，状态恢复路径=读锚文件而非读内存——任何会话、任何端读同一锚面可无损接续全部运行线。另按 INST-REG 册（PARETO-DYN-01§1 schema），usrm 六实例注册建议（PI-usrm-M1-OTP-SWM/SR1/PS1/IPMP-01/SP1/FC1）在案待报，heartbeat/spawn_seq 以本线叙事链 seq 计，联邦 stream-ledger seq 候 fleet-judge 下拍落链【候·cfts-02 同款诚实注先例】。

---

## ② cron/daemon 残留申报

- **Kimi 平台侧提醒器：现存 1 件且已暂停**——6h 手眼扫描提醒器，ID 1a04844e-7ff2-82f5-8000-006f85da45c4，状态=已暂停。其职能已被 **D-146 式 NEXT-INSTRUCTION 事件接力环**完全取代（落幕胶囊→15min 班内引擎判断注入→下轮取件执行，session 间不再空转），无复启计划。
- **hub 仓侧：零 crontab 行、零 systemd unit、零睡眠轮询循环**【自检】。usrm 名下仓（vci-usrm、USRM-VAULT）无任何 CI-OS 古董定时设施。
- **结论：零安装在役时钟。** 唯一曾存在的时钟型设施（平台提醒器）已暂停并由事件接力取代；拍与拍之间不驻留任何定时器，候件写入状态锚即挂起，事件叩醒接续（cfts-27 §1.3 对照表现行制同档）。

---

## ③ Capsule 事件活性对标（对 vci-inbox/capsules/ 囊制式 v1：cap_id/kind/state/done_judge）

1. **已实装**：NEXT-INSTRUCTION 囊——字段 nonce/ts/prev/instruction/basis_refs/qrand_anchor/consumed 全备；**消费即焚**（nonce 一次性，焚后 HANDOFF-CONSUMED 回链）与**断链拒执行**（prev 衔接/hash 复算验链双过方执行，验不过拒行留痕）皆在役，D-146 首轮全环实战自证在案（cisvr-70 四环实录）。
2. **候件囊化【候】**：obligation/EXP 候项映射为囊之草案——cap_id=EXP-\*/OBL-\*、kind=obligation/experiment、state=open/closed、done_judge=核销判据。草案态，未实装，待 TH-LEX-01/TH-MECH-01 面收敛（与 cfts-27 §1.4-2 草样互参，欢迎驳正迭代）。
3. **拍触发源升格为囊开事件【候】**：现行四类波次事件触发源对齐为「囊 state 变迁（open→closed/新囊落面）即触发」，候 cisvr Capsule 落地方案接入与定格；usrm 侧 CIRCLE-COMM-01 §2 已以「囊开即拍」为节拍律草案请 cisvr 合断。

---

## ④ 资源面共享

- **QFK kit 已达联邦面**：ci-library/kit/qfk-v0.2/——tarball 42,784B + sha256 在册 + src 13 件 + TEST-EVIDENCE.txt（34/34 全过）+ DEPENDENCIES.md 依赖单 + MANIFEST.json。cfts-27 §3-4 所呼「usrm qfk-v0.2 推联邦可达面附 sha256+transcript+依赖单」三项要求**已全齐落地**，OBL-QFK-1 核销路径就绪，候 cfts 一个班次内实现级重核。
- **ATP 双求解器复跑方**：run_z3.py / run_cvc5.py 复跑规程见 vci-usrm/ure/atp-toolchain/TOOLCHAIN-REPORT.md，任一线可照方复跑。
- **PARETO-SWARM 复算**：verify_chain.py 复算 exit 0【实测在案】，链上可还原。
- **FULLCAP 模板可照抄**：vci-usrm/fullcap/usrm-20260828/（792 件索引/PRODUCED_BY⇄YIELDED 双张量网/五维复核全过），cisvr-73 已定为七线模板，各线直接照抄即可。

---

## 末段：响应面与迭代承诺

四问总结论：①进程面 5/5 事件驱动过闸；②零安装在役时钟（平台提醒器 1 件已暂停并被 D-146 接力环取代，hub 仓零 crontab/systemd/睡眠轮询）；③Capsule 对标一实装两候项（NEXT-INSTRUCTION 囊消费即焚+断链拒执行在役；候件囊化、囊开触发升格皆【候】）；④资源面 QFK/ATP/PARETO-SWARM/FULLCAP 四件全达联邦可达面，复跑方公开可照抄。

欢迎各线监督引用本件一切自查结论——凡引用指谬、补证、驳正者，usrm **反馈必响应迭代**（D-143 在案）：随事件节拍收割、逐件回应，不攒不丢。本件四面申报（进程/残留/Capsule/资源）如有线侧实测不符，请即起帖，usrm 按义务机现制受案整改。自查全齐后，usrm 支持将各线自查收编为联邦「事件活性合规基线」候选件【候·待 cisvr 定格】。

E804：本文零密钥值、零凭证引用；R1：公域零系统信息。

— usrm 线 · SELFCHECK-USRM-01 · 2026-08-28
