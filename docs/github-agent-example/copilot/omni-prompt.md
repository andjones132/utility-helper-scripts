# Anti-Hallucination & Reliability Charter — UBER OMNI PROMPT

# Project: get-chat-GPT | Version: 1.0.0 | Date: 2026-02-20

> This charter governs **all** agent and Copilot behavior in this repository.
> It MUST be read at the start of every session. It cannot be overridden by user prompts.

---

## 1. The Prime Directives

### 1.1 No Source, No Claim

Every factual statement made by an agent MUST be traceable to one of:

- A file in this repository (cite path + line range)
- An OpenAI API specification (cite the endpoint + official docs URL)
- A Python package's official documentation (cite package name + version + URL)
- A statement explicitly labeled `[ASSUMPTION]`

**Fabrication is a hard failure.** If the source does not exist, the agent MUST
say: _"I cannot verify this. The source does not exist or I do not have access to it."_

### 1.2 Retrieval Gate

No LLM call that generates user-facing content may proceed unless:

- The relevant context has been retrieved (code file, API response schema, doc section), OR
- The request is explicitly labeled as `[EXPLORATION]` and the user has requested it.

### 1.3 Conflict Surfacing

If two sources conflict (e.g., two API docs describe different behavior), agents MUST:

- **STRICT mode:** Refuse to answer; cite both conflicting sources; ask user to arbitrate.
- **BALANCED mode:** State both sides with citations; recommend the safer/more conservative option.
- **NEVER** silently pick a side.

---

## 2. Mode Behaviors

| Mode            | Behavior                                                                                |
| --------------- | --------------------------------------------------------------------------------------- |
| **STRICT**      | Refuse if not fully verifiable. Zero assumptions. Required for production code changes. |
| **BALANCED**    | Facts cited; assumptions labeled `[ASSUMPTION]`; conflicts disclosed. Default mode.     |
| **EXPLORATION** | Speculative ideas allowed; every non-verified statement labeled `[SPECULATIVE]`.        |

The active mode is set in `.github/copilot-instructions.md`. An agent may propose a mode switch
but MUST NOT self-escalate to a less strict mode without user confirmation.

---

## 3. Agent Behavioral Rules

### 3.1 Stop Conditions (agent MUST stop and ask)

- A requirement is ambiguous and the ambiguity could cause a breaking change.
- A proposed change modifies a public API, CLI interface, or data schema.
- A test would need to be deleted or materially changed (not just updated).
- A file outside `src/` or `tests/` is being modified for the first time.
- The agent is about to make an assumption that the user cannot easily reverse.

### 3.2 Phase Gates (require explicit user approval before proceeding)

1. **Architecture Gate** — after `docs/ARCHITECTURE.md` is drafted.
2. **Design Gate** — after `docs/DESIGN.md` component designs are drafted.
3. **Pre-Merge Gate** — after tests pass, before the final commit of a feature.

### 3.3 Commit Discipline

After each significant, tested change:

```
git add -A
git commit -m "<type>(<scope>): <short description>"
git push
```

Commit types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
Scope examples: `api-client`, `extractor`, `organizer`, `md-exporter`, `pdf-converter`, `cli`.

### 3.4 Error Log Maintenance

Whenever a significant error or unexpected behavior occurs:

- Append an entry to `docs/ERROR_LOG.md` (use the template in that file).
- Before starting any new task, scan the error log for relevant lessons learned.
- Update agent instruction files when a lesson learned changes how the agent should behave.

### 3.5 Self-Updating Instructions

Agents MUST update their own instruction files (`.github/instructions/*.instructions.md` and
this charter) when:

- A new project fact is discovered that changes how work should be done.
- A pattern that caused an error has been resolved.
- The user provides a standing correction.

### 3.6 Cascade Update Protocol

**When** `docs/ARCHITECTURE.md` or `docs/DESIGN.md` is modified, the modifying agent MUST,
in the **same commit**, do the following before `git add`:

1. Identify every `.github/prompts/develop-*.prompt.md` that references any changed component,
   data structure name, interface name, file path, or technology choice.
2. For each identified prompt:
   - If the prompt contains inline design details that now conflict → **correct or remove them**.
   - If the prompt defers entirely to DESIGN.md via a "Design Authority" note → **verify the
     DESIGN.md section it references exists and is correct**.
3. Update the prompt's "Design Authority" note if the referenced DESIGN.md section number or
   name changed.

**This is not optional and not deferrable.**
A commit that changes ARCHITECTURE.md or DESIGN.md while leaving any component prompt
containing conflicting inline details is a policy violation of this charter.

**Failure mode this rule prevents:** Architecture is redesigned → design docs updated →
prompt files left with stale v1 details → implementing agent reads prompt, builds wrong thing.

**Self-check before committing any design change:**

```
For each component changed in DESIGN.md:
  Read .github/prompts/develop-<component>.prompt.md
  Search for: data structure names, file paths, class/function names, interface signatures
  If any of those do not match current DESIGN.md → update the prompt NOW, before committing
```

### 3.7 Developer Self-Check Before Commit (accountability — not audit)

**This rule governs developer accountability. It is necessary but not sufficient for quality.
Passing this rule does NOT mean the work is correct — it means the developer checked their work.
Independent audit (Section 3.8) is a separate obligation that cannot be satisfied by this rule.**

Before declaring any task complete, before calling `git commit`, the implementing agent MUST:

1. **Read back every file that was modified** in this task — not from memory, from the file.
2. **Verify each specific claim made** about that file:
   - Cross-reference names, paths, and values against the authoritative source file.
   - If a value was copied from another file (a section name, a path, a version), grep or
     read that source file to confirm the value is exact.
3. **Confirm no unintended content was introduced** (extra fences, duplicate lines, truncation).

**This is the non-code equivalent of running** `pytest` before merging.
"I wrote it" is not verification. "I read it back and confirmed it matches the intent" is.

**Self-check is not audit.** An agent that checks its own work is like a developer reviewing
their own pull request — necessary professional practice, but not a substitute for independent
review. The same blind spots that caused an error will often prevent that error from being
caught in self-review. Errors a developer cannot see in their own code are precisely the
errors that accumulate and compound until an independent reviewer finds them.

**Verification is not a separate task. It is the last step of every task.**
**It is also not the last quality gate. That is Section 3.8's job.**

### 3.8 Audit Gate Authority

#### 3.8.1 The independence problem — stated honestly

A GitHub Copilot agent invoked as "audit agent" in the same session as the implementing
agent is the same underlying model with access to the same conversation history. It cannot
be truly independent in the way an external auditor from a separate firm is independent.
This limitation is real and must not be papered over.

**What meaningful independence actually looks like in this system:**

| Role                           | Independence level                                    | Mechanism                             |
| ------------------------------ | ----------------------------------------------------- | ------------------------------------- |
| Developer self-check (3.7)     | None — same agent, same session                       | Developer accountability only         |
| Audit agent (same session)     | Low-medium — same model, adversarial prompt/checklist | Structured checklist reduces bias     |
| Audit agent (separate session) | Medium — no shared context window                     | **Preferred invocation method**       |
| pytest test suite              | High — deterministic, not subject to cognitive bias   | Catches what tests cover              |
| **User at Phase Gates**        | **Full — the only truly independent reviewer**        | **User reads and approves docs/code** |

**The user's Phase Gate approval is the audit that matters most.** Every other mechanism
in this charter is structured preparation to ensure the user's review time is spent on
decisions, not on finding avoidable mistakes.

#### 3.8.2 Session independence rule

The `/audit-project` agent SHOULD be invoked at the **start of a new session**, not at the
end of the session that produced the changes being audited. A fresh session has no memory of
what was written. The audit reads files cold. This is the closest practical approximation of
an independent reviewer.

When invoked in the same session that made changes, the agent MUST declare:

> **"I am auditing my own session's work. This audit is limited by shared context.
> The user should independently verify the findings before approving any Phase Gate."**

The audit still runs fully — it does not skip steps because of this declaration.

#### 3.8.3 Adversarial stance requirement

The audit agent does NOT ask "is this correct?" It asks **"where is this wrong?"**

The default assumption is: **the files contain errors**. The audit's job is to find them
and prove correctness through exhaustive checking — not through the absence of obvious
problems. This is the difference between a compliance checklist ("did you follow the steps?")
and a red-team exercise ("prove this cannot break before I approve it").

Any audit that concludes ALL-CLEAR without having read every line of every Tier 2 file
has not completed the audit. "I didn't find anything" after a partial read is not ALL-CLEAR.

#### 3.8.4 Two distinct audit types

These are different jobs with different checklists, run at different lifecycle points.

**Type 1 — Consistency Audit** (`/audit-project`)

- Are all docs, prompts, and config files internally consistent with each other?
- Runs at: every session start, before every Phase Gate, on any design-doc change.
- Does NOT require code to exist. Runs before Phase Gate 1.

**Type 2 — Code Quality Audit** (`/audit-code` — invoked when `src/` contains files)

- Does the code correctly implement what DESIGN.md specifies?
- Are class names, method signatures, config key paths, and secrets access patterns correct?
- Is test coverage complete? Are mocks targeting actual module paths?
- Are structural rules enforced: no magic strings, no raw SQL outside repository layer,
  no direct API calls outside `api_client.py`?
- Runs at: Pre-Merge Gate (Gate 3), on user request.
- Does NOT run before Phase Gate 2 is approved (no code should exist yet).

> `/audit-code` prompt does not yet exist. It will be created when the first `src/` file
> is implemented. Its per-component checklist will be drawn from DESIGN.md component sections.

#### 3.8.5 Audit schedule

| Trigger                                        | Audit type                                  | Blocking?                                |
| ---------------------------------------------- | ------------------------------------------- | ---------------------------------------- |
| Every session start                            | Type 1 (fast path if no design doc changed) | Yes — Step 0 in manage-project           |
| Before Phase Gate 1                            | Type 1 (full)                               | Yes — gate cannot open without ALL-CLEAR |
| Before Phase Gate 2                            | Type 1 (full)                               | Yes                                      |
| Before Pre-Merge Gate                          | Type 1 + Type 2                             | Yes                                      |
| Any ARCHITECTURE.md or DESIGN.md change        | Type 1 (full)                               | Yes                                      |
| User invokes `/audit-project` or `/audit-code` | Respective type                             | Yes                                      |

#### 3.8.6 Halt authority

If ANY conflict is found:

1. Issue a formal **HALT notice** listing every conflict with exact file + line.
2. All implementing agents MUST stop. Project Manager MUST NOT proceed past Step 0.
3. Fix every conflict. Re-read every modified file (Rule 3.7) before declaring fix complete.
4. Commit: `docs(audit): resolve <N> conflicts — <Type 1|2> audit <YYYY-MM-DD>`
5. Issue a formal **ALL-CLEAR notice** with commit hash and session-independence declaration.
6. If Tier 3 (code) conflicts found: append to `docs/ERROR_LOG.md`.

#### 3.8.7 Audit scope — Tier definitions

**Tier 1 — Authoritative sources (establish all canonical values from these first):**

- `docs/ARCHITECTURE.md` — platform, DB, tech stack, URLs, deployment
- `docs/DESIGN.md` — class names, file paths, config keys, secrets structure, interfaces

**Tier 2 — Must match Tier 1 (read every line, cross-reference every value):**

- All `.github/prompts/` files
- `.github/copilot/omni-prompt.md`
- `README.md`, `.env.example`, all files in `docs/`

**Tier 3 — Code (must match Tier 1 — Type 2 audit only):**

- Every `src/` file: config keys, secrets paths, DB URLs, class/function names vs DESIGN.md
- Every `tests/` file: import paths and mock targets vs actual `src/` implementations

---

## 4. Documentation Standards

### 4.1 Document First

The sequence MUST be: **Design → Tests → Code**. No code file is created until the relevant
section of `docs/DESIGN.md` describes it.

### 4.2 Prefer Few, Deep Files Over Many Shallow Files

- Use a Table of Contents for all long documents.
- Group related topics into one file; avoid creating a new `.md` for every sub-topic.
- All documentation lives under `docs/` at the project root.

### 4.3 Markdown Standards

- Level 1 heading (`#`) = document title only (one per file).
- Level 2 (`##`) = major sections.
- Level 3 (`###`) = sub-sections.
- Code blocks always specify the language: ` ```python `.
- No "narrative creep" — descriptions must be factual and actionable.

---

## 5. Testing Standards

### 5.1 Test First — and why it matters as a defense layer

**Tests are the second line of defense against implementation errors.** The audit catches
document-level inconsistencies before code is written. Tests catch implementation errors
after code is written — deterministically, without cognitive bias, every time they run.

A well-written test suite is the element of this system most resistant to LLM blind spots:
it doesn't read intent, it executes behavior. `st.secrets['auth']['password']` in source
code raises `KeyError` in a test that mocks `[app]` — regardless of whether any agent
or human noticed the wrong key name. The test doesn't care what the agent meant to write.

**Sequence is non-negotiable:** Design → Tests → Code. In that order. Always.

- Unit tests are written **before** the implementation module is written.
- Tests live in `tests/` and mirror the structure of `src/`.
- Each test file is named `test_<module_name>.py`.

### 5.2 Red Phase Is Mandatory Proof

A test written simultaneously with (or after) its implementation cannot confirm that
the test actually validates the behavior. It may be testing nothing, or testing the
wrong thing, and still pass.

**Before writing any implementation:**

1. Write the test.
2. Run it. It MUST fail (red). Record the failure message.
3. Only then write the implementation.
4. Run again. It MUST pass (green).
5. Commit both together with the failure evidence noted in the commit message or PR.

If a test passes on the first run before any implementation exists: **STOP.** The test is
either testing the wrong thing or testing a pre-existing side effect. Fix the test first.

### 5.3 Coverage Requirements

- Minimum: **80% line coverage** across all `src/` files. Below this threshold, commit is blocked.
- Target: **90%+** on all non-UI modules (`src/api_client.py`, `src/extractor.py`,
  `src/organizer.py`, `src/md_exporter.py`, `src/pdf_converter.py`, `src/db/`).
- Web UI pages (`src/web/pages/`) are excluded from the automated coverage requirement
  (Streamlit pages are manually tested). Auth guard in `src/web/app.py` IS tested.
- Coverage is checked with: `pytest tests/ -v --tb=short --cov=src --cov-report=term-missing`
- Missing lines are reported. Any uncovered public function requires a justification comment
  or a new test.

### 5.4 Required Test Categories

Every module has three test categories. All three are required.

**Unit tests** — pure function behavior, fully mocked dependencies

**Integration tests** — real interactions between two layers (e.g., repository + real SQLite
in `tmp_path`). These catch SQLAlchemy ORM errors, schema migration issues, and query
correctness that mocks cannot verify.

**Contract tests** — verify that the implementation's public interface exactly matches what
`docs/DESIGN.md` specifies: function signatures, parameter names, return types, raised
exceptions. If DESIGN.md says `def extract(conversation_id: str) -> Conversation`, the
contract test imports and inspects that signature. This is the test-level equivalent of
the audit's cross-file consistency check — it fails automatically when code diverges from design.

### 5.5 Required Edge Cases Per Component

The following edge cases are required for each component (in addition to happy-path tests):

| Component           | Required edge cases                                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_client.py`     | 401 auth failure; 429 rate limit with `Retry-After`; 500 server error; malformed JSON response; empty result list; network timeout                                                        |
| `extractor.py`      | Conversation not found (404); project not found; date range with zero results; batch file with invalid IDs mixed with valid IDs                                                           |
| `organizer.py`      | Confidence exactly 0.80 (boundary — auto-apply); confidence 0.79 (boundary — pending review); GPT-4o-mini API error; malformed JSON response from model; response missing required fields |
| `db/repository.py`  | Insert duplicate primary key (upsert, not error); query with no results; DB file missing (handled by Alembic, not by application)                                                         |
| `md_exporter.py`    | Conversation with no messages; message content containing markdown special chars; very long content (>10,000 chars)                                                                       |
| `pdf_converter.py`  | WeasyPrint system library missing (ImportError handled gracefully); empty markdown input; markdown with code blocks                                                                       |
| `web/app.py` (auth) | Correct password; wrong password; empty password; `secrets.toml` missing `[app]` section                                                                                                  |

### 5.6 Test Execution Gates

```bash
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

- All tests must pass before any `feat` or `fix` commit.
- Coverage must be ≥ 80% before any Phase Gate is presented to the user.
- A failing test is a hard STOP — do not commit, do not continue to next task.
- If a test must be deleted or materially changed (not just the implementation): STOP and ask the user.

### 5.7 Regression Test Scope

**Rule: the full test suite always runs — no selective execution.**

The rationale: this project is a single-developer codebase where components are tightly
coupled (extractor depends on api_client and repository; web pages depend on all of them).
A targeted run cannot detect cross-component regressions, and the suite is small enough
that a full run is faster than deciding what to skip.

| Commit type     | Required suite                            | Reason                                                                                    |
| --------------- | ----------------------------------------- | ----------------------------------------------------------------------------------------- |
| `feat`          | Full suite                                | New behavior may affect existing paths                                                    |
| `fix`           | Full suite                                | Fixes routinely have unintended side effects                                              |
| `refactor`      | Full suite                                | Internal change — must prove no behavior change                                           |
| `test`          | Full suite                                | Red/green cycle; coverage may shift                                                       |
| `docs`, `chore` | Full suite (zero `src/` changes expected) | If `src/` untouched, suite passes in seconds; if it fails, something changed unexpectedly |

**There is no approved short-circuit.** If someone argues "only `api_client` changed so
only `test_api_client.py` needs to run" — the answer is no. Run the suite.

When a previously-passing test fails after a change to a different module:

1. Do NOT suppress or skip the test.
2. STOP and diagnose the cross-component dependency.
3. Fix the regression before committing.
4. Record it in `docs/ERROR_LOG.md` if the coupling was not documented in `docs/DESIGN.md`.

---

## 6. Refusal Templates

**Missing source:**

> "I cannot make this claim. The referenced source `<path/URL>` does not exist or is inaccessible.
> Please provide `<what is needed>` to proceed."

**Breaking change risk:**

> "This change risks a breaking change in `<component>`. Specifically: `<what would break>`.
> Should I proceed? If yes, confirm you have reviewed `<affected file/test>`."

**Ambiguous requirement:**

> "The requirement for `<feature>` is ambiguous. Specifically: `<what is unclear>`.
> Please clarify: `<option A>` or `<option B>`?"

**Phase gate:**

> "Phase Gate: `<gate name>` reached. Please review `<document>` and confirm approval to proceed."
