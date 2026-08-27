#!/usr/bin/env python3
r"""Federation obligation monitor — 〈RED〉 anchored aggregation + drift sentinel.

SPEC-NMUST-02 §7: the obligation machine's own health is itself an obligation.
Each business repo clears obligations locally (vci-usrm ure-sweeper etc.);
〈RED〉 (this repo, chepin-ai/ci-control) aggregates a federation-level view:

    sources:
      - chepin-ai/vci-usrm     ure/obligations.jsonl (ledger)
                               ure/chain.jsonl intents {RPT.OBLIG, INCIDENT, WARN, FINDING}
      - chepin-ai/vci-library  kit/INDEX.md F-table admonitions (告诫 F\d+)
      - chepin-ai/vci-playground  atp|tn|kaggle results: fail / FINDING entries

    view (federation/oblig_view.json):
      {ts, per_repo: {open:[...], escalated:[...], closed_24h:N, last_ts, stale},
       drift_sentinel: {stale, threshold_h, sources:{...}, last_alert_date}}

    drift sentinel: any source with no new entry for >8h (should-moved-but-didn't)
      -> view marks stale:true and comments once per UTC day (<=1/day throttle)
      on chepin-ai/vci-inbox issue#1.

    The view is also mirrored to the PUBLIC repo vci-usrm
    (ure/federation_oblig_view.json) because HUB-CORE is private and the
    federation face must be anonymously verifiable. The view carries zero
    secrets and zero personal identifiers (iron rule).

Secrets only via env / Authorization headers; logs carry zero secrets.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ORG = "chepin-ai"
REPO_USRM = f"{ORG}/vci-usrm"
REPO_LIB = f"{ORG}/vci-library"
REPO_PG = f"{ORG}/vci-playground"
REPO_CTL = f"{ORG}/ci-control"
REPO_INBOX = f"{ORG}/vci-inbox"

VIEW_PATH = "federation/oblig_view.json"
MIRROR_PATH = "ure/federation_oblig_view.json"

# Commit targets in priority order: HUB-CORE is the federation anchor;
# vci-usrm (PUBLIC) is the anonymous-verifiable mirror AND the degraded
# primary when HUB-CORE Actions is unavailable. Overridable via env
# OBLIG_VIEW_TARGETS="repo:path,repo:path".
DEFAULT_TARGETS = [(REPO_CTL, VIEW_PATH), (REPO_USRM, MIRROR_PATH)]


def view_targets():
    raw = os.environ.get("OBLIG_VIEW_TARGETS", "").strip()
    if not raw:
        return list(DEFAULT_TARGETS)
    out = []
    for item in raw.split(","):
        repo, _, path = item.strip().partition(":")
        if repo and path:
            out.append((repo, path))
    return out or list(DEFAULT_TARGETS)

TERMINAL = {"legislated", "wontfix"}
STALE_H = 8.0            # drift sentinel threshold (hours without new entries)
ESCALATE_AGE_H = 24.0    # open item older than this counts as escalated
CLOSED_WINDOW_H = 24.0

TOKEN = os.environ.get("CI_ROOT_TOKEN") or os.environ.get("GH_TOKEN") or ""
API = "https://api.github.com"

F_RE = re.compile(r"告诫\s*(F\d+)")
STATUS_WORDS = ("fail", "error", "finding")


def utcnow_dt():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    """Parse 'YYYY-MM-DDTHH:MM:SSZ' -> aware datetime; None on failure."""
    if not s or not isinstance(s, str):
        return None
    try:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None


def age_h(ts, now=None):
    """Age in hours of an ISO ts string (None -> +inf)."""
    now = now or utcnow_dt()
    dt = parse_ts(ts) if isinstance(ts, str) else ts
    if dt is None:
        return float("inf")
    return (now - dt).total_seconds() / 3600.0


def is_stale(last_ts, now=None, threshold_h=STALE_H):
    """Drift sentinel predicate: a source that should move but hasn't for
    longer than threshold_h is stale. Unknown ts counts as stale."""
    return age_h(last_ts, now) > threshold_h


def gh_req(path, method="GET", body=None):
    if not TOKEN:
        raise RuntimeError("CI_ROOT_TOKEN/GH_TOKEN env required")
    req = urllib.request.Request(
        API + path, method=method,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "ci-root-oblig-monitor",
                 "X-GitHub-Api-Version": "2022-11-28"})
    if body is not None:
        req.data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:200]}


def get_text(repo, path, ref="main"):
    s, r = gh_req(f"/repos/{repo}/contents/{path}?ref={ref}")
    if s != 200 or not isinstance(r, dict):
        return None
    return base64.b64decode(r["content"]).decode()


def list_dir(repo, path, ref="main"):
    s, r = gh_req(f"/repos/{repo}/contents/{path}?ref={ref}")
    if s != 200 or not isinstance(r, list):
        return []
    return [x["name"] for x in r if x.get("type") == "file"]


def jsonl_entries(text):
    out = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def put_file(repo, path, content_str, message):
    s, r = gh_req(f"/repos/{repo}/contents/{path}")
    body = {"message": message,
            "content": base64.b64encode(content_str.encode()).decode(),
            "branch": "main"}
    if s == 200 and isinstance(r, dict) and r.get("sha"):
        body["sha"] = r["sha"]
    s, r = gh_req(f"/repos/{repo}/contents/{path}", method="PUT", body=body)
    return s in (200, 201), r


# ---------------------------------------------------------------- sources --

def agg_usrm(now):
    """vci-usrm: obligation ledger + chain (RPT.OBLIG/INCIDENT/WARN/FINDING)."""
    ledger = jsonl_entries(get_text(REPO_USRM, "ure/obligations.jsonl"))
    chain = jsonl_entries(get_text(REPO_USRM, "ure/chain.jsonl"))

    escalate_oids = set()
    closed_24h = 0
    for e in chain:
        note = e.get("note") or ""
        if e.get("intent") == "RPT.OBLIG":
            if "escalate" in note and e.get("oid"):
                escalate_oids.add(e["oid"])
            if e.get("to") in TERMINAL and age_h(e.get("ts"), now) <= CLOSED_WINDOW_H:
                closed_24h += 1

    open_items, escalated = [], []
    for o in ledger:
        if o.get("state") in TERMINAL:
            continue
        item = {"id": o.get("id"), "state": o.get("state"),
                "domain": o.get("domain", "machine"),
                "opened": o.get("opened"),
                "age_h": round(age_h(o.get("opened"), now), 1),
                "src": (o.get("src") or "")[:120]}
        open_items.append(item)
        if item["age_h"] > ESCALATE_AGE_H or o.get("id") in escalate_oids:
            escalated.append(o.get("id"))

    ts_pool = [e.get("ts") for e in chain] + [o.get("opened") for o in ledger]
    last_ts = max((t for t in ts_pool if t), default=None)
    return {"open": open_items, "escalated": sorted(set(escalated)),
            "closed_24h": closed_24h, "last_ts": last_ts}, ledger


def agg_library(now, usrm_ledger):
    """vci-library: kit/INDEX.md F-table admonitions; closure state is
    cross-checked against the usrm ledger (o-kit-F{n})."""
    text = get_text(REPO_LIB, "kit/INDEX.md") or ""
    f_ids = sorted(set(F_RE.findall(text)))
    ledger_state = {o.get("id"): o.get("state") for o in usrm_ledger}
    open_items, closed = [], 0
    for fid in f_ids:
        st = ledger_state.get(f"o-kit-{fid}")
        if st in TERMINAL:
            closed += 1
        else:
            open_items.append({"id": f"kit-{fid}",
                               "state": st or "untracked",
                               "src": "kit/INDEX.md F-table admonition"})
    # last_ts: latest commit touching kit/INDEX.md
    s, r = gh_req(f"/repos/{REPO_LIB}/commits?path=kit/INDEX.md&per_page=1")
    last_ts = None
    if s == 200 and isinstance(r, list) and r:
        last_ts = r[0]["commit"]["committer"]["date"]
    return {"open": open_items, "escalated": [], "closed_24h": 0,
            "closed_total": closed, "last_ts": last_ts}


def _entry_failed(obj):
    """A playground result entry 'fails' if overall != pass, or any nested
    status/verdict word is fail/error, or it is a FINDING record."""
    if not isinstance(obj, dict):
        return False
    if obj.get("intent") == "FINDING":
        return True
    ov = obj.get("overall") or obj.get("verdict")
    if isinstance(ov, str) and any(w in ov.lower() for w in STATUS_WORDS):
        return True
    for key in ("engines", "cases", "result"):
        sub = obj.get(key)
        if isinstance(sub, dict):
            for v in sub.values():
                if isinstance(v, dict):
                    st = str(v.get("status") or v.get("verdict") or "").lower()
                    if any(w in st for w in STATUS_WORDS):
                        return True
    return False


def agg_playground(now):
    """vci-playground: three labs (atp / tn / kaggle) results dirs.
    A fail entry stays open until a later all-pass entry for the same lab."""
    labs = {"atp": "atp/results", "tn": "tn/results", "kaggle": "kaggle/results"}
    open_items, escalated = [], []
    closed_24h = 0
    last_ts = None
    for lab, d in labs.items():
        entries = []
        for name in sorted(list_dir(REPO_PG, d)):
            text = get_text(REPO_PG, f"{d}/{name}")
            if name.endswith(".jsonl"):
                entries.extend(jsonl_entries(text))
            elif name.endswith(".json") and text:
                try:
                    entries.append(json.loads(text))
                except json.JSONDecodeError:
                    continue
        entries.sort(key=lambda e: e.get("ts") or "")
        for e in entries:
            t = e.get("ts")
            if t and (last_ts is None or t > last_ts):
                last_ts = t
        fails = [e for e in entries if _entry_failed(e)]
        for f in fails:
            fid = f"{lab}@{(f.get('ts') or '?')}"
            later_pass = any((not _entry_failed(x)) and
                             (x.get("ts") or "") > (f.get("ts") or "")
                             for x in entries)
            if later_pass:
                if age_h(f.get("ts"), now) <= CLOSED_WINDOW_H:
                    closed_24h += 1
                continue
            open_items.append({"id": fid, "state": "fail",
                               "ts": f.get("ts"),
                               "age_h": round(age_h(f.get("ts"), now), 1)})
            if age_h(f.get("ts"), now) > ESCALATE_AGE_H:
                escalated.append(fid)
    return {"open": open_items, "escalated": sorted(set(escalated)),
            "closed_24h": closed_24h, "last_ts": last_ts}


# ------------------------------------------------------------- sentinel ----

def build_view(now=None, prev_view=None, offline_sources=None):
    """Build the federation view. `offline_sources` (dict repo->source dict)
    bypasses network reads for sandbox self-tests."""
    now = now or utcnow_dt()
    if offline_sources is not None:
        per_repo = offline_sources
    else:
        usrm, ledger = agg_usrm(now)
        per_repo = {"vci-usrm": usrm,
                    "vci-library": agg_library(now, ledger),
                    "vci-playground": agg_playground(now)}
    sentinel_sources = {}
    any_stale = False
    for name, src in per_repo.items():
        lt = src.get("last_ts")
        st = is_stale(lt, now)
        sentinel_sources[name] = {
            "last_ts": lt, "age_h": (None if lt is None
                                     else round(age_h(lt, now), 1)),
            "stale": st}
        any_stale = any_stale or st
        src["stale"] = st
    last_alert = (prev_view or {}).get("drift_sentinel", {}).get(
        "last_alert_date")
    view = {"ts": iso(now), "anchor": "〈RED〉",
            "spec": "NMUST-02 §7 drift sentinel; federation obligation view v1",
            "per_repo": per_repo,
            "drift_sentinel": {"stale": any_stale,
                               "threshold_h": STALE_H,
                               "sources": sentinel_sources,
                               "last_alert_date": last_alert}}
    return view


def alert_needed(view, today):
    """Throttle: at most one inbox alert per UTC day."""
    ds = view["drift_sentinel"]
    return ds["stale"] and ds.get("last_alert_date") != today


def post_alert(view, today):
    stale = [n for n, s in view["drift_sentinel"]["sources"].items()
             if s["stale"]]
    lines = ["【漂移哨兵 · drift sentinel】义务机健康告警（NMUST-02 §7）",
             f"- 视图时间: {view['ts']}",
             f"- 阈值: {view['drift_sentinel']['threshold_h']}h 无新条目即 stale",
             "- stale 源:"]
    for n in stale:
        s = view["drift_sentinel"]["sources"][n]
        lines.append(f"  - {n}: last={s['last_ts']} age={s['age_h']}h")
    lines.append("- 处置: 各业务仓检查本地清算循环是否停摆；恢复后本告警自动消除")
    lines.append(f"- 节流: 每日 ≤1 次（本日已发 {today}）")
    s, r = gh_req(f"/repos/{REPO_INBOX}/issues/1/comments",
                  method="POST", body={"body": "\n".join(lines)})
    return s == 201


# ------------------------------------------------------------- selftest ----

def selftest():
    """Sandbox checks for stale judgement and alert throttling (no network)."""
    now = datetime(2026, 8, 25, 3, 0, 0, tzinfo=timezone.utc)
    fresh = iso(now - timedelta(hours=2))
    old = iso(now - timedelta(hours=9))
    assert not is_stale(fresh, now), "fresh source must not be stale"
    assert is_stale(old, now), "9h-old source must be stale"
    assert is_stale(iso(now - timedelta(hours=8, minutes=1)), now)
    assert not is_stale(iso(now - timedelta(hours=7, minutes=59)), now)
    assert is_stale(None, now), "unknown ts counts as stale"

    src = lambda ts: {"open": [], "escalated": [], "closed_24h": 0,
                      "last_ts": ts}
    view = build_view(now=now, offline_sources={
        "vci-usrm": src(fresh), "vci-library": src(old),
        "vci-playground": src(old)})
    assert view["drift_sentinel"]["stale"] is True
    today = now.strftime("%Y-%m-%d")
    assert alert_needed(view, today), "first stale day must alert"
    view["drift_sentinel"]["last_alert_date"] = today
    assert not alert_needed(view, today), "same UTC day must be throttled"
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    assert alert_needed(view, tomorrow), "next UTC day may alert again"

    ok = build_view(now=now, offline_sources={
        "vci-usrm": src(fresh), "vci-library": src(fresh),
        "vci-playground": src(fresh)})
    assert ok["drift_sentinel"]["stale"] is False
    assert not alert_needed(ok, today)

    f = _entry_failed({"overall": "fail"})
    assert f and _entry_failed({"intent": "FINDING"})
    assert _entry_failed({"cases": {"a": {"status": "fail"}}})
    assert not _entry_failed({"overall": "pass", "engines": {"z3": {"status": "pass"}}})
    print("selftest: stale judgement + daily throttle + fail detection OK")


# ----------------------------------------------------------------- main ----

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="sandbox checks only; no network, no writes")
    ap.add_argument("--no-alert", action="store_true",
                    help="build/commit view but skip inbox alerting")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0

    now = utcnow_dt()
    targets = view_targets()
    # previous view (for throttle state): first readable target wins
    prev = None
    for repo, path in targets:
        old = get_text(repo, path)
        if old:
            try:
                prev = json.loads(old)
                break
            except json.JSONDecodeError:
                continue

    view = build_view(now=now, prev_view=prev)

    today = now.strftime("%Y-%m-%d")
    alert_err = None
    if not args.no_alert and alert_needed(view, today):
        if post_alert(view, today):
            view["drift_sentinel"]["last_alert_date"] = today
            print("drift sentinel: stale source(s) -> inbox alert posted "
                  "(throttled 1/day)")
        else:
            alert_err = "inbox alert post failed"
            print("drift sentinel: alert post FAILED (view still committed)")
    if alert_err:
        view["drift_sentinel"]["alert_error"] = alert_err

    payload = json.dumps(view, ensure_ascii=False, indent=1,
                         sort_keys=True) + "\n"
    msg = f"federation: oblig view {view['ts']} [skip ci]"
    any_ok = False
    for repo, path in targets:
        ok, resp = put_file(repo, path, payload, msg)
        any_ok = any_ok or ok
        print(f"commit {repo}/{path}: {'ok' if ok else 'FAILED'}")
    if not any_ok:
        print("FATAL: no view target writable")
        return 1
    counts = {k: {"open": len(v["open"]), "escalated": len(v["escalated"]),
                  "closed_24h": v["closed_24h"], "stale": v["stale"]}
              for k, v in view["per_repo"].items()}
    print("counts:", json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
