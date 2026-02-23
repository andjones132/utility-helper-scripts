---
name: "audit-retrofit"
description: "Audit repo against the reliability charter and open targeted PRs"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md`. If it is missing, create it using the standard
Anti-Hallucination & Reliability Charter. Then perform an **Audit & Retrofit** and propose PRs.

## Goals
- Enforce retrieval gate before any LLM/API call (`if no results → return refusal`)
- Add freshness/metadata checks on API responses and cached data
- Add conflict detection policy (STRICT refuses; BALANCED reports)
- Wire the MODE flag (Exploration, Balanced, Strict) through all agent prompts
- Add startup and periodic health checks for API connectivity
- Add tests for zero-hit refusal, auth failure, and rate-limit handling
- Update README with refusal behavior and configuration instructions

## Steps

### 1. Discovery
- Scan `src/` for any locations that call the OpenAI API or subprocess.
- Identify missing retrieval gates (calls where `len(results) == 0` is not handled).
- Identify missing MODE branching.
- Check `tests/` mirrors `src/` structure.

### 2. Diagnosis
- For each gap, propose the smallest code change that enforces the guardrail.
- Keep API providers abstracted behind client interfaces so tests can mock calls.

### 3. Delivery (PRs)
Open one PR per area (guardrails, health checks, tests, docs). Each PR MUST include:
- Passing tests
- Updated `docs/ERROR_LOG.md` if a bug was found
- README section: "Reliability Rules & Refusal Behavior"

## Output
- A list of proposed PRs (title + summary)
- The diffs you intend to create
- A short commit message per PR

## Refusal Condition
If an invariant from the charter cannot be satisfied, STOP and ask a single concise question.
