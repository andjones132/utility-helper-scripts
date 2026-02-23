---
applyTo: "docs/**"
---

# Documentation — Scoped Instructions

These rules apply to ALL files under `docs/`. They supplement `omni-prompt.md` Document First
policy. If this file and `omni-prompt.md` conflict, `omni-prompt.md` governs.

---

## Canonical Documents

Do not create new top-level docs without approval.

| File | Purpose | Updated When |
| ---- | ------- | ------------ |
| `docs/utility-helper-scripts.md` | All script documentation (single source of truth) | Any script is added, modified, or removed |
| `docs/omni-prompt-setup-guide.md` | Implementation guide for the governance framework | Governance framework evolves |

## Document-First Sequence

The sequence is: **Design → Tests → Code**. No code file is created until the relevant
section of `docs/utility-helper-scripts.md` describes it (at minimum as a stub with inputs/outputs).

## Prefer Depth Over Breadth

- Related topics go in the SAME file with a Table of Contents — do NOT create a new `.md` per sub-topic.
- Exception: only create a new file if the document would exceed ~300 lines and the topic is truly orthogonal.
- All documentation lives under `docs/` — NEVER at the repo root (except `README.md`).

## Formatting Rules

- Every document starts with `# Title`, then a brief description, then a `## Table of Contents`.
- Section headings: `##` for major sections, `###` for sub-sections.
- Code blocks always specify the language: ` ```python `.
- Use tables for structured data (config options, function parameters, error types).
- No "narrative creep" — descriptions must be factual and actionable.
- No placeholder text (`TODO`, `TBD`, `<placeholder>`) in committed documentation.

## Cascade Update Rule

When any script in `scripts/` is modified, `docs/utility-helper-scripts.md` MUST be
updated in the **same commit**. See `omni-prompt.md` Cascade Update Protocol for the
full rule. This is not optional and not deferrable.

**Self-check before committing any script change:**

```
Does docs/utility-helper-scripts.md reflect the current behavior of every modified script?
  - Function names match?
  - Parameter names and types match?
  - Exceptions listed match what the code actually raises?
  - Examples are still accurate?
```

## Assumptions

If an assumption is made (e.g., about external tool behavior that hasn't been verified),
label it `[ASSUMPTION]` inline, and add a note to verify it.

Never publish a statement about script behavior that hasn't been validated by a test.
