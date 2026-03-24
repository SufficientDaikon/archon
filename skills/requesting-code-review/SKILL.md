# Requesting Code Review — The Quality Gate

> **Type:** Rigid for mandatory triggers, flexible for optional  
> **Trigger:** After completing tasks, major features, or before merging

## Iron Law

```
NO MERGE WITHOUT CODE REVIEW — NO REVIEW WITHOUT COMPLETE WORK
```

## Purpose

Ensures code quality through structured review requests. Dispatches a code reviewer (subagent or human) with the right context to catch issues before they reach the main branch.

## When to Request Review

### Mandatory (always request):
- Before merging any feature branch
- After completing a major feature (3+ tasks)
- Before deploying to production
- When changing shared/core code

### Optional (use judgment):
- After completing individual tasks (if complex)
- For config/documentation changes
- For refactoring-only changes

## Process

### Step 1: Prepare Review Context
```
- BASE_SHA: The commit before your changes
- HEAD_SHA: Your latest commit
- Changed files list: `git diff --name-only BASE..HEAD`
- Summary: What was built and why
```

### Step 2: Dispatch Code Reviewer
Provide the reviewer with:
- The spec/plan that was being implemented
- The file diff (`git diff BASE..HEAD`)
- Any known concerns or trade-offs
- Test results (proof they pass)

### Step 3: Act on Feedback

| Severity | Action |
|----------|--------|
| **Critical** | Fix immediately before proceeding |
| **Important** | Fix before merging/completing |
| **Minor** | Note for follow-up, don't block |
| **Suggestion** | Consider, decide, document decision |

### Step 4: Re-Review if Needed
If critical or important items were fixed:
- Re-run tests (verification-before-completion)
- Re-request review on the fixes only
- Don't re-review the entire changeset

## Two-Stage Review Order

When both spec compliance and code quality reviews are needed:
```
1. SPEC COMPLIANCE FIRST → "Did we build what was requested?"
2. CODE QUALITY SECOND  → "Is it well-built?"
   (only after spec compliance passes)
```

**NEVER reverse this order.** Code quality is meaningless if you built the wrong thing.

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Changes are too small for review" | Small changes still break things. Review catches what you missed. |
| "I already reviewed my own code" | Self-review has blind spots. Fresh eyes catch issues you can't. |
| "Review will slow us down" | Bugs slow us down more. Review is investment in quality. |
| "The tests pass, so it's fine" | Tests verify behavior, not quality. Review catches design issues. |
