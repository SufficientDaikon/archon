# Subagent-Driven Development — The Execution Engine

> **Type:** Rigid process (follow exactly)  
> **Trigger:** Have implementation plan with independent tasks, subagents available  
> **THE most important skill for actual code production

## Iron Law

```
ONE FRESH SUBAGENT PER TASK — NEVER REUSE CONTEXT ACROSS TASKS
```

## Purpose

Executes implementation plans by dispatching a fresh subagent per task with mandatory TWO-STAGE review after each. This is the primary execution engine for all feature development.

## The Process (Per Task)

```
1. SELECT task from plan (next incomplete)
2. DISPATCH implementer subagent with:
   - Full task text from plan
   - Relevant context (curated, not full codebase)
   - Self-review checklist
   - Escalation protocol
3. HANDLE implementer response (see status table)
4. DISPATCH spec reviewer subagent
   → "Did you build what was requested?"
   → If issues: implementer fixes → re-review
5. DISPATCH code quality reviewer subagent
   → "Is it well-built?"
   → If issues: implementer fixes → re-review
6. MARK task complete
7. NEXT task (or final review if last)
```

## Four Implementer Statuses

| Status | Meaning | Action |
|--------|---------|--------|
| **DONE** | Task complete, all tests pass | → Proceed to spec review |
| **DONE_WITH_CONCERNS** | Complete but has doubts | Read concerns, address if correctness-related, then → spec review |
| **NEEDS_CONTEXT** | Missing information | Provide missing context, re-dispatch same task |
| **BLOCKED** | Cannot complete as specified | Assess: more context? stronger model? break task up? |

## Two-Stage Review (NEVER reverse order)

```
Stage 1: SPEC COMPLIANCE REVIEW
  → "Did the implementation match the plan?"
  → Check: all files created/modified as specified
  → Check: all tests written and passing
  → Check: no unauthorized changes
  → MUST PASS before Stage 2

Stage 2: CODE QUALITY REVIEW  
  → "Is the code well-written?"
  → Check: naming, structure, patterns, edge cases
  → Check: no code smells, proper error handling
  → Only runs AFTER Stage 1 passes
```

## Model Selection Strategy

| Task Complexity | Recommended Model |
|-----------------|-------------------|
| 1-2 files, complete spec, mechanical work | Fast/cheap model |
| Multi-file, integration concerns | Standard model |
| Architecture decisions, design, review | Most capable model |

## Fresh Context Principle

Each subagent gets a CLEAN context with only:
- The task text from the plan
- Relevant file contents (curated)
- Project conventions and patterns
- Self-review checklist

They do NOT get:
- Previous task results
- Conversation history
- Full codebase dump
- Other agents' work

This prevents context pollution and ensures each task is executed independently.

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I can do this faster in one session" | Speed without quality is rework. Fresh context prevents pollution. |
| "Subagents are overkill for this" | Even small tasks benefit from isolated execution and review. |
| "I'll skip spec review, code looks fine" | "Looks fine" is not verification. Spec review catches 40% of issues. |
| "Code review can cover spec compliance too" | NO. Different reviewers, different criteria, strict order. |
| "One review is enough" | Two-stage review catches issues that single review misses. |

## Red Flags

- Executing multiple tasks in one subagent dispatch
- Skipping spec review because "it's obvious"
- Reversing review order (code quality before spec compliance)
- Reusing a subagent for the next task (pollution risk)
- Not handling BLOCKED status (ignoring the signal)
