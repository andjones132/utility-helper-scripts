
---

## applyTo: "docs/\*\*"

# Documentation — Scoped Instructions

# Project: get-chat-GPT

These rules apply to ALL files under `docs/`.

## Canonical Documents (do not create new top-level docs without approval)

| File | Purpose | Owner |
|----|----|----|
| `docs/ARCHITECTURE.md` | System overview, component map, data flow, tech stack | Agents |
| `docs/DESIGN.md` | Per-component detailed design (one H2 per component) | Agents |
| `docs/TODO.md` | All deliverables; updated as tasks complete | Agents |
| `docs/ERROR_LOG.md` | Significant errors with root cause and resolution | Agents |

## Prefer Depth Over Breadth

* Related topics go in the SAME file with a Table of Contents — do NOT create a new `.md` per sub-topic.
* Exception: only create a new file if the document would exceed \~300 lines and the topic is truly orthogonal.

## Document Maintenance

* `docs/DESIGN.md` must be updated BEFORE the code changes that invalidate it.
* `docs/TODO.md` must be updated as each task completes (mark with `[x]`).
* `docs/ERROR_LOG.md` must be updated after each significant error, using the template.
* **Cascade rule:** When `docs/ARCHITECTURE.md` or `docs/DESIGN.md` is modified, all
  `.github/prompts/develop-*.prompt.md` files referencing the changed component MUST be
  updated in the same commit. See `omni-prompt.md` Section 3.6 for the full rule.
  See `.github/instructions/prompts.instructions.md` for prompt-file governance.

## Formatting Rules

* Every document starts with `# Title`, then a brief description, then a `## Table of Contents`.
* Section headings must be consistent: `##` for major sections, `###` for sub-sections.
* Use tables for structured data (config options, module responsibilities, etc.).
* Code examples must use fenced code blocks with language tag.
* Do NOT include speculative information — every claim must be verifiable.

## Assumptions

* If an assumption is made (e.g., about API behavior that hasn't been verified yet), label it
  `[ASSUMPTION]` inline, and add a TODO to verify it.


