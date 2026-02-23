---
name: "commit-push"
description: "Run pre-push health checks, then commit and push all staged changes"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` and `ERROR_LOG.md` before proceeding.

## Pre-Push Health Checklist

Run each check. If any FAILS, fix it before committing.

### 1 — Tests green

```bash
pytest tests/ -q
```

Expected: `X passed, 0 failed`.
If failures → fix them first. Do NOT push broken tests.

### 2 — No bare except clauses

```bash
grep -rn "except:" scripts/ tests/
```

Expected: no output. If found → fix to use typed exceptions.

### 3 — No subprocess without timeout

```bash
grep -rn "subprocess.run\|subprocess.call\|subprocess.check" scripts/ | grep -v "timeout"
```

Expected: no output.

### 4 — Docs aligned

Confirm `docs/utility-helper-scripts.md` reflects all changes in this commit.

### 5 — CHANGELOG updated

Confirm `CHANGELOG.md` has an entry for this change under `[Unreleased]`.

### 6 — ERROR_LOG reviewed

Confirm `ERROR_LOG.md` has no unresolved issues related to this change.

## Commit & Push

```bash
git add .
git commit -m "<type>(<scope>): <description>"
git push
```

Commit type guide:

- `feat` — new script or feature
- `fix` — bug fix
- `test` — test-only change
- `docs` — documentation only
- `refactor` — code restructure, no behavior change
- `chore` — maintenance (requirements, config, agent files)

## Refusal Condition

If tests fail and you cannot fix the root cause — STOP and report the failure. Do NOT push.
