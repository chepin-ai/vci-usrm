#!/usr/bin/env python3
"""PROJ-ENGINE-01 v0.1 — pattern→投影 工程化原型（PROJECTION-THEORY-01§四）
输入: snapshot/{obligation,registry_pattern,registry_inst,ledger}.txt（四网实数据快照）
输出: PROJ-RUN-01.json（投影向量+覆盖度+同构签名+digest）| 可重放三件套: 本脚本sha+run件+重算digest
诚实档: 单沙箱 classical; 命中=名字面字符串匹配(坐标级近似,候坐标正文化精确化)
"""
import json, hashlib, sys
def H(s): return hashlib.sha256(s.encode()).hexdigest()
nets = {n: open(f"snapshot/{n}.txt", encoding="utf-8").read() for n in
        ["obligation", "registry_pattern", "registry_inst", "ledger"]}
objects = json.load(open("snapshot/objects.json", encoding="utf-8"))
def project(obj):
    vec = {}
    for net, blob in nets.items():
        coords, idx = [], 0
        while True:
            i = blob.find(obj, idx)
            if i < 0: break
            coords.append(i); idx = i + 1
        vec[net] = coords
    return vec
proj = {}
for o in objects:
    v = project(o)
    proj[o] = {"cover": sum(1 for k in v if v[k]), "hits": sum(len(c) for c in v.values()),
               "per_net": {k: len(v[k]) for k in v},
               "iso_sig": H(json.dumps([len(v[k]) for k in sorted(v)], sort_keys=True))[:12]}
run = {"run": "PROJ-RUN-01", "objects": len(objects), "projections": proj,
       "digest": H(json.dumps(proj, ensure_ascii=False, sort_keys=True))}
json.dump(run, open("PROJ-RUN-01.json", "w"), ensure_ascii=False, indent=1)
print("digest:", run["digest"])
iso = {}
for o, p in proj.items(): iso.setdefault(p["iso_sig"], []).append(o)
print("isomorphic classes:", [v for v in iso.values() if len(v) > 1])
