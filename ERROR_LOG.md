# Error Log

**Purpose:** Document every significant bug, error, or misconfiguration encountered during development.  
**Policy:** Review this file at the start of every session and before every `git push`.  
Agents MUST read this file and avoid repeating documented mistakes.

---

## Format

```
### ERROR-NNNN — <Short Title>
**Date:** YYYY-MM-DD
**Symptom:** What the user/agent observed.
**Root Cause:** Why it happened.
**Fix Applied:** What was done to resolve it.
**Prevention:** How to avoid this in the future.
**Status:** Resolved | Open
```

---

## Log

### ERROR-0001 — subprocess.run() missing timeout parameter

**Date:** 2026-02-23  
**Symptom:** A very large repo folder caused the GUI to appear to hang indefinitely with no way to detect or recover from a stalled 7-Zip process.  
**Root Cause:** All `subprocess.run()` calls in `_run_archives` lacked a `timeout=` argument. A subprocess that hangs blocks the worker thread silently.  
**Fix Applied:** Extracted subprocess call into `run_archive()` which always passes `timeout=SUBPROCESS_TIMEOUT` (3600s default). Per-archive `TimeoutExpired` is caught and logged; the loop continues to the next folder.  
**Prevention:** All `subprocess.run/call/check_output` calls MUST include `timeout=`. The `/commit-push` prompt checks for this before allowing a push: `grep -rn "subprocess.run" scripts/ | grep -v "timeout"` must return no output.  
**Status:** Resolved

---

### ERROR-0002 — Bare `except:` clause swallowed all errors silently

**Date:** 2026-02-23  
**Symptom:** Errors during archiving (e.g. missing folder, permission denied) were silently ignored; only the 7-Zip exit code was checked after the fact.  
**Root Cause:** Original `_run_archives` method had no exception handling around `build_7z_command()` or `subprocess.run()`. Any exception propagated to the thread boundary and was silently dropped.  
**Fix Applied:** Added per-folder `try/except` with typed exception blocks: `ValueError`, `FileNotFoundError`, `NotADirectoryError`, `subprocess.TimeoutExpired`, `PermissionError`. Each is logged with a descriptive message; the loop continues.  
**Prevention:** Never use bare `except:` or `except Exception:` without logging. Every exception block must log at minimum the exception type and message. The `/commit-push` prompt checks `grep -rn "except:" scripts/` before allowing a push.  
**Status:** Resolved
