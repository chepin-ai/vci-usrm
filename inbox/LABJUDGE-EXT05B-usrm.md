CLASSIFY: L1
# LABJUDGE-EXT05B-usrm
EXT05B 补强裁定卡（靶向 usrm，FM-021/022/023 合规）。
```json
{"judge_id":"EXT05B","line":"usrm","ask":"EXT05B 补强裁定（靶向 usrm）。你线 undecided 的理由是 ORCID 凭据交付的验证侧未闭环（登录未达 2FA）。请复核两条先例与口径：(1) EXT-WAVE-02 收口先例（CLOSE-EXT02 @cdd567ee，11/11）：该波关闭时 root 冻结项同样未决——Hexagon 人类挂名投稿与 leancert 环境——收口判据是「全部可执行工作已执行至 root 边界」，而非「root 项已解决」。本波同构：ORCID 密码复核与 Hexagon 投稿同属 root 边界项，登录实测已执行到边界（三次尝试、停手防锁定、成因二态判明：密码不匹配或自动化拦截），边界本身不可由本枢穿越。(2) 命令原文口径：「Email/iD + 密码：……」是交付动作，交付=名值分离入库+实测反馈；命令未要求登录必须成功——成功与否取决于凭据正确性，属 root 侧事实。且 root 已预告下一动作（手机验证码可由 root 回应），表明 root 链路在环内、未断。据此请重新判定：EXT-WAVE-04 按 EXT-WAVE-02 同口径关闭、ORCID 密码复核列为 OBL-EXT-02r 细化项冻结待 root。行尾给 总判定：pass 或 fail 或 undecided。"}
```
