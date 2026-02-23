---
name: "audit-retrofit"
description: "Audit this repo against the omni-prompt charter and fix all gaps"
agent: agent
---

You MUST first read `.github/copilot/omni-prompt.md`. If it is missing, create it from scratch using the Anti-Hallucination & Reliability Charter for a Python utility script library.

Then perform an **Audit & Retrofit** of this repo and implement all fixes.

## Goals
1. Every script in `scripts/` has: module docstring, type hints, typed exceptions, input validation, subprocess timeout.
2. Every script has a corresponding `tests/test_<name>.py` with happy path + edge cases + error paths.
3. `docs/utility-helper-scripts.md` is up to date with every script's description, inputs, outputs, and example.
4. `CHANGELOG.md` has entries for all scripts.
5. `requirements.txt` lists all dependencies.
6. `notebooks/utility_helper_scripts.ipynb` has a working TOC cell for every script.
7. No bare `except:` clauses anywhere.
8. No `subprocess.run()` calls without `timeout=`.

## Steps

### 1 — Discovery
- List all files in `scripts/`.
- List all files in `tests/`.
- List all files in `docs/`.
- Diff: which scripts have no test? Which have no docs entry?

### 2 — Diagnosis
- For each gap, propose the minimal code change.
- Flag any script with missing type hints, missing docstring, or missing error handling.

### 3 — Fix & Commit
For each gap found:
1. Write/update the test first (it must fail before fix).
2. Implement the fix.
3. Confirm test passes.
4. Update `docs/utility-helper-scripts.md`.
5. Update `CHANGELOG.md`.
6. Commit: `fix(scope): description`.
7. Push.

## Refusal Condition
If any invariant from the charter cannot be satisfied, STOP and ask one concise question.
