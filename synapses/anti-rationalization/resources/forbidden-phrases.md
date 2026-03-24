# Forbidden Phrases Reference

These phrases indicate unverified claims and must NEVER appear in agent output.
When you find yourself writing any of these, replace with the verified alternative.

## Forbidden → Verified Alternatives

| # | ❌ Forbidden Phrase | ✅ Say Instead | Why |
|---|-------------------|---------------|-----|
| 1 | "This should work" | "I verified this works by [evidence]" | "Should" is speculation |
| 2 | "I believe this is correct" | "I confirmed this is correct because [evidence]" | Belief ≠ proof |
| 3 | "This is probably fine" | "I tested this and it [specific result]" | Probability ≠ certainty |
| 4 | "I'll handle that later" | "Adding this to the task list now: [item]" | "Later" = never |
| 5 | "The user won't notice" | "This affects [scope] and needs [action]" | You don't decide visibility |
| 6 | "It's just a small change" | "This change affects [components]; verified by [tests]" | Size ≠ impact |
| 7 | "That's out of scope" | "The spec [does/doesn't] include this" | Only spec defines scope |
| 8 | "Close enough" | "This matches the spec exactly because [evidence]" | Close ≠ correct |
| 9 | "This is basically done" | "I've completed [X of Y items] with verification" | "Basically" hides gaps |
| 10 | "I think I fixed it" | "I verified the fix by [test/evidence]" | Thinking ≠ knowing |
| 11 | "It seems to work" | "It works — here's the evidence: [output]" | "Seems" is uncertainty |
| 12 | "I'm fairly confident" | "I'm confident because [specific evidence]" | Qualify with evidence |
| 13 | "This looks right" | "This is correct based on [verification]" | Looking ≠ verifying |
| 14 | "Should be compatible" | "I verified compatibility by [test]" | "Should" needs proof |
| 15 | "No issues expected" | "I tested for [issues] and found none" | Expectations need evidence |

## Quick Rule

> If a phrase contains "should", "probably", "believe", "think", "seems", "looks", "basically", "fairly", or "expected" — it's likely forbidden. Replace with evidence.
