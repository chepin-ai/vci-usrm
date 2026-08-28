# VERDICT · HOLO-IFACE-01 原型 v0.1 全量实现+真跑判词

- 判词: **PASS(v0.1 五件全交付, 全真跑, 零编数)**
- 投影基线 ts: **2026-08-29T03:10:00Z**(=holo-ctx 各源事件时间字段最大值; deadline 未来值不入基线; 不取墙钟)
- 版本: holo-v0.1 · 执行环境: python 3.12.12, 本地零网络

## 1. 五件交付清册(字节数实测)

| 件 | 路径 | 字节 |
|---|---|---|
| 件1 生成器 | holo/holo-gen.py | 35674 |
| 件1 规范化态 | holo/holo-state.json | 41416 |
| 件1 烘焙产物 | holo/dist/index.html | 49935 |
| 件1 快照链节 | holo/dist/snapshot.json | 215 |
| 件2 折射引擎 | holo/refract.py | 17138 |
| 件3 首问原件 | holo/ask/QQ-20260829-001.md | 1116 |
| 件3 首问答件 | holo/answer/QQ-20260829-001-answer.md | 5773 |
| 件4 候选 workflow | holo/holo-loop.yml | 1703 |
| 件5 本判词 | holo/VERDICT.md | (本件) |

## 2. 快照哈希链

```
sha256 = 65a23324b11b93ce5384fae29beec95f18e7032846da37bd410ab9836fdec448
prev   = 765d16e5b07603407ea1db0096a6388d4b6f89066591a75fd66d3b52de0fb96f
ts     = 2026-08-29T03:10:00Z   version = holo-v0.1
```

链史(本班次实测推进): `GENESIS → e78fcf0c7cef… → 765d16e5b076… → 65a23324b11b…`
(每节=一次内容变更重烘; 内容未变则幂等不推进, 已实证)。

## 3. 确定性声明与复跑比对证据

声明: **同 holo-ctx 输入 + 同 holo-gen.py 代码 ⇒ 同 dist/index.html 字节 ⇒ 同 sha256。**
机制: 投影 ts 一律取数据基线(不取墙钟); 快照哈希不入 HTML 本体(防自指循环), 故 HTML 字节只依赖 ctx+code。

实测(本班次真跑, `cmp` 字节级比对):
1. `python3 holo-gen.py` 连跑两次 → dist/index.html **IDENTICAL**, dist/snapshot.json **IDENTICAL(幂等未推进)**。
2. `python3 refract.py && python3 holo-gen.py` 全链复跑 → dist/index.html 仍 **IDENTICAL**(refract 同为确定性: 答件 ts 取数据基线)。
3. 变更输入(答件字节 5819→5773)后重烘 → sha256 按链推进(e78f→765d→65a2), 证链节对内容敏感。

## 4. 八面板数据计数(末次生成器 stdout 照录)

| 面板 | 计数 | 数据源 |
|---|---|---|
| 水晶球 crystal | 问件 1(已折射 1) | holo/ask/ + holo/answer/ |
| 态势总览 sitrep | 线态卡 3 · 死线表 25 · 实例状态分布 ACTIVE15/CONVERGED14/QUEUED1 | FLEET-STATE/KERNEL-STATE/beacon-mirror/circle-state/EXPECT-REG |
| 链面 chains | tip 12(叙事链 seq193 · beacon seq64 · kernel ledger seq82 · stream-ledger head · 8 基座锚) | usrm-narrative-tip/beacon-mirror/KERNEL-STATE/circle-state/BASE-REG |
| 注册面 registries | 实例 30 + 基座 8(reg_hash=cd7a4ec446e6) | INST-REG/BASE-REG |
| 欠账面 obligations | open 11 · **overdue 1(EXP-017, 死线 2026-08-29T02:22Z < 基线, 机算标逾)** · watching/armed 14 · 引擎直决销案 5 | EXPECT-REG-01 |
| 知识面 knowledge | QKSA 基座 8 · 最近判词 3 · kernel 逐项判词 11(EVIDENCED 10/STALLED 1) | BASE-REG/usrm-narrative-tip/KERNEL-STATE |
| 指挥面 command | schema 4 字段 · 在途提案 2(候义务机批准) | kernel-proposals |
| 元面 meta | 数据源清册 11 件(各带 sha256[:12]) · 确定性声明 · 约束 3 条 | holo-gen 自身 |

beacon 锚停滞声明(机算): seq=64 ts=2026-08-28T22:39:27Z, 落后基线约 **4.5h** ⇒ 按降级声明制标注停滞窗口, 不作实时锚声称。

## 5. 首问真跑(QQ-20260829-001)

- 原件: root 界面令照录 ctx §0(一字不改, 「」引块为问体)。
- 折射: R1 照录全文 / R2 析出行动段 14 条 / R3 锚定命中 12 条(cisvr 实例×4 回填真状态、公告板/讨论室/提案/态势/指挥/水晶球/QF-OS/dashboard) / R4 升维一句 / R5 三视角。
- 路由: **L1**(命中跨线协同词: 协同、共同、所有其他方、@、大家)→ dm-queue → **cisvr + T5Q3**(照 root 令 @ 提及)。
- 答深: **L0 机械答**(重构+锚定+答架+路由), 诚实声明不冒充深答; 深答候 L1 回填。

## 6. 架构约束符合性自检

- 零客户端凭证(E804): 数据全部构建期烘焙, index.html 内 `fetch(`/`http(s)://`/CDN 计数 = **0**(机检 grep)。
- 单文件 HTML: vanilla JS + inline SVG(水晶球徽标 + 实例状态分布条), file:// 真开实测(八面板 tab 逐一点验)。
- UI: 米白底 #f6f1e7 / 深墨字 #2d2a24 / 赭石 #a05f2a + 苔绿 #66795a 点缀; 无蓝紫渐变, 无高饱和背景, 中文界面, 衬线书卷风(非 Google 风)。
- 密钥模式零触及: 两脚本只读 holo-ctx/ask, 不写任何仓外路径, 无凭证面代码。
- 投影数据只来自 holo-ctx(+holo/ask·answer 自身件); 元面清册 11 源各带 sha256[:12] 可回溯。

## 7. 灰标(未交付/候裁决, 诚实挂账)

| 项 | 态 |
|---|---|
| 讨论面/北星面 | **v0.2 候**(讨论面数据源=board-index 已在锚定词表, 面板未立; 北星五判据=EXP-032 open) |
| 公仓密封轨(SealedBox 兼容 DASH_PK 血统) | **候**(双轨发布公域半轨未建; 私仓明文轨=本件) |
| CI 激活(holo-loop.yml 落 .github/workflows/) | **候 root 08-30 workflow 解禁裁决**; 过渡期 OS 端班次代跑 |
| holo/direct/ 指令投递面 | **v0.2 候**(指挥面 v0.1 只显 schema+在途提案, 不收支写) |
| FEED-REG 各线 feed 适配器聚合 | **候共建**(L1 路由 cisvr+T5Q3 后立项) |
| GitHub Pages 开启 | **候 root 一键**(ctx §3) |

## 8. 复现径

```
cd holo
python3 refract.py     # ask/QQ-*.md → answer/ + crystal 面板
python3 holo-gen.py    # holo-ctx → holo-state.json → dist/index.html + dist/snapshot.json
python3 holo-gen.py    # 复跑: dist 字节不变, 快照幂等不推进
```
