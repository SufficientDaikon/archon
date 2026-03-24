# Executing Plans — Single-Session Fallback

> **Type:** Rigid process  
> **Trigger:** Have plan to execute but NO subagent support available  
> **Fallback for:** subagent-driven-development

## Iron Law

```
FOLLOW THE PLAN EXACTLY — DEVIATIONS REQUIRE EXPLICIT APPROVAL
```

## Purpose

Simpler version of subagent-driven-development for environments without subagent capabilities. Loads the plan, reviews it critically, then executes tasks sequentially in the current session.

## Process

### Phase 1: Load and Review
1. Read the full implementation plan
2. Review critically — raise concerns BEFORE starting
3. Identify potential issues, missing context, unclear steps
4. Get user approval to proceed (or modify plan first)

### Phase 2: Execute Tasks
For each task in order:
1. Mark task as `in_progress`
2. Follow steps exactly as written in the plan
3. Run tests after each step (verify red → green)
4. Mark task as `completed` when all steps pass
5. If stuck → mark as `blocked`, explain why, ask for guidance

### Phase 3: Finish
1. Run full test suite
2. Review all changes holistically
3. Invoke `finishing-a-development-branch` skill

## Key Differences from Subagent Version

| Aspect | Subagent-Driven | Executing-Plans |
|--------|-----------------|-----------------|
| Context | Fresh per task | Accumulated (risk of pollution) |
| Review | Two-stage (spec + code) | Self-review only |
| Parallelism | Yes (multiple agents) | No (sequential) |
| Quality | Higher (isolation) | Lower (fatigue, bias) |

## Mitigation Strategies

Since you lack fresh context per task:
- **Re-read the plan** before each task (reset mental model)
- **Self-review checklist** after each task (spec compliance + quality)
- **Request human review** at task boundaries for complex features
- **Commit frequently** — each task gets its own commit

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll adjust the plan as I go" | Deviations need approval. Document, ask, then adjust. |
| "This step is wrong, I'll fix it" | Maybe the step is right and you're wrong. Verify first. |
| "I can combine these tasks" | Plan tasks are independent for a reason. Execute separately. |
| "Tests aren't needed for this step" | TDD is non-negotiable. Write the test. |
