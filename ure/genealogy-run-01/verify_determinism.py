#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确定性比对：两跑 transcript 归一化 ts/cost（实测耗时项）后逐字段比对。
用法: python3 verify_determinism.py transcript-run1.json transcript.json"""
import json, sys

def norm(doc):
    d = json.loads(json.dumps(doc))
    for e in d["entries"]:
        e["ts"] = "<TS>"
        e["cost"] = "<COST>"  # wall_ms/cost_acc 为实测机时，属归一化差项
    d["total"] = "<TOTAL>"
    return d

a = norm(json.load(open(sys.argv[1], encoding="utf-8")))
b = norm(json.load(open(sys.argv[2], encoding="utf-8")))
same = a == b
ha = [e["hash"] for e in a["entries"]]
hb = [e["hash"] for e in b["entries"]]
print(f"normalized_equal={same}")
print(f"hash_chain_equal={ha == hb}  entries={len(ha)}")
print(f"run1_tip={ha[-1] if ha else None}  run2_tip={hb[-1] if hb else None}")
if not same:
    for ea, eb in zip(a["entries"], b["entries"]):
        if ea != eb:
            print("DIFF phase", ea["phase"])
            for k in ea:
                if ea[k] != eb.get(k): print(" ", k, ea[k], "!=", eb.get(k))
sys.exit(0 if same else 1)
