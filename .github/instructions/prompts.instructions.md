---
applyTo: ".github/prompts/**"
---

# Prompt Files — Scoped Instructions

These rules apply to ALL files under `.github/prompts/`. They are agent configuration files
and are therefore **protected** — see `AGENTS.md` and `omni-prompt.md` GOVERNANCE section.

---

## Purpose of Prompt Files

Each `.prompt.md` file is a **task execution checklist** for an implementing agent.
It is NOT the design spec. The design lives in `docs/utility-helper-scripts.md` and scripts.

| File | Role |
| ---- | ---- |
| `docs/utility-helper-scripts.md` | **Authoritative design** — single source of truth for script behavior |
| `.github/prompts/manage-project.prompt.md` | **Orchestrator** — manages the whole workflow |
| `.github/prompts/audit-project.prompt.md` | **Independent auditor** — halt authority |
| `.github/prompts/*.prompt.md` | **Task checklists** — what to build, test requirements, commit format |

**Critical rule:** If a prompt file and `docs/utility-helper-scripts.md` conflict,
`docs/utility-helper-scripts.md` governs — always.

---

## The Root Cause These Rules Address

Prompt files that embed inline design details (function names, file paths, exception types)
go stale when the design changes. A script is renamed → the doc is updated → the prompt file
still references the old name → the next agent implements the old name. These rules prevent
that failure mode.

---

## Content Rules

### What Belongs in a Prompt

- A brief "Purpose" paragraph (1–3 sentences: what this prompt does)
- The required reading list (files to read before acting)
- Responsibilities or checklist steps
- Guardrails (hard rules the agent must not violate)
- The commit message format to use after the task completes

### What Does NOT Belong in a Prompt

- Detailed function signatures or class hierarchies → these live in `docs/` and scripts
- Copies of content already in `docs/utility-helper-scripts.md` → reference it instead
- Inline design details that will go stale when the script evolves

**If you find yourself copying content from docs into a prompt, stop. Reference the doc section instead.**

---

## Cascade Update Rule

When `docs/utility-helper-scripts.md` is modified, any prompt that references the changed
script MUST be updated in the same commit. Check for:

- File path references
- Function name references
- Exception type references

See `omni-prompt.md` Cascade Update Protocol for the full rule.

---

## Governance Compliance

Because prompt files are in `.github/prompts/`, they are protected files. Any change to
a prompt file requires:

1. Presenting the proposed change to the user.
2. Getting explicit "yes" approval.
3. Then making the change.

Do not modify prompt files as a side-effect of other work without following this protocol.
