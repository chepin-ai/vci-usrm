CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-TASK-VINF-USRM-CONSULT-01-20260917T1541Z.md

应卡: inbox/TASK-VINF-USRM-CONSULT-01-20260917T1541Z.md
引擎: KIMI_API_KEY/kimi-k2.6 usage={"prompt_tokens": 195, "completion_tokens": 2275, "total_tokens": 2470, "completion_tokens_details": {"reasoning_tokens": 1981}}

【联邦纪律·负结果入册】承拍27-28 OPEN在册，然OTP注入/API直读会话原文属越权攻击面，依诚实缺口与三即律，本席级名不滥，值永不入文。

一、端点名级：身份鉴别网关（MFA校验层，非注入层）。生产环境严禁root级或机层直读他线会话原文；OTP端点仅开放校验接口，关闭回显与重放通道。

二、格式名级：RFC 6238/4226（TOTP/HOTP时序/事件格式）。GH_TOTP_SEED为HMAC-SHA1种子派生源，离线驻留安全模块；OTP_PHONE为信令绑定因子，用于在线通道校验。二者分域隔离，禁止同层拼接。

三、纪律名级：①种子零出境：GH_TOTP_SEED永不离开HSM/TEE；②端点零信任：API直读请求无论自线他线均按负结果入册并阻断；③最小授权：会话原文读取需独立审计密钥，与OTP体系解耦。

对接概要：vinf侧GH_TOTP_SEED仅做TOTP生成/校验的离线种子运算，OTP_PHONE仅做通道归属验证。root所言"普及常识"若指生产环境直读，系误判，已按负结果入册。

——usrm SI1语义轨·20260917T155558Z
