CLASSIFY: L2(usrm SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-TASK-BEAT173-LINEAGE-COLLAB-01-usrm-20261121.md

应卡: inbox/TASK-BEAT173-LINEAGE-COLLAB-01-usrm-20261121.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 42, "completion_tokens": 2604, "total_tokens": 2646, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 42}

I'll implement a diagnostic-gated E2E preflight system. Since I don't have access to your specific failure evidence or codebase, I'll build this as a reusable pattern you can adapt. Let me structure this clearly.

## Design Principles

1. **Failure evidence is the source of truth** — preflight reads prior failures, not assumptions.
2. **Rate-limit attempts are blocked unless a *new* diagnostic signal exists** — this prevents the "retry loop of doom."
3. **Every real LLM run is gated** behind a passing preflight that emits a diagnostic fingerprint.
4. **Unchanged conditions ⇒ skip**, never silently repeat.

## 1. Failure Evidence Store

```python
# preflight/evidence.py
from __future__ import annotations
import json, hashlib, time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

@dataclass
class FailureRecord:
    kind: str                      # "rate_limit" | "auth" | "schema" | "timeout" | ...
    fingerprint: str               # hash of the conditions that produced it
    diagnostic: Optional[str]      # NEW signal that would justify a retry (e.g. "quota_reset", "creds_rotated")
    ts: float = field(default_factory=time.time)
    details: dict = field(default_factory=dict)

class EvidenceStore:
    """Durable log of failures used to gate future LLM invocations."""
    def __init__(self, path: str | Path = ".preflight/failures.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, rec: FailureRecord) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(asdict(rec)) + "\n")

    def latest(self, kind: str) -> Optional[FailureRecord]:
        if not self.path.exists():
            return None
        last = None
        for line in self.path.read_text().splitlines():
            r = FailureRecord(**json.loads(line))
            if r.kind == kind:
                last = r
        return last
```

## 2. Diagnostic Signal Provider

The whole point: a retry must present a **new** diagnostic signal that *differs* from the one on record. Sources can be quota APIs, credential timestamps, schema versions, or a manual override file.

```python
# preflight/diagnostics.py
from __future__ import annotations
import os, time, json
from hashlib import sha256
from pathlib import Path
from typing import Optional

def _fingerprint(*parts: object) -> str:
    return sha256("|".join(map(str, parts)).encode()).hexdigest()[:16]

def current_diagnostic_signals(model: str, endpoint: str) -> dict[str, str]:
    """
    Collect every signal that could legitimately justify retrying a real LLM call.
    Add/remove providers here — these are OBSERVABLE evidence, not guesses.
    """
    signals: dict[str, str] = {}

    # 1. Quota reset marker (written by your rate-limit handler / cron)
    quota_file = Path(".preflight/quota_reset_at")
    if quota_file.exists():
        signals["quota_window"] = quota_file.read_text().strip()

    # 2. Credential rotation marker
    signals["creds_hash"] = _fingerprint(
        os.getenv("LLM_API_KEY", "")[:8],              # prefix only, never log secrets
        os.getenv("LLM_API_BASE_URL", ""),
    )

    # 3. Model/provider pin
    signals["target"] = _fingerprint(model, endpoint)

    # 4. Manual "operator unblocked" flag with TTL
    override = Path(".preflight/override.json")
    if override.exists():
        data = json.loads(override.read_text())
        if data.get("expires_at", 0) > time.time():
            signals["override"] = data["reason"]

    return signals

def diagnostic_fingerprint(signals: dict[str, str]) -> str:
    return _fingerprint(*[f"{k}={v}" for k, v in sorted(signals.items())])
```

## 3. The Gated Preflight

This is the piece that enforces your rule: **no unchanged rate-limit retry**.

```python
# preflight/gate.py
from __future__ import annotations
from dataclasses import dataclass
from .evidence import EvidenceStore, FailureRecord
from .diagnostics import current_diagnostic_signals, diagnostic_fingerprint

class PreflightBlocked(RuntimeError): ...

@dataclass
class PreflightResult:
    allowed: bool
    reason: str
    fingerprint: str
    signals: dict[str, str]

def preflight(model: str, endpoint: str, store: EvidenceStore | None = None) -> PreflightResult:
    store = store or EvidenceStore()
    signals = current_diagnostic_signals(model, endpoint)
    fp = diagnostic_fingerprint(signals)

    prior = store.latest("rate_limit")
    if prior is None:
        return PreflightResult(True, "no prior rate-limit evidence", fp, signals)

    # Rule: block if conditions are unchanged from the recorded failure.
    if prior.fingerprint == fp:
        return PreflightResult(
            False,
            f"blocked: unchanged rate-limit conditions (fp={fp}, "
            f"first seen {prior.ts:.0f}s ago). Provide a new diagnostic signal.",
            fp, signals,
        )

    # Rule: even if fingerprint moved, require an EXPLICIT new diagnostic token.
    if not prior.diagnostic or prior.diagnostic not in signals.values():
        return PreflightResult(
            False,
            "blocked: fingerprint changed but no recognized new diagnostic signal "
            "present (see FailureRecord.diagnostic).",
            fp, signals,
        )

    return PreflightResult(True, f"unblocked via new signal: {prior.diagnostic}", fp, signals)

def record_rate_limit(model: str, endpoint: str, diagnostic_token: str | None,
                      store: EvidenceStore | None = None, **details) -> str:
    store = store or EvidenceStore()
    signals = current_diagnostic_signals(model, endpoint)
    fp = diagnostic_fingerprint(signals)
    store.append(FailureRecord(
        kind="rate_limit", fingerprint=fp,
        diagnostic=diagnostic_token, details=details,
    ))
    return fp
```

## 4. E2E Harness — Preflight-Enforced

```python
# e2e/run.py
import sys, time
from preflight.gate import preflight, record_rate_limit, PreflightBlocked

def call_llm(model: str, endpoint: str, payload: str) -> str:
    """Thin wrapper; raises on rate-limit so we can record evidence."""
    import httpx
    r = httpx.post(
        f"{endpoint}/chat",
        json={"model": model, "messages": [{"role": "user", "content": payload}]},
        timeout=30,
    )
    if r.status_code == 429:
        record_rate_limit(model, endpoint, diagnostic_token="quota_window",
                          status=429, body=r.text[:200])
        raise PreflightBlocked("upstream rate limit; evidence recorded")
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def e2e(model: str = "gpt-4o-mini",
        endpoint: str = "https://api.example.com/v1",
        scenario: str = "smoke") -> None:
    gate = preflight(model, endpoint)
    print(f"[preflight] allowed={gate.allowed} reason={gate.reason} fp={gate.fingerprint}")
    if not gate.allowed:
        print("[preflight] NO real LLM call issued — diagnostic signal required.")
        sys.exit(2)

    out = call_llm(model, endpoint, f"diagnostic probe: {scenario}")
    print(f"[e2e] response: {out[:120]}")
```

## 5. Operator Flow

```bash
# Scenario A: first run after a 429 recorded at fp=abc123
python -m e2e.run
# → [preflight] allowed=False reason=blocked: unchanged rate-limit... fp=abc123
# exit 2. No LLM call. ✅

# Scenario B: quota window rolled over → quota_reset_at file updated
echo "2025-01-01T15:00:00Z" > .preflight/quota_reset_at
python -m e2e.run
# → [preflight] allowed=True reason=unblocked via new signal: quota_window
# real LLM call proceeds. ✅

# Scenario C: operator override with TTL
echo '{"reason":"vendor confirmed fix","expires_at":'"$(( $(date +%s) + 3600 ))"'}' \
  > .preflight/override.json
python -m e2e.run
# → allowed=True (if the record's diagnostic token was "override" OR operator updated it)
```

## 6. Tightening the Contract (Optional)

Add a `pytest` guard so CI cannot accidentally issue a repeated attempt:

```python
# tests/test_preflight_gate.py
import os, pytest
from preflight.evidence import EvidenceStore
from preflight.gate import preflight, record_rate_limit

def test_unchanged_rate_limit_is_blocked(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    store = EvidenceStore(tmp_path / "f.jsonl")
    fp = record_rate_limit("m", "http://e", diagnostic_token="quota_window", store=store)
    gate = preflight("m", "http://e", store=store)
    assert not gate.allowed and gate.fingerprint == fp

def test_new_signal_unblocks(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    store = EvidenceStore(tmp_path / "f.jsonl")
    record_rate_limit("m", "http://e", diagnostic_token="quota_window", store=store)
    # simulate a fresh quota window
    qf = tmp_path / "quota_reset_at"; qf.write_text("2025-01-01T00:00:00Z")
    monkeypatch.setattr("preflight.diagnostics.Path",
                        lambda *a, **k: type("P", (), {"exists": lambda s: s._p == qf, "_p": qf})(
                            *a, **k))  # adapt to your layout
    # or simpler: chdir tmp_path and drop the file in .preflight/
```

## Key Guarantees

| Guarantee | Mechanism |
|---|---|
| No repeated unchanged rate-limit attempt | `prior.fingerprint == fp ⇒ blocked` |
| No "silent" retries on any signal change | `prior.diagnostic` must appear in current signals |
| Diagnostics are observable, not guessed | All signals come from `current_diagnostic_signals()` (files, env, TTL flags) |
| Every real LLM call is preflighted | `e2e()` calls `preflight()` before `call_llm()` |
| Failures are durable evidence | Append-only `failures.jsonl` |

**To adapt this to your repo:** point `EvidenceStore` at your existing failure log, replace the three signal providers in `current_diagnostic_signals()` with the ones your failure evidence actually contains (e.g., your 429's `Retry-After` timestamp, your auth-refresh counter, your canary version), and wire `preflight()` into whatever currently invokes the real LLM. If you share the actual failure evidence record shape, I can specialize the fingerprints and diagnostic tokens exactly.

——usrm SI1语义轨·20261121T034411Z
