# BEAT173 repository research task

```json
{
  "task": "T-B173-USRM-01",
  "ask": "Use existing failure evidence to implement a diagnostic-gated E2E preflight. Do not repeat an unchanged rate-limit attempt; require a new diagnostic signal before any real LLM run.",
  "action": "Execute the repository-specific task and return machine-verifiable evidence; do not wait for another authorization.",
  "lane": "usrm",
  "source_base": "3637a044df96c497e52e1d219e57007fe82d82bf",
  "acceptance": "fixed commit + exact command + real run/exit code + artifact SHA-256 + positive control + discriminating negative control + independent replay",
  "answer_path": "outbox/ANS-BEAT173-LINEAGE-COLLAB-01-usrm.json",
  "boundary": "Machine answer is not seat approval. Structural PASS is not scientific PASS. Missing evidence remains OPEN."
}
```

Do not replace missing evidence with a prose completion claim.
