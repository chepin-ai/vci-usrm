#!/usr/bin/env python3
"""F1-HARNESS-01 — EXP-FLOOR-01 F1 预测(floor/a_em=C·k^-1/2, C≈π±5%)独立验证闸 v1
线: usrm ｜ 依据: lgt-77 §四指定验证线; IC 交换纪律: float.hex() 逐字节(lgt 修法①, TH-RHYTHM)
功能: 日地月型三体(共面) DOP853 rtol=1e-9 atol=1e-14 千轨积分 → 逐轨近心 r_em 序列 → floor=min
     → 跨 k∈{20,40,80} 拟合 floor/a_em=C·k^α, 测 α 与 C, 判 F1 (α=-1/2∧|C-π|/π≤15% 则 F1 存)
IC 口径【候归档】: COM 架, 共面 i0=0, a_em 全精度, 地球圆轨 v=2π(日心)/COM 修正, 月相对速 v_M 全精度。
lgt 谱扫档 research/exp-floor-01-lgt-scan.json 渡至即以 float.hex IC 重跑互证; 此前一切输出标【第三实现·非互证】。
"""
import numpy as np
from scipy.integrate import solve_ivp

G = 1.0
def make_rhs(Ms, Me, Mm):
    def rhs(t, y):
        # y = [rE(2), vE(2), rM(2), vM(2)]  COM 架; 太阳在原点位质量 Ms? 否——太阳亦动。
        # 严格三体: rS=-(Me rE + Mm rM)/Ms 由 COM 条件内蕴, 用三体全方程更稳:
        raise NotImplementedError
    return rhs

def rhs3(t, y, Ms, Me, Mm):
    rS, vS, rE, vE, rM, vM = y[0:2], y[2:4], y[4:6], y[6:8], y[8:10], y[10:12]
    dSE = rE - rS; dSM = rM - rS; dEM = rM - rE
    aS = G*(Me*dSE/np.linalg.norm(dSE)**3 + Mm*dSM/np.linalg.norm(dSM)**3)
    aE = G*(-Ms*dSE/np.linalg.norm(dSE)**3 + Mm*dEM/np.linalg.norm(dEM)**3)
    aM = G*(-Ms*dSM/np.linalg.norm(dSM)**3 - Me*dEM/np.linalg.norm(dEM)**3)
    return np.concatenate([vS, aS, vE, aE, vM, aM])

def run(Ms, Me, k, a_em, n_orb=1000, samples_per_orb=256, y0_hex=None, conv="A"):
    """k=月质量参数; conv A: Mm=k×0.0123×Me(物理月倍率) / B: Mm=k×Me. y0_hex=float.hex IC 钉死."""
    Mm = k*0.0123*Me if conv=="A" else k*Me
    Ms = 4*np.pi**2  # 高斯年单位: GM_sun=4π² (lgt v_E=2π@a=1 钉死)
    if y0_hex is not None:
        y0 = np.array([float.fromhex(h) for h in y0_hex])
        T_orb = 2*np.pi
    else:
        vE = 2*np.pi  # 日心圆速
        vM_rel = np.sqrt(G*Me/a_em)  # 试验月轨道 IC(lgt 口径, 已逐位核验 0.21479697); Mm 不入 IC
        rE = np.array([1.0, 0.0]); vE_ = np.array([0.0, vE])
        rM = rE + np.array([a_em, 0.0]); vM = vE_ + np.array([0.0, vM_rel])
        # COM 架化
        Mtot = Ms + Me + Mm
        rCOM = (Me*rE + Mm*rM)/Mtot; vCOM = (Me*vE_ + Mm*vM)/Mtot
        rS0 = -rCOM; vS0 = -vCOM
        y0 = np.concatenate([rS0, vS0, rE-rCOM, vE_-vCOM, rM-rCOM, vM-vCOM])
        T_orb = 2*np.pi
    T = n_orb * T_orb
    t_eval = np.linspace(0, T, n_orb*samples_per_orb+1)
    sol = solve_ivp(rhs3, (0, T), y0, args=(Ms, Me, Mm), method="DOP853",
                    rtol=1e-9, atol=1e-14, t_eval=t_eval)
    r_em = np.linalg.norm(sol.y[8:10] - sol.y[4:6], axis=0)
    # 逐轨极小
    floors = [r_em[i*samples_per_orb:(i+1)*samples_per_orb+1].min() for i in range(n_orb)]
    return {"floor": float(min(floors)), "floor_over_a": float(min(floors)/a_em),
            "per_orbit_min": floors, "nfev": sol.nfev, "success": bool(sol.success)}

def f1_verdict(results):  # results: {k: floor_over_a}
    ks = np.array(sorted(results)); ys = np.array([results[k] for k in ks])
    A, B = np.polyfit(np.log(ks), np.log(ys), 1)  # ln y = A ln k + B
    alpha, C = A, np.exp(B)
    verdict = abs(alpha + 0.5) < 0.1 and abs(C - np.pi)/np.pi <= 0.15
    return {"alpha": float(alpha), "C": float(C), "F1_survives": bool(verdict)}

if __name__ == "__main__":
    import json, sys
    k = float(sys.argv[1]); conv = sys.argv[2] if len(sys.argv)>2 else "A"
    n_orb = int(sys.argv[3]) if len(sys.argv)>3 else 1000
    Ms = 4*np.pi**2; Me = 4*np.pi**2*3.003e-6
    r = run(Ms, Me, k, 0.00256956, n_orb=n_orb, samples_per_orb=256, conv=conv)
    out = {"k": k, "conv": conv, "n_orb": n_orb, "floor_over_a": r["floor_over_a"],
           "floor": r["floor"], "nfev": r["nfev"], "success": r["success"]}
    print(json.dumps(out))
