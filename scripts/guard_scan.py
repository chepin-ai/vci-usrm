#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Algorithmic safety guard — I5/I6 enforcement (SPEC-KERNEL-02 invariants).

Two scan planes over the repo HEAD:

  A. Permission surface (.github/workflows/*.yml, PyYAML):
     - G-WF-PERMS-MISSING   : workflow has no top-level permissions block
     - G-WF-CONTENTS-WRITE  : permissions.contents == write without an
                              adjacent comment rationale (# ... within 4 lines
                              above the block or on the same line)
     - G-WF-ISSUES-AUTH     : `on: issues` trigger but no job `if` carrying
                              author_association OWNER/MEMBER (I6 gate)
     - G-WF-PR-TARGET       : pull_request_target trigger (dangerous on a
                              public repo; untrusted head code + secrets)
  B. Full-repo plaintext scan (git ls-files, all text files, not only
     inbox/): pub_lint K7 rule set reused, calibrated for code context:
     - structural session markers (cookie/origin arrays), Bearer tokens,
       ghp_/github_pat_ values            — verbatim pub_lint shapes
     - refresh_token / access_token       — value context required
       (`name: <value>` / `name = <value>`), so API paths and comments do
       not false-positive
     - x-access-token:<inline value>      — `${VAR}` templates are exempt,
       a concrete inline credential is not
     - cn_phone                           — verbatim pub_lint shape, but a
       hit embedded in a >=32-char hex run (sha256 digest) is suppressed
     - inbox/.kimi_session.json.enc must be Fernet-form; a plaintext
       .kimi_session.json file is always a violation
     Inline suppression: `# guard:allow <rule> <reason>` on the same line.

Any violation -> exit 1 and a report at guard/report-YYYY-MM-DD.md with a
file:line:rule table plus pass counts; zero violations -> report says clean.
Iron rule: only file/line/rule names are ever printed or persisted — never
matched content, never secrets, never personal identifiers.
"""
import argparse
import base64
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import yaml

WF_DIR = ".github/workflows"
REPORT_DIR = "guard"
GATE_FILE = "guard/GATE"
JUSTIFY_WINDOW = 4  # comment lines above permissions block counted as rationale
# a rationale comment must say *why* write is needed, not just be any comment
JUSTIFY_KEYWORDS = re.compile(
    r"rationale|理由|commit|push|回写|写回|写入|落盘|入仓|write", re.I)

# Scanner sources necessarily *name* the patterns they enforce; the
# name-literal rules below would self-hit. Value-shaped rules (ghp_,
# Bearer, phone, structural markers) still apply to these files.
SCANNER_FILES = {"scripts/pub_lint.py", "scripts/guard_scan.py"}
SCANNER_EXEMPT_RULES = {"refresh_token", "access_token", "x_access_token_inline"}

CONTENT_RULES = {
    # --- verbatim pub_lint shapes ----------------------------------------
    "plaintext_storage_state": re.compile(rb'"cookies"\s*:\s*\['),
    "localstorage_origins": re.compile(rb'"origins"\s*:\s*\['),
    "bearer_token": re.compile(rb'Bearer\s+[A-Za-z0-9_\-.=]{16,}'),
    "gh_token": re.compile(rb'(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})'),
    "cn_phone": re.compile(rb'(?<!\d)1[3-9]\d{9}(?!\d)'),
    # --- repo-calibrated (value context required) -------------------------
    "refresh_token": re.compile(
        rb'refresh_?token["\']?\s*[:=]\s*["\']?(?!\$)[A-Za-z0-9_\-.]{8,}', re.I),
    "access_token": re.compile(
        rb'access_?token["\']?\s*[:=]\s*["\']?(?!\$)[A-Za-z0-9_\-.]{8,}', re.I),
    "x_access_token_inline": re.compile(
        rb'x-access-token:(?!\$\{?)[A-Za-z0-9_\-.]{8,}'),
}
HEX_RUN = re.compile(rb'[0-9a-fA-F]+')
ENC_SUFFIX = ".kimi_session.json.enc"
PLAIN_SUFFIX = ".kimi_session.json"
ALLOW_MARK = re.compile(r"#\s*guard:allow\s+([A-Za-z0-9_,\-]+)\s*(\S.*)?$")
MAX_FILE_BYTES = 2 * 1024 * 1024


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def norm(p):
    return p.replace(os.sep, "/")


class Violation:
    def __init__(self, plane, path, line, rule):
        self.plane, self.path, self.line, self.rule = plane, path, line, rule

    def row(self):
        return f"| {self.plane} | {self.path} | {self.line} | {self.rule} |"


# ---------------------------------------------------------------------------
# Plane A: workflow permission surface
# ---------------------------------------------------------------------------

def _line_no(lines, pattern, start=0, end=None):
    rx = re.compile(pattern)
    for i in range(start, end if end is not None else len(lines)):
        if rx.search(lines[i]):
            return i + 1
    return 1


def scan_workflow(path):
    """Return (violations, checks_passed_count) for one workflow file."""
    viol, passed = [], 0
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    lines = raw.splitlines()
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError:
        return [Violation("workflow", norm(path), 1, "G-WF-YAML-PARSE")], 0
    if not isinstance(doc, dict):
        return viol, passed
    triggers = doc.get("on", doc.get(True)) or {}  # YAML 1.1: `on` -> True
    if isinstance(triggers, str):
        triggers = {triggers: None}
    if isinstance(triggers, list):
        triggers = {t: None for t in triggers}

    jobs_line = _line_no(lines, r"^jobs:") - 1
    perms = doc.get("permissions")

    # G-WF-PERMS-MISSING
    if perms is None:
        viol.append(Violation("workflow", norm(path), 1, "G-WF-PERMS-MISSING"))
    else:
        passed += 1
        # G-WF-CONTENTS-WRITE (top-level block only: lines before `jobs:`)
        write_ok = True
        if isinstance(perms, dict) and perms.get("contents") == "write":
            write_ok = False
            ln = _line_no(lines, r"^permissions:", end=jobs_line or None)
            # rationale = comment within JUSTIFY_WINDOW lines above the block
            # or on the `contents: write` line itself, containing a keyword
            ctx_lines = lines[max(0, ln - 1 - JUSTIFY_WINDOW):ln - 1]
            ctx_lines += lines[ln:ln + 3]  # contents: write entry line(s)
            for ctx in ctx_lines:
                if "#" in ctx and JUSTIFY_KEYWORDS.search(
                        ctx.split("#", 1)[1]):
                    write_ok = True
                    break
            if not write_ok:
                viol.append(Violation("workflow", norm(path), ln,
                                      "G-WF-CONTENTS-WRITE"))
        if write_ok:
            passed += 1

    # G-WF-ISSUES-AUTH (I6: external issue triggers gated by author_association)
    if "issues" in triggers:
        authed = False
        for job in (doc.get("jobs") or {}).values():
            cond = str((job or {}).get("if", ""))
            if "author_association" in cond and (
                    "OWNER" in cond or "MEMBER" in cond):
                authed = True
                break
        if authed:
            passed += 1
        else:
            ln = _line_no(lines, r"^\s+issues:")
            viol.append(Violation("workflow", norm(path), ln,
                                  "G-WF-ISSUES-AUTH"))

    # G-WF-PR-TARGET (pull_request_target on a public repo)
    if "pull_request_target" in triggers:
        ln = _line_no(lines, r"pull_request_target")
        viol.append(Violation("workflow", norm(path), ln, "G-WF-PR-TARGET"))
    else:
        passed += 1

    return viol, passed


# ---------------------------------------------------------------------------
# Plane B: full-repo plaintext scan (K7/pub_lint rules, repo-calibrated)
# ---------------------------------------------------------------------------

def is_fernet_token(blob):
    tok = blob.strip()
    if not tok.startswith(b"gAAAA"):
        return False
    try:
        base64.urlsafe_b64decode(tok + b"=" * (-len(tok) % 4))
        return True
    except Exception:
        return False


def _allowed(line_text, rule):
    """Inline suppression: `# guard:allow <rule> <reason...>` (reason mandatory)."""
    m = ALLOW_MARK.search(line_text)
    if not m:
        return False
    rules = {r.strip() for r in m.group(1).split(",")}
    return ("all" in rules or rule in rules) and bool(m.group(2))


def scan_content_file(root, path):
    """Return (violations, suppressed_count) for one tracked file."""
    viol, suppressed = [], 0
    rel = norm(path)
    full = os.path.join(root, path)
    if rel.endswith(PLAIN_SUFFIX):
        viol.append(Violation("content", rel, 0, "plaintext_session_file"))
        return viol, suppressed
    try:
        with open(full, "rb") as fh:
            data = fh.read(MAX_FILE_BYTES + 1)
    except OSError:
        return [Violation("content", rel, 0, "unreadable")], suppressed
    if len(data) > MAX_FILE_BYTES or b"\0" in data[:8192]:
        return viol, suppressed  # binary/oversized: out of scan plane
    if rel.endswith(ENC_SUFFIX) and not is_fernet_token(data):
        viol.append(Violation("content", rel, 0, "enc_not_fernet_form"))
    exempt = SCANNER_EXEMPT_RULES if rel in SCANNER_FILES else set()
    for lineno, raw_line in enumerate(data.split(b"\n"), start=1):
        try:
            text = raw_line.decode("utf-8", "replace")
        except Exception:
            text = ""
        for rule, rx in CONTENT_RULES.items():
            if rule in exempt:
                continue
            m = rx.search(raw_line)
            if not m:
                continue
            if rule == "cn_phone":
                # suppress phone-shaped digits inside a >=32-char hex digest
                for hr in HEX_RUN.finditer(raw_line):
                    if hr.start() <= m.start() and hr.end() >= m.end() \
                            and hr.end() - hr.start() >= 32:
                        m = None
                        break
                if m is None:
                    continue
            if _allowed(text, rule):
                suppressed += 1
                continue
            viol.append(Violation("content", rel, lineno, rule))
    return viol, suppressed


def tracked_files(root):
    out = subprocess.run(["git", "ls-files"], cwd=root,
                         capture_output=True, text=True, check=True).stdout
    return [l.strip() for l in out.splitlines() if l.strip()]


# ---------------------------------------------------------------------------
# Report + main
# ---------------------------------------------------------------------------

def write_report(report_dir, date, violations, stats):
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"report-{date}.md")
    lines = [
        f"# guard report {date}",
        "",
        f"- ts: {utcnow()}",
        f"- scope: {stats['workflows']} workflow(s), "
        f"{stats['files']} tracked text file(s) at HEAD",
        f"- result: {'CLEAN' if not violations else f'{len(violations)} violation(s)'}",
        "",
        "## violations (file:line:rule — content never echoed, I5)",
        "",
    ]
    if violations:
        lines += ["| plane | file | line | rule |",
                  "|---|---|---|---|"]
        lines += [v.row() for v in violations]
    else:
        lines.append("clean — zero violations on both scan planes")
    lines += [
        "",
        "## pass counters",
        "",
        f"- workflow checks passed: {stats['wf_passed']}",
        f"- content files clean: {stats['files_clean']}/{stats['files']}",
        f"- inline suppressions (guard:allow, reason mandatory): "
        f"{stats['suppressed']}",
        "",
        "rules: G-WF-PERMS-MISSING / G-WF-CONTENTS-WRITE / G-WF-ISSUES-AUTH "
        "/ G-WF-PR-TARGET + pub_lint K7 set (repo-calibrated). "
        "I5: zero secrets/PII in public repo; I6: external triggers gated "
        "by author_association OWNER/MEMBER.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    ap = argparse.ArgumentParser(description="I5/I6 guard scan")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--report-dir", default=REPORT_DIR)
    ap.add_argument("--no-report", action="store_true",
                    help="print summary only, do not write guard/report-*.md")
    args = ap.parse_args()
    root = args.repo_root

    violations, stats = [], {"workflows": 0, "wf_passed": 0, "files": 0,
                             "files_clean": 0, "suppressed": 0}

    wf_dir = os.path.join(root, WF_DIR)
    if os.path.isdir(wf_dir):
        for name in sorted(os.listdir(wf_dir)):
            if not name.endswith((".yml", ".yaml")):
                continue
            stats["workflows"] += 1
            v, p = scan_workflow(os.path.join(wf_dir, name))
            violations += v
            stats["wf_passed"] += p

    for path in tracked_files(root):
        rel = norm(path)
        if rel.startswith(WF_DIR + "/"):
            continue  # plane A owns workflow files' structure; content still scanned below
        stats["files"] += 1
        v, s = scan_content_file(root, path)
        violations += v
        stats["suppressed"] += s
        if not v:
            stats["files_clean"] += 1
    # workflow files are text too: run content rules on them as well
    if os.path.isdir(wf_dir):
        for name in sorted(os.listdir(wf_dir)):
            if not name.endswith((".yml", ".yaml")):
                continue
            stats["files"] += 1
            v, s = scan_content_file(root, os.path.join(WF_DIR, name))
            violations += v
            stats["suppressed"] += s
            if not v:
                stats["files_clean"] += 1

    for v in violations:
        print(f"VIOLATION {v.plane} {v.path}:{v.line} :: {v.rule}")
    date = utcnow()[:10]
    if not args.no_report:
        rp = write_report(os.path.join(root, args.report_dir), date,
                          violations, stats)
        print(f"guard report written: {norm(rp)}")
    if os.path.exists(os.path.join(root, GATE_FILE)):
        print(f"note: {GATE_FILE} present — report commit must be skipped "
              "(log only)")
    print(f"guard_scan: {stats['workflows']} workflow(s), "
          f"{stats['files']} file(s), {len(violations)} violation(s), "
          f"{stats['suppressed']} suppression(s)")
    if violations:
        print("guard_scan: FAIL (I5/I6)")
        return 1
    print("guard_scan: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
