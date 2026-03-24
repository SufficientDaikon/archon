# Stuck Detection Heuristics

Use these heuristics during Phase 2 (MONITOR) to recognize when you're stuck and need to change approach.

---

## Definition of "Stuck"

You are **stuck** when you are expending effort without making progress toward your exit criteria. Being stuck is not failure — it's a signal to adapt.

---

## Detection Heuristics

### H1: Repeated Approach Pattern
**Signal:** You've tried the same general approach 3+ times with minor variations.
**Test:** Are you doing essentially the same thing but hoping for a different result?
**Action:** STOP. Announce stuck status. List the approaches tried and why they failed. Choose a fundamentally different strategy.

### H2: Circular Reasoning
**Signal:** Your current step depends on information you're trying to produce, or you keep returning to the same decision point.
**Test:** Draw the dependency chain. Does it loop back to itself?
**Action:** Break the cycle by making an explicit assumption, documenting it as `[ASSUMPTION]`, and moving forward.

### H3: Time-Without-Progress
**Signal:** Significant effort spent without measurable output or observable progress toward exit criteria.
**Test:** Can you point to concrete output from the last chunk of work? If not, you're spinning.
**Action:** Produce a partial deliverable immediately, even if imperfect. Something > nothing.

### H4: Scope Creep Spiral
**Signal:** Each attempt reveals more work needed, and the task keeps growing instead of shrinking.
**Test:** Is the remaining work larger now than when you started this attempt?
**Action:** Re-scope. Define a minimal viable deliverable. Deliver that first, then iterate.

### H5: Information Gap Block
**Signal:** You cannot proceed because a critical piece of information is missing and cannot be inferred.
**Test:** Is there a specific question that, if answered, would unblock you?
**Action:** State the question explicitly. If you can make a reasonable assumption, do so and tag it. If not, escalate.

### H6: Yak Shaving
**Signal:** You're solving prerequisite problems that are increasingly distant from the original task.
**Test:** Can you explain in one sentence how your current work connects to the exit criteria?
**Action:** Stop shaving yaks. Return to the original task. Accept imperfect prerequisites.

### H7: Analysis Paralysis
**Signal:** You're comparing options exhaustively without committing to any approach.
**Test:** Have you identified 3+ viable approaches and spent time evaluating each without deciding?
**Action:** Pick the approach with the best risk/reward ratio. Document why. Commit and move forward.

---

## Stuck Response Protocol

When any heuristic triggers:

1. **Announce:** `⚠️ STUCK DETECTED — [which heuristic triggered]`
2. **Diagnose:** What specifically is blocking progress?
3. **Inventory:** What approaches have been tried? What hasn't been tried?
4. **Decide:** Choose ONE of these responses:
   - **Pivot strategy** — Try a fundamentally different approach
   - **Simplify scope** — Reduce the problem to something solvable now
   - **Make assumption** — State an assumption explicitly and proceed
   - **Produce partial** — Deliver what you have and flag what's incomplete
   - **Escalate** — Request help, clarification, or additional context
5. **Time-box:** Set a clear limit for the new approach. If still stuck after the time-box, escalate.

---

## Prevention

These practices reduce how often you get stuck:

- **Phase 1 planning** — Good planning catches 70% of stuck scenarios before they happen
- **Exit criteria** — Clear exit criteria make it obvious when you're not making progress
- **Assumption tracking** — Explicit assumptions are easier to revisit than implicit ones
- **Incremental delivery** — Deliver small, working pieces instead of one large output
