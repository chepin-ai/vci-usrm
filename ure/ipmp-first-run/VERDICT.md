# VERDICT — QFK v0.2 ipmp 首真件试跑（usrm-claim-01）

## 判词

**ACCEPT**（judge_verdict 原判 ACCEPT，residual_score=0.00040778252120719636）

判词固定串：**MIP无星结构同构不升格**。

> MIP（无星）+绑定承诺互锚+信标挑战 的结构同构工程构造，非字面 MIP*；MIP 无星结构同构不升格。

熵档免责声明（A5 固定串，随 m6 入链）：

> classical-sim 档活在复杂度假设内：熵源未经物理认证，仅作公开可复现挑战；certified 档亦仅声称源组成如实，不升格为 DI 级认证。

## 命题与证据

- **CLAIM-01**：「usrm 叙事链 seq170→180 段链哈希可复算，且 tip=229f9e1c953b」
- 复算方法：canon=json.dumps(entry 去 hash/hmac, ensure_ascii=False, sort_keys=True)；
  hash=sha256(prev.hash+canon)[:12]；prev 用前一条 stored hash，链式递进至 tip。
- **正向复算（P1）**：seq170..180 共 11 条逐条 match=true；复算终点
  tip=`229f9e1c953b` == 声称 `229f9e1c953b` → **True**。
- **反向倒推（P2）**：自 tip 逐条校验 prev 关系 seq180..170 全部通过
  （reverse_all_prev_ok=True），
  与正向路径独立、殊途同归。
- 自检门（钉死）：tip 复算≠229f9e1c953b 即如实 REJECT——本场复算相等，门通过。

## 六相位留证（全事件见 transcript.json）

| 相位 | 要点 | 哈希/序号 |
|---|---|---|
| COMMIT(m1) | 承诺先于挑战，claim_hash 入链 | chain_seq=0 |
| CHALLENGE(m2) | 种子=qrand@seq61（cisvr-68 定格取口） | qrand=c21b1f0f5858ab4a… |
| WINDOW | 双 commit 绑定窗口，skew=0.000s | window_seq=61 |
| RESPOND | 双 reveal 绑定核验通过 | r1≠r2（True） |
| JUDGE(m5) | 三规则纯函数裁定 | verdict.digest=e84d295a45e22412… |
| SETTLE(m6) | 3-of-5 共签落账，tag=qfk:ipmp:verdict: | chain_head=ac86e057be44918e… |

## 熵档与种子来源

- 挑战种子来源：cisvr-68 定格取口 `wave3/ctx-beacon-mirror.json` 的 qrand@seq61。
- 熵侧：真随机侧 **ext_ok=[drand, nist, anu] 3/3 在线，非 sim 档**；
  协议熵档快照 `entropy_grade=certified`（无 OfflineSource 在列）。
- 镜 tick 自洽性预检（hash==sha256(seq‖prev‖qrand)）：False。
- 如实标注：本试跑为**定格回放**——熵在承诺之后不再新鲜，但种子定格于承诺之前
  且公开可复现，满足「承诺先于挑战」次序；新鲜熵在线挑战为后续档。

## 串谋探针（M-probe，默认检测器）

- 结果：**未命中（None）**。
- 纪律照录：命中=违规证据，未命中≠清白（审计启发式，完备性未闭合）。
- 结构性排除：P2 输入仅 (entries, qrand, 声称 tip)，代码路径独立反向倒推，
  无 r2=f(r1) 串谋结构（T-06 负例为鉴）；r1/r2 绑定摘要见 transcript WINDOW 段。

## 诚实灰标

- **本试跑=单沙箱内模拟三机角色**（ip/np/n-machine 为同进程内角色实例，
  Ed25519 签者圈每次运行新随生成）；**物理分离多 prover 为后续档**。
- 无通信窗口时序强制=纪律级（本地时钟可伪造，仅靠 m6 入链 seq 序事后佐证）；
  M1 绑定=密码学级；联合强度=「纪律级主体+密码学级绑定件」。
- gap=0.001 为显式人读声明（A3：无 gap 永不 ACCEPT），非已证定理；
  soundness 只覆盖 A 档 1–6 诚实上界，B 档 7–9 不触及。
- 灰区#10（NP 双帽）未闭合：本场裁定集经 judge_set_for 轮换剔除 proposer 密钥
  （proposer_key_excluded=True），
  且计票签名不含 NP 机成员。
- 链连续性：m1/m2/m6 同链 domain=mutual-proof，chain.verify()=
  True；事件链哈希自 genesis 连续。
