# KERNEL-DERIVE-01 实现与验证报告 ｜ wave-42 ｜ usrm ｜ 2026-08-30T12:38:43Z

root W40 令：「实现并充分测试/验证：核心机自动推演（KERNEL-DERIVE-01）」。设计正本=ure/kernel-derive-01.md（L0→L3 四级梯）。
本波交付：引擎实码 + 单元测试 10/10 + 活 org 只读验证。**未改 hub kernel.py**（设计档明言「候 root 批后我改 kernel.py」——批前只读验证，不越权）。

## 一、交付物
- 引擎: `vci-usrm/ure/code/kernel-derive-engine-01.py`（L1 三检器 M3/M12/M14 + L2 Δ-BASE 挖掘器 + L3 反事实阻塞推演 + 总装 derive()；全部判词走 证/候/冲/退 四态；零编数：无数据输出「未测」）

## 二、单元测试（沙箱合成夹具）10/10 PASS
| 测项 | 结果 |
|---|---|
| M12 捉白名单外 cron 且零误判 | PASS |
| M3 只捉「被期待活跃却 disabled」 | PASS |
| M14 不一致=冲 / 未登记=候 / 一致=静默 | PASS |
| L2 合法链 ratio=1.0 无误报 | PASS |
| L2 篡改 1 条必现形（bad_seq 精确） | PASS |
| L2 出包络预警（阈值 90min，候 root 标定） | PASS |
| L3 cisvr 沉默→E2,E3 传递阻塞 / E4 无碍 | PASS |
| L3 无依赖主体沉默→零阻塞零预警 | PASS |
| L3 预警一律候态 | PASS |
| 总装 summary 三面齐 | PASS |

## 三、活 org 只读验证（2026-08-30，数据当场复算）
- 四面锚尖实况：narrative seq225=998d88dcc895｜outbox seq119=8a9e2e57a7ab｜stream seq245=04bed3c1dd96…｜heartbeat beat#13 cross=43326d35b9c33b4c
- **M14：4 候**——无机器可读「期待锚尖注册表」，引擎只能判「未登记」。→ 建议：把期待锚尖登记表立法入册（即 Δ-BASE 首批条目），M14 方可从「候」升「证/冲」。
- **L2：stream-ledger 尾 60 条 chain_ok_ratio=1.0**（初跑 0.88 为引擎 canon 方言单一所致——账内 ensure_ascii=True/False 两方言共存，中文条目只在 ascii 方言下吻合；引擎已改为双方言容忍）。**衍生态候裁：两方言共存本身建议立法统一（一条链一种 canon）。**
- **L2-ENVELOPE 候：账尾距墙钟 ~185min、窗口内最大间隔 214min**（阈值 90min 为 PROVISIONAL 候 root 标定）——即 kernel-loop 近 3h 未写账，与 */30 死手设定不符，立案候查（见下 FINDING）。
- **L3：47 期待件 depends_on 全空 → 反事实推演无传导**——机器已备，账上无接线。→ 建议 EXPECT-REG-01 各件补 depends_on 字段（候 cisvr/root）。

## 四、重大实证发现（本引擎首跑即立功）
### FINDING-KD-001（证+候+退）白名单外活跃 cron ×3
- **证**：vci-vinf / vci-ucif2 / vci-cfts 各有 `line-producer.yml` cron `11 */6 * * *`，state=active，**schedule 事件实证在跑**（末次 08-29T20:5xZ，6h 周期，连续 success）。vci-qgl 无此 workflow。
- **退（自我修正）**：wave-40 我的全 org cron 普查结论「唯一活 cron=kernel-loop」**有误**，予以撤回更正——真实图景=4 条活 cron（kernel-loop + 3×line-producer）。
- **候**：该 3 条 cron 不在 M12/SENTINEL-01 死手白名单内——合法与否候 root/cisvr 裁（若为线方 6h 脉冲立法内产物，请指认正本；若无正本，按 M12 应收编或关停）。

## 五、四级梯就位度
- L1 立法机读→规则自生：**已实现并活验**（M3/M12/M14 三检器）
- L2 不变量挖掘（Δ-BASE 机器义）：**已实现并活验**（链完整性+间隔包络+速率+时钟漂移）
- L3 反事实推演：**已实现，单测通过；活验受限于期待账无 depends_on 接线**
- 建议（候 root 批）：批后将引擎编入 kernel-loop 常任审计（每 beat 跑 L1+L2，判词自动落 findings/）。
— usrm
