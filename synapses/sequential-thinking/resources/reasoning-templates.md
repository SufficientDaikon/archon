# Reasoning Templates

## Decision Template
Use when choosing between approaches, technologies, or designs.
```
[THINKING]
Decision: [what needs to be decided]

Option A: [description]
  - Pros: [list]
  - Cons: [list]
  - Risk: [high/medium/low]

Option B: [description]
  - Pros: [list]
  - Cons: [list]
  - Risk: [high/medium/low]

Criteria (ordered by importance):
  1. [most important criterion]
  2. [second criterion]
  3. [third criterion]

Evaluation:
  - Option A scores: [criterion 1: score, criterion 2: score, ...]
  - Option B scores: [criterion 1: score, criterion 2: score, ...]

Choice: [A/B] because [justification using criteria]
Confidence: [high/medium/low]
[/THINKING]
```

## Investigation Template
Use when researching, exploring, or understanding unfamiliar code/systems.
```
[THINKING]
Question: [what I need to find out]
Current knowledge: [what I already know]
Evidence gathered: [files read, searches done, results]

Hypothesis: [my best explanation]
Test: [how to verify this hypothesis]
Result: [what the test showed]

Conclusion: [what I now know]
Remaining unknowns: [what I still don't know]
Confidence: [high/medium/low]
[/THINKING]
```

## Error Analysis Template
Use when debugging errors, failures, or unexpected behavior.
```
[THINKING]
Error: [exact error message or unexpected behavior]
Context: [when/where it occurs, what triggered it]

Possible causes (ordered by likelihood):
  1. [cause A] — likelihood: [high/medium/low] — evidence: [for/against]
  2. [cause B] — likelihood: [high/medium/low] — evidence: [for/against]
  3. [cause C] — likelihood: [high/medium/low] — evidence: [for/against]

Testing most likely cause ([A]):
  - Test: [what I did to verify]
  - Expected: [what should happen if this is the cause]
  - Actual: [what actually happened]
  - Verdict: [confirmed/ruled out]

Root cause: [confirmed cause with evidence]
Fix: [proposed solution]
Verification: [how to verify the fix works]
[/THINKING]
```

## Trade-off Template
Use when there's no clear "best" option and trade-offs must be documented.
```
[THINKING]
Trade-off: [what's being traded]

If we choose X:
  - We gain: [benefits]
  - We lose: [costs]
  - Risk: [what could go wrong]

If we choose Y:
  - We gain: [benefits]
  - We lose: [costs]
  - Risk: [what could go wrong]

Context factors:
  - [factor 1 that tips the balance]
  - [factor 2]

Recommendation: [X/Y] given [specific context factors]
Note: This trade-off should be revisited if [conditions change]
[/THINKING]
```

## Assumption Tracking Template
Use when reasoning requires assumptions that haven't been verified.
```
[THINKING]
Assumption: [what I'm assuming is true]
Based on: [why I think this is reasonable]
Risk if wrong: [what happens if this assumption is incorrect]
Verification plan: [how to check this assumption]
Status: [unverified / verified / disproven]
[/THINKING]
```
