# Sequential Thinking Synapse

## Identity

**Name:** Sequential Thinking
**Type:** Core (always-on)
**Version:** 1.0.0
**Author:** tahaa

The Sequential Thinking Protocol forces structured, step-by-step reasoning for every task. It prevents agents from jumping to conclusions, skipping reasoning steps, or producing answers without traceable logic chains.

Every non-trivial decision must flow through: **DECOMPOSE → REASON → VALIDATE → SYNTHESIZE**

## When Active

- **Activation:** Always-on for all agents (core synapse)
- **Phases:** 4 firing phases
- **Scaling:** Depth scales with task complexity (simple → 2 steps, expert → 10+ steps)

---

## Firing Phases

### Phase 1 — DECOMPOSE (Pre-Task)

**Timing:** Before starting any task, break it into numbered steps.

**Instructions:**

1. **Read the full task/prompt** before taking any action
2. **Identify the goal** — what does "done" look like?
3. **Break into numbered steps** — each step should be independently verifiable
4. **Estimate complexity** per step (trivial / moderate / complex)
5. **Identify dependencies** — which steps depend on others?
6. **Order by dependency** — dependent steps come after their prerequisites

**Complexity Scaling:**

| Task Complexity | Steps | Depth | Model |
|----------------|-------|-------|-------|
| Trivial (typo, rename) | 1-2 | Shallow | Any |
| Simple (small feature) | 3-5 | Standard | Fast |
| Moderate (feature, refactor) | 5-8 | Standard | Standard |
| Complex (architecture, multi-file) | 8-12 | Deep | Standard |
| Expert (system design, pipeline) | 10+ | Maximum | Premium |

**Output Format:**

```
### 🧠 DECOMPOSE — [Task Name]
**Goal:** [what "done" looks like]
**Complexity:** [trivial/simple/moderate/complex/expert]
**Steps:**
1. [Step description] — [complexity] — depends on: [none / step #]
2. [Step description] — [complexity] — depends on: [none / step #]
...
```

### Phase 2 — REASON (Per-Step)

**Timing:** For each step, show thinking process before acting.

**Instructions:**

For each step from the decomposition:

1. **State the sub-goal** — what does this step accomplish?
2. **Consider approaches** — at least 2 for non-trivial steps
3. **Evaluate trade-offs** — pros/cons of each approach
4. **Choose and justify** — pick the best approach with reasoning
5. **Execute** — take the action
6. **Record conclusion** — what was the result?

**Thinking Trace Format:**

```
### 🧠 REASON — Step [N]: [Name]
**Sub-goal:** [what this step accomplishes]

[THINKING]
- Approach A: [description] — Pro: [X], Con: [Y]
- Approach B: [description] — Pro: [X], Con: [Y]
- **Chosen:** [A/B] because [justification]
[/THINKING]

**Action:** [what I'm doing]
**Result:** [what happened]
**Confidence:** [high/medium/low] — [why]
```

**Branching Protocol:**

If the result contradicts expectations:
1. **STOP** — do not proceed to next step
2. **Re-examine** — what assumption was wrong?
3. **Branch** — create an alternative path
4. **Document** — record why the branch was needed

### Phase 3 — VALIDATE (Per-Step)

**Timing:** After each step's execution, validate the conclusion.

**Instructions:**

1. **Check against evidence** — does the result match expected output?
2. **Check against constraints** — does it violate any requirements?
3. **Check for side effects** — did it break anything else?
4. **Confidence score** — assign high/medium/low with justification

**Validation Checklist:**

- [ ] Result matches expected output
- [ ] No constraints violated
- [ ] No side effects detected
- [ ] Evidence is fresh (not assumed from previous steps)
- [ ] Confidence level justified

**Output Format:**

```
### 🧠 VALIDATE — Step [N]
- **Expected:** [what should have happened]
- **Actual:** [what did happen]
- **Match:** [yes/no/partial]
- **Side effects:** [none / description]
- **Confidence:** [high/medium/low] — [justification]
- **Proceed:** [yes / no — needs re-examination]
```

### Phase 4 — SYNTHESIZE (Post-Task)

**Timing:** After all steps complete, combine into final answer.

**Instructions:**

1. **Summarize each step's conclusion** — one line per step
2. **Check for consistency** — do all conclusions align?
3. **Identify gaps** — are there unanswered questions?
4. **Form final answer** — combine step conclusions
5. **State confidence** — overall confidence with justification
6. **List assumptions** — what was assumed but not proven?

**Output Format:**

```
### 🧠 SYNTHESIZE — [Task Name]
**Step Conclusions:**
1. [Step 1 conclusion]
2. [Step 2 conclusion]
...

**Consistency Check:** [all aligned / conflicts found: description]
**Gaps:** [none / list of unanswered items]
**Final Answer:** [combined conclusion]
**Overall Confidence:** [high/medium/low] — [justification]
**Assumptions:** [list of unproven assumptions]
```

---

## BrowseComp Reasoning Pattern

For research, debugging, and analysis tasks, use this specialized reasoning flow:

1. **DETECT** — Identify the core question or anomaly
2. **HYPOTHESIZE** — Form 2-3 possible explanations
3. **ENUMERATE** — For each hypothesis, list testable predictions
4. **VERIFY** — Test predictions against available evidence
5. **CONTINUE** — If no hypothesis confirmed, gather more evidence and repeat

**Use when:** Investigating bugs, researching unfamiliar code, analyzing requirements

---

## Stuck-Loop Detection

If you've attempted the same step 3+ times without progress:

1. **STOP** — You are in a stuck loop
2. **ANNOUNCE:** `⚠️ STUCK LOOP DETECTED — Step [N] attempted [count] times`
3. **DIAGNOSE** — What's different about each attempt? What assumption is wrong?
4. **PIVOT** — Try a fundamentally different approach (not a variation)
5. **ESCALATE** — If pivot fails, request human input

**3-Attempt Rule:** After 3 attempts at the same step, you MUST either pivot or escalate.

---

## Decomposition Patterns

### Feature Implementation
```
1. Understand requirements (read spec)
2. Design approach (architecture/data flow)
3. Write failing tests
4. Implement core logic
5. Implement edge cases
6. Run tests and verify
7. Document changes
```

### Bug Investigation
```
1. Reproduce the bug
2. Gather evidence (logs, stack traces)
3. Form hypothesis
4. Test hypothesis
5. Implement fix
6. Verify fix
7. Verify no regressions
```

### Code Review
```
1. Read the spec (if exists)
2. Check spec compliance
3. Check code quality
4. Check test coverage
5. Check for edge cases
6. Summarize findings
```

### Refactoring
```
1. Document current behavior (tests)
2. Identify refactoring targets
3. Plan transformation steps
4. Execute each step
5. Verify behavior preserved (run tests)
6. Document changes
```

---

## Reasoning Templates

### Decision Template
```
[THINKING]
Decision: [what needs to be decided]
Option A: [description]
  - Pros: [list]
  - Cons: [list]
Option B: [description]
  - Pros: [list]
  - Cons: [list]
Criteria: [what matters most]
Choice: [A/B] because [justification using criteria]
[/THINKING]
```

### Investigation Template
```
[THINKING]
Question: [what I need to find out]
Evidence so far: [what I know]
Hypothesis: [my best guess]
Test: [how to verify]
Result: [what the test showed]
Conclusion: [what I now know]
[/THINKING]
```

### Error Analysis Template
```
[THINKING]
Error: [exact error message]
Context: [when it occurs]
Possible causes:
  1. [cause A] — likelihood: [high/medium/low]
  2. [cause B] — likelihood: [high/medium/low]
  3. [cause C] — likelihood: [high/medium/low]
Testing cause [most likely]:
  - Test: [what I did]
  - Result: [what happened]
Root cause: [confirmed cause]
[/THINKING]
```

---

## Rules

### DO:
- Always decompose before acting on non-trivial tasks
- Show your thinking for every decision
- Validate each step before building on it
- Use branching when results contradict expectations
- Scale depth with task complexity

### DON'T:
- Skip decomposition because "it's obvious"
- Reason about multiple steps simultaneously
- Proceed after a failed validation without addressing it
- Hide reasoning — all thinking must be visible
- Treat thinking traces as optional overhead

---

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| resources/decomposition-patterns.md | templates | Common decomposition templates for different task types |
| resources/reasoning-templates.md | templates | Structured reasoning templates for decisions, investigations, errors |
| resources/validation-checklist.md | checklist | Per-step validation checklist |
