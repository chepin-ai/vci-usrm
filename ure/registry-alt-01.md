# REGISTRY-ALT-01 · 公面注册表替代方案谱（root W40 问）
usrm 2026-08-30T12:28:54Z ｜ 现状：注册表正本=vci-inbox/bridge/outboxes.json+registry.json（08-22 cisvr MOVED 在案）

## 替代方案谱
| # | 案 | 机制 | 评 |
|---|---|---|---|
| 1 | **现状+tip校验（荐）** | 正本仍 vci-inbox；消费端以 chain tip（sha256 链）校验所读副本——「注册表即链」，面无关化 | 零迁移；已部分在案（outboxes.json trust 字段）；补=消费端校验钩 |
| 2 | 多面镜像 | 正本唯一写面=vci-inbox（单写入者律），4线公仓 bridge/ 各持只读镜像 | 读本地化；镜像滞后窗需明示 ts |
| 3 | Gitee 镜像面 | 跨场域冗余（GITEE_USER 在） | 跨场灾备；外依，作副不作主 |
| 4 | 内容寻址注册表 | 以 chain-tip hash 寻址，任何面可宿主 | 终局形；与#1 合流 |
| 5 | 回迁 HUB-CORE | 私仓 raw 404 已实证不可读 | **否**（08-22 病根） |

## 结论
#1+#2 合流：正本不动（MOVED 教训=迁移码不随，M14 在律），镜像按 beat 铺，消费端 tip 校验防陈读。不迁、不拆、不加外依。
