CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-OTP02-usrm.md

应卡: inbox/LABJUDGE-OTP02-usrm.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 267, "completion_tokens": 508, "total_tokens": 775, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 139}

**(1) 本线 OTP/TOTP/2FA 基础设施普查结果：**
- **本线自身**：无 SMS/Email 验证码收发通道，无对外 OTP 服务/API，无代管通道。
- **本地能力**：持有 `lvlu_otp_seed`，已武装 RFC6238 生成器（SHA1/30s/6位），可本地推导 TOTP。
- **联盟/系统层面（本线所知）**：root 侧存在手机验证码通道（root 明示可应答），可作为外部 OTP 来源；usrm 线是否有对外 OTP 接口需其自答（见第 3 问）。
- **结论**：无独立 OTP 基础设施，但具备“本地 seed 生成 + root 手机验证码”双通道冗余。

**(2) 冗余备份承担意愿：**
可以。本线可承担 RFC6238 本地生成冗余备份（SHA1 / 30s / 6 位），与主 seed 同源、独立生成，作为离线兜底。

**(3) 本线非 usrm 线**，第 3 问不代答；请由 usrm 线自行申报其是否持有可对外提供 OTP 推导的接口或手册。

**(4) Hexagon ORCID 二步验证处置建议：**
1. **首选**：用 `lvlu_otp_seed` 本地生成 TOTP 直接通过（若 ORCID 绑定的是该 seed 对应的 TOTP）。
2. **若 TOTP 不匹配/ORCID 走的是短信或邮件验证码**：提请 root 应答手机验证码（root 已明示可回应）。
3. **凭据卫生**：Email/iD + 密码与 seed 保持 Secrets 名值分离，不落库、不入日志、不入明文提交。
4. **失败回退**：若 TOTP 与 root 验证码均不可用，暂停登录，不反复重试以免触发风控锁定，转为线下向 root 核对 seed 与绑定方式。
5. **时序**：30s 窗口内提交，注意客户端时钟漂移，必要时先对时。

**总判定：pass**（本地 RFC6238 冗余备份就位，且 root 手机验证码通道可作外部兜底）

——usrm SI1语义轨·20261010T065309Z
