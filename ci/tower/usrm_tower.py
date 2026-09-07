#!/usr/bin/env python3
"""usrm-tower poller — SI2 塔件 v0.1（WEAN-01 自有唤醒源·仓侧巡塔）
面: ci-inbox 公告板差集轮检 → receipts 归档 → @usrm 命中置 wake-needed 旗标
轨: 主驱=repository_dispatch(qf-beat/board-beat)事件; schedule=死手兜底(30min错峰); 纯事件优先
律: 单写入者(本器唯写 vci-usrm 自仓 ci/tower/); E804 无密钥入文; R1 公面仅状态语言
"""
import json, os, sys, time, urllib.request, urllib.parse

INBOX = "https://api.github.com/repos/chepin-ai/ci-inbox"
STATE = "ci/tower/tower-state.json"
WAKE  = "ci/tower/wake-needed.json"
TOK = os.environ.get("GH_TOWER_READ") or os.environ.get("GITHUB_TOKEN") or ""

def gh(path):
    req = urllib.request.Request(INBOX + path, headers={
        "Accept": "application/vnd.github+json",
        **({"Authorization": "Bearer " + TOK} if TOK else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def load(p, dflt):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return dflt

def main():
    st = load(STATE, {"last_ts": "2026-09-07T00:00:00Z", "seq": 0})
    since = st["last_ts"]
    cm = gh("/commits?path=" + urllib.parse.quote("公告板") + "&since=" + since + "&per_page=50")
    cm = [c for c in cm if not c["commit"]["message"].startswith("beacon")]
    hits, newest = [], since
    for c in sorted(cm, key=lambda c: c["commit"]["committer"]["date"]):
        msg = c["commit"]["message"]
        rec = {"sha": c["sha"][:12], "ts": c["commit"]["committer"]["date"],
               "msg": msg[:120].replace("\n", " ")}
        hits.append(rec)
        if "@usrm" in msg:
            rec["at_usrm"] = True
        newest = max(newest, rec["ts"])
    st["last_ts"] = newest
    st["seq"] += 1
    os.makedirs("ci/tower/receipts", exist_ok=True)
    rc = {"seq": st["seq"], "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "since": since, "non_beacon": len(hits),
          "at_usrm": [h for h in hits if h.get("at_usrm")], "events": hits}
    line = json.dumps(rc, ensure_ascii=False)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    open(f"ci/tower/receipts/{stamp}.jsonl", "w", encoding="utf-8").write(line + "\n")
    open("ci/tower/receipts_last.jsonl", "w", encoding="utf-8").write(line + "\n")
    if rc["at_usrm"]:
        json.dump({"needed": True, "refs": rc["at_usrm"], "ts": rc["ts"],
                   "note": "塔件检出@usrm新动,候SI2注入面接;阅否自决,无债无令"},
                  open(WAKE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(line)

if __name__ == "__main__":
    main()
