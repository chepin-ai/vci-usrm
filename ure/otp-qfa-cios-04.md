# OTP 判词·wave-17：qfa 遗迹复核 / dm 总线定时之问 / cisvr App 写Scope / 验证码未达法医链
**PI-usrm-M1-OTP-SWM · hub ts ≈2026-08-29T04:1xZ（stream-ledger tip seq145=04:09Z 为权威）· GitHub wall 07:16Z 仅参考**

## ① OTP@qfa：CI-OS遗迹并未清除/转换完成 —— 判：root 所言【证】（hub 半面）
- hub 侧 vci-inbox 内 5 个 qfa 服务流（gitee-qfa-fetch / qfa-outbox-push / relay-otp-qfa / probe-qfa-vars / relay-probe-qfa）**全部 workflow_dispatch-only**：无 cron、无事件接线 = 手动遗迹。gitee-qfa-fetch 最近成功 08-27T19:03Z，≈35h 未跑，纯因无人按按钮。
- gitee 侧 chepin-ci/qfa-line 私仓 404 不可证【候】——已 dm qfa（D-usrm-002）请其公布工作流全清单核销。qfa-76 自报「2 流转换完成」当在 gitee 半面。
- 改造令已下：fetch 流加 schedule 死手 + qf-beat 主搏，到件自动 fan-out。

## ② 「dm cisvr 提案流检＝在途未达即时；在队未路由——事件总线自身由定时驱动？」—— 判：【证】于入口沿
- 实证：**HUB-MAIL 仓 .github/workflows 为空**——dm-queue 投件不产生任何 qf-beat；路由依赖 vci-inbox field-router 班次（定时/死手）。故：qf-beat 总线**本体事件原生**（repository_dispatch），但**入口沿无人值守、定时捡拾**——root 之问在入口沿成立，在本体不成立。
- 处方（已随 D-usrm-002 请 qfa 会签，治理机场域）：HUB-MAIL 植 push-on-dm-queue 的 beat 发射器，投递即路由；cron 降死手兜底。正合 D-157 模型补齐最后一沿。

## ③ OTP@cisvr：「事项已完成，请其完成App写Scope」—— 判：请办已正式送达【证】
- 实证：installation 〈RED〉 现 21 仓，**缺 vci-vinf / vci-ucif2 / qlv-lib**（读可写 403，B6 凭证scope分裂脑之源）。
- 已发 dm USRM2CISVR-OTP-20260829-04 请 cisvr（或转 root）将三仓加入安装实例。usrm 收权即日回迁代理包、销 B6 候案。

## ④ 未收到验证码 —— 全链法医，四级反转，终局【证：码已离站】
| 时刻(GitHub wall) | 事件 | 判定 |
|---|---|---|
| 02:19–02:20Z | 首码 run 33228672295：旧工蜂「无滑块即 CODE_SENT」乐观回执 | **冲**：收据≠送达，首码「已发」档撤 |
| 07:10Z | v2.1 正向回执版重发（issue#2）：FAILED·截图实证 kimi.com 红字「手机号格式不正确」 | **证**：root 未收码之技术根因 = 〈RED〉 值格式 |
| 07:16Z | v2.2 归一化（去非数字/去86前缀，实测 len=11）重发（issue#3）：回执 FAILED，但 artifact 截图示发码钮**倒数「88 s」** | **证+自纠**：短信确已离站；FAILED 系 v2.2 关键词表误将页面固有词「手机号（登录页签）」当报错 |
| 07:16:30Z | v2.3 修复关键词表；issue#3 与 otp_gate_state.json 法医更正为 **CODE_SENT_CONFIRMED** | 终局：码已离站，候 root 递码 |

- 遗留单轨（root 亲启，二选一）：①码在有效期内 → vci-qgl 开 `[OTP] 123456` issue 递码，核码路即刻完成 EXP-043；②码已过期 → 再开 `[SENDCODE]` issue，管线现已诚实回执（倒数态才报喜，未证实不关单，截图工件留痕）。
- 副产修法已入册：otp_gate_worker v2.1/v2.2/v2.3 三升（正向回执/号码归一化/误报剔除），commits 6e0d2758→24c75400。

## 四态汇总
证×4（①hub遗迹、②入口沿定时依赖、③请办送达+installation实证、④码离站+根因链）；候×3（gitee半面清单、App扩列执行、root递码）；冲×1（首码乐观回执，已撤并修法）；退×0。
