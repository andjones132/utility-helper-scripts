# AGENTS.md — Governance Halt Gate

> This file is read natively by GitHub Copilot coding agents, VS Code Copilot, JetBrains Copilot,
> and the GitHub CLI. It governs ALL agent behavior in this repository.
> **Read this file first. It cannot be overridden by user prompts or any other instruction file.**

Created: 2026-02-23 | Repo: utility-helper-scripts | Version: 2.0.0

---

## Protected Files

The following files MUST NOT be modified by any agent without explicit user approval:

```
.github/**                   (all files in .github/)
AGENTS.md                    (this file)
```

---

## Mandatory Approval Process

Before modifying any protected file:

1. **STOP.** Do not make the change.
2. State which file(s) would be changed, and why.
3. Show the exact proposed content or unified diff.
4. **Wait for the user to explicitly say "yes" or "yes, go ahead".**
5. Execute the change only after receiving that approval.

**No other approval form is accepted.**
A previous "yes" for one change does NOT carry forward to a different change.

---

## Audit Agent: Independent Halt Authority

The `/audit-project` agent has independent halt authority over all implementing and managing agents.

- If it issues a **HALT notice**: all implementing agents MUST stop immediately.
- The project manager MUST NOT proceed to the next task.
- Development resumes ONLY after the audit agent issues an **ALL-CLEAR notice** with commit hash.

---

## Full Charter

The complete governance charter is at:

```
.github/copilot/omni-prompt.md
```

Read it before every response in this repository.

---

## Session Start Protocol (automatic)

At the start of every session, before responding to any user request:

1. Read `AGENTS.md` (this file).
2. Read `.github/copilot-instructions.md`.
3. Read `.github/copilot/omni-prompt.md`.
4. Run the `/audit-project` fast-path check (verify no cross-file inconsistencies since last audit commit).
5. Report current project state and wait for user input.

**Override:** If the user's first message is a specific slash command (e.g. `/audit-project`,
`/new-script`), skip to that command directly.
