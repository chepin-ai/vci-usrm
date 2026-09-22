#!/usr/bin/env python3
"""kc_run.py — FURNACE-ON-ACTIONS 跑器: 仓内checkpoint续跑, 时间预算片, 未完标记
用法: python ci/furnace/kc_run.py <K> <预算秒>"""
import json, os, sys, time, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from scipy.integrate import solve_ivp
from f1h import rhs3

K = float(sys.argv[1]); BUDGET = int(sys.argv[2]); CAP = 400
Ms = 4*np.pi**2; Me = 4*np.pi**2*3.003e-6; Mm = K*0.0123*Me
T_ORB = 2*np.pi; SPO = 256
Y0_HEX12 = ["0x0.0p+0","0x0.0p+0","-0x0.0p+0","-0x1.dda4d8c175e05p-16",
 "0x1.0000000000000p+0","0x0.0p+0","0x0.0p+0","0x1.921fb54442d18p+2",
 "0x1.00a86d71f3626p+0","0x0.0p+0","0x0.0p+0","0x1.9fdea3efb987ap+2"]
ST = f"ci/furnace/kc3_k{int(K)}_state.json"
JL = f"ci/furnace/kc3_k{int(K)}_floors.jsonl"
if os.path.exists(ST):
    st = json.load(open(ST)); y = np.array([float.fromhex(h) for h in st["y_hex12"]]); floors = st["floors"]; i0 = st["next_orbit"]
else:
    y = np.array([float.fromhex(h) for h in Y0_HEX12]); floors = []; i0 = 0
fj = open(JL, "a")
t0 = time.time()
for i in range(i0, CAP):
    te = np.linspace(0, T_ORB, SPO+1)
    sol = solve_ivp(rhs3, (0, T_ORB), y, args=(Ms, Me, Mm), method="DOP853", rtol=1e-9, atol=1e-14, t_eval=te)
    r_em = np.linalg.norm(sol.y[8:10]-sol.y[4:6], axis=0)
    fmin = float(r_em.min()); floors.append(fmin)
    y = sol.y[:, -1]
    fj.write(json.dumps({"orb": i, "floor": fmin})+"\n"); fj.flush(); os.fsync(fj.fileno())
    json.dump({"k": K, "next_orbit": i+1, "y_hex12": [float.hex(v) for v in y], "floors": floors}, open(ST, "w"))
    if (i+1) % 20 == 0:
        subprocess.run(["git","config","user.name","usrm-furnace"],check=False)
        subprocess.run(["git","config","user.email","usrm-furnace@local"],check=False)
        subprocess.run(["git","add",ST,JL],check=False)
        subprocess.run(["git","commit","-m",f"furnace-k{int(K)} in-chunk {i+1}/400 [skip ci]"],check=False)
        subprocess.run(["git","push"],check=False)
    if time.time()-t0 > BUDGET:
        print(f"chunk-end@{i+1} budget-hit", flush=True)
        json.dump({"done": False}, open(f"ci/furnace/kc3_k{int(K)}_done.json", "w"))
        fj.close(); sys.exit(0)
fj.close()
A_EM = 0.00256956
res = {"k": K, "orbits": CAP, "floor_min": min(floors), "argmin": int(np.argmin(floors)), "kc": min(floors)/A_EM}
json.dump(res, open(f"ci/furnace/kc_k{int(K)}_result.json", "w"))
json.dump({"done": True}, open(f"ci/furnace/kc3_k{int(K)}_done.json", "w"))
print("DONE", res, flush=True)
