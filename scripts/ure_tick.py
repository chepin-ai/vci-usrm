#!/usr/bin/env python3
"""URE-00 U0 sweeper tick (dry-run mode, no LLM calls).

Design (URE-00 v0.1):
- Source of truth lives in the repo (git-scraping): ure/roadmap.json +
  append-only hash chain ure/chain.jsonl (prev/hash/hmac, hmac=HMAC(CMD_AUTH, hash)).
- Task-board projection: one issue per node, label state machine
  agent/queued -> agent/running -> agent/blocked -> agent/done.
- One node per tick: promote first queued node to running (or continue the
  running one), post heartbeat comment, simulated score += delta;
  score >= done_threshold -> done + RETURN stamp on vci-inbox issue #1.
- Human gate: if ure/GATE exists, the sweeper is read-only (notice comment only).
- Keepalive: touches ure/.keepalive every tick (prevents 60d schedule disable).
- Idempotent / resumable: issue numbers and chain tail are persisted; a
  re-run after a crash continues from repo state.

The workflow handles git commit/push ([skip ci]); this script only mutates
the working tree and talks to the GitHub API.
"""
import hashlib
import hmac as hmac_mod
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
REPO = os.environ.get("GITHUB_REPOSITORY", "chepin-ai/vci-usrm")
INBOX_REPO = os.environ.get("URE_INBOX_REPO", "chepin-ai/vci-inbox")
INBOX_ISSUE = int(os.environ.get("URE_INBOX_ISSUE", "1"))
TOKEN = os.environ.get("URE_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
CMD_AUTH = os.environ.get("CMD_AUTH", "")

ROADMAP = "ure/roadmap.json"
CHAIN = "ure/chain.jsonl"
KEEPALIVE = "ure/.keepalive"
GATE = "ure/GATE"

STATES = ["queued", "running", "blocked", "done"]
STATE_LABELS = {s: f"agent/{s}" for s in STATES}
EXTRA_LABELS = ["ure"]


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh(method, path, payload=None, repo=REPO):
    url = f"{API}/repos/{repo}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode() or "{}"
            return r.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return e.code, {"error": body}


def ensure_labels():
    for name in EXTRA_LABELS + [STATE_LABELS[s] for s in STATES]:
        st, _ = gh("POST", "/labels", {"name": name, "color": "0e8a16"})
        if st not in (201, 422):  # 422 = already exists
            print(f"::warning::label {name} create -> {st}")


def set_issue_labels(node):
    labels = EXTRA_LABELS + [STATE_LABELS[node["state"]]]
    st, _ = gh("PUT", f"/issues/{node['issue']}/labels", {"labels": labels})
    if st >= 300:
        print(f"::warning::set labels issue#{node['issue']} -> {st}")


def comment(issue_number, body, repo=REPO):
    st, _ = gh("POST", f"/issues/{issue_number}/comments", {"body": body}, repo=repo)
    if st >= 300:
        print(f"::warning::comment -> {st}")
    return st


def ensure_issues(roadmap):
    """Task-board projection: one issue per node. Idempotent via stored number."""
    for n in roadmap["nodes"]:
        if n.get("issue"):
            continue
        title = f"[URE-00] {n['id']}: {n['title']}"
        body = (f"Research-DAG node `{n['id']}` (URE-00 v0.1, dry-run).\n\n"
                f"- state: `{n['state']}`\n- score: `{n.get('score', 0)}`\n\n"
                f"Managed by ure-sweeper; label state machine "
                f"agent/queued -> agent/running -> agent/blocked -> agent/done.")
        st, resp = gh("POST", "/issues", {"title": title, "body": body,
                                          "labels": EXTRA_LABELS + [STATE_LABELS[n["state"]]]})
        if st >= 300:
            print(f"::error::create issue for {n['id']} -> {st} {resp}")
            sys.exit(1)
        n["issue"] = resp["number"]
        print(f"created issue #{resp['number']} for {n['id']}")


def chain_tail():
    if not os.path.exists(CHAIN):
        return 0, "0" * 64
    last = None
    with open(CHAIN) as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    if last is None:
        return 0, "0" * 64
    return last["seq"], last["hash"]


def append_chain(action, node_id, score, state, ts):
    if not CMD_AUTH:
        print("::error::CMD_AUTH secret missing; refusing to append chain")
        sys.exit(1)
    prev_seq, prev_hash = chain_tail()
    entry = {"seq": prev_seq + 1, "ts": ts, "node": node_id, "action": action,
             "score": score, "state": state, "prev": prev_hash}
    digest = hashlib.sha256(json.dumps(entry, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
    entry["hash"] = digest
    entry["hmac"] = hmac_mod.new(CMD_AUTH.encode(), digest.encode(),
                                 hashlib.sha256).hexdigest()
    with open(CHAIN, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"chain seq={entry['seq']} action={action} node={node_id}")
    return entry["seq"]


def save_roadmap(roadmap):
    with open(ROADMAP, "w") as f:
        json.dump(roadmap, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    ts = utcnow()
    if not TOKEN:
        print("::error::URE_TOKEN/GITHUB_TOKEN missing")
        sys.exit(1)
    with open(ROADMAP) as f:
        roadmap = json.load(f)
    budget = roadmap.get("budget", {})
    delta = float(budget.get("tick_score_delta", 0.1))
    threshold = float(budget.get("done_threshold", 0.8))

    # --- human gate: read-only mode -------------------------------------
    if os.path.exists(GATE):
        notice = (f"[URE-00] {ts} human-gate active (`ure/GATE` present); "
                  f"sweeper is read-only this tick. Remove `ure/GATE` to resume.")
        target = next((n["issue"] for n in roadmap["nodes"] if n.get("issue")), None)
        if target:
            comment(target, notice)
        else:
            comment(INBOX_ISSUE, notice, repo=INBOX_REPO)
        print("human-gate active; read-only tick, no writes")
        return

    ensure_labels()
    ensure_issues(roadmap)

    # --- pick active node: continue running, else promote first queued ---
    active = next((n for n in roadmap["nodes"] if n["state"] == "running"), None)
    promoted = False
    if active is None:
        active = next((n for n in roadmap["nodes"] if n["state"] == "queued"), None)
        if active is not None:
            active["state"] = "running"
            promoted = True
            set_issue_labels(active)

    if active is None:
        seq = append_chain("idle", None, None, None, ts)
    else:
        active["score"] = round(float(active.get("score", 0)) + delta, 6)
        heartbeat = (f"[URE-00] heartbeat {ts} — node `{active['id']}` "
                     f"state=`{active['state']}` score=`{active['score']}` "
                     f"(dry-run, no LLM){' [promoted queued->running]' if promoted else ''}")
        comment(active["issue"], heartbeat)
        if active["score"] >= threshold:
            active["state"] = "done"
            set_issue_labels(active)
            comment(active["issue"],
                    f"[URE-00] {ts} node `{active['id']}` DONE "
                    f"(score={active['score']} >= {threshold}).")
            if not active.get("returned"):
                stamp = (f"[URE-00] RETURN stamp {ts} — node `{active['id']}` "
                         f"completed in {REPO} issue #{active['issue']} "
                         f"(score={active['score']}, dry-run skeleton U0).")
                comment(INBOX_ISSUE, stamp, repo=INBOX_REPO)
                active["returned"] = True
            if active["id"] in roadmap.get("frontier", []):
                roadmap["frontier"].remove(active["id"])
        seq = append_chain("tick", active["id"], active["score"], active["state"], ts)

    roadmap["last_session_anchor"] = {"ts": ts, "chain_seq": seq}
    save_roadmap(roadmap)
    with open(KEEPALIVE, "w") as f:
        f.write(ts + "\n")
    print(f"tick complete at {ts}")


if __name__ == "__main__":
    main()
