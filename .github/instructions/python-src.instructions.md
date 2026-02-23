---
applyTo: "scripts/**/*.py"
---

# Python Scripts — Scoped Instructions

These rules apply to ALL files under `scripts/`. They supplement `omni-prompt.md` Script
Standards. If this file and `omni-prompt.md` conflict, `omni-prompt.md` governs.

---

## Module Structure

- Every script file MUST have a module-level docstring describing: Purpose, Inputs, Outputs,
  Requirements, and a `Run example:` showing how to use it.
- All public functions MUST have docstrings with `Args:`, `Returns:`, and `Raises:` sections.
- Use type hints on all function signatures (Python 3.11+).
- Import order: stdlib → third-party → local (separated by blank lines).

## File Placement

- Python scripts → `scripts/python/<category>/`
- Never place scripts at the repo root or bare `scripts/` folder.
- Category examples: `compression/`, `file-management/`, `text-processing/`

## Error Handling Contract

Every function that interacts with the filesystem, subprocesses, or external tools MUST:

- Validate inputs BEFORE taking any action.
- Raise typed exceptions:
  - `FileNotFoundError` — required file or executable not found
  - `NotADirectoryError` — expected directory but got file
  - `ValueError` — parameter value is invalid (empty string, out of range, wrong type)
  - `PermissionError` — OS denied access
  - `subprocess.TimeoutExpired` — external process exceeded timeout
- NEVER use bare `except:` or `except Exception:` without re-raising or logging.
- NEVER swallow exceptions silently.

## Subprocess Rules

Every `subprocess.run()` or `subprocess.Popen()` call MUST include:

- `timeout=` parameter (use a named constant, e.g. `SUBPROCESS_TIMEOUT = 3600`)
- `check=True` OR explicit returncode handling — never ignore the return code
- Captured stderr for error diagnosis

## GUI Code

If the script includes a `tkinter` GUI:

- All GUI operations MUST run on the main thread.
- Background tasks MUST use `threading.Thread` with thread-safe UI update methods.
- Define thread-safe helpers (`_ui_set_status`, `_ui_log`, etc.) that use `self.after()`.
- Never call `tkinter` widget methods from a non-main thread.

## Before Writing Any Script

1. Confirm the Design Gate has been approved (see `manage-project.prompt.md`).
2. Write the test file `tests/<category>/test_<script_name>.py` first.
3. Run the test — it MUST fail (red phase) before you write any implementation.
4. Implement the script to make the tests pass.
5. Run `pytest tests/ -q` — full suite, not just the new tests.

## Naming Conventions

- Script files: `snake_case.py`
- Function names: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Classes: `PascalCase`

## Self-Check Before Committing

Read back the script file from disk. Confirm:

- [ ] Module-level docstring is present and accurate
- [ ] All public functions have type hints and docstrings
- [ ] No bare `except:` clauses
- [ ] All subprocess calls have `timeout=`
- [ ] Input validation precedes all filesystem or subprocess operations
