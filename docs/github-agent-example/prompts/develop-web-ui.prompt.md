---
name: "develop-web-ui"
description: "Build or maintain the Streamlit multi-page Web UI (src/web/)"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

> **Design Authority:** `docs/DESIGN.md` — Section `## 9. Web UI (\`src/web/app.py\`)` is the authoritative design
> for this component. This prompt is the **task execution checklist only**.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt. (Rule: `omni-prompt.md` Section 3.6)

## Project Context
The Web UI is the sole user-facing interface. It is a Streamlit multi-page application
that lives at `src/web/`. Entry point: `src/web/app.py`, invoked as:
```bash
streamlit run src/web/app.py
```
Authentication is enforced via `streamlit/secrets.toml` (single-user password).
All data is read from and written to SQLite via `ConversationRepository`.

## Directory Structure
```
src/web/
  app.py            ← entry point: st.navigation(), auth guard, DB session init
  pages/
    01_extract.py   ← trigger extraction + optional AI categorization
    02_browse.py    ← browse, search, filter conversations
    03_review.py    ← review AI-pending_review items; approve/edit/reject
    04_export.py    ← export to Markdown (zip) or PDF
    05_settings.py  ← environment info, DB stats, clear cache
  components/
    auth.py         ← password guard using st.secrets
    db.py           ← DB session init, cached `@st.cache_resource`
    pagination.py   ← reusable paginator for conversation lists
```

## Page Responsibilities

### `app.py` — Entry Point
1. Call `auth.require_login()` — stop rendering if not authenticated.
2. Initialize `db.get_session()` with `@st.cache_resource`.
3. Define `st.navigation()` with the 5 pages.
4. Show app title and current DB path in sidebar.

### `pages/01_extract.py` — Extract
1. Form: API key (password input, overrides `.env`), extraction mode radio
   (Single ID / Date Range / Project / Keyword / Batch paste).
2. "Preview" button: calls `APIClient.list_conversations(filters)`, shows count.
3. Guard: if count > 500, show `st.warning` + confirmation checkbox before enabling Extract.
4. "Extract" button: calls `Extractor.run(config)`, shows `st.progress` bar.
5. Shows `ExtractionSummary` on completion: conversations saved, messages saved, errors.
6. "Categorize with AI" button (separate, below summary): calls `Organizer.run()`,
   shows `OrganizationSummary`. This is OPTIONAL — never automatic.

### `pages/02_browse.py` — Browse
1. Sidebar filters: keyword search, subtopic select, date range, model_slug.
2. `st.dataframe` with columns: title, subtopic, date, message_count, model_slug.
3. Clicking a row opens a `st.expander` with full message thread.
4. Messages show role label (`[User]` / `[Assistant]`), content, and model_slug if present.
5. Pagination via `components/pagination.py` (25 per page default).

### `pages/03_review.py` — AI Review Queue
1. Show only conversations with `review_status = 'pending_review'`.
2. For each item: show suggested category + confidence score from `categorization_log`.
3. Actions: Approve (apply category, set `review_status='approved'`),
            Edit + Approve (text input for custom category),
            Reject (set `subtopic=NULL`, `review_status='rejected'`).
4. Batch approve: select all + "Approve All" button.
5. Show queue count in page title badge.

### `pages/04_export.py` — Export
1. Filter selection: export by subtopic, date range, or 'all'.
2. "Export Markdown" button: calls `MDExporter.run(ids, export_dir)`,
   returns zip path → `st.download_button`.
3. "Export PDF" button: calls `PDFConverter.run(md_dir)` → `st.download_button`.
4. Show file size + file count in the download summary.

### `pages/05_settings.py` — Settings
1. Show DB path, total conversations, total messages, DB file size.
2. "Re-sync all" button: re-extracts all known conversation IDs (calls Extractor).
3. Show Python version, Streamlit version, WeasyPrint version.
4. "Clear export cache" button: deletes files in `EXPORT_PATH`.

## Auth Pattern (`components/auth.py`)
```python
import streamlit as st

def require_login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if pw == st.secrets["app"]["password"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()
```

## DB Session Pattern (`components/db.py`)
```python
import streamlit as st
from src.db.session import get_engine
from src.db.repository import ConversationRepository

@st.cache_resource
def get_repo() -> ConversationRepository:
    engine = get_engine()
    return ConversationRepository(engine)
```

## Guardrails
- NEVER expose the API key in any `st.write`, `st.code`, or log output.
- NEVER call GPT-4o-mini automatically — only on explicit button click.
- All DB access MUST go through `ConversationRepository` — no raw SQL in page files.
- Every page MUST call `auth.require_login()` as the first statement.
- Long operations (extract, export) MUST use `st.progress` or `st.spinner`.
- Do NOT use `st.experimental_*` APIs — use only stable Streamlit ≥1.35 APIs.

## Design Check
Confirm `docs/DESIGN.md` Section 9 (Web UI) is approved before writing any page code.

## Test Requirements (`tests/test_web_ui.py`)
Use `streamlit.testing.v1.AppTest` for all tests.
- `test_auth_blocks_unauthenticated` — unauthenticated user sees only password form
- `test_auth_correct_password` — correct password sets session_state authenticated=True
- `test_auth_wrong_password` — wrong password shows error, remains unauthenticated
- `test_extract_page_preview` — mock APIClient; preview shows conversation count
- `test_extract_over_500_guard` — count > 500 shows warning + checkbox before Extract enabled
- `test_browse_filter_by_subtopic` — filter reduces displayed rows
- `test_review_queue_approve` — clicking Approve updates review_status in DB
- `test_export_md_download_button` — Export Markdown produces download button

## Commit
After tests pass: `git commit -m "feat(web-ui): implement Streamlit multi-page app with auth, browse, review, export"`


