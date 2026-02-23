---
name: "develop-cli"
description: "DEPRECATED — replaced by develop-web-ui"
agent: agent
---

> **DEPRECATED**
> The CLI (`src/main.py`) was removed in the v2 architecture redesign.
> The sole user-facing interface is now the Streamlit Web UI.
>
> Use `/develop-web-ui` instead.
> See `.github/prompts/develop-web-ui.prompt.md`.

## Commands and Options

### `extract`
```
python -m src.main extract [OPTIONS]

Options:
  --conversation-id TEXT    Single conversation ID to extract
  --batch-file PATH         File containing one conversation ID per line
  --project-id TEXT         Extract an entire project
  --from TEXT               ISO date filter: YYYY-MM-DD
  --to TEXT                 ISO date filter: YYYY-MM-DD
  --keyword TEXT            Filter conversations by keyword in title/content
  --output-dir PATH         Output directory (default: ./output)
  --no-organize             Skip AI subtopic organization
  --categories TEXT         Comma-separated list of fixed categories
  --format [md|pdf|both]    Output format (default: md)
  --pdf-dir PATH            Separate dir for PDFs (default: alongside .md files)
  --api-key TEXT            Override OPENAI_API_KEY env var (not recommended)
  --verbose                 Enable verbose logging
```

### `list`
```
python -m src.main list [OPTIONS]

Options:
  --project-id TEXT    List conversations within a project
  --limit INT          Max conversations to list (default: 20)
  --format [table|json]  Output format (default: table)
```

### `projects`
```
python -m src.main projects    List available projects
```

## Responsibilities
1. Parse arguments using `argparse` (stdlib — no click dependency unless user requests it).
2. Load `OPENAI_API_KEY` from environment (or `.env` file via `python-dotenv`).
3. If key is missing: print a clear error and exit code 1.
4. Orchestrate: `APIClient → Extractor → Organizer → MDExporter → PDFConverter`.
5. Print a summary on completion: conversations exported, attachments saved, PDFs created.
6. Respect `--verbose` for debug-level logging.

## Guardrails
- NEVER print the API key to stdout under any circumstances, even in verbose mode.
- Exit code 0 = success; 1 = user error (bad args, missing key); 2 = API error.
- If `--format pdf` is requested but WeasyPrint is not installed, print a clear error
  with install instructions and exit 1.

## Design Check
Confirm `docs/DESIGN.md` section "CLI" exists and is approved.

## Test Requirements (`tests/test_cli.py`)
- `test_extract_no_api_key` — missing env var → exit code 1 + clear message
- `test_extract_by_id` — end-to-end with all dependencies mocked
- `test_list_command` — table output contains expected conversation titles
- `test_projects_command` — lists project names from mocked API

## Commit
After tests pass: `git commit -m "feat(cli): implement extract, list, and projects commands"`
