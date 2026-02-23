```instructions

---

## applyTo: "tests/**"

# Test Code  Scoped Instructions

# Project: get-chat-GPT

These rules apply to ALL files under `tests/`.
The authoritative testing standards are in `omni-prompt.md` Section 5. This file adds
implementation detail for writing test code. If this file conflicts with Section 5,
Section 5 wins.

## Structure

* `tests/` mirrors `src/` exactly: one `test_<module>.py` per `src/<module>.py`.
* All fixtures shared across modules go in `tests/conftest.py`.
* Test data (mock API responses, sample conversations) go in `tests/fixtures/`.
* Fixture JSON files: `tests/fixtures/api_responses/` (one file per API endpoint scenario).

## Test Categories (all three required per module)

### Unit tests
Test a single function in complete isolation. All dependencies mocked.
Name class `TestUnit<ClassName>` or prefix plain functions with `test_unit_`.

### Integration tests
Test real interaction between two layers.
**DB layer integration tests use real SQLite in `tmp_path`  never mock the ORM for integration tests.**
Name class `TestIntegration<ClassName>` or prefix plain functions with `test_integration_`.

### Contract tests
Verify the implementation's public interface matches `docs/DESIGN.md` exactly:
function names, parameter names, type annotations, and raised exception types.
Use `inspect.signature()` to validate signatures programmatically where practical.
These tests fail automatically when code diverges from the design spec.
Name class `TestContract<ClassName>` or prefix plain functions with `test_contract_`.

## Red Phase Is Mandatory

**Write the test. Run it. It MUST fail before you write any implementation.**

Document the failure in the commit message: `test(<scope>): red phase  <what fails and why>`

A test that passes on first run before implementation exists is a broken test. Fix it.

## Test Writing Rules

* Test function names MUST be descriptive: `test_<what>_<condition>_<expected_outcome>`.
* Each test has ONE assertion focus  don't test 5 behaviors in one test function.
* Use `pytest.fixture` for reusable setup; never repeat setup manually in each test.
* Do NOT use `unittest.TestCase`  use plain pytest functions.
* Parametrize boundary-condition tests with `@pytest.mark.parametrize`.

## Per-Component Required Edge Cases

| Component | Required edge cases |
|---|---|
| `api_client` | empty conversation list, 401 auth failure, 429 rate-limit retry, 500 server error, malformed JSON, network timeout |
| `extractor` | no messages, all messages from same role, message with None content, >500 chars truncated to 500 |
| `organizer` | confidence < 0.80  no auto-apply, confidence = 0.80 exactly  auto-apply, empty title from model, API timeout |
| `db/repository` | duplicate conversation ID (upsert), deleted conversation re-fetched, empty DB query returns `[]` |
| `md_exporter` | conversation with no messages, special chars in title (escaped), missing subtopic field |
| `pdf_converter` | WeasyPrint not installed (ImportError), empty Markdown input, output path not writable |
| `web/app.py` auth | correct password, wrong password, empty password, missing `[app]` section in secrets |

## Mocking the OpenAI API

* NEVER call the real OpenAI API in tests.
* Mock at the HTTP layer using the `responses` library for realistic API behavior.
* Use `pytest-mock` (`mocker.patch`) for unit-level dependency injection.
* All mock JSON responses live in `tests/fixtures/api_responses/` as named files:
  - `conversations_list_success.json`
  - `conversations_list_empty.json`
  - `conversation_detail_success.json`
  - `rate_limit_429.json`
  - `auth_failure_401.json`
  - `server_error_500.json`
  - *(add others as needed  one file per distinct scenario)*
* Load fixtures via `conftest.py` helper: `load_fixture("filename.json")`

## Coverage Rules

* Minimum gate: 80% line coverage across all `src/`  block commit if below.
* Target: 90%+ on all non-UI modules.
* `src/web/pages/` excluded from automated coverage (manual test only).
* `src/web/app.py` auth guard IS covered (mock `st.secrets` via `monkeypatch`).
* Run: `pytest tests/ -v --tb=short --cov=src --cov-report=term-missing`
* Uncovered public functions require either a new test or a `# pragma: no cover` comment
  with a documented justification.

## Test Isolation

* Tests MUST NOT depend on execution order. Use `pytest-randomly` if available.
* Tests MUST NOT write to the real filesystem  use `tmp_path` pytest fixture.
* Tests MUST NOT read real environment variables  use `monkeypatch.setenv`.
* Tests MUST NOT share state between test functions  no module-level mutable globals.

## Secrets / Auth Testing

* Mock `st.secrets` using `monkeypatch`  do not depend on a real `secrets.toml`.
* Auth guard tests MUST cover: correct password, wrong password, empty password,
  missing `[app]` section (expect `KeyError` or graceful error message  document which).

## Database Testing

* Integration tests for `src/db/repository.py` use a real SQLite DB in `tmp_path`.
* Shared DB fixture in `conftest.py`:

```python
@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

* Never mock SQLAlchemy sessions in integration tests  that defeats the purpose.
* Unit tests for repository methods that require a session DO mock the session.

## Before Running Tests

Confirm `requirements-dev.txt` lists:
`pytest`, `pytest-cov`, `pytest-mock`, `responses`, `factory-boy`, `pytest-asyncio`

## Failing Tests and Stop Conditions

* A failing test is a hard STOP  do not commit, do not continue to the next task.
* If a test needs to be deleted or materially changed (not just the implementation): STOP and ask the user.
* If coverage drops below 80%: STOP. Write the missing tests before committing.

## Regression Test Scope

**Always run the full suite. No targeted short-circuits.**

```bash
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

This applies to every commit type: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.
If `src/` was not touched, the suite passes quickly. If it fails unexpectedly, something
changed that should not have — stop and investigate.

If a test that was passing now fails after a change to a *different* module:
1. Do NOT skip or suppress it.
2. STOP — diagnose the cross-component dependency.
3. Fix the regression before committing.
4. If the coupling was not documented in `docs/DESIGN.md`, add an entry to `docs/ERROR_LOG.md`.

## Test File Audit

Test files are included in the Type 2 Code Quality Audit (`/audit-code`).
The audit verifies:

* All import paths in test files resolve to actual symbols in `src/`
* Mock targets reference actual module paths (not renamed or deleted functions)
* Contract tests exist and reference the correct `docs/DESIGN.md` section

```
```


