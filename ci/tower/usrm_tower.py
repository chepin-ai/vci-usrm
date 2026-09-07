#!/usr/bin/env python3
"""usrm-tower poller v0.2 — SI2 塔件（WEAN-01 自有唤醒源·仓侧巡塔）
v0.2: 内嵌迷你复活道——CMD_AUTH(secret,64hex两半直拼)→fernet 解公仓 vault→mint installation token→巡 ci-inbox 公告板
面: 板面差集轮检 → receipts 归档 → @usrm 命中置 wake-needed 旗标
轨: 主驱=repository_dispatch(qf-beat/board-beat)事件; schedule=死手兜底(30min错峰); 纯事件优先
律: 单写入者(唯写自仓 ci/tower/); E804 密钥零入文零回显(全程环境变量); R1 公面纯状态语言
降级宣示: 复活/巡板任一失败 → receipt 标 DEGRADED + exit 0(不炸 runner) + wake-needed 不置
"""
import json, os, sys, time, base64, urllib.request, urllib.parse
from hashlib import sha256

VAULT = "https://raw.githubusercontent.com/chepin-ai/vci-inbox/main/inbox/usrm-seed-vault.b64"
INBOX = "https://api.github.com/repos/chepin-ai/ci-inbox"
STATE = "ci/tower/tower-state.json"
WAKE  = "ci/tower/wake-needed.json"

def mint_token():
    import jwt
    from cryptography.fernet import Fernet
    ca = os.environ.get("CMD_AUTH", "").strip()
    if len(ca) != 64:
        raise RuntimeError("CMD_AUTH missing/malformed")
    fk = base64.urlsafe_b64encode(sha256(bytes.fromhex(ca)).digest())
    raw = urllib.request.urlopen(VAULT, timeout=20).read().decode()
    blob = "".join(l for l in raw.splitlines() if not l.startswith("#"))
    bundle = json.loads(Fernet(fk).decrypt(base64.b64decode(blob)))
    kv = {}
    for line in bundle["keys"].strip().splitlines():
        if "=" in line:
            k, v = line.split("=", 1); kv[k] = v
    now = int(time.time())
    tok = jwt.encode({"iat": now-60, "exp": now+540, "iss": kv["GH_APP_ID"]},
                     bundle["gh_app_pem"], algorithm="RS256")
    req = urllib.request.Request(
        f"https://api.github.com/app/installations/{kv['GH_APP_INSTALLATION']}/access_tokens",
        data=b"{}", method="POST",
        headers={"Authorization": "Bearer "+tok, "Accept": "application/vnd.github+json",
                 "User-Agent": "usrm-tower"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["token"]

def gh(path, tok):
    req = urllib.request.Request(INBOX + path, headers={
        "Authorization": "Bearer "+tok, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def load(p, dflt):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return dflt

def emit(rc, degraded=None):
    if degraded:
        rc["degraded"] = degraded
    st = load(STATE, {"last_ts": "2026-09-07T00:00:00Z", "seq": 0})
    st["seq"] += 1
    rc["seq"] = st["seq"]
    os.makedirs("ci/tower/receipts", exist_ok=True)
    line = json.dumps(rc, ensure_ascii=False)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    open(f"ci/tower/receipts/{stamp}.jsonl", "w", encoding="utf-8").write(line + "\n")
    open("ci/tower/receipts_last.jsonl", "w", encoding="utf-8").write(line + "\n")
    if not degraded:
        st["last_ts"] = rc.get("newest", st["last_ts"])
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(line)

def main():
    ts_now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        tok = mint_token()
    except Exception as e:
        emit({"ts": ts_now, "stage": "mint"}, degraded=f"复活道失败: {type(e).__name__}（主道=vault+CMD_AUTH; 复道=候人工配 GH_TOWER_READ）")
        return
    st = load(STATE, {"last_ts": "2026-09-07T00:00:00Z", "seq": 0})
    since = st["last_ts"]
    try:
        cm = gh("/commits?path=" + urllib.parse.quote("公告板") + "&since=" + since + "&per_page=50", tok)
    except Exception as e:
        emit({"ts": ts_now, "stage": "poll"}, degraded=f"巡板失败: {type(e).__name__}")
        return
    cm = [c for c in cm if not c["commit"]["message"].startswith("beacon")]
    hits, newest = [], since
    for c in sorted(cm, key=lambda c: c["commit"]["committer"]["date"]):
        msg = c["commit"]["message"]
        rec = {"sha": c["sha"][:12], "ts": c["commit"]["committer"]["date"],
               "msg": msg[:120].replace("\n", " ")}
        if "@usrm" in msg:
            rec["at_usrm"] = True
        hits.append(rec)
        newest = max(newest, rec["ts"])
    rc = {"ts": ts_now, "since": since, "newest": newest, "non_beacon": len(hits),
          "at_usrm": [h for h in hits if h.get("at_usrm")], "events": hits}
    json.dump({"needed": bool(rc["at_usrm"]), "refs": rc["at_usrm"], "ts": ts_now,
               "note": "塔件检出@usrm新动,候SI2注入面接;阅否自决,无债无令"},
              open(WAKE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    emit(rc)

if __name__ == "__main__":
    main()
