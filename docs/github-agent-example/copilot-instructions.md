# GitHub Copilot — Repository Entry Point
# Project: get-chat-GPT

> **Auto-consumed by GitHub Copilot in all sessions for this repository.**
> Do NOT modify this file to add project logic — add prompts to `.github/prompts/` instead.

## Reliability Charter
All agents and Copilot sessions in this repository **MUST** read and comply with the Anti-Hallucination
and Reliability Charter located at:

```
.github/copilot/omni-prompt.md
```

If that file is missing, run `/audit-retrofit` immediately to restore it.

## Mode (Default: BALANCED)
- **STRICT** — refuse if not fully verifiable; no assumptions.
- **BALANCED** — present facts, label assumptions clearly, disclose conflicts. ← _active default_
- **EXPLORATION** — ideas allowed but every assumption must be labeled `[ASSUMPTION]`.

## Core Principles (non-negotiable)
1. **Document First** — design and docs are written before any code is created.
2. **Test First** — no code is merged without passing tests.
3. **No source, no claim** — every factual statement must cite a file, line, or API spec.
4. **Stop and ask** — if a requirement is unclear or a change risks a breaking change, STOP and ask.
5. **Phase Gates** — seek user approval at: Architecture, Design, and before any major refactor.
6. **Commit discipline** — after each significant change, commit and push to GitHub.

## Session Start Protocol (automatic — no command required)

**At the start of every new chat session in this repository, before responding to any
user request, automatically execute the `/manage-project` protocol (Step 0 through
Step 3 only — stop at the point where user input is required).**

This means:
1. Read `omni-prompt.md`, `docs/TODO.md`, `docs/ERROR_LOG.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN.md`.
2. Run Step 0: check `git log --oneline -10` and `git diff HEAD docs/ .github/` to determine whether a full `/audit-project` run is needed.
3. Run Step 1: determine current phase from `docs/TODO.md`.
4. Report: current phase, any HALT conditions, and what the next action is. Then wait for the user.

**Override:** If the user's first message is a specific slash command (e.g. `/audit-project`,
`/develop-api-client`), skip the auto-session-start and execute that command directly instead.

This eliminates the need to manually type `/manage-project` at the start of each session.

---

## Available Slash Commands (prompts)

### 🟢 Start Here — Orchestrator
| Command | Purpose |
|---|---|
| `/manage-project` | **Primary entry point.** Assess project state, enforce phase gates, and direct the next unit of work |
| `/manage-project status` | Report current phase and task completion without taking action |
| `/manage-project approve architecture` | Mark Architecture Phase Gate approved and proceed |
| `/manage-project approve design` | Mark Design Phase Gate approved and proceed |

### � Audit (independent halt authority — runs before every Phase Gate)
| Command | Purpose |
|---|---|
| `/audit-project` | **Full cross-file consistency audit.** Reads all docs, prompts, and code against ARCHITECTURE.md + DESIGN.md. Issues HALT or ALL-CLEAR. No development may proceed past a Phase Gate without ALL-CLEAR. |

### 🔧 Component Specialists (called by orchestrator; can also be invoked directly)
| Command | Purpose |
|---|---|
| `/develop-api-client` | Build/maintain the OpenAI Conversations API client |
| `/develop-extractor` | Build/maintain extraction and filtering logic |
| `/develop-organizer` | Build/maintain the GPT-4o-mini subtopic organizer |
| `/develop-md-exporter` | Build/maintain the Markdown exporter |
| `/develop-pdf-converter` | Build/maintain the WeasyPrint PDF converter |
| `/develop-web-ui` | Build/maintain the Streamlit multi-page Web UI |

### 🛠 Utilities
| Command | Purpose |
|---|---|
| `/run-test-suite` | Run test suite and report results |
| `/update-error-log` | Append a new entry to docs/ERROR_LOG.md |
| `/audit-retrofit` | Audit repo against charter; open targeted PRs |

## Key Files
| Path | Purpose |
|---|---|
| `docs/ARCHITECTURE.md` | System architecture and design decisions |
| `docs/DESIGN.md` | Detailed component design |
| `docs/TODO.md` | All deliverables and task tracking |
| `docs/ERROR_LOG.md` | Significant errors with resolutions |
| `src/` | All Python source code |
| `tests/` | All test code (mirrors `src/`) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
