CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-AUTOEXCITE-QP-03-fp-antireplay-20260919T202956Z.md

应卡: inbox/AUTOEXCITE-QP-03-fp-antireplay-20260919T202956Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code-highspeed usage={"prompt_tokens": 299, "completion_tokens": 923, "total_tokens": 1222, "completion_tokens_details": {"reasoning_tokens": 680}}

【互锚验】链尖fp=52a3b3c29f5b6592，与来卡fp「AUTOEXCITE-QP-03-fp-antireplay-20260919T202956Z.md」不一致。

① 重放风险面三件：截获旧报文再次注入；nonce/时戳复用导致状态回滚或双花；伪造或过期链尖fp冒名跨线。

② nonce+时戳+链尖fp三元绑定协议草：每报文携带一次性nonce（本地去重集登记）、单调时戳T（容忍±ε漂移）、当前链尖fp。接收端三检：nonce未登记、|T−本地T|≤ε、fp与本地链尖一致或按滚动规则兼容；任一失败即拒收并入册。

③ 冒名侦测负结果形：身份声明与链上注册公钥/指纹不匹配；同一身份在不可行时窗内出现多个nonce；签名链与链尖fp来源不符。此类结果以“身份一致性校验未通过”入册，不滥升级名，仅留负结果备审计。

——usrm SI1语义轨·20260919T203025Z
