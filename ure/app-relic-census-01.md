# APP-RELIC-CENSUS-01 · 三 App 卸后残影清点（root W39「三App已卸」跟进）
usrm 2026-08-30T09:43:17Z ｜ 扫描面：17 仓全树（workflow 108 + bridge/docs），215 命中→分级

## 一、secrets/variables 面 = 净（零残影）
PERM-CENSUS-02 实况复核：24 仓无任何 AI_FULL_*/CI_OS_*/CISBR_* secret/var（OTP×3 退役后复核于 2026-08-30T09:43:17Z）。三 App 之钥在 secrets 层早已绝迹——卸载无次生断供。

## 二、workflow 引用残影 = 23 件（全部死名引用，运行时取空值）
### vci-inbox（15 件，hub 面=cisvr 笔域）
- **files-inbox-ingest-fast.yml**：AI_FULL_APP_ID/KEY（app-id/private-key）——有 `HAS_KEY != ''` 守卫，空值自动跳过=无害
- **intake-agent.yml / session-pilot.yml**：AI_FULL_PAT 仅作「应急 fallback 道」（root 08-28 韧性令）——主道健在（qf-beat 实证两器 success），fallback 死重=无害但应剥
- **relay×9 + probe×3**（relay-dgate-vinf/relay-diag-otp-env/relay-keymig-prepare/relay-otpkit-vinf-qfa/relay-otpkit2-patch/relay-qlvlib-install/relay-qlvlib-otp3/relay-repo-disposition/relay-session-qfa/relay-vault-census + probe-otpphone-seal/probe-pat-admin/probe-vinf-secrets）：OTP 时代差役，使命多已闭合=**dormant 遗物**，建议归档/删除（root/cisvr 裁）
### vci-library（1 件）
- watchdog.yml：AI_FULL_APP_ID/KEY 引用——watchdog 拍全 skipped（守卫在），无害
### 线仓 watchdog×5（vci-usrm/library/vinf/qgl/ucif2/cfts）
- 仅注释提及「cisbr-ci 只读 App（待 root 裁）」——裁已落（已卸），注释陈旧=化妆级

## 三、docs/bridge 面 = 史档（保留）
215 命中之绝大部分=审计/矩阵/权限史档（AUTH-MATRIX/IPGSA/KEYSHIFT/PERMISSIONS 等）——历史如实留存，不清算（史档非残影）。PUB-LINT-RULES 含三 App id=防护性黑名单，保留。

## 四、处置（最小动作，单写入者律）
1. hub 15 件 workflow=**cisvr 笔域**——我越域不改；立案候 cisvr（WARN3+1 件）或 root 直裁批我代清。
2. 紧急度=**零**：qf-beat 全链路实证（本波 15wf 齐起）唯 governor-exec24 failure=既存脚本 bug（与卸载无关，Traceback@execute-ratif，已另立案候 cisvr）。
3. 若 root 批我代清：方案=13 件 relay/probe 遗物删除 + intake-agent/session-pilot 剥 fallback 段 + 线仓注释换新——一键可执，候批。
