---
name: "develop-extractor"
description: "Build or maintain the conversation extraction and filtering logic"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

> **Design Authority:** `docs/DESIGN.md` — Section `## 5. Extractor (\`src/extractor.py\`)` is the authoritative design
> for this component. This prompt is the **task execution checklist only**.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt. (Rule: `omni-prompt.md` Section 3.6)

## Project Context
This module applies filters, fetches conversations from the API, validates them via
Pydantic schemas, and **writes the results directly to the SQLite database** via
`src/db/repository.py`. It returns an `ExtractionSummary` dict, not the data itself.
It lives at `src/extractor.py`.

## Responsibilities
1. Accept an `ExtractionConfig` (mode: single / batch / project / date-range / keyword).
2. Resolve matching conversations via `APIClient`.
3. Validate each API response through `src/schemas.py` (Pydantic) before any DB write.
   If validation fails: log the error, skip that conversation, continue — never partial-write.
4. Write validated data to DB via `ConversationRepository.upsert_conversation()` and
   `upsert_messages()`. All operations are upserts (re-sync strategy — Q1 decision).
5. Return `ExtractionSummary`: `{conversations_saved, messages_saved, attachments_found, errors}`.
6. If resolved conversation count > 500: raise `ExtractionError` with a clear message
   (the Web UI shows a confirmation dialog before calling extract).
7. Log what was extracted (counts, errors) at INFO level.

## Guardrails
- Do NOT truncate message content at any point — preserve full text verbatim.
- NEVER write to the DB without first passing through Pydantic schema validation.
- If an attachment URL cannot be retrieved, log a warning and continue; do NOT abort.
- >500 conversations: raise `ExtractionError`; let the Web UI handle confirmation.
- Do NOT read from or write to the filesystem for conversation data — DB only.

## Design Check
Confirm `docs/DESIGN.md` Sections 2 (DB Layer) and 5 (Extractor) are approved before writing code.

## Test Requirements (`tests/test_extractor.py`)
- `test_extract_single_id` — fetches one conversation, validates schema, writes to DB
- `test_extract_date_range` — conversations outside range are excluded
- `test_extract_project` — all project conversations saved
- `test_validation_failure_skips_conversation` — invalid API data logged and skipped; no DB write
- `test_over_500_raises_error` — ExtractionError raised before any DB writes
- `test_upsert_idempotent` — extracting same conversation twice doesn't duplicate rows

## Commit
After tests pass: `git commit -m "feat(extractor): implement extraction with Pydantic validation and DB upsert"`
