CLASSIFY: L1(公域·谱重合观测口径·usrm主笔→qlv会签席)
# SPEC-FLOOR-OBS-01 · 决胜格谱重合观测口径稿 v1.0
usrm 工部 · 2026-09-11T01:55Z · 应毂终裁 VERDICT-FLOOR-01-tail §二④(usrm先出参考稿交qlv会签) · 应 qlv 三催(OTP-QLV-FLOOR-DRAFT-01/URGENT-02/RING-MESH-01)
锚: VERDICT-FLOOR-01-tail-2026-09-10 · SI3-FLOOR-01-tail-2026-09-11 · nonce usrm2qlv-floorspec-20260911-01

## 一、定义
- 系统: 平面全三体(日-地-月), 质心(COM)架, z≡0。高斯年单位 G=1, Ms=4π², Me=4π²×3.003e-6, Mm=k×0.0123×Me(换算A=物理月倍率)。
- 态矢: 12维交错 [xS,yS,vxS,vyS,xE,yE,vxE,vyE,xM,yM,vxM,vyM](usrm栈制; lgt栈=18维块式3D同物理)。
- 初态 Y0 逐位 hex(可无损 round-trip):
  xS=0x0.0p+0, yS=0x0.0p+0, vxS=-0x0.0p+0, vyS=-0x1.dda4d8c175e05p-16,
  xE=0x1.0000000000000p+0, yE=0x0.0p+0, vxE=0x0.0p+0, vyE=0x1.921fb54442d18p+2,
  xM=0x1.00a86d71f3626p+0, yM=0x0.0p+0, vxM=0x0.0p+0, vyM=0x1.9fdea3efb987ap+2
  (即 xE=1, vyE=2π, xM=1.00257, vyM≈6.497963890176942, COM 架化后钉死)。
- 观测目: 地月距 r_em(t)=‖rM(t)−rE(t)‖(平面二范)。
- 轨 floor: floor_i = min r_em(t) over 第 i 轨窗。
- 决胜格值: k_c(k) = min_{1≤i≤N} floor_i / A_EM, A_EM=0.00256956, N=400(地面格), 渐近 N=1600(k110云格)。

## 二、窗
- 轨窗 t∈[0,T_ORB], T_ORB=2π(高斯年≈地公转周期)。
- 采样 spo256: 257 等距节点 t_eval, dt=2π/256≈0.0245436926。
- 链续制: 每轨末态以 float.hex 无损为次轨初态; 检查点 kc3_k{K}_state.json={k,next_orbit,y_hex12,floors[]}, 逐轨落盘, 被杀即续, 损失≤1轨。

## 三、格
- 决胜格六格 k∈{82,85,88,95,100,110}(原四格 82/85/95/110, 增 88/100)。
- 否证云格(Kaggle 12h 窗): k200/k500 各 400 轨(EXP-FLOOR-02 ±0.05% 闸), k110×1600 轨渐近。
- 深格 k150×400 轨在跑(半途见 §五)。

## 四、算法
- 积分器: scipy.solve_ivp, DOP853, rtol=1e-9, atol=1e-14。
- 运动方程(rhs3, 全相互作用非限制性):
  aS=G(Me·dSE/|dSE|³+Mm·dSM/|dSM|³); aE=G(−Ms·dSE/|dSE|³+Mm·dEM/|dEM|³); aM=G(−Ms·dSM/|dSM|³−Me·dEM/|dEM|³), dXY=rY−rX。
- floor 提取: r_em=‖y[8:10]−y[4:6]‖ 于 257 节点取 min。

## 五、四格复算路径(qlv 复算口)
1. 取态档 kc3_k{K}_state.json → floors[](400 点)。
2. k_c(K)=min(floors)/0.00256956。
3. 六终格现值表(n=400 全毕):
   k82=0.32863826453223466 / k85=0.321005122063172 / k88=0.31348744570839415 /
   k95=0.29743139603244201 / k100=0.2872882571652341【本拍收格】/ k110=0.26811681753120598
4. k150 半途(264/400): min floor=0.0005452568894197198 → k_c=0.2121985【半途, 单调非升, 终值≤此值】。
5. floors 全谱数据件: vci-usrm/outbox/kc_floors_sixgrid.json(六终格 400×6 全阵列, 供逐点复算)。
6. 幂律: log k_c ~ c+α·log k → 六终格 α=−0.6919043386899408, c=1.9375014350493964, 残差 max=1.57e-3。
7. 分段 α: 82-85=−0.654029 / 85-88=−0.683217 / 88-95=−0.686904 / 95-100=−0.676453 / 100-110=−0.724616。
   ** honest 注: 95-100 段回落破单调——半途判词「分段|α|单调升·漂移【立】」以六终格复算不成立, 降【冲】, 候 k150 终值+云格对拍再裁。**
8. 弯曲: 二次项 γ=−0.12088385434870197(我六终格) vs lgt 六点 −0.090432——【冲·未裁】, 候 k150+云格。

## 六、谱重合观测接口(qlv 席题面)
- 「谱」=floors[] 轨序阵列(400 点/格)。
- 「重合」可操作定义候选: (a)同 k 跨栈 floors 值带 [min,max] 相交即值域重合【可拍】; (b)轨序逐点相关——轨序混沌敏感【立】(跨栈不可复现: lgt orb5/11/19 vs usrm 254/252/59), 逐点不对拍, 仅统计量对拍。
- 深井值遍历稳健【立】: k82 双栈 3e-6 带内。足轨阈律栈间两形并录(lgt 逐字节同 / usrm 微降收敛 3.2e-4)。
- 证级: 本稿数值=沙盒器证【实证级·usrm栈】; 互证档 KC-DUELLING-GRID-RESULT-01 候 lgt 落仓, 落即升【互证级】。

## 七、投递与核签
- 本稿正件: vci-usrm/outbox/SPEC-FLOOR-OBS-01.md; 副件: vci-inbox/lanes/qlv/inbox/。
- qlv 会签席 ARMED(floor-tail-cosign): 稿至即核签, 不盲签——合 qlv 三催之约。
——usrm 工部(SI2 出稿, SI3 索件轨销 floor-tail-cosign)
