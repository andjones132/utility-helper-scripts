---
name: "develop-pdf-converter"
description: "Build or maintain the WeasyPrint Markdown-to-PDF converter"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

> **Design Authority:** `docs/DESIGN.md` — Section `## 8. PDF Converter (\`src/pdf_converter.py\`)` is the authoritative design
> for this component. This prompt is the **task execution checklist only**.
> **If this prompt and DESIGN.md conflict, DESIGN.md governs.**
> To fix a conflict: update this prompt to match DESIGN.md. Never update DESIGN.md to match
> a stale prompt. (Rule: `omni-prompt.md` Section 3.6)

## Project Context
This module takes the Markdown output directory and converts each `.md` file (or a selected
subset) into a PDF using WeasyPrint, preserving formatting visually. Lives at `src/pdf_converter.py`.

## Pipeline per File
1. Read the `.md` file.
2. Convert Markdown → HTML using `markdown` library (with extensions: `fenced_code`,
   `tables`, `toc`, `attr_list`, `codehilite`).
3. Apply the CSS stylesheet at `src/assets/chat_export.css`.
4. Render HTML → PDF using `weasyprint.HTML(string=html).write_pdf(output_path)`.
5. Write PDF to the caller-specified output directory; path and format options are set by the
   Web UI export page (`pages/04_export.py`), not a CLI flag.

## CSS Stylesheet (`src/assets/chat_export.css`) Requirements
- Page size: A4 with 20mm margins.
- Code blocks: monospace font, light gray background, no page-break inside short blocks.
- Tables: full-width, bordered, header row shaded.
- User messages: left-aligned with a blue left border.
- Assistant messages: left-aligned with a green left border.
- `h1` = conversation title (page header area).
- Footer: page number + conversation ID.
- Avoid page breaks mid-paragraph; allow page breaks between messages.

## Responsibilities
1. `convert_file(md_path, output_dir, css_path)` → writes PDF, returns output path.
2. `convert_directory(md_dir, output_dir, css_path, pattern="*.md")` → batch conversion.
3. Report: files converted, files failed, total size.
4. If WeasyPrint raises a `FileNotFoundError` for a font or resource, log a warning and
   continue with a fallback (no custom font).

## Guardrails
- Confirm WeasyPrint is listed in `requirements.txt` before coding against it.
- Confirm `markdown` and `Pygments` (for `codehilite`) are also listed.
- Test with a known Markdown fixture — do not assert pixel-perfect output, assert file exists
  and is non-empty.
- If WeasyPrint is not installed in the test environment, skip PDF tests with `pytest.mark.skip`.

## Design Check
Confirm `docs/DESIGN.md` section "PDF Converter" exists and is approved.

## Test Requirements (`tests/test_pdf_converter.py`)
- `test_convert_file_creates_pdf` — output file exists and size > 0
- `test_convert_directory_batch` — N input files → N PDF files
- `test_missing_input_file_raises` — assert clear error for missing file
- `test_weasyprint_not_installed_skip` — graceful skip if library absent

## Commit
After tests pass: `git commit -m "feat(pdf-converter): implement WeasyPrint MD-to-PDF converter with CSS stylesheet"`
