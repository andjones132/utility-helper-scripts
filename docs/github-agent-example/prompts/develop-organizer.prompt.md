---
name: "develop-organizer"
description: "Build or maintain the GPT-4o-mini subtopic organizer"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

> **Design Authority:** `docs/DESIGN.md` — Section `## 6. AI Organizer (\`src/organizer.py\`)` is the authoritative design
> for this component. This prompt is the **task execution checklist only**.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt. (Rule: `omni-prompt.md` Section 3.6)

## Project Context
This module is **optional and user-triggered** — the user clicks "Categorize with AI" in
the Web UI; it never runs automatically after extraction.

It reads conversations with `subtopic IS NULL` from the DB, calls GPT-4o-mini for
classification, and writes results back via `ConversationRepository`. It lives at
`src/organizer.py`.

## Responsibilities
1. Read unclassified conversations from DB: `repo.list_conversations(subtopic=None)`.
2. For each batch of 20, call GPT-4o-mini with (title + first 500 chars) — **never full content**.
3. Validate the response against `CategorizationResultSchema` (Pydantic).
4. Write `categorization_log` record FIRST, then apply category:
   - `confidence ≥ 0.80`: `apply_category(..., review_status='auto')`
   - `confidence < 0.80`: `apply_category(..., review_status='pending_review')`
5. If GPT response is invalid JSON or fails Pydantic validation: entire batch →
   `pending_review`; raw response logged; no category applied.
6. Return `OrganizationSummary`: `{classified: int, pending_review: int, errors: int}`.

## GPT-4o-mini Prompt Pattern
```
System: You are a conversation categorizer. Given ChatGPT conversation titles and
excerpts, assign each a short subtopic category (2–4 words, Title Case, no special
characters) and a confidence score (0.0–1.0).
Return JSON array: [{"id": "<id>", "category": "<category>", "confidence": 0.87}]

User: <JSON array of {id, title, excerpt}>
```
Use `response_format={"type": "json_object"}` in the API call (structured output mode).

## Guardrails
- NEVER pass full message content to GPT-4o-mini — title + first 500 chars only.
- NEVER use AI to generate, modify, or fill in message content.
- ALWAYS write `categorization_log` before applying any category to `conversations`.
- If GPT response fails validation: batch → `pending_review`; raw response logged; no category written.
- NEVER cache results to disk — the DB is the single source of truth.
- Log estimated token usage per batch at INFO level.

## Design Check
Confirm `docs/DESIGN.md` Section 6 (AI Organizer) is approved before writing code.

## Test Requirements (`tests/test_organizer.py`)
- `test_classify_batch_auto` — mock GPT response with confidence 0.90; assert category applied, log written
- `test_classify_batch_pending_review` — mock confidence 0.60; assert review_status='pending_review'
- `test_invalid_json_response` — mock malformed response; assert batch → pending_review, raw logged
- `test_category_name_sanitized` — assert filesystem-unsafe chars stripped from category
- `test_api_error_graceful` — mock API error; assert error counted, no crash
- `test_only_unclassified_fetched` — assert already-classified conversations not re-sent

## Commit
After tests pass: `git commit -m "feat(organizer): implement GPT-4o-mini classification with confidence gating"`
- `test_fixed_categories_override` — user-provided categories used, no GPT call
- `test_no_organize_flag` — all conversations → "Uncategorized"

## Commit
After tests pass: `git commit -m "feat(organizer): implement GPT-4o-mini subtopic organizer with caching"`
