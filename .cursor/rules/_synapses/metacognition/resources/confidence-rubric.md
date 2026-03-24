# Confidence Rubric — Calibrated Scale

Use this rubric to assign honest, evidence-based confidence ratings. The goal is **calibration** — a rating of 7/10 should mean ~70% of the time, the output is correct and complete.

---

## Three-Level Confidence Tags (Phase 2 — MONITOR)

Use these inline tags at major decision points during task execution:

### `[CONFIDENCE: HIGH]`
**Criteria — all must apply:**
- Proven pattern or well-documented approach
- Strong evidence from the task context (specs, docs, code, examples)
- Personal experience with this exact type of problem
- Low ambiguity in requirements
- Result is verifiable or has been verified

**Example triggers:** Following an explicit spec, using a known API pattern, implementing a well-defined algorithm.

### `[CONFIDENCE: MEDIUM]`
**Criteria — most apply:**
- Reasonable basis from context or experience
- Some uncertainty about edge cases or completeness
- Approach is standard but not fully validated against this specific case
- Requirements are mostly clear but have some interpretation needed
- Result is plausible but hasn't been fully verified

**Example triggers:** Adapting a known pattern to new context, making reasonable inferences from partial information, choosing between two viable approaches.

### `[CONFIDENCE: LOW]`
**Criteria — any apply:**
- Weak or no direct evidence for the approach
- Significant ambiguity in requirements
- First time with this type of problem
- Multiple viable approaches with no clear winner
- Result depends on unverified assumptions
- Working outside domain expertise

**Example triggers:** Guessing at undocumented behavior, extrapolating from limited data, making architectural decisions without full context.

---

## Ten-Point Confidence Scale (Phase 3 — REFLECT)

Use this scale for the `OVERALL CONFIDENCE` rating in the reflection phase:

| Score | Label | Evidence Required | Interpretation |
|-------|-------|-------------------|----------------|
| **10** | Certain | Verified output against requirements; all edge cases handled; tested | Output is correct and complete. No known issues. |
| **9** | Very High | Strong evidence; proven patterns; minor uncertainties only | Extremely likely correct. Minor gaps are cosmetic. |
| **8** | High | Solid approach; most requirements verified; few assumptions | Very likely correct. Small risk of minor issues. |
| **7** | Moderately High | Good basis; some unverified aspects; reasonable assumptions | Likely correct but should be reviewed at key points. |
| **6** | Moderate | Reasonable approach; several assumptions; some ambiguity | Probably correct but has meaningful risk areas. Needs review. |
| **5** | Even | Mixed signals; significant assumptions; unclear requirements | Coin-flip quality. Major sections need validation. |
| **4** | Moderately Low | Weak basis; many assumptions; working with incomplete info | More likely to have issues than not. Treat as draft. |
| **3** | Low | Minimal evidence; largely assumption-driven; outside expertise | Significant revision likely needed. Flag to reviewer. |
| **2** | Very Low | Near-guessing; critical information missing; unfamiliar domain | Output is a starting point only. Do not use without major review. |
| **1** | Speculative | No evidence; pure inference; placeholder content | Output is speculative. Treat as brainstorming, not deliverable. |

---

## Calibration Rules

1. **Never default to HIGH** — Start at MEDIUM and adjust based on evidence
2. **Evidence over feeling** — Rate based on what you can point to, not gut instinct
3. **Uncertainty is information** — A LOW rating with clear reasoning is more valuable than a false HIGH
4. **Aggregate honestly** — If 3 sections are HIGH and 1 is LOW, overall should reflect the LOW section's impact
5. **Match to consequence** — Rate relative to how much damage a wrong answer would cause
