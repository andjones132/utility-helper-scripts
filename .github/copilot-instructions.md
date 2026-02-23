# utility-helper-scripts — Copilot Instructions (Auto-consumed by GitHub Copilot Chat)

# Effective: 2026-02-23 | Version: 1.0.0

This file is the **repo-level entry point** for all Copilot agents.
Read `.github/copilot/omni-prompt.md` **before every response** — it is the governing charter.

## Quick Rules

- **Structure First, Test First, Document First.** Before writing any code, verify the file belongs in the right folder. Clean structure is a first-class deliverable.
- No feature ships without a failing test written first and docs updated.
- After every significant change: run tests, update `docs/utility-helper-scripts.md`, update `CHANGELOG.md`, then `git add . && git commit -m "<msg>" && git push`.
- Accuracy > completeness. If uncertain, stop and ask rather than guess.
- Consult `ERROR_LOG.md` at the start of every session and before every `git push`.
- Keep this file and `omni-prompt.md` current. If you learn something new that future agents must know, update these files immediately.
- **File placement rules:** All `.md` files except `README.md` → `docs/`. Python scripts → `scripts/python/<category>/`. Bash → `scripts/bash/`. Batch/CMD → `scripts/batch/`. Tests → `tests/<category>/`.

## Repo Layout

```
utility-helper-scripts/
├── .github/
│   ├── copilot-instructions.md   ← this file (auto-read by Copilot)
│   ├── copilot/
│   │   └── omni-prompt.md        ← UBER OMNI PROMPT charter (Balanced Mode)
│   └── prompts/
│       ├── audit-retrofit.prompt.md
│       ├── new-script.prompt.md
│       ├── test-doc-align.prompt.md
│       └── commit-push.prompt.md
├── docs/
│   └── utility-helper-scripts.md  ← all script documentation (single source of truth)
├── scripts/                        ← all automation scripts live here
│   └── compress_folders_filtered.py
├── tests/                          ← pytest tests mirror scripts/
│   └── test_compress_folders.py
├── notebooks/
│   └── utility_helper_scripts.ipynb ← Jupyter TOC + script runner UI
├── CHANGELOG.md
├── ERROR_LOG.md
├── README.md
└── requirements.txt
```

## Session Start Checklist

1. Read `ERROR_LOG.md` for known issues.
2. Read `.github/copilot/omni-prompt.md` for the full charter.
3. Run `pytest tests/ -q` to confirm green baseline.
4. Confirm `docs/utility-helper-scripts.md` reflects current script behavior.

## Commit Policy

Commit after every significant change. Format: `type(scope): description`
Examples: `feat(compress): add timeout to subprocess`, `test(compress): add edge-case for empty folder`
Always: `git add . && git commit -m "..." && git push`
