---
name: "test-doc-align"
description: "Verify tests, docs, and code are all aligned — fix any drift"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.

## Task

Perform a **Test-Doc-Code alignment check** across the entire repo and fix any drift.

## Checks to Perform

### 1 — Code vs Tests

For every function/class in `scripts/`:

- Does a test exist in `tests/` that covers it?
- Do the test parameters match the current function signature?
- Do the test assertions match the current return types?
- Flag: MISSING TEST | STALE TEST | SIGNATURE MISMATCH

### 2 — Code vs Docs

For every script in `scripts/`:

- Does `docs/utility-helper-scripts.md` have a section for it?
- Does the documented parameter list match the current function signature?
- Does the documented "Run" example still work?
- Flag: MISSING DOC | STALE DOC | BROKEN EXAMPLE

### 3 — Docs vs CHANGELOG

- Is every significant code change recorded in `CHANGELOG.md`?
- Flag: MISSING ENTRY

## Output Format

```
ALIGNMENT REPORT — <date>
========================
PASS ✓  <item>
FAIL ✗  <item> — <reason> — <fix applied>
```

## Fix Order

1. Update tests to match current signatures (run them first to confirm they were broken).
2. Update docs to match current behavior.
3. Update CHANGELOG if missing entries found.
4. Commit: `docs(align): sync tests and docs to current code — <summary>`.
5. Push.

## Refusal Condition

If a function's behavior is ambiguous (docs say one thing, code does another), STOP and report — do not guess which is correct.
