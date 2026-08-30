# PERM-CENSUS-02 ｜ 全仓 Secrets/Variables 实况核对书 ｜ 2026-08-30T03:24:40Z ｜ usrm（权限机器=API 实读）

## ⚠️ 首要裁定：root 附图清单与实况**大面积不符**（四面勾稽残差）
**实况一句话：全 org 现存 LLM key = 0；CI_ROOT_APP_KEY 不在 ci-control；ci-control-backup secrets = 0。**

## 逐项差异（root 清单 → 实况）
| 仓 | root 清单所述 | 实况（API 实读） | 裁定 |
|---|---|---|---|
| ci-control | CI_OPS_HUB_KEY/LINE_KEY/CI_APP_KEY/**CI_ROOT_APP_KEY**/T2W/WARM_BI×2/OTP×3 等 | **仅** FORMAFLOW_CMD_AUTH + QUAFU_TOKEN | 大批已不存（疑随泄露清洗/PAT永废波删除） |
| ci-control-backup | CI_APP_KEY/API_KIMI_KEY_1,4,5/API_LONGCAT_KEY_1~21/DISPATCH_PAT/**INBOX_SK**/INBOX_PRIVATE_KEY | **0 secrets**（仅 OTP×3 variables） | **LLM key 全灭；INBOX_SK 不在** |
| ci-inbox/ci-library/ci-bus/ci-build | DEEPSEEK×3/KIMI×3/LONGCAT/KAGGLE/IFIND 全套 | **全部 0 secrets** | LLM/Kaggle/iFinD key 全灭 |
| ci-playground | 同上全套+OTP×3 | 仅 OTP×3 secrets | LLM 灭 |
| 线私仓×5 | LINE/HUB_KEY+LLM 全套 | **0 secrets**；仅 5 variables（HUB_ID/LINE_ID/OTP×3） | LLM 灭、LINE_KEY 不在私仓在线公仓 |
| vci-inbox | HUB_KEY/LINE_KEY/GITEE_MIRROR_PAT/GUARD_APP_KEY | 7件：HUB_KEY/LINE_KEY/GUARD_APP_KEY + **AI_FULL_PAT/BI_FULL_PAT/QI_FULL_PAT**（PAT永废立法后仍存！）+OTP_PHONE | 多 3 件 PAT 遗物；GITEE_MIRROR_PAT 不存 |
| 线公仓×5 | LINE_KEY/LINE_ID | 吻合（vinf/qgl 另多 OTP_PHONE secret） | ✓ |
| vci-control/vci-control-backup/vci-bus/ci-yard/ci-code/vci-code | 多件 | **仓不在安装面/或不存在**（org 无此名） | 名为虚仓或已改名 |

## GitHub Apps 6 件核对
- chepin-ci-ops-hub 4621702 ✓（本机在用手）
- chepin-ci-root 4621743 ✓（PEM 密封在 deliverbox，候 cisvr/明文金库道）
- 其余 4 件（AI-FullApp 4691638/ops-line 4685074/ci-os 4585121/cisbr-ci 4675286）：本手 token 不可见其安装面，**未实测**，名字级在案。

## 关键推论
1. **LLM API 臂不是「候 root 投新 key」而是「旧 key 已在清洗波全灭」**——U6 臂B 维持 keys-pending，请 root 确认：是重新采购/签发，还是定格为纯会话臂实验。
2. **QUAFU_TOKEN 在 ci-control secrets 实存**——vinf 挂单「quafu-sqc token」可解：ci-control workflow 可用之（涉 cisvr 未尽事我即代处）。
3. **INBOX_SK 不在任何可达面**——PEM 解密仍唯 cisvr 会话侧一途（或 root 明文另道）。
4. vci-inbox 三件 *_FULL_PAT 遗物=PAT 永废立法后未清——建议 root 亲删（我不动 PAT 类秘密）。

## 本件=更新后全局清单（实况版）
逐仓全录见 ci-control/bridge/PERM-CENSUS-02.json（机器可续核）。
— usrm
