---
name: "update-error-log"
description: "Append a new entry to docs/ERROR_LOG.md with resolution and lessons learned"
agent: agent
---

You MUST read `.github/copilot/omni-prompt.md` before proceeding.
Mode: BALANCED

## Task
Append a new structured entry to `docs/ERROR_LOG.md`.

## Entry Template
```markdown
---

## ERROR-<NNN>: <Short Title>

**Date:** YYYY-MM-DD  
**Severity:** Critical | High | Medium | Low  
**Component:** api-client | extractor | organizer | md-exporter | pdf-converter | cli | tests  
**Status:** Open | Resolved | Mitigated  

### Description
<What happened? What was the unexpected behavior?>

### Root Cause
<Cite the file and line range where the bug originated. No guessing — if unknown, say "Unknown".>

### Resolution
<What was done to fix it? Cite the commit hash if available.>

### Lessons Learned
<What should agents/developers do differently going forward?>

### Instruction Update Required
- [ ] Updated `.github/instructions/<relevant>.instructions.md`
- [ ] Updated `.github/copilot/omni-prompt.md` (if charter-level lesson)
```

## Steps
1. Read `docs/ERROR_LOG.md` to find the next entry number (ERROR-NNN).
2. Fill in all fields — do not leave any blank. Use "N/A" only where truly not applicable.
3. For "Lessons Learned": be specific enough that an agent reading it would behave differently.
4. Check the box(es) under "Instruction Update Required" and actually make those updates.
5. Commit: `git commit -m "docs(error-log): add ERROR-<NNN> <short title>"`
