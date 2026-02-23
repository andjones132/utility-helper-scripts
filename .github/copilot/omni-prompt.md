UBER OMNI PROMPT — Anti-Hallucination & Reliability Charter

# Repo: utility-helper-scripts | Mode: BALANCED | Version: 1.0.0 | Updated: 2026-02-23

## Purpose

This file is the **governing constitution** for every Copilot agent working in this repo.
It supersedes any other instruction when there is a conflict.
Update this file whenever you learn something that future agents must know.

## Core Principles

1. **Accuracy > Completeness.** Never fabricate module names, parameters, behaviors, or Python APIs. If uncertain, stop and ask.
2. **Test First.** Write the failing test before writing any implementation code.
3. **Document First.** Update `docs/utility-helper-scripts.md` before (or simultaneously with) writing or changing code.
4. **No Silent Guessing.** If a Python stdlib function, third-party module, or OS behavior is not known with certainty — verify it in a code cell or ask the user.
5. **Provenance.** Every claim in documentation must cite its source (e.g., "Python 3.11 docs", "subprocess.run() signature", direct test observation).
6. **Self-Documenting Agent.** When you learn something new (a bug, a pattern, a constraint), update `copilot-instructions.md`, `omni-prompt.md`, and/or `ERROR_LOG.md` immediately.
7. **Structure First.** Before writing any new code or documentation, verify the file belongs in the correct folder. A clean, predictable structure is not optional — it is a first-class deliverable alongside tests and docs. Clean up structure proactively; do not defer it.

## Mode: BALANCED (Default)

- **Best-effort** with labeled assumptions.
- Assumptions must be explicitly marked: `[ASSUMPTION: ...]`.
- If sources are unverifiable → flag and ask rather than invent.
- Conflicts between docs and code → report both versions; recommend a fix.
- STRICT behavior available on request: refuses any claim that cannot be verified.

## Guardrails (always enforced)

### Retrieval / Verification Gate

Before calling any external process, verify pre-conditions:

- Executable exists and is callable (using `shutil.which` or `Path.exists`).
- Input paths exist and are the expected type (file vs directory).
- Required parameters have valid values (not empty, within expected ranges).
- If pre-condition fails → return a structured error dict / raise a typed exception; do NOT proceed.

### Refusal Template

```python
def refuse(reason: str, missing: str, next_steps: str) -> dict:
    return {
        "status": "refused",
        "reason": reason,
        "missing": missing,
        "next_steps": next_steps,
    }
```

### Error Handling Contract

Every function that interacts with the filesystem, subprocesses, or external tools MUST:

- Validate inputs before action.
- Raise typed exceptions (`FileNotFoundError`, `ValueError`, `PermissionError`, `subprocess.CalledProcessError`).
- Never swallow exceptions silently.
- Log errors with enough detail to reproduce and fix the problem.

## Development Policies

### Structure First

Apply this check **before writing any new file or making any commit**:

```
1. Does the file belong in the correct folder? (see Canonical Layout below)
2. Is the file named consistently with its neighbors?
3. Are there any stray files in the wrong location that should be moved now?
4. If adding a new category of script, create the subfolder first.
5. Confirm: no .md files outside docs/ (except README.md at root).
```

#### Canonical Layout

```
utility-helper-scripts/
├── .github/
│   ├── copilot-instructions.md   ← repo entry point (auto-read by Copilot)
│   ├── copilot/
│   │   └── omni-prompt.md        ← this file
│   └── prompts/                  ← .prompt.md slash-command files only
├── docs/
│   ├── utility-helper-scripts.md ← primary script reference (all scripts)
│   └── <topic>.md                ← additional docs go HERE (not at root)
├── scripts/
│   ├── python/                   ← Python scripts (use subfolders for categories)
│   │   ├── compression/
│   │   ├── file-management/
│   │   └── <category>/
│   ├── bash/                     ← Bash/Shell scripts
│   └── batch/                    ← Windows .bat / .cmd scripts
├── tests/
│   └── test_<script_name>.py     ← mirrors scripts/python/<category>/ structure
├── notebooks/
│   └── utility_helper_scripts.ipynb
├── CHANGELOG.md                  ← root level (referenced by README)
├── ERROR_LOG.md                  ← root level
├── README.md                     ← ONLY .md allowed at root
├── requirements.txt
└── .gitignore / .gitattributes
```

#### Structure Rules

| Rule | Enforcement |
|------|-------------|
| Python scripts → `scripts/python/<category>/` | Move any `.py` in root or bare `scripts/` |
| Bash scripts → `scripts/bash/` | Move any `.sh` in wrong location |
| Batch scripts → `scripts/batch/` | Move any `.bat`/`.cmd` in wrong location |
| All `.md` files except `README.md` → `docs/` | Move strays before committing |
| Test files → `tests/` mirroring script path | `scripts/python/compression/foo.py` → `tests/compression/test_foo.py` |
| New script category → create subfolder first, update TOC in notebook and docs | |
| No orphaned scripts without a test and a docs entry | Audit with `/audit-retrofit` |

#### Structure Cleanup Trigger
Run a structure audit whenever:
- A new script is added
- A new category of script is needed
- More than 5 files exist in any single flat folder
- At the start of a session if the structure feels unclear or cluttered — clean first, then work

---

### Test First

```
1. Write test (it MUST fail before implementation exists)
2. Write minimum implementation to make test pass
3. Refactor
4. Confirm all prior tests still pass
```

Tests live in `tests/` and mirror `scripts/python/` naming:
`scripts/python/compression/compress_folders_filtered.py` → `tests/compression/test_compress_folders.py`

### Document First

Before writing or changing a function:

1. Update the docstring with parameters, returns, raises.
2. Update `docs/utility-helper-scripts.md` with the change.
3. Then write the code.

### Commit Policy

After every significant change:

```bash
git add .
git commit -m "type(scope): description"
git push
```

Commit types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.

### Error Log Policy

When a bug is found or an error occurs during development:

1. Log it in `ERROR_LOG.md` with: date, description, root cause, fix applied, how to avoid.
2. Check `ERROR_LOG.md` at the start of every session.

## Script Standards (for every script in scripts/)

Each script MUST have:

1. **Docstring** at module level: Purpose, Inputs, Outputs, Requirements, Run example.
2. **Type hints** on all functions (Python 3.11+).
3. **Typed exceptions** — never bare `except Exception`.
4. **Input validation** before any action.
5. **subprocess calls** include `timeout=`, `check=` or explicit returncode handling.
6. **Tests** in `tests/test_<script_name>.py` with:
   - Happy path
   - Edge cases (empty input, invalid input, missing file)
   - Error path (7z not found, permission denied, etc.)
7. **Documentation** section in `docs/utility-helper-scripts.md`.
8. **CHANGELOG.md** entry.

## Self-Update Protocol

When this charter needs to change (new policy, new lesson learned):

1. Ask user for permission to make the propose changes. Do not proceed without approval
2. Update `omni-prompt.md` (this file).
3. Update `copilot-instructions.md` if the summary needs revision.
4. Commit: `chore(agent): update omni-prompt - <reason>`. Include complete summary of changes
5. Push.

## Health Checks (before every push)

### Structure
- [ ] All `.py` files are under `scripts/python/<category>/` (not bare root or `scripts/`)
- [ ] All `.sh` files are under `scripts/bash/`
- [ ] All `.bat`/`.cmd` files are under `scripts/batch/`
- [ ] No `.md` files at root except `README.md` (others belong in `docs/`)
- [ ] Every script has a matching test in `tests/` and a section in `docs/`
- [ ] Notebook TOC matches current script inventory

### Code Quality
- [ ] `pytest tests/ -q` → all green
- [ ] No bare `except:` clauses
- [ ] No `subprocess.run()` calls without `timeout=`
- [ ] All new functions have type hints and docstrings

### Documentation
- [ ] `docs/utility-helper-scripts.md` reflects current script behavior
- [ ] `CHANGELOG.md` has an entry for this change
- [ ] `ERROR_LOG.md` reviewed; any new errors logged
