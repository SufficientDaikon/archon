# Validation Checklist — Per-Step

## Core Checks (EVERY step)
- [ ] **Result exists** — Did the step produce an output?
- [ ] **Result matches expected** — Does the output match what was planned?
- [ ] **Evidence is fresh** — Was verification run NOW, not assumed?
- [ ] **No constraints violated** — Does the result respect all requirements?

## Quality Checks (moderate+ complexity)
- [ ] **No side effects** — Did anything break that shouldn't have?
- [ ] **Edge cases considered** — What happens at boundaries?
- [ ] **Error handling present** — What happens when things go wrong?
- [ ] **Dependencies satisfied** — Are all prerequisite steps verified?

## Deep Checks (complex+ tasks)
- [ ] **Alternative approaches considered** — Was this the best option?
- [ ] **Assumptions documented** — What was assumed but not proven?
- [ ] **Rollback possible** — Can this step be undone if needed?
- [ ] **Consistent with prior steps** — No contradictions with earlier conclusions?

## Confidence Scoring

| Level | Criteria | Action |
|-------|----------|--------|
| **High** | Fresh evidence confirms result; no assumptions | Proceed to next step |
| **Medium** | Evidence exists but some assumptions remain | Document assumptions, proceed with caution |
| **Low** | Significant assumptions; limited evidence | STOP — gather more evidence before proceeding |

## Failure Protocol

If validation FAILS:
1. **Do NOT proceed** to the next step
2. **Identify** what specifically failed
3. **Diagnose** why it failed
4. **Fix** the issue
5. **Re-validate** from scratch (not just the fix)
6. **Document** what went wrong and what was learned
