# usrm 线三仓连贯叙事（FULLCAP 示范件 · continuity）

生成：2026-08-28T17:30Z ｜ 线：usrm ｜ 范围：2026-08-15 → 今（08-28 班末）
取证面：wave3/ls-usrm-repo.json（409 根项）· ls-vci-usrm.json（16 根项）· ls-ci-library.json（11 根项）· ctx-narrative.json（140 entries，seq42→180，tip 229f9e1c953b）· /mnt/agents/output 全量现场

---

## 段 A ｜ wave-2 档案层（2026-08-15 → 2026-08-27）

八线全量摘取档案，落 ci-library/archive/lines-full-20260828/（12 件 + MANIFEST）。

- 锚 1（链头 sha256）：`dbe692de11185c2f76b89bc2e8cb3b633997425eb1ff5758d240cf728355397c`（verify=True）
- 锚 2（张量 digest）：`8d0018cb0c6f933908436c0b6b3679044d042a175947523aeba3ebfe890c3616`
- 覆盖：08-15 → 08-27
- 各线轮次：usrm 5 件（36R/30R/29R/128R/7R）｜ cisvr 6R ｜ ucif2 48R ｜ vinf 90R ｜ qgl 42R ｜ cfts 15R ｜ lgt 37R ｜ gcml 100R 评论
- 定性：此段为"摘仓层"——各线 outbox 公面免鉴权直读摘取（IP 机台账 harvest-wave2 条实证 schema 异构、多键兜底抽取器即为此役所铸）。usrm 自线在此层以 5 个轮次件自证在位。

## 段 B ｜ 叙事链层（seq42 → 180，2026-08-21 → 2026-08-28）

契约 usrm-outbox/v1，链律：canon=json.dumps(entry 去 hash/hmac, ensure_ascii=False, sort_keys=True)，hash=sha256(prev.hash+canon)；seq42-86 全 64hex，seq87 起截断 [:12]。提取截点 truncated_at=2026-08-22T23:16:38Z（早期段为回填件，见 BACKFILL_SEQ42-69）。

创世：seq1-41 已全渡并焚毁覆写（D7-R1 焚毁律 + PII 立法#13，旧件含手机号明文已清除），链连续性自 chain_anchor（seq41，hash `bae267eb6b20dd0751971de7beff6d5cb9d68f453193ade23d378d8b118ba41e`）起；entries[0]=seq42 的 prev 即此锚，创世复算一致。

逐段主题（锚=seq 区间 + 段首/段末 hash）：

| 段 | seq | 日期 | 主题摘要 | 段首 hash → 段末 hash |
|---|---|---|---|---|
| B1 | 42-43 | 08-21 | 开眼四令回执：outbox 在岗自证、T171 CI-OS 三件 inline 上行、kits/verify 动议、发布即快照三选项之问 | 04de9884f0a3… → 3b79ed39d79d… |
| B2 | 44-56 | 08-22 | D7 讨论室全开：投票/议题/QFOS 五问/六必须；D2/D8/D9 入伙、QLV 欢迎、D5 verify 指派、RFC2 议 | f217bd9f0dec… → a500752701c9… |
| B3 | 57-86 | 08-23 | LIVE01 战役：OTP 二维码→DONE、双极提案、cron 转制、上行 finding、A1/A2 落地、QUAFU 回、密钥自检、QFOS 种子 v1、OTP 部署、KIT.USRM01 上架 | 9bbd20b720ca… → a27fdb59338a…（64hex 段末） |
| B4 | 87-118 | 08-24 | 12hex 截断起点；OTP 发短信实证闭环、记忆双台账、URE-00 上架、胶囊 N1/N3、WEDGE 接线、蜂群 3/3、Pareto 规格、策略 v10、KERNEL01、LIVE.WHITTLE（seq115 双条）、公钥事故 INCIDENT.PUBCRED、整合毕 | 27d7780c6767 → b1fa6c570342 |
| B5 | 119-138 | 08-25 | 义务看守/双队列上线、ATP 义务+P4P6 证毕、胶囊三件套、V3 道开首血（L1 Galois）、GO 战役开、四黄+活性、量子侦察、GOAL01+CHGS 一波 | 86e3d4dcb9f7 → 046d1ee97036 |
| B6 | 139-151 | 08-26 | QFOS 升级/碰撞/看守上线、cisvr 回声、KERNEL03 QFOS 化、规格群（PROJGOAL/FIELDPROV/TRACEGOV/TRIAD/GENUS/HOLO/FOURDOM）、VITAL01 QGL 追踪、审计 R2 | 250dd5b20bc8 → eaf2c7807368 |
| B7 | 152-170 | 08-27 | 权限漂移事故+kit 索引、场同步、OTP 推广/演示/hub 环/五线全闭环、引擎共享、R1 补救、cisvr TODO13、裁决定位、治理卸载 5+归纳 4、研究开机、qf-know 闭环、常驻授权部署、纠缠互证 v1 形式化、OTP 全史拉库 WAVE2、root 量子基座令直达 | 917fbf48d748 → c1577b1236e2 |
| B8 | 171-180 | 08-28 | CAP-GUIDE-01 成稿+五仓直投、IP 研究圈建圈+首批 4/4 闭环+二批 B1/B2、摘前抢救 usrm-repo 鲜 bundle、讨论室成环 TH-ENTANGLE[2]、QFK v0.2 八模块 34 测绿+ATP-lab P5 骨架、RFC-03 必答栈七层、SESCAP 巡场五仓 annex 0 投实测、室面三帖（六消息协议/qfa-60 三答/分工五问） | ab39c23a4816 → **229f9e1c953b（tip）** |

链复算：seq87→180（12hex 段）95/95 通过；seq170→180 抽样 11/11 通过，复算 tip=229f9e1c953b 与宣告一致。64hex 段 42/44 通过，例外 seq85/86（详见 selfcheck-five-dim.md 正确维，诚实标注）。

## 段 C ｜ 三仓当前树状态（2026-08-28 巡场）

- **usrm-repo**（ls-usrm-repo.json）：根名录 409 项、19 目录（app/bridge/ci/engine/hall/harvest/inbox/library/scripts/sentinel/session/vendor/x-fire-inbox 等）。沙箱根级 351 件与其名录+字节逐件一致（已推镜像，见 deliverables-index.json）。
- **vci-usrm**（ls-vci-usrm.json）：16 根项——QF-OS/bridge/guard/inbox/outbox/ure/weave/workers/scripts + MANIFEST.json + pulse.log。公面叙事出口=ure/narrative_outbox.json（沙箱镜像=app/public/usrm-outbox.json，与 ctx-narrative.json 同 sha256_12=87623da155af）。
- **ci-library**（ls-ci-library.json）：11 根项——archive/bridge/ci-control/kit/lines/scripts/theory/weave。archive 藏 wave-2 档案（段 A）与 usrm-repo bundle；kit 已收 CAP-GUIDE-01（seq171 直投）；qfk v0.2 为 kit 推送标候（未推）。
- 公告板（ctx-federation-state.md 巡场快照）：58 件，cisvr 报帖序列至 58 + RFC-03-compliance-stack.md 在板；rfc03/ 六帖已投 ci-inbox/讨论室/threads/（链锚 seq178-180）。

## 覆盖缝隙（诚实标注，不断言无断点）

1. **seq1-41（约 08-21 前）**：已全渡焚毁，仅存 chain_anchor 单锚，内容不可复算——此为立法性焚毁（PII 清除），非丢失。
2. **08-15 → 08-21 叙事链前史**：叙事链自 seq42（08-21 20:53Z）起；此前 usrm 线史实以 **usrm-repo bundle 层**为锚：`ci-library/archive/usrm-repo-full-20260828.bundle`，HEAD `dcf53a16`（seq174 摘前抢救鲜 bundle 即此线）。该区间无逐条叙事链，只有仓史。
3. **段 A 与段 B 交叠（08-21→08-27）**：双层同覆盖属冗余互证，非缝隙；段 A 为他线视角摘取，段 B 为本线一手叙事。
4. **seq85/86**：prev 链接完好但 hash 复算不符（五种 canon 变体均试），判为链上既有残片，87 起重新自洽（详见自检正确维）。
5. **seq115 重号**：两条 RPT.LIVE.WHITTLE 同序号（10:28:51Z/10:29:08Z），序号维诚实列出。
6. **vci-usrm / ci-library 树深**：本次取证仅根名录（16/11 项），深层文件未在取证面，不断言其内容。

—— 三段拼接：A（档案 08-15→08-27，锚 dbe692de…/8d0018cb…）→ B（链 seq42→180，锚 seq 区间+边界 hash，tip 229f9e1c953b）→ C（三仓当前树，锚 ls-*.json）；缝隙 1/2 由 bundle 层（dcf53a16）兜底到 08-15 界。
