# Writing Plans — TDD-Sized Task Breakdown

> **Type:** Rigid process (follow structure exactly)  
> **Trigger:** Have a spec/requirements for multi-step task, before touching code  
> **Input:** Approved design document from brainstorming

## Iron Law

```
NO CODING UNTIL THE PLAN IS WRITTEN AND REVIEWED
```

## Purpose

Creates step-by-step implementation plans with TDD-sized tasks that any developer (or agent) with zero codebase context can execute. Each task is one action (2-5 minutes), producing a plan that's mechanically executable.

## Task Granularity

Each step is ONE atomic action:
```
Step 1: Write the failing test
Step 2: Run it to see it fail
Step 3: Implement minimal code to pass
Step 4: Run tests to see them pass
Step 5: Commit with descriptive message
```

## Plan Document Structure

```markdown
# [Feature Name] Implementation Plan

> REQUIRED: Use subagent-driven-development (or executing-plans if no subagents)

**Goal:** [one sentence]
**Architecture:** [2-3 sentences on approach]
**Tech Stack:** [key technologies]

---

### Task N: [Component Name]
**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Steps:**
- [ ] Step 1: Write failing test
  [complete test code]
- [ ] Step 2: Verify it fails
  [exact command + expected output]
- [ ] Step 3: Write implementation
  [complete production code]
- [ ] Step 4: Verify it passes
  [exact command + expected output]
- [ ] Step 5: Commit
  [exact git commands]
```

## Plan Review Process

After writing each chunk (≤1000 lines):
1. Review the plan critically — are tasks truly independent? Are steps atomic?
2. Check for missing edge cases, error handling, test coverage
3. Verify file paths exist or are clearly marked as "create"
4. Ensure each task has clear success criteria
5. Max 5 review iterations, then escalate unclear items to human

## Key Rules

- **Complete code in steps** — no "implement the rest" or "similar to above"
- **Exact file paths** — no guessing, verify against project structure
- **Test FIRST in every task** — TDD is non-negotiable
- **Independent tasks** — each task can be executed without knowledge of others
- **Line numbers for modifications** — `file.py:123-145` not just `file.py`

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Too detailed, wastes time" | Vague plans waste MORE time in execution. Detail prevents rework. |
| "The developer will figure it out" | Plans should work for zero-context agents. Explicit > implicit. |
| "I can adjust during implementation" | That's scope creep. Plan changes go through review. |
| "Tests are obvious, don't need to write them" | If they're obvious, it takes 30 seconds. Write them. |
| "This task is too small to break down" | If it takes >5 minutes, break it down further. |

## Transition

After plan is approved:
- If subagents available → invoke `subagent-driven-development`
- If no subagents → invoke `executing-plans`
- NEVER start implementing directly — use the execution skills
