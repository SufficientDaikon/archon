# Dispatching Parallel Agents — The Parallelizer

> **Type:** Flexible  
> **Trigger:** 2+ independent tasks that don't share state or files

## Iron Law

```
PARALLEL AGENTS MUST NOT SHARE MUTABLE STATE OR EDIT THE SAME FILES
```

## Purpose

When multiple independent tasks exist (failures in different subsystems, features in separate modules), dispatch one agent per domain in parallel instead of investigating sequentially. This dramatically reduces total completion time.

## When to Use

✅ **Use when:**
- 2+ independent failures in different subsystems
- Multiple features that touch different files
- Research tasks that don't affect each other
- Test investigations in separate test suites

❌ **Do NOT use when:**
- Failures might be related (fix one → fixes others)
- Tasks need full system context to solve
- Agents would edit the same files (merge conflicts)
- Sequential ordering matters (A depends on B)

## Process

### Step 1: IDENTIFY Independent Domains
```
For each task:
  - What subsystem does it affect?
  - What files does it touch?
  - Does it depend on any other task?
  
Group by subsystem. Tasks in the same subsystem = sequential.
Tasks in different subsystems = parallel candidates.
```

### Step 2: CREATE Focused Agent Tasks
Each parallel agent gets:
- **Specific scope** — exactly which files/components they own
- **Clear goal** — what "done" looks like
- **Constraints** — what files/areas to NOT touch
- **Test command** — how to verify their work

### Step 3: DISPATCH in Parallel
```
Agent 1: "Fix authentication module tests"
   Scope: src/auth/*, tests/auth/*
   
Agent 2: "Fix database migration errors"  
   Scope: src/db/*, migrations/*
   
Agent 3: "Fix API endpoint validation"
   Scope: src/api/validators/*, tests/api/*
```

### Step 4: REVIEW and Integrate
After all agents complete:
1. **Check for conflicts** — any file edited by multiple agents?
2. **Run full test suite** — do their changes work together?
3. **Resolve integration issues** — if tests fail, identify which agent's changes conflict
4. **Merge sequentially** — apply each agent's changes one at a time, testing after each

## Conflict Resolution

If agents accidentally overlap:
```
1. Identify conflicting changes
2. Keep the change from the agent with better test coverage
3. Have the other agent redo their work with the first change in place
4. Run full suite again
```

## Sizing Guide

| # of Independent Tasks | Strategy |
|------------------------|----------|
| 1 | Sequential (no parallelism needed) |
| 2-3 | Parallel all |
| 4-6 | Parallel in groups of 3 |
| 7+ | Break into phases, parallel within phases |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Sequential is simpler" | Simpler but 3x slower. Parallel for independent tasks. |
| "They might be related" | Check first. If truly independent, parallelize. |
| "I can't track parallel agents" | That's what the review/integrate step is for. |
| "One agent can handle all of this" | One agent accumulates context and fatigue. Fresh agents don't. |

## Red Flags

- Dispatching agents that will edit the same files
- No clear "done" criteria for each agent
- Forgetting the integration/review step after parallel dispatch
- Dispatching for dependent tasks (A needs B's output)
