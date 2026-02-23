```instructions
---
applyTo: ".github/prompts/**"
---

# Prompt Files — Scoped Instructions

# Project: get-chat-GPT

These rules apply to ALL files under `.github/prompts/`.

---

## Purpose of Prompt Files

Each `develop-*.prompt.md` file is a **task execution checklist** for an implementing agent.
It is NOT the design spec. The design spec lives in `docs/DESIGN.md`.

| File | Role |
|---|---|
| `docs/DESIGN.md` | **Authoritative design** — the single source of truth for what each component does |
| `docs/ARCHITECTURE.md` | **Authoritative architecture** — tech stack, data flow, deployment |
| `.github/prompts/develop-*.prompt.md` | **Task checklist** — what to build, test requirements, commit message format |

**Critical rule:** If a component prompt and `docs/DESIGN.md` conflict, **DESIGN.md wins — always.**

---

## The Root Cause These Rules Address

In the initial scaffold, component prompts embedded inline design details (data structure
names, interface names, file paths). When the architecture was redesigned, DESIGN.md was
updated but the prompts were not — leaving 6 prompts describing a deleted design.

These rules prevent that failure mode from recurring.

---

## Design Authority Rule

Every `develop-*.prompt.md` MUST contain a "Design Authority" block immediately after the
`Mode:` line:

```markdown
> **Design Authority:** `docs/DESIGN.md` — Section `## <Component Name>` is the authoritative
> design for this component. This prompt is the task execution checklist only.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt.
```

The section name must match the actual heading in `docs/DESIGN.md`. If DESIGN.md is
restructured, update the Design Authority note in the same commit.

---

## Content Rules for Prompt Files

### What Belongs in a Prompt

- A brief "Project Context" paragraph (1–3 sentences: what the module does, where it lives)
- Responsibilities list (short, action-oriented — defer detail to DESIGN.md)
- Guardrails (hard rules the implementing agent must not violate)
- Test requirements (test function names + one-line description of what each tests)
- The commit message to use after the task is complete

### What Does NOT Belong in a Prompt

- Detailed data structure definitions → these live in `docs/DESIGN.md`
- Function signatures or class hierarchies → these live in `docs/DESIGN.md`
- DB schema details → these live in `docs/ARCHITECTURE.md` and `docs/DESIGN.md`
- Copies of content already in DESIGN.md → reference it instead

**If you find yourself copying content from DESIGN.md into a prompt, stop. Reference the
DESIGN.md section instead.**

---

## Cascade Update Rule (summary — full rule in `omni-prompt.md` Section 3.6)

When ANY of the following is modified:
- `docs/ARCHITECTURE.md`
- `docs/DESIGN.md`

The modifying agent MUST — **in the same commit** — update every `develop-*.prompt.md`
that references the changed component. If the prompt defers to DESIGN.md via a
Design Authority note, verify the reference is still accurate.

**The prompt update is not a separate task. It is part of the design change commit.**

---

## Prompt File Lifecycle

| Event | Required Action |
|---|---|
| Architecture redesign | Update all affected develop-*.prompt.md in same commit |
| New component added | Create new develop-<component>.prompt.md with Design Authority note |
| Component removed | Replace prompt file with a deprecation stub pointing to replacement |
| DESIGN.md section renamed | Update Design Authority note in the affected prompt |
| Inline design detail found in prompt | Remove it; replace with a reference to DESIGN.md section |

---

## Deprecation Stub Format

When a component is removed, replace its prompt with:

```markdown
---
name: "develop-<component>"
description: "DEPRECATED — <reason>"
agent: agent
---

> **DEPRECATED**
> <Component> was removed in <version/date> because <reason>.
> Use `/<replacement-command>` instead.
> See `.github/prompts/<replacement>.prompt.md`.
```

Do NOT delete deprecated prompt files — the stub acts as a redirect for any agent that
was pointed at the old command.

---

## Verification Checklist (run before committing any prompt file change)

- [ ] The prompt has a "Design Authority" note referencing the correct DESIGN.md section
- [ ] The prompt does NOT duplicate content that is already in DESIGN.md
- [ ] All module names, file paths, and data structure names match the current DESIGN.md
- [ ] The test function names listed match what is described in DESIGN.md
- [ ] The commit message format in the prompt matches the `omni-prompt.md` Section 3.3 pattern
```
