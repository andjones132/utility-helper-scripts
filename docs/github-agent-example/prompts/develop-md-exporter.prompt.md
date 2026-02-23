---
name: "develop-md-exporter"
description: "Build or maintain the Markdown exporter"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

> **Design Authority:** `docs/DESIGN.md` — Section `## 7. Markdown Exporter (\`src/md_exporter.py\`)` is the authoritative
> design for this component. This prompt is the **task execution checklist only**.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt. (Rule: `omni-prompt.md` Section 3.6)

## Project Context
This module reads conversations from the **SQLite database** (via `ConversationRepository`)
and writes a zip archive of `.md` files to the export directory, which the Web UI offers
as a download. It does NOT read from the filesystem or from in-memory results.
It lives at `src/md_exporter.py`.

## Responsibilities
1. Accept a list of conversation IDs (or subtopic name, or 'all') and an export directory.
2. Read full conversations + messages from DB via `repo.get_messages(conversation_id)`.
   Messages are always ordered by `sequence_order` — rely on the repository for ordering.
3. Write one `.md` file per conversation using the format below.
4. Write an `index.md` with a Table of Contents grouped by subtopic.
5. Zip all files into a single archive; return the zip path.
6. Sanitize filenames: `YYYY-MM-DD_<slug>.md`; slug is lowercase, spaces→`-`, max 80 chars.
7. Handle filename collisions by appending `_2`, `_3`, etc.

## Per-Conversation Markdown File Format
```markdown
# <Conversation Title>

**Date:** YYYY-MM-DD HH:MM UTC  
**Conversation ID:** <id>  
**Project:** <project name or "None">  
**Category:** <subtopic>

---

## Messages

### [User] — YYYY-MM-DD HH:MM UTC
<message content — preserve code blocks, lists, tables, bold/italic>

---

### [Assistant] — YYYY-MM-DD HH:MM UTC
<message content — preserve code blocks, lists, tables, bold/italic>

---

## Attachments
- [<filename>](../_attachments/<conversation_id>/<filename>)
```

## Guardrails
- NEVER truncate message content — write full verbatim text from DB.
- NEVER modify or reformat message content — only wrap in Markdown structure.
- Read ONLY from DB via repository; do NOT read from filesystem for conversation data.
- If a conversation ID is not found in DB: log a warning; skip; do not raise.

## Design Check
Confirm `docs/DESIGN.md` Section 7 (Markdown Exporter) is approved before writing code.

## Test Requirements (`tests/test_md_exporter.py`)
- `test_single_conversation_format` — assert header, metadata, messages in correct order
- `test_role_labels` — assert `[User]` and `[Assistant]` labels present
- `test_model_slug_in_output` — assert model_slug shown for assistant messages when present
- `test_filename_slug` — assert filename is lowercase-dashed, max 80 chars
- `test_filename_collision` — two conversations with same title get `_2` suffix
- `test_zip_created` — export returns a valid zip path containing the .md files
- `test_unknown_id_skipped` — missing conversation ID logged, others exported

## Commit
After tests pass: `git commit -m "feat(md-exporter): implement DB-backed Markdown export with zip output"`
8. If a conversation has no title, use `untitled-<conversation_id[:8]>`.

## Guardrails
- NEVER truncate message content.
- Preserve the role label exactly: `User`, `Assistant`, `System` (or `Tool`).
- If a message contains raw HTML-like content, escape it so it renders as text in Markdown.
- If an attachment cannot be written (permission error, etc.), log a warning and continue.

## Design Check
Confirm `docs/DESIGN.md` section "Markdown Exporter" exists and is approved.

## Test Requirements (`tests/test_md_exporter.py`)
- `test_creates_directory_structure` — correct folders created
- `test_conversation_file_content` — metadata header + messages correct
- `test_code_block_preserved` — fenced code blocks survive export
- `test_table_preserved` — Markdown tables survive export
- `test_filename_sanitization` — special chars removed, collisions handled
- `test_index_md_generated` — index contains all conversations grouped by category
- `test_attachment_copied` — attachment file present in `_attachments/`

## Commit
After tests pass: `git commit -m "feat(md-exporter): implement Markdown exporter with TOC and attachment handling"`
