#!/usr/bin/env python3
"""One-shot migration of ure/chain.jsonl to the unified v2 format (AUDIT-01 P1-2).

Two chain algorithms historically coexisted:
  v1 (legacy ure_tick.py): entries carried node/action/state/hmac fields and
                           the hash was authenticated with HMAC(CMD_AUTH, ...).
  v2 (pareto_tick.py):     {seq, ts, arm, pi, score, prev, hash} with
                           hash = sha256(prev + canon(entry)).

This script rewrites every legacy entry into the v2 schema (arm := node,
pi := null where absent, keeping the original ts/arm/score/pi values),
relinks the whole prev chain from the genesis hash, and recomputes every
hash with the v2 rule. A format header comment line is written first:
  # v2: hash=sha256(prev+canon)

Usage:
  python3 scripts/chain_migrate.py           # migrate in place (idempotent)
  python3 scripts/chain_migrate.py --check   # verify only, no writes
"""
import hashlib
import json
import sys

CHAIN = "ure/chain.jsonl"
GENESIS = "0" * 64
HEADER = "# v2: hash=sha256(prev+canon)"

V2_FIELDS = ("seq", "ts", "arm", "pi", "score", "prev", "hash")


def canon(obj):
    """Canonical JSON, identical to pareto_tick.canon."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def v2_hash(entry):
    """sha256(prev + canon(entry-without-hash)), identical to pareto_tick."""
    payload = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256((entry["prev"] + canon(payload)).encode()).hexdigest()


def normalize(entry):
    """Project any historical entry onto the v2 schema (prev/hash excluded)."""
    return {
        "seq": entry.get("seq"),
        "ts": entry.get("ts"),
        "arm": entry.get("arm", entry.get("node")),
        "pi": entry.get("pi"),
        "score": entry.get("score"),
    }


def load_entries(path):
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.append(json.loads(line))
    return entries


def relink(entries):
    """Return v2 entries with the whole prev chain + hashes recomputed."""
    out, prev = [], GENESIS
    for raw in entries:
        e = normalize(raw)
        e["prev"] = prev
        e["hash"] = v2_hash(e)
        prev = e["hash"]
        out.append(e)
    return out


def check(entries):
    """Verify v2 schema + chain integrity; returns list of problems."""
    problems = []
    prev = GENESIS
    for i, e in enumerate(entries, 1):
        extra = set(e) - set(V2_FIELDS)
        if extra:
            problems.append(f"seq {e.get('seq')}: legacy fields {sorted(extra)}")
        if e.get("prev") != prev:
            problems.append(f"entry {i}: prev mismatch (broken link)")
        if e.get("hash") != v2_hash(e):
            problems.append(f"entry {i}: hash mismatch (wrong algorithm or tamper)")
        prev = e.get("hash", prev)
    return problems


def main():
    check_only = "--check" in sys.argv
    entries = load_entries(CHAIN)
    if check_only:
        problems = check(entries)
        if problems:
            print("chain check FAIL:")
            for p in problems:
                print(" -", p)
            return 1
        print(f"chain check PASS ({len(entries)} entries, v2 sha256(prev+canon))")
        return 0

    migrated = relink(entries)
    changed = migrated != entries
    with open(CHAIN, "w") as f:
        f.write(HEADER + "\n")
        for e in migrated:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    problems = check(load_entries(CHAIN))
    if problems:
        print("migration verification FAIL:")
        for p in problems:
            print(" -", p)
        return 1
    print(f"migrated {len(migrated)} entries to v2 "
          f"({'rewritten' if changed else 'already v2; relinked/verified'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
