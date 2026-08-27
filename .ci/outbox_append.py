#!/usr/bin/env python3
"""OUTBOX-LIVE-01 解 A · usrm 线适配器（vci-usrm 仓内）
输入：环境变量 ITEM_JSON（DISC-01 单件）或批量文件；动作：追加+指纹+prev 链咬→覆盖写 outbox/usrm-outbox.json
信任：HMAC(CMD_AUTH) 若 secret 在仓则签名，否则诚实标 unsigned-hash-chain
"""
import json, hashlib, hmac, os, sys, datetime
H = lambda s: hashlib.sha256(s.encode()).hexdigest()
canon = lambda o: json.dumps(o, ensure_ascii=False, sort_keys=True)
FP = "outbox/usrm-outbox.json"
KEY = os.environ.get("CMD_AUTH", "")  # repo secret（可选，有则 hmac-preferred）

os.makedirs("outbox", exist_ok=True)
if os.path.exists(FP):
    ob = json.load(open(FP))
else:
    ob = {"contract": "usrm-outbox/v1", "repo": "USRM-VAULT",
          "law": "零凭证出站: HMAC(CMD_AUTH) 为唯一信任根; dtag 幂等; 2h 无 ack 自动升级",
          "entries": []}

raw = os.environ.get("ITEM_JSON", "").strip()
if not raw:
    print("ITEM_JSON 为空，无可追加"); sys.exit(0)
items = json.loads(raw)
if isinstance(items, dict): items = [items]
for it in items:
    prev = ob["entries"][-1]["hash"] if ob["entries"] else (
        ob.get("chain_anchor", {}).get("hash", "genesis"))
    e = {"seq": (ob["entries"][-1]["seq"] if ob["entries"]
                 else ob.get("chain_anchor", {}).get("seq", 0)) + 1,
         "ts": datetime.datetime.now(datetime.UTC).isoformat(),
         "intent": it.get("intent", "DISC"), "dtag": it.get("dtag", it.get("id", "")), "prev": prev}
    for k in ("id", "thread", "in_reply_to", "to", "body", "payload"):
        if k in it: e[k] = it[k]
    e["hash"] = H(prev + canon({k: v for k, v in e.items() if k not in ("hash", "hmac")}))
    e["hmac"] = hmac.new(KEY.encode(), e["hash"].encode(), hashlib.sha256).hexdigest() if KEY else "UNSIGNED-NO-KEY"
    # dtag 幂等
    if any(x.get("dtag") == e["dtag"] and e["dtag"] for x in ob["entries"]):
        print("dup dtag, skip:", e["dtag"]); continue
    ob["entries"].append(e)
    print("appended seq", e["seq"], e["dtag"])
json.dump(ob, open(FP, "w"), ensure_ascii=False, indent=1)
