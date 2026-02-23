
---

## applyTo: "src/\*\*"

# Python Source Code — Scoped Instructions

# Project: get-chat-GPT

These rules apply to ALL files under `src/`.

## Module Structure

* Every module must have a module-level docstring describing its purpose, inputs, and outputs.
* Public functions and methods must have docstrings with Args, Returns, and Raises sections.
* Use type hints on all public function signatures.
* Imports order: stdlib → third-party → local (separated by blank lines).

## Data Models (`src/models.py`)

* All data structures use `@dataclass` (not plain dicts).
* Use `Optional[T]` for fields that may be None.
* Do NOT use mutable default arguments (use `field(default_factory=list)`).

## API Client (`src/api_client.py`)

* All HTTP calls go through a single `_request(method, path, **kwargs)` method.
* Auth header is set once at client init; never re-read the env var on each call.
* Implement `_retry_with_backoff(fn, max_retries=3)` for transient errors.
* Never call `time.sleep()` directly in tests — use the retry abstraction.

## Error Handling

* Raise specific exception types (`AuthenticationError`, `RateLimitError`, `APIError`,
  `FeatureNotAvailableError`) — never `raise Exception("...")`.
* All exception types are defined in `src/exceptions.py`.
* Log exceptions with `logging.error(...)` before re-raising.

## Secrets

* NEVER print, log, or include API keys in any output, even debug logs.
* Load secrets only from `os.environ` or `python-dotenv` (`.env` file).

## Coding Patterns

* Prefer composition over inheritance.
* Keep functions under 50 lines; extract helpers if longer.
* No global mutable state.
* Use `Path` (from `pathlib`) for all filesystem operations — never `os.path.join`.

## Before Writing Any Module


1. Confirm the corresponding section in `docs/DESIGN.md` is approved.
2. Write the test file `tests/test_<module>.py` first (test-first).
3. Then implement the module to make the tests pass.


