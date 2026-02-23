# Omni-Prompt Governance Framework — Implementation Guide

> Version: 2.0.0 | Updated: 2026-02-23 | Repo: utility-helper-scripts
>
> This guide distills lessons and patterns from two full project implementations
> (utility-helper-scripts and get-chat-GPT) into a reusable, project-agnostic reference
> for setting up the governance framework in any new or existing project.

---

## Table of Contents

1. [Why This Framework Exists](#1-why-this-framework-exists)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [The Canonical File Set](#3-the-canonical-file-set)
4. [File-by-File Reference](#4-file-by-file-reference)
5. [The Independent Audit Agent](#5-the-independent-audit-agent)
6. [The Manager-Orchestrator Pattern](#6-the-manager-orchestrator-pattern)
7. [Phase Gates](#7-phase-gates)
8. [Setting Up a New Project](#8-setting-up-a-new-project)
9. [Retrofitting an Existing Project](#9-retrofitting-an-existing-project)
10. [What NOT to Put in Prompt Files](#10-what-not-to-put-in-prompt-files)
11. [Cascade Update Protocol](#11-cascade-update-protocol)
12. [Developer Self-Check vs Independent Audit](#12-developer-self-check-vs-independent-audit)
13. [GitHub Agent Documentation References](#13-github-agent-documentation-references)
14. [Customizing for Your Project Type](#14-customizing-for-your-project-type)
15. [Structure-First Policy](#15-structure-first-policy)

---

## 1. Why This Framework Exists

AI coding agents are productive and autonomous — but they have a fundamental flaw: they
operate in a shared context window. An agent that writes a file, then audits it in the
same session, will often miss its own errors. It has the same blind spots that produced the
errors in the first place.

Without governance, agents:

- Update one file and forget to update the three files that depend on it
- Modify their own instruction files without asking permission
- Write documentation that contradicts the code
- Issue self-audits that pass because the checker shares context with the writer
- Accumulate stale cross-file inconsistencies across sessions until something breaks

This framework addresses all of these failure modes systematically.

---

## 2. The Problem It Solves

### Observed Failure Patterns (from real project implementations)

| Pattern | What Happened | Root Cause |
| ------- | ------------- | ---------- |
| **Stale cross-file drift** | Prompt files still described deleted architecture after redesign | No cascade update rule |
| **Self-audit blind spot** | Inline audit passed because agent shared context with implementer | Same session = shared blind spots |
| **Agent "groupthink"** | Multiple passes needed to fix errors the agent kept recreating | No independent verification step |
| **Governance without teeth** | "Ask user for permission" in execution-mode config — agent never read it early enough | Rule was in wrong file section |
| **Missing test coverage** | Functions added without corresponding test updates | No enforced red-phase requirement |
| **Silent doc drift** | Scripts changed, docs not updated | No cascade update protocol |

### The Fix: Layered Governance

```
Layer 1 — Halt Gate:      AGENTS.md (read first, by any agent, every session)
Layer 2 — Charter:        omni-prompt.md (governing constitution)
Layer 3 — Entry Point:    copilot-instructions.md (session start protocol)
Layer 4 — Independent:    audit-project.prompt.md (adversarial, read files cold)
Layer 5 — Orchestrator:   manage-project.prompt.md (calls audit before anything)
Layer 6 — Scoped Rules:   .github/instructions/*.instructions.md (auto-injected)
```

No single layer is sufficient. All six work together.

---

## 3. The Canonical File Set

These files should exist in every governed project. Files marked ★ are the minimum viable set.

```
<repo-root>/
├── AGENTS.md ★                          ← halt gate (read by GitHub agent, VS Code, JetBrains, CLI)
├── .github/
│   ├── copilot-instructions.md ★        ← entry point (auto-consumed by Copilot every session)
│   ├── copilot/
│   │   └── omni-prompt.md ★             ← governing charter (supersedes all other instructions)
│   ├── instructions/                    ← path-scoped rules (auto-injected by VS Code by file glob)
│   │   ├── python-src.instructions.md   (applyTo: src/**/*.py or scripts/**/*.py)
│   │   ├── tests.instructions.md        (applyTo: tests/**)
│   │   ├── docs.instructions.md         (applyTo: docs/**)
│   │   └── prompts.instructions.md      (applyTo: .github/prompts/**)
│   └── prompts/
│       ├── audit-project.prompt.md ★    ← /audit-project  (independent halt authority)
│       ├── manage-project.prompt.md ★   ← /manage-project (orchestrator, calls audit first)
│       ├── new-script.prompt.md         ← /new-script (or /new-feature, /new-component)
│       ├── audit-retrofit.prompt.md     ← /audit-retrofit (for existing projects)
│       ├── test-doc-align.prompt.md     ← /test-doc-align
│       └── commit-push.prompt.md        ← /commit-push
├── docs/
│   ├── <project-name>.md ★              ← primary documentation (single source of truth)
│   └── omni-prompt-setup-guide.md       ← this file
├── ERROR_LOG.md ★
├── CHANGELOG.md ★
└── README.md ★
```

---

## 4. File-by-File Reference

### `AGENTS.md` — Root Halt Gate

**What it is:** The first file read by GitHub coding agents. It defines protected files
and the mandatory approval process for modifying them.

**What it MUST contain:**
- Protected file set (`.github/**`, `AGENTS.md` itself)
- The 5-step approval process (stop → state → show → wait → execute)
- Reference to the full charter (`omni-prompt.md`)
- Session start protocol (what to do automatically at session start)

**Why it exists separately from `copilot-instructions.md`:**
GitHub's coding agent reads `AGENTS.md` natively as an authoritative halt gate. The nearest
`AGENTS.md` in the directory tree wins. This makes it the right place for rules that must
apply before any other file is read.

**File placement:** Repo root. One `AGENTS.md` governs the whole repo unless overridden
by a subfolder `AGENTS.md` (which governs only that subtree).

---

### `copilot-instructions.md` — Repo Entry Point

**What it is:** Auto-consumed by GitHub Copilot in every chat session. It is the human-readable
summary that delegates to the full charter.

**What it MUST contain:**
- Version number and effective date
- Quick Rules (including the STOP rule for protected files)
- Link to `omni-prompt.md`
- Auto-session-start protocol (read AGENTS.md → read ERROR_LOG → read omni-prompt → run audit fast-path → report)
- Slash command table
- Repo layout (so agents know where files live)
- Commit policy

**What it MUST NOT contain:**
- The full governance charter (that belongs in `omni-prompt.md`)
- Detailed task execution logic (that belongs in `prompts/`)
- Anything that changes every time a new script is added (keep it stable)

---

### `omni-prompt.md` — Governing Charter

**What it is:** The constitution. It supersedes all other instructions when there is a conflict.

**What it MUST contain:**
- **GOVERNANCE section as the very first section** (not buried in execution-mode reading)
- Core Principles (Accuracy > Completeness, Test First, Document First, Structure First)
- Mode: BALANCED / STRICT / EXPLORATION
- Guardrails (verification gate, refusal template, error handling contract)
- **Phase Gates** (design gate, pre-merge gate, governance gate)
- **Cascade Update Protocol** (which files must update together)
- **Developer Self-Check Before Commit** (distinct from audit)
- **Audit Gate Authority** (session independence problem, adversarial stance, tiers, halt authority)
- Script/Code Standards
- Self-Update Protocol (references the GOVERNANCE section — does not repeat the rules)
- Health Checks

**Key lesson:** The GOVERNANCE section must be the very first section after the title/purpose.
An agent reads files in order. If the approval requirement is buried in "Self-Update Protocol"
(which is read after the agent has already decided to modify the file), it is too late.
The governance rule must be the first thing the agent reads, not the last.

---

### `audit-project.prompt.md` — The Independent Auditor

**What it is:** A slash command (`/audit-project`) that implements an adversarial,
read-cold audit of all project files. Its findings have halt authority.

**Critical design principles:**

1. **Adversarial stance:** "Where is this wrong?" — not "Is this correct?"
2. **Session independence declaration:** Must declare whether it's a fresh session or same-session.
   Same-session audits are limited by shared context and must say so.
3. **Tier structure:** Read Tier 1 (authoritative sources) first; then verify every Tier 2
   file against Tier 1. ALL-CLEAR requires reading every line of every Tier 2 file.
4. **Preferred invocation:** At the START of a new session (before the implementing agent
   does anything). This is the only way to approach true independence.
5. **Halt authority:** If conflicts found → HALT notice → all work stops → fix → read-back
   → ALL-CLEAR with commit hash.

**Tier definition (adapt for your project):**

| Tier | Contents |
| ---- | -------- |
| Tier 1 (authoritative) | Source code, test suite; OR ARCHITECTURE.md + DESIGN.md for design-first projects |
| Tier 2 (must match Tier 1) | Documentation, README, CHANGELOG, notebook TOC, all prompt files |

---

### `manage-project.prompt.md` — The Orchestrator

**What it is:** A slash command (`/manage-project`) that coordinates all work.

**Critical design principles:**

1. **Step 0 is always `/audit-project`** — the orchestrator never skips the audit.
   This was the critical lesson: inline Session Start checks (checking one or two files)
   missed errors that a full adversarial audit would have caught. The fix: dispatch to the
   full audit agent, not a reduced inline check.
2. **Fast-path rule:** Skip the full audit ONLY if: (a) last N commits include a `docs(audit):`
   commit, AND (b) `git diff HEAD` on all tracked files shows zero changes since that commit.
   If ANY file changed — run the full audit. No exceptions.
3. **Phase Gate enforcement:** The orchestrator stops at every Phase Gate and waits for
   explicit user approval before continuing.
4. **Execute, don't route:** When the orchestrator selects a task, it executes it fully
   (inline, using rules from the relevant prompt). It does not just name the next step.

**Why the orchestrator update was necessary (from real session logs):**
Original design had the orchestrator run its own inline Step 0 that only checked prompt files.
This missed `README.md`, `.env.example`, and code examples in `DESIGN.md`. The same errors
recurred across three sessions because the incomplete check issued a false ALL-CLEAR each time.
The fix: dispatch to the full `/audit-project` agent. One independent call instead of a
partial inline check.

---

### `.github/instructions/*.instructions.md` — Path-Scoped Rules

**What they are:** Rules that VS Code automatically injects when editing files matching
the `applyTo:` glob. No manual activation required.

**Frontmatter format:**
```markdown
---
applyTo: "src/**/*.py"
---
```

**Available `applyTo:` glob patterns:**
- `scripts/**/*.py` or `src/**/*.py` — Python source files
- `tests/**` — Test files
- `docs/**` — Documentation files
- `.github/prompts/**` — Prompt files (to enforce governance)

**What they should contain:**
- Module structure rules
- Error handling contracts
- Naming conventions
- Self-check checklists specific to that file type
- References to the relevant sections of `omni-prompt.md` (don't duplicate — reference)

**Priority:** Path-scoped instructions apply ONLY when editing matching files. They do not
override `omni-prompt.md` — they supplement it with file-type-specific detail.

---

## 5. The Independent Audit Agent

This is the most important pattern in the framework. The single change that had the most
impact on quality: **running the audit as a separate, fresh-session agent rather than as
an inline Step 0 in the orchestrator.** 

### The Session Independence Problem

An AI agent cannot truly audit its own work in the same session. The same context window
that produced an error prevents the agent from seeing it. This is not a flaw in the agent —
it is a fundamental limitation of bounded context.

| Reviewer | Independence | Notes |
| -------- | ------------ | ----- |
| Agent self-check (same session) | None | Necessary but not sufficient |
| Audit agent (same session) | Low-medium | Adversarial structure reduces bias; shared context limits it |
| Audit agent (fresh session) | Medium | No shared context; reads files cold; **the preferred method** |
| Deterministic test suite | High | Best tool for code correctness; not applicable to docs |
| **User at Phase Gates** | **Full** | **The only truly independent reviewer; the audit that matters most** |

### How to Invoke the Audit for Maximum Independence

1. Make your changes in one session.
2. Commit (or save) the changes.
3. Start a **new chat session**.
4. Type `/audit-project` as the first message.
5. The audit reads every Tier 2 file cold — no shared context with the session that wrote the files.

### The ALL-CLEAR Notice

An audit that issues ALL-CLEAR without reading every Tier 2 file is not ALL-CLEAR.
The notice must include: date, session type (fresh or same-session), number of files audited,
number of conflicts (must be 0), and commit hash.

### When HALT is Issued

Every conflict is listed with: file, section/line, found value, expected value, source.
All work stops. Conflicts are fixed. The fixer reads back every modified file. A new
audit runs. NEW ALL-CLEAR is issued with a new commit hash. Only then does work resume.

---

## 6. The Manager-Orchestrator Pattern

### Why Projects Need an Orchestrator

Without a central orchestrator, each implementing agent makes local decisions without
awareness of global project state. The result: work is done out of order, Phase Gates are
skipped, and the audit is never called because no one is responsible for calling it.

The orchestrator solves this by being the single entry point for all work.

### Step 0 Is Sacred

Step 0 (run the audit) must ALWAYS run. It cannot be skipped except via the explicit
fast-path rule (last audit commit + zero diffs). Every other step depends on the project
being in a known consistent state.

### The Agent Hierarchy

```
User
  └─ /manage-project  (orchestrator — entry point for all work)
        ├─ /audit-project  (independent auditor — halt authority)
        ├─ /new-script      (task specialist)
        ├─ /test-doc-align  (task specialist)
        └─ /commit-push     (task specialist)
```

---

## 7. Phase Gates

Phase Gates are explicit stop points that require user approval. They cannot be bypassed.

### Universal Phase Gates (every project type)

| Gate | Trigger | What Agent Presents |
| ---- | ------- | ------------------- |
| **Design Gate** | Before writing the first implementation of any major new component | Purpose, inputs/outputs, test plan, file paths |
| **Pre-Merge Gate** | After all tests pass, before final commit | Test results, docs diff, CHANGELOG entry |
| **Governance Gate** | Before any `.github/` or `AGENTS.md` change | Proposed diff, reason, impact |

### Additional Gates for Design-First Projects

| Gate | Trigger |
| ---- | ------- |
| **Architecture Gate** | After ARCHITECTURE.md is drafted |
| **Design Gate** | After DESIGN.md component designs are drafted |

### Phase Gate Protocol

```
1. STOP at the gate.
2. Present: current state, proposed change, expected impact.
3. Wait for explicit user approval ("yes" or "yes, go ahead").
4. Only proceed after approval.
5. Commit: type(scope): description.
```

---

## 8. Setting Up a New Project

### Step 1: Create the Minimum Viable Governance Set

Create these files first, before any code:

1. `AGENTS.md` — use the template in this repo; update project name
2. `.github/copilot-instructions.md` — entry point; update project name and layout
3. `.github/copilot/omni-prompt.md` — full charter; update project name
4. `.github/prompts/audit-project.prompt.md` — adapt Tier 1/2 for your project's authoritative sources
5. `.github/prompts/manage-project.prompt.md` — adapt state table and task flows
6. `ERROR_LOG.md` — empty template with the logging format
7. `CHANGELOG.md` — empty with version header
8. `README.md` — basic project description

### Step 2: Adapt for Your Project Type

See [Section 14](#14-customizing-for-your-project-type) for project-type-specific guidance.

### Step 3: Add Path-Scoped Instructions

Create `.github/instructions/` files for your primary source file types. At minimum:
- One for source code
- One for tests
- One for docs

### Step 4: Initial Commit

```bash
git add .
git commit -m "chore(setup): initial governance scaffold — AGENTS.md, omni-prompt, audit agent"
git push
```

### Step 5: Session Start Verification

Open a new chat session. Type `/manage-project`. Verify:
- It reads AGENTS.md and omni-prompt.md
- It runs `/audit-project` (Step 0)
- It reports project state and waits for input

---

## 9. Retrofitting an Existing Project

If your project already has code but no governance framework, use `/audit-retrofit`.

### Retrofit Sequence

1. Run `/audit-retrofit` — it audits the existing codebase against the governance charter
   and produces a prioritized list of gaps.
2. Create the governance files (see Section 8, Step 1).
3. Run `/test-doc-align` — find and fix gaps between tests, docs, and code.
4. Run `/audit-project` in a fresh session to confirm ALL-CLEAR.
5. Commit: `chore(agent): retrofit governance framework`

### Common Retrofit Findings

- Missing `AGENTS.md` → create it
- `copilot-instructions.md` exists but is outdated → update with STOP rule and auto-session-start
- `omni-prompt.md` exists but lacks GOVERNANCE section at top → add it first
- No `audit-project.prompt.md` → create it (this is always the highest-value addition)
- Inline self-checks in `manage-project` instead of dispatching to `/audit-project` → update
- Stale prompt files referencing deleted components → run `/test-doc-align` and fix

---

## 10. What NOT to Put in Prompt Files

This is the lesson that took the most sessions to learn.

### The Stale Prompt Problem

A prompt file that embeds inline design details (function names, file paths, class names)
becomes stale whenever the design changes. If DESIGN.md or the scripts are updated and
the prompt file is not updated in the same commit, the next agent reads the prompt file
and implements the old design.

**Rule:** Prompt files are task checklists. They contain: what to do, in what order,
what tests to write, what commit message to use. They do NOT contain the design itself.

### Use Design Authority References Instead

Instead of embedding function signatures in a prompt:

```markdown
<!-- WRONG: stale when design changes -->
The function signature is: def find_7z(explicit_path: str | None = None) -> str

<!-- RIGHT: refer to the authoritative source -->
Refer to docs/utility-helper-scripts.md Section "find_7z" for the function specification.
If this prompt and the docs conflict, the docs govern.
```

---

## 11. Cascade Update Protocol

The Cascade Update Protocol prevents the silent drift that accumulates when one file is
updated but its dependents are not.

### The Rule

When file X is modified, all Y files that depend on X MUST be updated in the same commit.

### Dependency Map

| Modified (X) | Must Also Update (Y) |
| ------------ | -------------------- |
| Any `scripts/*.py` | Matching `tests/` file, `docs/<project>.md`, `CHANGELOG.md`, notebook TOC |
| `docs/<project>.md` | Verify `README.md` script references are accurate |
| Any `.github/prompts/*.prompt.md` | Verify it doesn't contradict `omni-prompt.md` |
| `omni-prompt.md` | `copilot-instructions.md` summary; `AGENTS.md` if halt rules changed |
| `ARCHITECTURE.md` or `DESIGN.md` | All `develop-*.prompt.md` that reference changed components |

### Enforcing the Rule

The self-check before every commit:

```
For each file modified in this task:
  1. What other files depend on this file?
  2. Are all dependent files updated?
  3. Do I need to update docs, tests, changelog, notebook, or prompts?
  4. Are there any file references in other files that are now incorrect?
```

---

## 12. Developer Self-Check vs Independent Audit

These are distinct. Both are required. Neither substitutes for the other.

| Check | Who | When | What It Catches |
| ----- | --- | ---- | --------------- |
| **Developer Self-Check** | Implementing agent | Before every commit | Careless mistakes, truncation, missing sections |
| **Independent Audit** | Audit agent (fresh session preferred) | Every session start, before every Phase Gate | Systematic cross-file inconsistencies |
| **Test Suite** | pytest | Before every commit | Code behavior errors |
| **User Phase Gate Review** | User | At every Phase Gate | Everything else |

**Developer self-check is not a substitute for audit.** An agent that checks its own work
is like a developer reviewing their own PR — necessary professional practice, but not a
substitute for independent review. The same blind spots that caused an error will often
prevent detection during self-review.

---

## 13. GitHub Agent Documentation References

These are the authoritative sources for GitHub Copilot agent configuration. Consult them
to verify current best practices before updating governance files.

### File Types and Their Roles

| File | Platform Support | Notes |
| ---- | ---------------- | ----- |
| `.github/copilot-instructions.md` | GitHub.com, VS Code, JetBrains, CLI | Auto-consumed by Copilot in every session; max usefulness at < 500 lines |
| `AGENTS.md` | GitHub coding agent, VS Code, JetBrains, CLI | Nearest file in directory tree wins; authoritative halt gate |
| `.github/instructions/*.instructions.md` | VS Code only | Path-scoped with `applyTo:` frontmatter; supports `excludeAgent:` |
| `.github/prompts/*.prompt.md` | VS Code only (slash commands in chat) | Used for `/command-name` invocation |
| `CLAUDE.md` | Claude (Anthropic) | Alternative to `AGENTS.md` for Claude-specific instructions |
| `GEMINI.md` | Gemini (Google) | Alternative to `AGENTS.md` for Gemini-specific instructions |

### Instruction Priority Order

```
Personal instructions (user-level)
    > Repository instructions (.github/copilot-instructions.md)
        > Organization instructions
```

### Official Documentation URLs

- **Repository custom instructions:**
  https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot

- **VS Code customization (instructions, prompts, agents, hooks):**
  https://code.visualstudio.com/docs/copilot/copilot-customization

- **Cross-platform support matrix:**
  https://docs.github.com/en/copilot/reference/custom-instructions-support

- **GitHub Copilot agents UI:**
  https://github.com/copilot/agents

- **Copilot changelog (new features as they ship):**
  https://github.blog/changelog/label/copilot/

### Key Behaviors (verified Feb 2026)

- `copilot-instructions.md` is injected automatically — no user action required.
- `AGENTS.md` is the recommended halt gate for multi-agent coding scenarios.
- Path-scoped `.instructions.md` files are injected automatically by VS Code when editing
  files that match the `applyTo:` glob — no manual activation needed.
- `.prompt.md` files in `.github/prompts/` appear as `/command-name` slash commands in
  VS Code Copilot Chat.
- The GitHub coding agent at `github.com/copilot/agents` can auto-generate a
  `copilot-instructions.md` for a new repo if one doesn't exist.

---

## 14. Customizing for Your Project Type

### Scripts / Utility Library (this repo)

- **Tier 1 (authoritative):** `scripts/**/*.py` and `tests/**/*.py`
- **Phase Gates:** Design Gate (before first implementation), Pre-Merge Gate
- **Cascade rule:** Script changes cascade to: test, docs, changelog, notebook TOC
- **Audit focus:** docs vs code vs test alignment; no architecture docs needed

### Application / Service (e.g. web app, API)

- **Tier 1 (authoritative):** `docs/ARCHITECTURE.md` and `docs/DESIGN.md`
- **Phase Gates:** Architecture Gate, Design Gate, Pre-Merge Gate
- **Additional audit types:** Consistency Audit (docs only) + Code Quality Audit (code vs design)
- **Cascade rule:** Design doc change → all `develop-*.prompt.md` must update
- **Additional prompts:** One `develop-<component>.prompt.md` per major component

### Data Science / ML

- **Tier 1 (authoritative):** Data schema definitions, model specifications
- **Phase Gates:** Data validation gate, model review gate
- **Adapt omni-prompt:** Add data integrity checks, model versioning policy

### VS Code Extension / Library

- **Tier 1 (authoritative):** API documentation, type definitions
- **Additional scoped instructions:** One per contribution point type
- **Cascade rule:** API change → all dependent prompt files + README + CHANGELOG

---

## 15. Structure-First Policy

### Why Structure Is a First-Class Deliverable

ADHD-friendly development relies on predictable structure. When files are in unexpected
locations, the cognitive overhead of "where does this go?" and "where is that?" compounds
across every session. A clean, enforced structure reduces this overhead to zero.

### The Structure-First Rule

Before writing any new file or making any commit, verify:

1. Does the file belong in the correct folder?
2. Is the file named consistently with its neighbors?
3. Are there any stray files that should be moved now?
4. If adding a new category, create the subfolder first.
5. No `.md` files outside `docs/` (except `README.md` at root).

### Structure Cleanup Trigger

Run a structure audit whenever:

- A new script is added
- A new category of script is needed
- More than 5 files exist in any single flat folder
- At the start of a session if the structure feels unclear — clean first, then work

### Canonical Layout for Scripts Library

```
<repo-root>/
├── AGENTS.md
├── .github/
│   ├── copilot-instructions.md
│   ├── copilot/omni-prompt.md
│   ├── instructions/
│   └── prompts/
├── docs/
├── scripts/
│   ├── python/<category>/    ← never place .py at bare scripts/ or root
│   ├── bash/
│   └── batch/
├── tests/
│   └── <category>/           ← mirrors scripts/python/<category>/
├── notebooks/
├── CHANGELOG.md
├── ERROR_LOG.md
├── README.md
└── requirements.txt
```

---

*This guide is a living document. Update it when the governance framework evolves or when
new project patterns are discovered. Do not drop sections without checking with the user.*
