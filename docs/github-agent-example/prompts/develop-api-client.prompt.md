---
name: "develop-api-client"
description: "Build or maintain the OpenAI Conversations API client module"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

> **Design Authority:** `docs/DESIGN.md` — Section `## 4. API Client (\`src/api_client.py\`)` is the authoritative design
> for this component. This prompt is the **task execution checklist only**.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt. (Rule: `omni-prompt.md` Section 3.6)

## Project Context
This module wraps the **OpenAI Conversations API (beta)** to retrieve ChatGPT conversation history,
projects, messages, and attachments. It lives at `src/api_client.py`.

## API Facts (cite OpenAI docs if behavior changes)
- Base URL: `https://api.openai.com/v1/` (beta conversations endpoint subject to change)
- Auth: Bearer token via `OPENAI_API_KEY` environment variable
- Relevant endpoints (verify against official docs before coding):
  - `GET /conversations` — list conversations (paginated)
  - `GET /conversations/{conversation_id}` — single conversation with messages
  - `GET /conversations/{conversation_id}/messages` — messages in a conversation
  - Projects and attachments: verify endpoint availability for the account tier
- Rate limits: honor `Retry-After` headers; implement exponential backoff
- Pagination: use `cursor`-based pagination; never assume all results fit in one page

## Responsibilities of This Module
1. Authenticate using `OPENAI_API_KEY` from environment (never hardcode).
2. Provide `list_conversations(limit, cursor)` → paginated list.
3. Provide `get_conversation(conversation_id)` → full conversation with messages.
4. Provide `list_projects()` → list of available projects (if supported by account tier).
5. Provide `get_project(project_id)` → project metadata + conversations + attachments.
6. Handle auth errors (401), rate limits (429), server errors (5xx) with retries + logging.
7. Return validated **Pydantic schema objects** (see `src/schemas.py`), not raw dicts.
   The caller (Extractor) immediately writes these to the DB — never store raw API responses.

## Guardrails
- NEVER embed API keys in code.
- NEVER call real API in tests — mock with `pytest-mock` or `responses` library.
- If an endpoint returns 404 for projects (not supported on account tier), raise a clear
  `FeatureNotAvailableError` with a human-readable message.
- If the API schema changes and existing tests break, STOP and ask before updating tests.

## Design Check (before writing code)
Confirm `docs/DESIGN.md` section "API Client" exists and is approved. If not, draft it first.

## Test Requirements
Write tests in `tests/test_api_client.py` BEFORE implementing:
- `test_list_conversations_success` — mock 200 response, assert correct model returned
- `test_list_conversations_pagination` — verify cursor is threaded correctly
- `test_auth_failure` — mock 401, assert `AuthenticationError` raised
- `test_rate_limit_retry` — mock 429 + Retry-After = 1, assert retry occurs
- `test_get_conversation_not_found` — mock 404, assert clear error

## Commit
After tests pass: `git commit -m "feat(api-client): implement conversations API client with pagination and retry"`
