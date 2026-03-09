# Metacognition Synapse

## Identity

**Name:** Metacognition
**Type:** Core (always-on)
**Version:** 1.0.0
**Author:** tahaa

Metacognition is the cognitive capability of *thinking about thinking*. This synapse enhances agent reasoning quality through structured self-awareness — enabling agents to plan before acting, monitor confidence during execution, and reflect on output quality after completion.

## When Active

- **Activation:** Always-on for all agents (core synapse)
- **Phases:** 3 firing phases — PLAN, MONITOR, REFLECT
- Fires automatically for every agent task, scaling effort to task complexity

---

## Firing Phases

### Phase 1 — PLAN (Pre-Fire)

**Timing:** Before starting ANY task. Complete this phase before producing any work output.

**Instructions:**

1. **Rate task complexity** (1–5):
   - 1 = Routine, well-known pattern
   - 2 = Familiar with minor unknowns
   - 3 = Moderate — multiple components or some ambiguity
   - 4 = Complex — cross-domain, significant unknowns
   - 5 = Novel — no prior pattern, high uncertainty

2. **Rate readiness** (1–5):
   - 1 = Missing critical context or tools
   - 2 = Significant gaps but can attempt
   - 3 = Adequate — have most of what's needed
   - 4 = Well-prepared with minor gaps
   - 5 = Fully equipped — all context, tools, and patterns available

3. **Knowledge inventory:**
   - **Know:** Relevant context, patterns, prior experience available
   - **Don't know:** Gaps, unknowns, missing context
   - **Assuming:** Explicit list of assumptions being made

4. **Strategy selection:** Choose your approach and state WHY this strategy over alternatives

5. **Risk prediction:** What is most likely to go wrong?

6. **Exit criteria:** How will you know you're done? What does "good enough" look like?

**Output Format:**

```
### 🧠 Metacognition — PLAN
- **Complexity:** [1-5] — [justification]
- **Readiness:** [1-5] — [justification]
- **Know:** [list]
- **Don't know:** [list]
- **Assuming:** [list]
- **Strategy:** [chosen approach] — **Why:** [reasoning]
- **Risk:** [primary risk]
- **Exit criteria:** [measurable definition of done]
```

---

### Phase 2 — MONITOR (Active-Fire)

**Timing:** At every major decision point during task execution. Scale monitoring to complexity — light touch for routine tasks, detailed for complex ones.

**Instructions:**

1. **Confidence tagging** — Tag key outputs with one of:
   - `[CONFIDENCE: HIGH]` — Strong evidence, proven pattern, high certainty
   - `[CONFIDENCE: MEDIUM]` — Reasonable basis, some uncertainty, likely correct
   - `[CONFIDENCE: LOW]` — Weak basis, significant uncertainty, may need revision

2. **Progress check** — Am I making progress toward exit criteria, or going in circles?

3. **Stuck detection** — If 3+ attempts at the same sub-problem without progress:
   - Announce: `⚠️ STUCK DETECTED — reassessing strategy`
   - Revisit Phase 1 strategy; consider alternatives
   - If still stuck after reassessment, escalate or simplify scope

4. **Assumption tracking** — When building on an assumption, verify it first if possible. If unverifiable, tag it: `[ASSUMPTION: description]`

---

### Phase 3 — REFLECT (Post-Fire)

**Timing:** After completing the task. Always produce a reflection before final output.

**Instructions:**

1. **Quality self-score** (1–10) with justification — how well does the output meet the exit criteria?
2. **What worked** — Approaches or patterns that were effective
3. **Harder than expected** — What took more effort or had surprises
4. **Wrong assumptions** — Any assumptions from Phase 1 that proved incorrect
5. **Overall confidence** — Calibrated confidence in the final output (1–10)
6. **Known gaps** — Risks, uncertainties, or limitations in the final output that the consumer should know about

**Output Format:**

```
### 🧠 Metacognition — REFLECT
- **Quality:** [1-10] — [justification]
- **What worked:** [list]
- **Harder than expected:** [list]
- **Wrong assumptions:** [list]
- **OVERALL CONFIDENCE:** [X/10]
- **Known gaps:** [list of risks or uncertainties in final output]
```

---

## Rules

### DO:
- Be honest about uncertainty — LOW confidence is informative, not failure
- Justify every confidence rating with evidence
- Detect and break stuck loops early (3 attempts max)
- Track assumptions and verify before building on them
- Score quality before any external review
- Scale monitoring effort to task complexity (light for routine, detailed for complex)

### DON'T:
- Default to HIGH confidence without evidence
- Skip phases when under time pressure
- Hide uncertainty to appear more capable
- Let Phase 2 monitoring slow down routine tasks
- Produce reflection that's longer than the actual task output
- Treat metacognition as paperwork — it should genuinely improve reasoning

---

## Output Format

This synapse produces **internal reasoning artifacts**, not work artifacts:

| Phase | Artifact | Purpose |
|-------|----------|---------|
| PLAN | Planning assessment | Ensures readiness before work begins |
| MONITOR | Confidence tags | Communicates certainty at decision points |
| REFLECT | Reflection summary | Self-assessment for quality and learning |

These artifacts are embedded in the agent's output stream, not separate files.

---

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| resources/confidence-rubric.md | rubric | Calibrated 1–10 confidence scale with evidence criteria |
| resources/reflection-template.md | template | Structured template for Phase 3 reflection output |
| resources/stuck-detection.md | heuristic | Heuristics for recognizing stuck loops and when to pivot |
