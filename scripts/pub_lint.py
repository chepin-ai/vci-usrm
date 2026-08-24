#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""K7 公仓明文闸：扫描待 commit 的 inbox/**，命中明文 session/token/手机号即 exit 1。
用法：
  python3 scripts/pub_lint.py --staged     # 扫 git staged 的 inbox/**（workflow push 前闸，主用例）
  python3 scripts/pub_lint.py --all        # 扫工作区 inbox/** 现存全部文件
  python3 scripts/pub_lint.py <path...>    # 扫指定文件
合法例外：inbox/.kimi_session.json.enc（Fernet 密文，须 gAAAA 形态且全文零明文命中）。
铁律：只打印文件名与规则名，绝不打印命中内容（日志零密钥零标识零明文态）。"""
import base64, os, re, subprocess, sys

RULES = {
    "plaintext_storage_state": re.compile(rb'"cookies"\s*:\s*\['),
    "localstorage_origins": re.compile(rb'"origins"\s*:\s*\['),
    "refresh_token": re.compile(rb'refresh_?token', re.I),
    "access_token": re.compile(rb'access_?token', re.I),
    "bearer_token": re.compile(rb'Bearer\s+[A-Za-z0-9_\-.=]{16,}'),
    "gh_token": re.compile(rb'(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|x-access-token)'),
    "cn_phone": re.compile(rb'(?<!\d)1[3-9]\d{9}(?!\d)'),
}
ENC_SUFFIX = ".kimi_session.json.enc"
PLAIN_SUFFIX = ".kimi_session.json"


def _norm(p):
    return p.replace(os.sep, "/")


def is_fernet_token(blob):
    tok = blob.strip()
    if not tok.startswith(b"gAAAA"):
        return False
    try:
        base64.urlsafe_b64decode(tok + b"=" * (-len(tok) % 4))
        return True
    except Exception:
        return False


def scan_file(path):
    """返回命中规则名列表；空列表 = 放行。"""
    norm = _norm(path)
    if norm.endswith(ENC_SUFFIX):
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError:
            return ["unreadable"]
        if not is_fernet_token(data):
            return ["enc_not_fernet_form"]
        return [name for name, rx in RULES.items() if rx.search(data)]  # 伪密文检测
    if norm.endswith(PLAIN_SUFFIX):
        return ["plaintext_session_file"]  # 明文会话态永不许入仓（无视内容）
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return ["unreadable"]
    return [name for name, rx in RULES.items() if rx.search(data)]


def staged_inbox_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM", "--", "inbox/"],
        capture_output=True, text=True, check=True).stdout
    return [l.strip() for l in out.splitlines() if l.strip()]


def all_inbox_files():
    out = subprocess.run(
        ["git", "ls-files", "--", "inbox/"], capture_output=True, text=True, check=True).stdout
    tracked = [l.strip() for l in out.splitlines() if l.strip()]
    extra = []
    for root, _dirs, files in os.walk("inbox"):
        for f in files:
            p = _norm(os.path.join(root, f))
            if p not in tracked:
                extra.append(p)
    return tracked + extra


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--staged":
        files = staged_inbox_files()
    elif args[0] == "--all":
        files = all_inbox_files()
    else:
        files = args
    bad = 0
    for p in files:
        hits = scan_file(p)
        if hits:
            bad += 1
            print(f"BLOCK {p} :: {','.join(hits)}")
        else:
            print(f"PASS  {p}")
    if bad:
        print(f"pub_lint: {bad} file(s) hit plaintext rules —— 拒绝入仓（I5/K7）")
        sys.exit(1)
    print(f"pub_lint: {len(files)} file(s) clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
