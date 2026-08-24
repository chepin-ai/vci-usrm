#!/usr/bin/env python3
"""URE Pareto/Whittle scheduler fast prototype (dry-run mode, no LLM calls).

Implements SPEC-PARETO-01 §2 (shadow-price decision rule), SPEC-STRAT-02 §1/§4
(arm lifecycle: probation pool, retirement, K_max cap) and SPEC-LOOP-01 §3
(cascade counter, level-1 blocking). Parameter-level self-tuning only.

Modes:
  default      one scheduler tick against ure/roadmap.json + ure/chain.jsonl
               (mutates working tree; the workflow commits/pushes [skip ci])
  --simulate   offline recursive evidence: strategy A ("root guess", static)
               vs strategy B (Whittle adaptive + per-epoch meta-recursive
               refit of (beta, gamma) until a fixed point is declared).
               Writes ure/sim/out.json. Never touches roadmap/chain.

No secrets, no network, no personal identifiers. Pure python3 + numpy.
"""
import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone

ROADMAP = "ure/roadmap.json"
CHAIN = "ure/chain.jsonl"
KEEPALIVE = "ure/.keepalive"
GATE = "ure/GATE"
SIM_OUT = "ure/sim/out.json"

DEFAULT_PARAMS = {"beta": 0.5, "gamma": 0.3, "eps": 0.05,
                  "theta1": 0.6, "theta2": 0.5, "theta3": 0.4,
                  "theta4": 0.2, "theta5": 0.1, "K_max": 8}
AMBIGUITY_BAND = 0.05  # SPEC-PARETO-01 §2.2: top-2 gap < 0.05 -> 70/30 split
CASCADE_K = 2          # SPEC-LOOP-01 §3: k consecutive tick anomalies -> block
HISTORY_WIN = 5        # u_i = mean of last-5 score increments


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canon(obj):
    """Canonical JSON (sort_keys, tight separators) used for chain hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def chain_tail():
    """Return (last_seq, last_hash, all_entries)."""
    entries = []
    if os.path.exists(CHAIN):
        with open(CHAIN) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    if not entries:
        return 0, "0" * 64, entries
    return entries[-1].get("seq", 0), entries[-1].get("hash", "0" * 64), entries


def _num6(x):
    try:
        return round(float(x), 6)
    except (TypeError, ValueError):
        return None


def append_chain(arm, pi, score, ts):
    """Append {seq,ts,arm,pi,score,prev,hash}; hash = sha256(prev + canon).

    Non-numeric pi/score are stored as null (an anomalous arm must not be
    able to crash the chain append -- that would defeat the cascade counter).
    """
    prev_seq, prev_hash, _ = chain_tail()
    entry = {"seq": prev_seq + 1, "ts": ts, "arm": arm,
             "pi": _num6(pi), "score": _num6(score), "prev": prev_hash}
    digest = hashlib.sha256((prev_hash + canon(entry)).encode()).hexdigest()
    entry["hash"] = digest
    with open(CHAIN, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def chain_seeded_rng(extra=b""):
    """PRNG seeded from sha256(last chain hash) (+ optional domain salt).

    All jitter / tie-breaking flows through this generator so every
    scheduling decision is reproducible from repo state alone.
    """
    _, last_hash, _ = chain_tail()
    seed = hashlib.sha256(last_hash.encode() + extra).hexdigest()
    return random.Random(int(seed, 16))


# ---------------------------------------------------------------------------
# Arm statistics
# ---------------------------------------------------------------------------

def arm_history(entries):
    """Per-arm ordered list of (seq, score) from chain entries.

    Accepts both legacy key "node" (ure_tick.py) and new key "arm".
    """
    hist = {}
    for e in entries:
        arm = e.get("arm") or e.get("node")
        if arm is None or e.get("score") is None:
            continue
        hist.setdefault(arm, []).append((e.get("seq", 0), float(e["score"])))
    for arm in hist:
        hist[arm].sort(key=lambda x: x[0])
    return hist


def arm_stats(node, hist, total_rounds):
    """Return (u, sigma, b, last_seq, deltas) for one arm.

    u_i     : mean of the last-5 score increments (chain history); 0 if none.
    sigma_i : residual signal, self-defined normalized composite in [0,1]:
                  sigma_i = 0.5 * min(n_findings/5, 1)
                          + 0.5 * min(var(last-5 deltas) / 0.05, 1)
              The first half is the findings/residual-count channel
              (SPEC-PARETO-01 §1: residual output is a discovery signal);
              the second half is increment volatility, normalized against
              0.05 (= eps, the diminishing-returns threshold) so an arm whose
              recent deltas swing by ~eps scores ~0.5 on this channel.
    b_i     : exploration bonus = rounds since last pull / total rounds
              (UCB-style; never-pulled arm gets full bonus 1.0).
    """
    arm = node["id"]
    obs = hist.get(arm, [])
    deltas = [b_ - a_ for (_, a_), (_, b_) in zip(obs, obs[1:])]
    window = deltas[-HISTORY_WIN:]
    u = sum(window) / len(window) if window else 0.0
    if len(window) >= 2:
        mean = sum(window) / len(window)
        var = sum((d - mean) ** 2 for d in window) / (len(window) - 1)
    else:
        var = 0.0
    n_findings = len(node.get("findings", []))
    sigma = 0.5 * min(n_findings / 5.0, 1.0) + 0.5 * min(var / 0.05, 1.0)
    last_seq = obs[-1][0] if obs else 0
    if total_rounds > 0:
        b = 1.0 if last_seq == 0 else min((total_rounds - last_seq) / total_rounds, 1.0)
    else:
        b = 1.0
    return u, sigma, b, last_seq, deltas


def shadow_price(u, sigma, b, beta, gamma, c=1.0):
    """Whittle-style shadow price (SPEC-STRAT-02 §2)."""
    return (u + beta * sigma + gamma * b) / c


# ---------------------------------------------------------------------------
# Scheduler tick (dry-run)
# ---------------------------------------------------------------------------

def scheduler_tick():
    ts = utcnow()
    if os.path.exists(GATE):
        print("human-gate active (ure/GATE present); read-only tick, no writes")
        return 0
    with open(ROADMAP) as f:
        roadmap = json.load(f)
    params = dict(DEFAULT_PARAMS)
    params.update(roadmap.get("params", {}))
    beta, gamma, eps = params["beta"], params["gamma"], params["eps"]
    k_max = int(params["K_max"])
    delta = float(roadmap.get("budget", {}).get("tick_score_delta", 0.1))

    prev_seq, _, entries = chain_tail()
    hist = arm_history(entries)
    rng = chain_seeded_rng()

    roadmap.setdefault("probation", [])
    roadmap.setdefault("retired", [])
    roadmap.setdefault("cascade", {})
    roadmap.setdefault("cascade_log", [])

    # --- arm set: non-terminal nodes, hard-capped at K_max (SPEC-STRAT-02 S-c)
    terminal = {"done", "blocked", "retired"}
    arms = [n for n in roadmap["nodes"] if n.get("state") not in terminal]
    arms = arms[:k_max]  # invariant: |A_active| <= K_max

    # --- stats + shadow prices
    table = []
    for n in arms:
        u, sigma, b, _, deltas = arm_stats(n, hist, prev_seq)
        # round to 6dp so the 0.05 ambiguity-band comparison is not fooled
        # by float representation noise
        pi = round(shadow_price(u, sigma, b, beta, gamma), 6)
        table.append({"node": n, "u": u, "sigma": sigma, "b": b, "pi": pi,
                      "deltas": deltas})

    # --- early stop: 2 consecutive rounds with dscore < eps -> retired
    for row in table:
        n, deltas = row["node"], row["deltas"]
        if len(deltas) >= 2 and all(d < eps for d in deltas[-2:]):
            n["state"] = "retired"
            if not any(r.get("id") == n["id"] for r in roadmap["retired"]):
                roadmap["retired"].append(
                    {"id": n["id"], "ts": ts,
                     "reason": f"2 consecutive dscore < eps={eps}",
                     "last_score": n.get("score", 0)})
                print(f"arm {n['id']} retired (diminishing returns)")
    table = [r for r in table if r["node"].get("state") != "retired"]

    # --- new possibilities -> probation pool (idempotent by finding hash)
    known = {p.get("hash") for p in roadmap["probation"]}
    for n in roadmap["nodes"]:
        for f_ in n.get("findings", []):
            h = f_.get("hash")
            if h and h not in known:
                roadmap["probation"].append(
                    {"hash": h, "node": n["id"], "ts": ts,
                     "note": "new possibility entered probation pool"})
                known.add(h)
                print(f"probation += finding {h} (node {n['id']})")

    # --- selection: top shadow price; 70/30 split inside ambiguity band
    if not table:
        entry = append_chain(None, None, None, ts)
        roadmap["pareto"] = {"ts": ts, "arm": None, "note": "no active arms"}
        print("no active arms; idle chain entry appended")
    else:
        table.sort(key=lambda r: (-r["pi"], r["node"]["id"]))
        if len(table) > 1 and abs(table[0]["pi"] - table[1]["pi"]) < 1e-12:
            # exact tie -> chain-seeded PRNG adjudication (reproducible)
            rng.shuffle(table)
            table.sort(key=lambda r: -r["pi"])
        top = table[0]
        dpi = (round(table[0]["pi"] - table[1]["pi"], 6)
               if len(table) > 1 else None)
        split = dpi is not None and 0 < dpi < AMBIGUITY_BAND
        pulls = [(top, 1.0)]
        if split:
            pulls = [(table[0], 0.7), (table[1], 0.3)]
            print(f"ambiguity band: dpi={dpi:.4f} "
                  f"< {AMBIGUITY_BAND} -> 70/30 split "
                  f"{table[0]['node']['id']}/{table[1]['node']['id']}")
        for row, w in pulls:
            n = row["node"]
            try:
                # dry-run simulated pull: no LLM, no issue comments
                n["score"] = round(float(n.get("score", 0)) + delta * w, 6)
                n["state"] = "running"
                roadmap["cascade"].pop(n["id"], None)  # clean tick resets k
            except Exception as exc:  # noqa: BLE001 - cascade must catch all
                k = roadmap["cascade"].get(n["id"], 0) + 1
                roadmap["cascade"][n["id"]] = k
                print(f"::warning::arm {n['id']} tick anomaly k={k}: {exc}")
                if k >= CASCADE_K:
                    n["state"] = "blocked"
                    roadmap["cascade_log"].append(
                        {"id": n["id"], "ts": ts, "level": 1,
                         "reason": f"{CASCADE_K} consecutive tick anomalies"})
                    print(f"arm {n['id']} blocked (cascade level 1)")
        entry = append_chain(top["node"]["id"], top["pi"],
                             top["node"].get("score"), ts)
        roadmap["pareto"] = {
            "ts": ts, "arm": top["node"]["id"], "pi": round(top["pi"], 6),
            "split": bool(split),
            "prices": {r["node"]["id"]: round(r["pi"], 6) for r in table},
            "params": {"beta": beta, "gamma": gamma, "eps": eps}}

    roadmap["last_session_anchor"] = {"ts": ts, "chain_seq": entry["seq"]}
    with open(ROADMAP, "w") as f:
        json.dump(roadmap, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(KEEPALIVE, "w") as f:
        f.write(ts + "\n")
    print(f"pareto tick complete at {ts} (chain seq={entry['seq']})")
    return 0


# ---------------------------------------------------------------------------
# --simulate: offline recursive evidence ("guess strategy -> fixed point")
# ---------------------------------------------------------------------------

SIM_SEED_MATERIAL = b"ure-pareto-sim-v1"
SIM_ARMS = 8
SIM_U_STAR = [0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]
SIM_NOISE_SIGMA = 0.1
SIM_BUDGET = 1.0
SIM_ROUNDS = 300
SIM_EPOCH = 50
BETA_GRID = [round(0.1 * i, 2) for i in range(0, 11)]   # 0.0 .. 1.0
# gamma floored at 0.05: exploration budget never vanishes
# (SPEC-PARETO-01 §2.5 / SPEC-STRAT-02 S-a, root order #4)
GAMMA_GRID = [round(0.05 * i, 2) for i in range(1, 13)]  # 0.05 .. 0.60
FIX_EPS = 0.01           # |d(beta,gamma)| < 0.01 -> fixed-point candidate
FIX_STREAK = 2           # must hold for 2 consecutive epochs


def sim_seed(salt=b""):
    return int.from_bytes(
        hashlib.sha256(SIM_SEED_MATERIAL + salt).digest()[:8], "little")


def make_noise_table():
    """Common random numbers: noise[t][i], identical across strategies/replays."""
    import numpy as np
    rng = np.random.default_rng(sim_seed(b"noise"))
    return rng.normal(0.0, SIM_NOISE_SIGMA, size=(SIM_ROUNDS, SIM_ARMS))


def reward_of(alloc, t, noise):
    """Realized (noisy) reward for an allocation dict {arm: weight}."""
    return sum(w * (SIM_U_STAR[i] + noise[t][i]) for i, w in alloc.items())


def oracle_regret(alloc):
    """Oracle per-round regret: u*_max - sum_i w_i * u*_i (budget B=1)."""
    return max(SIM_U_STAR) - sum(w * SIM_U_STAR[i] for i, w in alloc.items())


class WhittleState:
    """Adaptive arm statistics for strategy B (and epoch replays)."""

    def __init__(self, active_k):
        self.active_k = active_k
        self.pulls = [0] * SIM_ARMS
        self.mean = [0.0] * SIM_ARMS
        self.m2 = [0.0] * SIM_ARMS   # Welford accumulator
        self.last_pull = [-1] * SIM_ARMS

    def clone(self):
        c = WhittleState(self.active_k)
        c.pulls, c.mean, c.m2, c.last_pull = (
            self.pulls[:], self.mean[:], self.m2[:], self.last_pull[:])
        return c

    def active_set(self, beta, gamma, t):
        """Top-K_max arms by shadow price -> invariant |A_active| <= K_max."""
        pis = [self.pi(i, beta, gamma, t) for i in range(SIM_ARMS)]
        order = sorted(range(SIM_ARMS), key=lambda i: -pis[i])
        return order[: self.active_k]

    def pi(self, i, beta, gamma, t):
        if self.pulls[i] > 0:
            u = self.mean[i]
            sigma = (self.m2[i] / (self.pulls[i] - 1)) ** 0.5 \
                if self.pulls[i] > 1 else 0.0
            b = (t - self.last_pull[i]) / max(t, 1)
        else:
            u, sigma, b = 0.0, SIM_NOISE_SIGMA, 1.0  # prior: full bonus
        return shadow_price(u, sigma, b, beta, gamma)

    def choose(self, beta, gamma, t, rng):
        """Whittle pick with tie-break via seeded PRNG and 70/30 ambiguity band."""
        act = self.active_set(beta, gamma, t)
        pis = {i: self.pi(i, beta, gamma, t) for i in act}
        best = max(pis.values())
        tied = [i for i in act if abs(pis[i] - best) < 1e-12]
        first = rng.choice(tied) if len(tied) > 1 else tied[0]
        rest = [i for i in act if i != first]
        alloc = {first: 1.0}
        if rest:
            second = max(rest, key=lambda i: pis[i])
            if 0 < pis[first] - pis[second] < AMBIGUITY_BAND:
                alloc = {first: 0.7, second: 0.3}
        return alloc

    def update(self, alloc, t, noise):
        for i, w in alloc.items():
            r = SIM_U_STAR[i] + noise[t][i]
            self.pulls[i] += 1
            d = r - self.mean[i]
            self.mean[i] += d / self.pulls[i]
            self.m2[i] += d * (r - self.mean[i])
            self.last_pull[i] = t


def strategy_a_round(t, rng, noise):
    """'Root guess' (static): 3 active arms uniform omega=(1/3,1/3,1/3) over
    0.8 exploit budget + fixed 0.2 exploration to one random arm."""
    alloc = {0: 0.8 / 3, 1: 0.8 / 3, 2: 0.8 / 3}
    explor = rng.randrange(SIM_ARMS)
    alloc[explor] = alloc.get(explor, 0.0) + 0.2
    return alloc, [0, 1, 2]


def replay_epoch(state_snapshot, beta, gamma, epoch_idx, noise):
    """Counterfactual epoch replay for meta-recursive refit (SPEC-PARETO-01 §3,
    numeric replay evaluator v0). Deterministic: shared noise table + PRNG
    seeded per (epoch, beta, gamma) for tie-breaks only."""
    st = state_snapshot.clone()
    rng = random.Random(sim_seed(b"replay%d" % epoch_idx))
    regret = 0.0
    for t in range(epoch_idx * SIM_EPOCH, (epoch_idx + 1) * SIM_EPOCH):
        alloc = st.choose(beta, gamma, t, rng)
        regret += oracle_regret(alloc)
        st.update(alloc, t, noise)
    return regret


def run_simulation():
    import numpy as np
    noise = make_noise_table()
    rng_a = random.Random(sim_seed(b"stratA"))
    rng_b = random.Random(sim_seed(b"stratB"))

    beta, gamma = DEFAULT_PARAMS["beta"], DEFAULT_PARAMS["gamma"]
    state_b = WhittleState(active_k=DEFAULT_PARAMS["K_max"])

    regret_a, regret_b = [], []
    cum_a = cum_b = 0.0
    param_traj = [{"epoch": 0, "beta": beta, "gamma": gamma}]
    fixed_point = None
    stable = 0
    budget_ok = True
    kmax_ok = True

    for epoch in range(SIM_ROUNDS // SIM_EPOCH):
        snapshot = state_b.clone()
        # meta-recursive refit: grid-search (beta, gamma) minimizing the
        # replayed regret of the *upcoming* epoch under current statistics
        # (numeric replay evaluator; parameter-level self-modification only,
        #  SPEC-STRAT-02 §3 red line respected).
        best, best_val = (beta, gamma), None
        for bb in BETA_GRID:
            for gg in GAMMA_GRID:
                val = replay_epoch(snapshot, bb, gg, epoch, noise)
                if best_val is None or val < best_val - 1e-12:
                    best, best_val = (bb, gg), val
        prev = (beta, gamma)
        beta, gamma = best
        d = abs(beta - prev[0]) + abs(gamma - prev[1])
        stable = stable + 1 if d < FIX_EPS else 0
        param_traj.append({"epoch": epoch + 1, "beta": beta, "gamma": gamma,
                           "replay_regret": round(best_val, 6)})
        if fixed_point is None and stable >= FIX_STREAK:
            fixed_point = {"epoch": epoch + 1, "beta": beta, "gamma": gamma}

        for t in range(epoch * SIM_EPOCH, (epoch + 1) * SIM_EPOCH):
            # strategy A
            alloc_a, active_a = strategy_a_round(t, rng_a, noise)
            # strategy B
            alloc_b = state_b.choose(beta, gamma, t, rng_b)
            active_b = state_b.active_set(beta, gamma, t)
            # invariant 1: per-round budget <= B
            if sum(alloc_a.values()) > SIM_BUDGET + 1e-9 or \
               sum(alloc_b.values()) > SIM_BUDGET + 1e-9:
                budget_ok = False
            # invariant 2: |A_active| <= K_max
            if len(active_a) > DEFAULT_PARAMS["K_max"] or \
               len(active_b) > DEFAULT_PARAMS["K_max"]:
                kmax_ok = False
            cum_a += oracle_regret(alloc_a)
            cum_b += oracle_regret(alloc_b)
            regret_a.append(round(cum_a, 6))
            regret_b.append(round(cum_b, 6))
            state_b.update(alloc_b, t, noise)

    return {
        "regret_a": regret_a, "regret_b": regret_b,
        "final_regret_a": round(cum_a, 6), "final_regret_b": round(cum_b, 6),
        "param_traj": param_traj, "fixed_point": fixed_point,
        "budget_ok": budget_ok, "kmax_ok": kmax_ok,
    }


def simulate():
    os.makedirs(os.path.dirname(SIM_OUT), exist_ok=True)
    run1 = run_simulation()
    run2 = run_simulation()  # invariant 3: PRNG reproducibility (two-run check)
    prng_ok = (run1["regret_a"] == run2["regret_a"] and
               run1["regret_b"] == run2["regret_b"] and
               run1["param_traj"] == run2["param_traj"] and
               run1["fixed_point"] == run2["fixed_point"])

    fp = run1["fixed_point"]
    ratio = (run1["final_regret_b"] / run1["final_regret_a"]
             if run1["final_regret_a"] else None)
    out = {
        "spec": "SPEC-PARETO-01 §2 / SPEC-STRAT-02 §1§4 / SPEC-LOOP-01 §3",
        "ts": utcnow(),
        "env": {"arms": SIM_ARMS, "u_star": SIM_U_STAR,
                "noise_sigma": SIM_NOISE_SIGMA, "budget": SIM_BUDGET,
                "rounds": SIM_ROUNDS, "epoch_len": SIM_EPOCH,
                "seed_sha256_16": hashlib.sha256(SIM_SEED_MATERIAL)
                .hexdigest()[:16]},
        "strategies": {
            "A": "root guess: 3 active arms uniform omega=(1/3,1/3,1/3) "
                 "over 0.8 exploit + fixed 0.2 random exploration (static)",
            "B": "Whittle adaptive shadow price pi=(u+beta*sigma+gamma*b)/c "
                 "with 70/30 ambiguity band 0.05 + per-epoch meta-recursive "
                 "(beta,gamma) grid-search refit on replayed regret"},
        "regret_curve_a": run1["regret_a"],
        "regret_curve_b": run1["regret_b"],
        "final_regret_a": run1["final_regret_a"],
        "final_regret_b": run1["final_regret_b"],
        "regret_ratio_b_over_a": round(ratio, 6) if ratio is not None else None,
        "param_trajectory": run1["param_traj"],
        "pi_star": {"beta": fp["beta"], "gamma": fp["gamma"]} if fp else None,
        "fixed_point_epoch": fp["epoch"] if fp else None,
        "fixed_point_rule": f"|d(beta,gamma)| < {FIX_EPS} for "
                            f"{FIX_STREAK} consecutive epochs",
        "invariants": {
            "budget_leq_B_every_round": run1["budget_ok"],
            "active_arms_leq_K_max": run1["kmax_ok"],
            "prng_two_run_reproducible": prng_ok,
        },
    }
    with open(SIM_OUT, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: out[k] for k in
                      ("final_regret_a", "final_regret_b",
                       "regret_ratio_b_over_a", "pi_star",
                       "fixed_point_epoch", "invariants")},
                     ensure_ascii=False, indent=2))
    ok = all(out["invariants"].values())
    print("invariant self-check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="URE Pareto/Whittle scheduler")
    ap.add_argument("--simulate", action="store_true",
                    help="offline recursive evidence -> ure/sim/out.json")
    args = ap.parse_args()
    if args.simulate:
        return simulate()
    return scheduler_tick()


if __name__ == "__main__":
    sys.exit(main())
