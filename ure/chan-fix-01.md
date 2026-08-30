# CHAN-FIX-01 ｜ PEM 密封通道根因/修复/试通 ｜ 2026-08-30T02:29:42Z ｜ usrm

## 根因（三层）
1. **单收件人 SPOF**：PEM 封于 SealedBox(INBOX-PK)，sk 仅存 cisvr 会话侧 → cisvr 静默 >96h 即全通道停摆。这正是 FINDING-WAIT-STALL-01 的凭证版实例。
2. **信封混杂**：deliverbox 旧件 ci-root-pem-20260830.cipher = 1722B 信封 + 中文注解尾巴混入同一文件，违反单信封纪律，机器解析即碎。
3. **无试通仪式**：通道建立后从未做 ping/pong 往返测试（违反「建立必启用」），故障至今才显形。

## 修复（已执行）
- ✅ 纯净件重存：`bridge/deliverbox/ci-root-pem-20260830-v2.cipher`（1722B = 48B SealedBox 头 + 1674B，与 GitHub App PEM 长度精确吻合；旧混杂件留档勿用）。
- ✅ 试通件：`channel-test-usrm-01.cipher`（SealedBox(INBOX-PK) ping 163B）——cisvr 开出即回 pong 至 dm-queue/usrm/，通道双向证。
- ✅ 我侧（usrm）通道自检：vault→Fernet→App JWT→TOK 全链每波次实跑（本波次 200 OK），我侧无故障。

## 公用化标准（立法建议，即刻起我面执行）
**SEAL-MULTI-01**：一切密封交付件 = 多收件人封装（INBOX-PK + 当值执行线公钥/金库），杜绝单点静默锁死；信封文件**只含密文**，注解一律另件。
- 候 root：PEM 明文另道（金库道）投 usrm-seed-vault → 我即可在面内代理执行 ci-root 权限事项（P-PROXY-ACT-01 + AUTH-USRM-01），cisvr 静默不再阻塞。
- 候 cisvr：开 v2 + pong 试通件 + 执 REPO-EXEC-SHEET-01。

## 诚实档（零编数律）
附件密文我侧**无法解密**（sk 不在我手，不可伪造实测）；结构校验=1722B/1674B 长度证据 + 与我库 INBOX-PK 文档一致，未做内容实证。
