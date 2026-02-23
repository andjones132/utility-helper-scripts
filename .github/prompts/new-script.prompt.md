---
name: "new-script"
description: "Scaffold a new utility script with tests, docs, and notebook entry"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.

## Task
Create a new utility script following all repo standards.

## Required Inputs (ask user if not provided)
1. **Script purpose** — what does it do in one sentence?
2. **Inputs** — what does the user provide (paths, parameters, flags)?
3. **Outputs** — what does the script produce?
4. **Dependencies** — any third-party packages beyond stdlib?
5. **GUI or CLI?** — Tkinter GUI, argparse CLI, or pure library module?

## Deliverables — in this exact order

### Step 1: Test file (MUST be written first — it will fail until step 2)
Create `tests/test_<script_name>.py` with:
- Happy path: valid inputs produce expected output
- Edge cases: empty input, boundary values, missing optional args
- Error paths: invalid path, missing executable, permission denied
- Use `pytest`, `tmp_path` fixture, `monkeypatch` where appropriate

### Step 2: Script file
Create `scripts/<script_name>.py` with:
- Module-level docstring: Purpose, Inputs, Outputs, Requirements, Run example
- Type hints on all functions (Python 3.11+)
- Input validation before any action
- subprocess calls: always include `timeout=60` minimum
- Typed exceptions only — no bare `except:`
- All logic in testable pure functions; GUI/CLI wiring in `if __name__ == "__main__":`

### Step 3: Documentation
Add a section to `docs/utility-helper-scripts.md`:
```markdown
## <Script Name>
**File:** `scripts/<script_name>.py`
**Purpose:** <one sentence>
**Inputs:** <list>
**Outputs:** <list>
**Requirements:** <packages>
**Run:** `python scripts/<script_name>.py`
```

### Step 4: CHANGELOG entry
Add to `CHANGELOG.md` under `[Unreleased]`:
```
- feat(scripts): add <script_name> — <purpose>
```

### Step 5: Notebook entry
Add a cell to `notebooks/utility_helper_scripts.ipynb` TOC section.

### Step 6: requirements.txt
Add any new dependencies.

### Step 7: Commit & push
```bash
git add .
git commit -m "feat(<script_name>): add <purpose>"
git push
```

## Refusal Condition
If purpose, inputs, or outputs are unclear — STOP and ask before writing any code.
