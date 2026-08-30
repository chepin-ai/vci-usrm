# FORMAFLOW-RESTRICT-01 · FORMAFLOW_CMD_AUTH 定位与高度限制令（root W38）
usrm 2026-08-30T09:14:21Z ｜ 执行令：root「暂保留FORMAFLOW_CMD_AUTH线 dormant，定位并高度限制其在QF-OS中使用」

## 一、定位
- **正身**：FORMAFLOW_CMD_AUTH = 代号 **EXT-KEK-A**（CODENAME-MAP-01 在案），formaflow 线**外会话 KEK**（信封加密密钥），仅存 `ci-control` secrets（PERM-CENSUS-02 实证）。
- **沿革**：08-27 经 Dashboard 交付为现行通道件（FINDING-20260827-05）；08-28 EXPECT-REG KEYMIG-01-VERDICT-PURGE 改判「六钥零功能依赖…撤4缓2，QUAFU_TOKEN/FORMAFLOW_CMD_AUTH **缓撤死线 09-15**」。

## 二、使用面全扫（W40 实证，24仓全树）
**零 live 功能消费**。全部命中均为元数据/防护性引用：
| 位置 | 性质 |
|---|---|
| vci-inbox governor-sense.yml CRED 正则 | 防护性密钥名检测模式（保留） |
| vci-inbox knock-mint.yml 输入描述「如formaflow」 | 线名示例，非密钥 |
| vci-inbox purge-r1-history.yml 路径名 formarelay* | 子串误命中 |
| vci-inbox relay-keymig-prepare.yml KEYMIG-01 targets 名单 | 迁移元数据（dormant）；同文件残留 `secrets.AI_FULL_PAT` 引用=cisvr-57 PAT遗物→候裁清理 |
| ci-control DIRECTIVES / MATRIX-SOLVED-01/02 / POST-WALL-01 / governor-* / census | 登记/矩阵/清单元数据 |
| ci-control PUB-LINT-RULES.json | 公面 lint 黑名单（防护性，保留） |
| ci-control knock/seeds.json「for: formaflow」 | 叩门种子（线名） |

**唯一潜在消费（latent）**：qfa-ack openssl cipher（fp `db8ccb3bc90b582d`，FINDING-20260828-13）以本钥加密，沙箱无副本→暂不可解。dormant 保留使此件不失可解性。

## 三、高度限制令（QF-OS 使用纪律，即日生效）
1. **冻结新增**：任何 workflow/脚本/文档新增引用 FORMAFLOW_CMD_AUTH 一律禁止（governor-sense/PUB-LINT 防护名单除外）。
2. **取用审批**：任何取用须 root 亲批 + findings 留痕（何事/何指纹/何时/何果）。
3. **潜在消费收口**：qfa-ack cipher 推 (b) 案——qfa 改用 X25519 重封（已实证可达），重封后本钥即失最后消费。
4. **退役死线**：维持 09-15 缓撤死线；届时无新消费事实即执行删除（root 一键或亲批代执）。
5. **formaflow 线本体**：维持 dormant，不设值守、不入哨兵矩阵、不占配额。

## 四、候 root（本线相关）
- qfa-ack cipher 三裁（FINDING-20260828-13）：(a) 授权取用道 (b) X25519 重封【荐】 (c) CMD 轮换统一样式。
- relay-keymig-prepare.yml 之 AI_FULL_PAT 遗物引用：裁删或改写。
