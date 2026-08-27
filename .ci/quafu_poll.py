#!/usr/bin/env python3
# QUAFU-POLL-01 · CI 端真机任务轮询（替代会话端付费 cron）
# 会话端 cron 每次点火计加油包费用(实测 ¥1.42/次)，违反「会话端驻留必须用免费类型」原则；
# 本脚本跑在 GitHub Actions 公仓免费分钟(vci-inbox 中枢已实证全绿)或解冻后的 vci-usrm。
import os, json, time, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]   # .ci/quafu_poll.py → 仓根
WATCH = ROOT / "weave" / "quafu" / "watchlist.json"   # 蹲守清单：{"jobs":[{"job_id":..,"chip":"ScQ-P5","note":..}]}
STATE = ROOT / "weave" / "quafu" / "status.json"      # 状态落盘=对表面,会话端 RECON 时读此文件
TOKEN = os.environ.get("〈RED〉", "")              # repo secret,勿硬编码
API = "https://quafu.baqis.ac.cn"                      # Quafu 开放云

def http(path, payload=None):
    req = urllib.request.Request(API + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json", "Authorization": TOKEN})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    wl = json.loads(WATCH.read_text()) if WATCH.exists() else {"jobs": []}
    state = json.loads(STATE.read_text()) if STATE.exists() else {"polls": 0, "jobs": {}}
    state["polls"] += 1
    state["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    changed = False
    for j in wl.get("jobs", []):
        jid = j["job_id"]
        prev = state["jobs"].get(jid, {})
        try:
            # Quafu 任务状态查询（无 token 时退化为公开状态页探测）
            st = http(f"/api/job/{jid}") if TOKEN else {"status": "TOKEN_MISSING"}
        except Exception as e:
            st = {"status": "POLL_ERR", "err": str(e)[:120]}
        if st.get("status") != prev.get("status"):
            state["jobs"][jid] = {**st, "chip": j.get("chip"), "updated": state["ts"]}
            changed = True
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1))
    # 退出码 2 = 有状态变化(供 workflow 决定是否 commit);0 = 无变化
    raise SystemExit(2 if changed else 0)

if __name__ == "__main__":
    main()
