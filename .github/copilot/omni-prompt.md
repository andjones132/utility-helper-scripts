UBER OMNI PROMPT — Anti-Hallucination & Reliability Charter

# Repo: utility-helper-scripts | Mode: BALANCED | Version: 2.0.0 | Updated: 2026-02-23

## Purpose

This file is the **governing constitution** for every Copilot agent working in this repo.
It supersedes any other instruction when there is a conflict.
Update this file whenever you learn something that future agents must know.

---

## GOVERNANCE — Protected Files (Read This First)

> This section governs modification of this file and all agent configuration files.
> It MUST be read before any action is taken. It is enforced by `AGENTS.md` at the repo root.

### Protected File Set

```
.github/**                   (all agent config, prompts, scoped instructions)
AGENTS.md                    (root halt gate)
```

### Before Modifying Any Protected File

1. **STOP. Do not make the change.**
2. State which file(s) would be changed and why.
3. Show the exact proposed content or unified diff.
4. **Wait for the user to explicitly say "yes" or "yes, go ahead".**
5. Execute the change only after receiving that approval.

**No other approval form is accepted.** A "yes" for one change does not apply to another change.

### Why This Rule Exists

The agent that writes a governance file cannot independently audit it. The same context
window that produced the content prevents the agent from seeing its own errors. User
approval is the only truly independent review gate for agent configuration files.

---

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

| Rule                                                                          | Enforcement                                                           |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Python scripts → `scripts/python/<category>/`                                 | Move any `.py` in root or bare `scripts/`                             |
| Bash scripts → `scripts/bash/`                                                | Move any `.sh` in wrong location                                      |
| Batch scripts → `scripts/batch/`                                              | Move any `.bat`/`.cmd` in wrong location                              |
| All `.md` files except `README.md` → `docs/`                                  | Move strays before committing                                         |
| Test files → `tests/` mirroring script path                                   | `scripts/python/compression/foo.py` → `tests/compression/test_foo.py` |
| New script category → create subfolder first, update TOC in notebook and docs |                                                                       |
| No orphaned scripts without a test and a docs entry                           | Audit with `/audit-retrofit`                                          |

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

---

## Phase Gates (Explicit Stop Points Requiring User Approval)

Phase Gates are mandatory checkpoints. The agent MUST stop, present findings, and wait for
explicit "yes" before continuing. These cannot be bypassed.

| Gate | Trigger | What to Present |
| ---- | ------- | --------------- |
| **Design Gate** | Before writing the first implementation of a new script | Purpose, inputs/outputs, test plan, target file path |
| **Pre-Merge Gate** | After all tests pass, before final commit of a new/changed script | Test results, docs diff, CHANGELOG entry |
| **Governance Gate** | Before any `.github/` or `AGENTS.md` change | Proposed diff, reason, impact |

### Phase Gate Protocol

```
1. Stop at the gate.
2. Present: current state, proposed change, expected impact.
3. Wait for explicit user approval.
4. Only proceed after "yes".
5. Commit with: type(scope): description.
```

---

## Cascade Update Protocol

When any of the following are modified, you MUST update all related files **in the same commit**:

| Modified File | Also Update |
| ------------- | ----------- |
| `scripts/**/*.py` | Matching `tests/` file, `docs/utility-helper-scripts.md`, `CHANGELOG.md`, `notebooks/` TOC |
| `docs/utility-helper-scripts.md` | Verify `README.md` references are accurate |
| Any `.github/prompts/*.prompt.md` | Verify it does not contradict `omni-prompt.md` |
| `omni-prompt.md` | `copilot-instructions.md` summary; `AGENTS.md` if halt rules changed |

**This rule prevents the most common failure mode**: a script is updated, documentation
is skipped, tests drift, and the notebook TOC becomes stale. One file out of sync compounds
into three files out of sync within two sessions.

**Before committing any script change, run this cascade self-check:**

```
For each file modified:
  1. Is the matching test file up to date?
  2. Is docs/utility-helper-scripts.md accurate?
  3. Is CHANGELOG.md updated with an entry for this change?
  4. Does the notebook TOC still match the current script inventory?
```

---

## Developer Self-Check Before Commit

Before calling `git commit`, the implementing agent MUST:

1. **Read back every file modified in this task** — from the file, not from memory.
2. **Verify each specific claim**: cross-reference names, paths, and values against the authoritative source.
3. **Confirm no unintended content** was introduced (duplicate lines, truncation, missing sections).

**"I wrote it" is not verification. "I read it back and confirmed it matches the intent" is.**

Self-check is NOT the same as audit. The agent that wrote a file has the same blind spots
that produced any errors. Self-check catches careless mistakes. The independent audit
catches systematic errors. Both are required.

---

## Audit Gate Authority

### The Independence Problem — Stated Honestly

A Copilot agent invoked as "audit agent" in the same session as the implementing agent
shares the same conversation history. It cannot be fully independent. This limitation
must not be papered over.

| Role | Independence | Mechanism |
| ---- | ------------ | --------- |
| Developer self-check | None — same agent | Developer accountability only |
| Audit agent (same session) | Low-medium — adversarial checklist | Structured checklist reduces bias |
| Audit agent (fresh session) | Medium — no shared context | **Preferred invocation method** |
| Full test suite (`pytest`) | High — deterministic | Catches what tests cover |
| **User at Phase Gates** | **Full — only truly independent** | **User reads and approves** |

**The user's Phase Gate approval is the audit that matters most.** Every other mechanism
prepares the user's review to be productive — not to replace it.

### Session Independence Declaration

`/audit-project` SHOULD be invoked at the **start of a new session** — not at the end of
the session that made the changes. A fresh session reads files cold.

When invoked in the same session that made changes, the agent MUST declare:

> **"AUDIT CONTEXT: Same-session audit — I wrote or modified files this session. This audit
> is limited by shared context. The user should independently verify findings before
> approving any Phase Gate."**

### Adversarial Stance Requirement

The audit agent does NOT ask "is this correct?" It asks **"where is this wrong?"**

Default assumption: **the files contain errors**. The audit's job is to find them and
prove correctness through exhaustive checking — not through the absence of obvious problems.
ALL-CLEAR requires reading every line of every Tier 2 file. A partial read is not ALL-CLEAR.

### Audit Tiers (this repo)

**Tier 1 — Authoritative sources (establish all canonical values first):**
- `scripts/**/*.py` — actual script implementations (source of truth for behavior)
- `tests/**/*.py` — test suite (source of truth for expected behavior)

**Tier 2 — Must match Tier 1 (read every line, cross-reference every value):**
- `docs/utility-helper-scripts.md` — documentation
- `README.md`
- `CHANGELOG.md`
- `notebooks/utility_helper_scripts.ipynb` — TOC and script runner cells
- All `.github/prompts/` files
- `.github/copilot/omni-prompt.md` (this file)

### Halt Authority

If ANY inconsistency is found:

1. Issue a formal **HALT notice** listing every conflict with exact file + section.
2. All implementing agents MUST stop.
3. Fix every conflict. Read back every modified file (Self-Check above) before declaring fix complete.
4. Commit: `docs(audit): resolve <N> conflicts — <YYYY-MM-DD>`
5. Issue a formal **ALL-CLEAR notice** with commit hash and session-independence declaration.
6. Append new issues to `ERROR_LOG.md`.

---

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

When this charter or any governance file needs to change:

1. **Follow the GOVERNANCE section above** — present the proposed change and wait for explicit user approval before touching any `.github/` file or `AGENTS.md`.
2. Update `omni-prompt.md` (this file).
3. Update `copilot-instructions.md` if the summary needs revision.
4. Update `AGENTS.md` if halt authority rules changed.
5. Commit: `chore(agent): update omni-prompt - <reason>`. Include complete summary of changes.
6. Push.

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
