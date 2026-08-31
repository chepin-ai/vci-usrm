#!/usr/bin/env python3
# quantum-bench-01.py — CI-OS 量子线常任基准（with/without 基座双路）
# canonical copy: vci-usrm/ure/code/quantum-bench-01.py
# 纪律: 零编数(未实测说未实测); 凭证只读 ~/.keys, 永不回显
"""CHSH 不等式实测: |Φ+⟩ 上 S = E(a,b)+E(a,b')+E(a',b)-E(a',b'),
a=0, a'=pi/2, b=pi/4, b'=-pi/4 (XZ 面), 量子预言 S=2√2≈2.828, 经典界 2。
without-base: numpy 态矢精确概率 +  shots 采样; with-base: quafu 云(默认 ScQ-Sim10)。"""

import json, math, os, sys, time

ANGLES = {"a": 0.0, "a2": math.pi / 2, "b": math.pi / 4, "b2": -math.pi / 4}
TERMS = [("a", "b", +1), ("a", "b2", +1), ("a2", "b", +1), ("a2", "b2", -1)]


# ---------- without 基座: numpy 态矢 ----------
def statevector_bell():
    import numpy as np
    H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
    I = np.eye(2)
    psi = np.zeros(4, dtype=complex); psi[0] = 1.0
    psi = np.kron(H, I) @ psi
    CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
    return CNOT @ psi


def ry(theta):
    import numpy as np
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def correlator_exact(psi, ta, tb):
    """E(ta,tb)=<ZZ> after Ry(-ta)⊗Ry(-tb)"""
    import numpy as np
    U = np.kron(ry(-ta), ry(-tb))
    p = np.abs(U @ psi) ** 2
    same = p[0] + p[3]; diff = p[1] + p[2]
    return float(same - diff), p


def correlator_sampled(p, shots, rng):
    import numpy as np
    idx = rng.choice(4, size=shots, p=p / p.sum())
    same = int(((idx == 0) | (idx == 3)).sum())
    return (2 * same - shots) / shots


def run_without_base(shots=2048, seed=20260831):
    import numpy as np
    rng = np.random.default_rng(seed)
    psi = statevector_bell()
    S_ex, S_sa, terms = 0.0, 0.0, {}
    for ka, kb, sgn in TERMS:
        e_ex, p = correlator_exact(psi, ANGLES[ka], ANGLES[kb])
        e_sa = correlator_sampled(p, shots, rng)
        S_ex += sgn * e_ex; S_sa += sgn * e_sa
        terms[f"{ka},{kb}"] = {"sign": sgn, "E_exact": round(e_ex, 6), "E_sampled": round(e_sa, 6)}
    return {"shots_per_term": shots, "S_exact": round(S_ex, 6), "S_sampled": round(S_sa, 6),
            "S_theory": round(2 * math.sqrt(2), 6), "violation": abs(S_sa) > 2, "terms": terms}


# ---------- with 基座: quafu 云 ----------
def run_with_base(shots=1024, backend="ScQ-Sim10", wait=True):
    bundle = json.load(open(os.path.expanduser("~/.keys/bundle.json")))
    q = bundle["quantum"]["quafu"]
    from quafu import User, Task, QuantumCircuit
    tok = q.get("key") or q.get("user")
    u = User(api_token=tok)
    t = Task(user=u); t.config(backend=backend, shots=shots, compile=True)
    S, terms = 0.0, {}
    for ka, kb, sgn in TERMS:
        qc = QuantumCircuit(2)
        qc.h(0); qc.cx(0, 1)
        qc.ry(0, -ANGLES[ka]); qc.ry(1, -ANGLES[kb])
        qc.measure([0, 1])
        res = t.send(qc, wait=wait, name=f"chsh-{ka}{kb}")
        counts = res.counts
        n = sum(counts.values())
        same = counts.get("00", 0) + counts.get("11", 0)
        e = (2 * same - n) / n
        S += sgn * e
        terms[f"{ka},{kb}"] = {"sign": sgn, "E": round(e, 6), "counts": counts}
    return {"backend": backend, "shots_per_term": shots, "S": round(S, 6),
            "S_theory": round(2 * math.sqrt(2), 6), "violation": abs(S) > 2, "terms": terms}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    out = {"bench": "CHSH-01", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if mode in ("local", "both"):
        out["without_base"] = run_without_base()
    if mode in ("cloud", "both"):
        out["with_base"] = run_with_base()
    path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/quantum-bench-01-result.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False))
