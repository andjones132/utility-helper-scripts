---
name: "run-test-suite"
description: "Run the full test suite and report results with failure analysis"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

## Task
Run the full test suite for the get-chat-GPT project and produce a structured report.

## Steps

### 1. Pre-flight
- Confirm `requirements.txt` and `requirements-dev.txt` are installed.
- Confirm `.env` or `OPENAI_API_KEY` is set (or that all tests mock the API correctly).

### 2. Execute
```bash
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

### 3. Report Structure
For EACH test module, report:
- **Module:** `tests/test_<name>.py`
- **Passed:** N
- **Failed:** N (list each failed test with error summary)
- **Skipped:** N (list reason)
- **Coverage:** % for corresponding `src/<name>.py`

### 4. On Failure
For each failure:
1. Identify root cause (cite the exact line in `src/` that failed).
2. Propose the minimal fix.
3. If the fix risks a breaking change, STOP and report it — do not auto-fix.
4. If the failure matches a known issue, cite the entry in `docs/ERROR_LOG.md`.

### 5. After All Fixes Pass
```bash
git add -A
git commit -m "test: fix failing tests in <module>"
git push
```

## Refusal
If a fix would require deleting a test or changing its intent, STOP and ask the user.
