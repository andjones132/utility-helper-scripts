# utility-helper-scripts

A curated library of Python utility / automation scripts designed to eliminate time-consuming repetitive tasks.

Every script is: easy to find, clearly documented, testable, and launchable with a single click or command.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/andjones132/utility-helper-scripts.git
cd utility-helper-scripts

# 2. Create virtual environment and install deps
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 3. Run tests to verify green baseline
pytest tests/ -q

# 4. Launch a script (example)
python scripts/compress_folders_filtered.py
```

---

## Scripts

| Script                                                               | Type        | Purpose                                                                      | Run                                           |
| -------------------------------------------------------------------- | ----------- | ---------------------------------------------------------------------------- | --------------------------------------------- |
| [compress_folders_filtered.py](scripts/compress_folders_filtered.py) | Tkinter GUI | Archive multiple repo/project folders to individual `.7z` files in one click | `python scripts/compress_folders_filtered.py` |

Full documentation: [docs/utility-helper-scripts.md](docs/utility-helper-scripts.md)

---

## Script: Compress Folders Filtered (Repo Archiver)

**The "push here" button for backing up all your repos.**

1. Run `python scripts/compress_folders_filtered.py`
2. Click **Browse…** next to _Repos parent folder_ — select the folder that **contains** your repo folders.
3. Click **Browse…** next to _Output folder_ — pick where the `.7z` files go.
4. Click **▶ Start Archiving**.

Each subdirectory becomes its own `.7z` archive. Junk folders (`.venv`, `node_modules`, `__pycache__`, etc.) are excluded automatically.

> **Requirements:** Python 3.11+ · [7-Zip](https://7-zip.org) installed

---

## Jupyter Notebook

The [notebooks/utility_helper_scripts.ipynb](notebooks/utility_helper_scripts.ipynb) notebook provides:

- A clickable **Table of Contents** of all scripts.
- Short description and launch cell for each script.
- Interactive runner for scripts that support a CLI interface.

```bash
jupyter notebook notebooks/utility_helper_scripts.ipynb
```

---

## Development

### Repo Layout

```
utility-helper-scripts/
├── .github/
│   ├── copilot-instructions.md   ← Copilot repo-level charter entry point
│   ├── copilot/omni-prompt.md    ← UBER OMNI PROMPT (reliability charter)
│   └── prompts/                  ← Slash-command prompt files for Copilot Chat
│       ├── audit-retrofit.prompt.md
│       ├── new-script.prompt.md
│       ├── test-doc-align.prompt.md
│       └── commit-push.prompt.md
├── docs/
│   └── utility-helper-scripts.md   ← All script docs (single source of truth)
├── notebooks/
│   └── utility_helper_scripts.ipynb
├── scripts/
│   └── compress_folders_filtered.py
├── tests/
│   └── test_compress_folders.py
├── CHANGELOG.md
├── ERROR_LOG.md
├── README.md
└── requirements.txt
```

### Adding a New Script

Use the Copilot Chat slash command `/new-script` — it will walk you through adding a test, implementation, docs entry, and CHANGELOG update.

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=scripts --cov-report=term-missing
```

### Commit Convention

```
feat(scope): description
fix(scope): description
test(scope): description
docs(scope): description
chore(scope): description
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Error Log

See [ERROR_LOG.md](ERROR_LOG.md).
