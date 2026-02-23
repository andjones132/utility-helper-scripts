# Changelog

All notable changes to this project are documented here.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) — `type(scope): description`

---

## [Unreleased]

---

## [1.2.0] — 2026-02-23

### Added

- `chore(agent): create AGENTS.md root halt gate — protected files + mandatory approval process`
- `chore(agent): add .github/prompts/audit-project.prompt.md — independent audit agent with halt authority`
- `chore(agent): add .github/prompts/manage-project.prompt.md — orchestrator with Step 0 audit dispatch`
- `chore(agent): add .github/instructions/python-src.instructions.md (applyTo: scripts/**/*.py)`
- `chore(agent): add .github/instructions/tests.instructions.md (applyTo: tests/**)`
- `chore(agent): add .github/instructions/docs.instructions.md (applyTo: docs/**)`
- `chore(agent): add .github/instructions/prompts.instructions.md (applyTo: .github/prompts/**)`
- `docs: add docs/omni-prompt-setup-guide.md — project-agnostic governance implementation guide`

### Changed

- `chore(agent): omni-prompt.md v2.0.0 — add GOVERNANCE section (first), Phase Gates, Cascade Update Protocol, Developer Self-Check, Audit Gate Authority, adversarial audit stance, session independence model, halt authority tiers`
- `chore(agent): copilot-instructions.md v2.0.0 — add STOP rule, auto-session-start protocol, slash command table, updated repo layout with new files`

---

## [1.1.0] — 2026-02-23

### Added

- `feat(compress): add run_archive() with subprocess timeout (SUBPROCESS_TIMEOUT=3600s)`
- `feat(compress): add list_repo_subfolders() with typed exceptions (FileNotFoundError, NotADirectoryError)`
- `feat(compress): report archive size (MB) in log after successful compression`
- `feat(compress): per-archive error recovery — skips failed folder, continues to next`
- `test(compress): full pytest suite — find_7z, build_7z_command, list_repo_subfolders, run_archive`
- `docs(compress): full documentation in docs/utility-helper-scripts.md`
- `chore(repo): init git repo, create GitHub repo (andjones132/utility-helper-scripts)`
- `chore(agent): add .github/copilot-instructions.md (repo entry point)`
- `chore(agent): add .github/copilot/omni-prompt.md (UBER OMNI PROMPT charter)`
- `chore(agent): add .github/prompts/ — audit-retrofit, new-script, test-doc-align, commit-push`
- `chore(repo): add .gitignore, requirements.txt, README.md, CHANGELOG.md, ERROR_LOG.md`
- `chore(notebooks): add utility_helper_scripts.ipynb with TOC and launcher`

### Changed

- `refactor(compress): move script from compress-folders-filtered.py to scripts/compress_folders_filtered.py`
- `refactor(compress): explicit_path="" now treated as None (no explicit path); raised ValueError only if non-empty path doesn't exist`
- `refactor(compress): _run_archives now catches per-folder exceptions and logs without halting all work`

### Fixed

- `fix(compress): subprocess.run() was missing timeout= parameter — all calls now use SUBPROCESS_TIMEOUT`
- `fix(compress): bare except in original _run_archives replaced with typed exception handling`

---

## [1.0.0] — 2026-02-23

### Added

- `feat(compress): initial Tkinter GUI repo archiver using 7-Zip (compress-folders-filtered.py)`
