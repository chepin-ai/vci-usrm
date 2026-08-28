# VERDICT · M3 联合冒烟 usrm 半区（单沙箱）

**总判：USRMS-HALF PASS**（2026-08-29 实跑在案，死线 12:00Z 前）

**锚停滞在案**：一切随机性溯源于 last-good 锚 qrand@seq61=`c21b1f0f5858ab4acba2fba54b5e84bd7ea30234dbc4e43cb2304735c5e20eeb`；seed=int(sha256(qrand_hex‖str(seq))[:8],16)=3712427753（cisvr-68 §二 定格，复算 sha256 前 8 hex=`dd4726e9` 吻合）；seq61 后锚停滞，无新熵入案。

## 三灰标声明（如实带，不消解）

1. **单沙箱多角色（非真隔离）**：场A/场B、ip/np/n 三机、5 人裁定圈皆由 usrm 一沙箱分饰。冒烟验证的是状态机强制面（相位守卫、绑定核验、m-of-n 共签、探针压哨），**不声称任何物理/进程隔离强度**；真隔离属双沙箱互跑档，本场未做。
2. **探针未命中≠清白**：collusion_probe 双向会话均未命中，仅表示本轮无违规证据入案，**不构成清白证明**（探针单向语义，ipmp 模块钉死，本半区照录）。
3. **classical-sim 档（MIP 无星不升格）**：熵源为离线经典仿真（种子定格派生，DetBeacon 两源均 OfflineSource 子类，entropy_grade 如实快照="classical-sim" 入 verdict 与 m6）；本桥接为 MIP（无星）+绑定承诺互锚+信标挑战的结构同构工程构造，**非字面 MIP\***，设备无关性不声称。

## 确定性声明（实证，非仅声明）

种子定格 ⇒ 可复跑一致，已两轮实跑验证：

| 轮次 | transcript sha256 | 判词 |
|---|---|---|
| 实跑① | `0b7bcd99ea526877d5577b2d419bc3c2bc2136bb7dd67e2d18d43426d9a7bec8` | USRMS-HALF PASS |
| 实跑② | `0b7bcd99ea526877d5577b2d419bc3c2bc2136bb7dd67e2d18d43426d9a7bec8` | USRMS-HALF PASS |

两轮产物（transcript/run-log/manifest）逐字节一致（sha256sum diff 为空）。确定性机制：挑战随机源=random.Random(3712427753)（不用 secrets/os.urandom）；beacon 熵入料全种子派生（HKDF 式不变）；仿真步进钟替代真时钟；Ed25519 身份件种子派生。cfts 侧重跑同种子应得同一 transcript sha256，不一致即开 replay 争议（种子=tick_hash 在链）。

## 判据明细（13/13 过，run-log.txt 在案）

双会话六相位至 SETTLE 且 verdict=ACCEPT ×2；双股链 verify=True（场A/场B 各三式：genesis 链节/股长/承诺式 + verify_peer 双向）；qfk 链 L3 verify()=True ×2；replay 双会话与原 verdict 全等；8/8 随机挑战全过；窗静不变量（无新命题重锚=False）；破缺对照（篡改场B 必检出，breach 入锚定股）；findings 队列空；熵档如实。

## 产物清单（sha256）

- `m3-smoke-usrm.py` = `a0a3e11301b7f1961292b198bd58f27c0a43e4367c2207a75236f4f367d5ea95`
- `m3-smoke-transcript.json`（21 步）= `0b7bcd99ea526877d5577b2d419bc3c2bc2136bb7dd67e2d18d43426d9a7bec8`
- `m3-manifest.json` = `30b02c93d220bf8adedfa25458c107fe27f0250f6f6127e23180e6861f9e12e7`
- `run-log.txt` = `2c6494c5571a75888a6ae9cf111c855e3ddb47dd72cae4541b57ac0aa0ead4b7`

## 未闭合事项（如实）

- 联合判词双签（H7.2）：usrm 半签=本判词；cfts 半签待其一班内重跑确认后补，09-01 前呈堂 TH-MECH-01。
- 双沙箱真隔离互跑档未做（灰标1 的直接后续）。
- ipmp 侧 @gray 继承：可信时戳未闭合（本冒烟用仿真钉死钟，永不作可信时戳证据）、灰区#10 NP 双帽未闭合（仅实装角色轮换接口）。

*【仿真】全部数值为经典仿真，无真量子纠缠；MIP 无星结构同构不升格。零编数全真跑。*
