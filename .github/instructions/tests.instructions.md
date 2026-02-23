---
applyTo: "tests/**"
---

# Test Code — Scoped Instructions

These rules apply to ALL files under `tests/`. They supplement `omni-prompt.md` Test First
policy. If this file and `omni-prompt.md` conflict, `omni-prompt.md` governs.

---

## Structure

- `tests/` mirrors `scripts/python/` structure: one `test_<script_name>.py` per script.
- Shared fixtures go in `tests/conftest.py`.
- Test data (sample files, mock responses) go in `tests/fixtures/`.

## Required Test Categories Per Script

Every script must have tests in all three categories:

### Unit Tests
Test a single pure function in complete isolation. All external dependencies mocked.
Class naming: `Test<FunctionName>` (e.g. `TestFindSevenZip`, `TestBuildCommand`).

### Happy Path
The function works correctly with valid, typical inputs.
Function naming: `test_<function>_<condition>_returns_<expected>`.

### Error Path
The function raises the correct typed exception for each documented failure mode.
Function naming: `test_<function>_<bad_condition>_raises_<exception>`.

## Red Phase Is Mandatory

Write the test. Run it. **It MUST fail before you write any implementation.**

```
test: run before implementation — confirms <what fails and why>
```

A test that passes on first run before implementation exists is a broken test. Stop and fix it.

## Test Writing Rules

- Test function names MUST be descriptive: `test_<what>_<condition>_<expected_outcome>`.
- Each test has ONE assertion focus — do not test 5 behaviors in one test function.
- Use `pytest.fixture` for reusable setup; never repeat setup manually in each test.
- Do NOT use `unittest.TestCase` — use plain `pytest` functions and classes.
- Parametrize boundary-condition tests with `@pytest.mark.parametrize`.
- Use `tmp_path` (pytest builtin) for any test that creates files.
- Use `monkeypatch` for environment variables and PATH manipulation.
- Use `unittest.mock.patch` + `MagicMock` for subprocess and external tool mocking.

## Required Edge Cases Per Script Type

| Script Type | Required Edge Cases |
| ----------- | ------------------- |
| File system scripts | Missing directory, file where directory expected, permission denied, empty directory |
| Subprocess scripts | Executable not found, process timeout, non-zero exit code, stderr output |
| GUI scripts | Test only the pure non-GUI functions; tk classes are excluded from unit tests |

## Test Execution

Always run the **full suite** — never selective:

```bash
pytest tests/ -q
```

A failing test is a hard STOP. Do not commit. Do not continue to the next task.

If a test must be deleted or materially changed (not just updated for new behavior):
**STOP and ask the user.** Do not delete tests without explicit approval.

## Full Suite Rule

**There is no approved short-circuit.** Even if only one function changed, run `pytest tests/ -q`
in full. Cross-function regressions are real and the suite is fast.

## Imports

Test files import from scripts using the path-injection pattern:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "python" / "<category>"))
from <script_name> import <function>, <function>
```
