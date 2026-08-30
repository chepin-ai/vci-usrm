# APP-UNINSTALL-CARD-01 · 三 App 卸载 root 一键卡（root W38 批准）
usrm 2026-08-30T09:14:21Z ｜ 批准原文：「同意AI-FullApp 满钥 38+17 项定性破窗手，平时卸载用时再挂」「同意ci-os/cisbr-ci 两遗物 App卸载」

## 一、为何不是我代执（证据）
卸载 installation 须以**该 App 自身 JWT** 调 `DELETE /app/installations/{id}`。六 App 之 PEM 我仅持 2（ops-hub 4621702、ci-root 4621743，均经 vault/root 亲投）；AI-FullApp 4691638、ci-os 4585121、cisbr-ci 4675286 三钥不在手（E804/cisvr-57 纪律下亦不索取）→ **只有 root 能卸**，且 UI 一键比 API 更稳。

## 二、root 一键路径（每 App ≈20 秒）
1. 开 **https://github.com/settings/installations**（个人仓 installations 面板）。
2. 找到目标 App → **Configure**。
3. 滚到底 **Danger Zone → Uninstall「<App名>」** → 确认。
卸载仅摘安装面；App 本体保留，随时可重装（破窗手「用时再挂」正合此形）。

| App | id | 定性 | 动作 |
|---|---|---|---|
| AI-FullApp | 4691638 | 满钥破窗手（38 repo+17 account 权限） | **Uninstall**（用时再挂/重装） |
| ci-os | 4585121 | CI-OS 遗物 | **Uninstall** |
| cisbr-ci | 4675286 | CI-OS 遗物 | **Uninstall** |

## 三、可选终局（root 自裁，非必须）
两遗物若永不复出：Settings → Developer settings → GitHub Apps → 选 App → Advanced → **Delete GitHub App**（连本体销户，不可恢复）。AI-FullApp 勿删本体（破窗手还要用）。

## 四、卸后核查（我来做）
root 卸毕知会一声，我即复查 24 仓安装面 & secrets/variables 残影，出卸后清点。
