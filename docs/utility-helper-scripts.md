# utility-helper-scripts — Script Documentation

<!-- Single source of truth for all scripts. Update this file whenever a script changes. -->
<!-- Last updated: 2026-02-23 -->

## Table of Contents


1. [Compress Folders Filtered](#compress-folders-filtered)


---

## Compress Folders Filtered




**File:** `scripts/compress_folders_filtered.py`**Original file:** `compress-folders-filtered.py` (root, kept for reference)**Type:** Tkinter GUI application**Status:** Active — v1.1.0

### Purpose

Create individual `.7z` archives for each immediate subfolder under a chosen parent directory.
Designed for developers who want to back up multiple project/repo folders in a single GUI operation.

### Inputs (via GUI)

| Field | Required | Default | Description |
|----|----|----|----|
| Repos parent folder | Yes | — | The directory whose *immediate subdirectories* will each be archived |
| Output folder | Yes | — | Where `.7z` files are written (created if missing) |
| 7z.exe path | No | auto-detect | Leave blank; script searches PATH and `%ProgramFiles%\7-Zip\7z.exe` |
| Dictionary size | No | `256m` | LZMA2 `-md` setting. Larger = better compression, more RAM |
| Threads | No | `on` | 7-Zip `-mmt` setting. `on` = auto-detect CPU count |
| Solid archive | No | ✓ checked | `-ms=on` gives better ratio for many small files |
| Exclude .git | No | ✓ checked | Omit `.git` directory (smaller archive; repo history NOT preserved) |

### Outputs

* One `<subfolder_name>.7z` per immediate subdirectory of the selected parent folder.
* Archives use: `7z + LZMA2 + Ultra (-mx=9) + solid mode + multithreaded`.

### Excluded by default


**Directories:** `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `node_modules`, `dist`, `build`, `out`, `target`, `.next`, `.nuxt`, `.cache`, `.tox`, `.eggs`, `.idea`, `.vscode` (and optionally `.git`).**File patterns:** `*.pyc`, `*.pyo`, `*.log`, `*.tmp`, `*.temp`, `*.obj`, `*.o`, `*.class`.

### Requirements

* Python 3.11+ (Tkinter included in standard CPython)
* [7-Zip](https://7-zip.org) installed — or `7z`/`7za`/`7zr` on PATH

### Run

```bash
python scripts/compress_folders_filtered.py
```

### Testable Functions

| Function | Description |
|----|----|
| `find_7z(explicit_path)` | Locate 7-Zip executable (PATH → Windows default) |
| `build_7z_command(...)` | Build the `subprocess` command list for one archive operation |
| `list_repo_subfolders(parent)` | Return sorted list of immediate subdirectories |
| `run_archive(cmd, timeout)` | Execute the 7-Zip command and return `(returncode, stdout, stderr)` |

### Error Handling

| Scenario | Behavior |
|----|----|
| 7-Zip not found | `FileNotFoundError` raised; GUI shows error dialog |
| Invalid explicit 7z path | `ValueError` raised; GUI shows error dialog |
| Repos folder not a directory | `FileNotFoundError` raised; GUI shows error dialog |
| Subfolder disappears mid-run | Skipped with log message; continues to next folder |
| 7-Zip process times out (>3600s) | `subprocess.TimeoutExpired`; logged; continues to next folder |
| Permission denied | `PermissionError`; logged; continues to next folder |
| 7-Zip non-zero exit code | Logged with stdout/stderr details; continues to next folder |

### Version History

| Version | Date | Change |
|----|----|----|
| 1.1.0 | 2026-02-23 | Added `run_archive()`, `list_repo_subfolders()`, typed exceptions, subprocess timeout, archive size reporting, improved error handling per omni-prompt charter |
| 1.0.0 | 2026-02-23 | Initial version — functional GUI with 7-Zip compression |


