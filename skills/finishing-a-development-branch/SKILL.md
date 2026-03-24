# Finishing a Development Branch — The Closer

> **Type:** Rigid  
> **Trigger:** Implementation complete, all tests pass, ready to integrate work

## Iron Law

```
NO MERGE WITHOUT PASSING TESTS — NO CLEANUP WITHOUT CONFIRMATION
```

## Purpose

Provides a structured process for completing feature work: verifying, integrating, and cleaning up. Prevents the common "just merge and forget" pattern that leaves orphaned branches and broken worktrees.

## Pre-Requisites

Before invoking this skill:
- [ ] All implementation tasks are complete
- [ ] All tests pass (verified via `verification-before-completion`)
- [ ] Code review is complete (if applicable)

## Process

### Step 1: Verify Tests Pass
```bash
<test-command>  # Run FULL test suite
# If ANY test fails → STOP. Fix before proceeding.
```

### Step 2: Determine Base Branch
```bash
# Auto-detect: main or master
BASE=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')
```

### Step 3: Present Exactly 4 Options

**Option 1: Merge Locally**
```bash
git checkout $BASE
git merge --no-ff feature/<name>  # Preserve merge commit
```

**Option 2: Push + Create PR**
```bash
git push origin feature/<name>
# Create PR via CLI or web
```

**Option 3: Keep As-Is**
- Branch stays, worktree stays
- User will handle integration later

**Option 4: Discard**
- **Requires confirmation**: User must type "discard" to confirm
- Removes all work permanently
```bash
git checkout $BASE
git worktree remove .worktrees/feature/<name>
git branch -D feature/<name>
```

### Step 4: Execute Choice

Follow the chosen option exactly. No modifications, no "improvements".

### Step 5: Cleanup (Options 1, 2, 4 only)
```bash
# Remove worktree if it exists
git worktree remove .worktrees/feature/<name> 2>/dev/null || true

# Delete local branch (only for Option 1 — already merged)
git branch -d feature/<name> 2>/dev/null || true
```

## Key Rules

- **Always present all 4 options** — never assume which the user wants
- **Discard requires explicit confirmation** — "discard" typed by user
- **No partial merges** — merge all or nothing
- **Cleanup is automatic** for options 1, 2, 4 — but NOT option 3

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll clean up later" | You won't. Orphaned branches accumulate. Clean up now. |
| "Just merge, no need for options" | User might want a PR, or want to keep the branch. Ask. |
| "Tests were passing earlier" | Re-verify NOW. State changes between then and now. |
| "Discard confirmation is overkill" | Permanently deleting work deserves one extra step. |
