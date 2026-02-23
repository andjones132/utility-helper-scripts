# utility-helper-scripts — Copilot Instructions (Auto-consumed by GitHub Copilot Chat)

# Effective: 2026-02-23 | Version: 2.0.0

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
- **STOP — Protected Files.** NEVER modify any `.github/` file or `AGENTS.md` without first presenting the proposed change and receiving an explicit "yes" from the user. See `AGENTS.md` and `omni-prompt.md` GOVERNANCE section.

## Repo Layout

```
utility-helper-scripts/
├── AGENTS.md                       ← governance halt gate (read by all coding agents)
├── .github/
│   ├── copilot-instructions.md   ← this file (auto-read by Copilot)
│   ├── copilot/
│   │   └── omni-prompt.md        ← UBER OMNI PROMPT governing charter (v2)
│   ├── instructions/             ← path-scoped rules (auto-injected by VS Code)
│   │   ├── python-src.instructions.md   (applyTo: scripts/**/*.py)
│   │   ├── tests.instructions.md        (applyTo: tests/**)
│   │   ├── docs.instructions.md         (applyTo: docs/**)
│   │   └── prompts.instructions.md      (applyTo: .github/prompts/**)
│   └── prompts/
│       ├── audit-project.prompt.md  ← /audit-project (independent audit, halt authority)
│       ├── manage-project.prompt.md ← /manage-project (orchestrator, runs audit first)
│       ├── audit-retrofit.prompt.md
│       ├── new-script.prompt.md
│       ├── test-doc-align.prompt.md
│       └── commit-push.prompt.md
├── docs/
│   ├── utility-helper-scripts.md   ← all script docs (single source of truth)
│   └── omni-prompt-setup-guide.md ← implementation guide for any new project
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

## Session Start Protocol (automatic — no command required)

**At the start of every new chat session, before responding to any user request,
automatically execute the following steps:**

1. Read `AGENTS.md` — governance halt gate and protected file rules.
2. Read `ERROR_LOG.md` for known issues and lessons learned.
3. Read `.github/copilot/omni-prompt.md` for the full charter.
4. Run `/audit-project` fast path: check `git log --oneline -10` and `git diff HEAD docs/ .github/`
   to determine if a full audit is needed.
5. Report: current project state, any HALT conditions, and the recommended next action. Then wait.

**Override:** If the user's first message is a specific slash command (e.g. `/audit-project`,
`/new-script`), skip the auto-session-start and execute that command directly.

## Available Slash Commands

### 🟢 Orchestrator (start here)

| Command | Purpose |
| ------- | ------- |
| `/manage-project` | Assess project state, enforce phase gates, direct next unit of work |
| `/manage-project status` | Report current state without taking action |

### 🔍 Audit (independent halt authority)

| Command | Purpose |
| ------- | ------- |
| `/audit-project` | Full cross-file consistency audit. Issues HALT or ALL-CLEAR. Runs before every Phase Gate. |

### 🔧 Development

| Command | Purpose |
| ------- | ------- |
| `/new-script` | Scaffold a new script: design → test → implement → docs → changelog → notebook → commit |
| `/test-doc-align` | Detect and fix drift between tests, docs, and code |
| `/audit-retrofit` | Retrofit an existing project with the governance framework |
| `/commit-push` | Pre-push health checklist then commit + push |

## Commit Policy

Commit after every significant change. Format: `type(scope): description`
Examples: `feat(compress): add timeout to subprocess`, `test(compress): add edge-case for empty folder`
Always: `git add . && git commit -m "..." && git push`
