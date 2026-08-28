# 复核五维自检报告（FULLCAP-usrm）

生成：2026-08-28T17:30Z ｜ 全部数值为本轮真跑代码复算所得（Python 3 / hashlib.sha256 / json sort_keys canon）

## 维 1 ｜ 完整（覆盖 08-15 → 今）

覆盖拼图：wave-2 档案层（08-15→08-27，链头 dbe692de…397c，verify=True）＋ 叙事链层（seq42→180，08-21 20:53Z→08-28 16:45Z，tip 229f9e1c953b）＋ 三仓当前树（ls-*.json 三份）。两层交叠段（08-21→08-27）为冗余互证。

**断点清单（诚实标注）：**
1. seq1-41 已立法焚毁（PII 清除），仅存 chain_anchor（bae267eb…a41e）——内容层断点，锚层不断。
2. 08-15→08-21 无逐条叙事链；该区间由 USRM-VAULT bundle 层兜底：ci-library/archive/usrm-repo-full-20260828.bundle HEAD dcf53a16。
3. seq85/86 hash 复算不符（见正确维）——链上有残片，prev 链接未断。
4. seq115 重号双条（见序号维）。
5. vci-usrm / HUB-LIB 本次仅根名录取证（16/11 项），深层未覆盖，不断言。

结论：叙事面 08-15→今无未声明断点；声明断点 5 处如上。

## 维 2 ｜ 正确（叙事链复算，真跑代码）

- **必答题 seq170→180 抽样：11/11 全部复算一致**；seq180 复算 hash=`229f9e1c953b` == 宣告 tip == entries[-1].hash，三处一致 ✅
- 扩展全扫 12hex 段（seq87→180）：**95/95 通过**
- 扩展全扫 64hex 段（seq42→86）：**42/44 通过**；例外 **seq85、seq86** 复算不符——prev 字段链接完好（85.prev==84.hash、86.prev==85.hash），五种 canon 变体（去 hmac/去 prev/去 dtag/紧凑分隔符/prev 取值替换）均试不匹配，判为链上既有残片（疑事后编辑未重铸），seq87 起重新自洽。诚实列出，不掩饰。
- 创世复算：sha256(chain_anchor.hash + canon(entries[0])) == entries[0].hash（04de9884…b419）✅

## 维 3 ｜ 唯一（交付物 sha256_12 查重）

索引 792 件 → 唯一内容 752 份；**重复组 34 组（涉 74 件）**，全列于 deliverables-index.json 与 file-tensor-net.json 的 same_content 边。要组：
- `87623da155af`：wave3/ctx-narrative.json == app/public/usrm-outbox.json（叙事链公面镜像，**预期重复**，即 Web 版绑定的实证）
- fieldkit 镜像组 17 组：根级正本 == app/public/fieldkit/ 同件（BACKFILL_SEQ42-69/HANDOFF_TO_CISVR/SEED.qf/CARD_D7_MECH/T176 等，预期发布镜像）
- otp-gate.yml / otp-issue-trigger.yml / otp_gate_worker.py / quafu_poll.py / quafu-poller.yml：fieldkit 内两处同件（CI-CAP-MAX/otp 与 fieldkit 根，kit 打包冗余）
- 仪表盘状态件 8 组：app/public/*.json == 根级同名（cios_watch/fleet_heartbeats/library_status/library_verify/outboxes_patched/T157/T163）
- 其他：rfc03/ctx-t154.md==T154_cron_daemon_arch.md；rfc03/ctx-wakeup.md==wake_up.py（简报包直接引用源件）；T177_qr.log==T177_qr3.log；abc_1e10_seg8-15 八件空段同 hash（e3b0c44298fc=sha256("")，空文件组）；abc_field_c1e7==abc_field_kaggle

判：重复均为镜像/引用/空文件，无"同 hash 异名义"冲突；唯一性按内容计 752 份。

## 维 4 ｜ 序号可复算（seq 连续单调验证）

- seq 覆盖 42→180，**缺号：无**（missing=[]，程序化全扫）
- **单点异常：seq115 出现 2 次**（entries[73] ts=2026-08-24T10:28:51Z / entries[74] ts=2026-08-24T10:29:08Z，均 RPT.LIVE.WHITTLE，hash 4c8484208e74 / 35fe8dba6021 互异，链 prev 各自衔接完好）——序号非严格单调仅此一处，诚实列出
- 除此处外全列严格单调递增；140 entries = 139 个序号（42-180）+ 1 重号，账目自洽 ✅

## 维 5 ｜ 创世锚唯一

- chain_anchor 字段：全档**唯一**（seq41，hash bae267eb6b20dd0751971de7beff6d5cb9d68f453193ade23d378d8b118ba41e，note 载焚毁律缘由）✅
- entries[0]（seq42）创世标注成立：其 prev == chain_anchor.hash（程序化比对一致）✅
- 创世复算通过（见正确维）✅
- 无第二创世点：全 entries 中仅 entries[0] 的 prev 指向外部锚；112 条带 prev 字段者程序化全扫 112/112 指向前条 hash、0 失配 ✅
- 位置式全链复算（每条对前条）：139 对相邻中 137 通过，唯 seq85/86 不符（见正确维）✅

---

## 本交付自足数据

- session-tensor-net state_digest：`d9a5162ce805043f7d27137305f6299d03587f7618439215b0422b5ab42ffefe`（12 节点 / 8 链边+6 跨仓引用边）
- file-tensor-net state_digest：`af9793275836d6707cbc712c09ea34d849fd59fe8d5122ee134bdaa5b8270136`（752 内容节点+7 外部标的节点 / 34 same_content+27 derived+7 push_binding 边）
- 索引交付物：792 件逐件 + 18 目录聚合（另 3379 件）｜ 推送状态分布：已推镜像 351 / 候 223 / 已发布-Web 75 / 候-部分已推 42 / 施工面 31 / 已投 28 / 同名异版-候 27 / 候-未推 13 / 已推 1 / 已推-公面镜像 1
- Web/Dashboard 版：有 96 件 / 无 696 件
