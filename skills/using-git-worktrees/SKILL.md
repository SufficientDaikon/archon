# Using Git Worktrees — The Isolator

> **Type:** Rigid  
> **Trigger:** Starting feature work that needs workspace isolation

## Iron Law

```
FEATURE WORK HAPPENS IN ISOLATION — NEVER ON THE MAIN BRANCH
```

## Purpose

Uses git worktrees to create isolated workspaces for feature development. Prevents "works on my branch" issues and keeps the main branch clean.

## Directory Selection Priority

1. Check for existing worktree directory: `.worktrees/` (preferred) or `worktrees/`
2. Check project documentation (README, CONTRIBUTING) for conventions
3. Ask the user for preference

## Safety Verification

**MUST verify the worktree directory is gitignored before creating.**

```bash
# Check .gitignore
grep -q '.worktrees' .gitignore || echo '.worktrees/' >> .gitignore
git add .gitignore && git commit -m "chore: gitignore worktrees directory"
```

## Process

### Step 1: Detect Project
```bash
PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))
BRANCH_NAME="feature/<descriptive-name>"
```

### Step 2: Create Worktree
```bash
git worktree add .worktrees/$BRANCH_NAME -b $BRANCH_NAME
cd .worktrees/$BRANCH_NAME
```

### Step 3: Project Setup
Auto-detect and run setup:
| Indicator | Setup Command |
|-----------|---------------|
| `package.json` | `npm install` |
| `Cargo.toml` | `cargo build` |
| `requirements.txt` | `pip install -r requirements.txt` |
| `go.mod` | `go mod download` |
| `Gemfile` | `bundle install` |
| `pyproject.toml` | `pip install -e .` |

### Step 4: Verify Clean Baseline
```bash
# Run tests to establish baseline
<test-command>
# Verify all pass before starting work
```

### Step 5: Report
```
Worktree created at: .worktrees/feature/<name>
Branch: feature/<name>
Test baseline: X tests passing
Ready for development.
```

## When to Use Worktrees

- Feature development (always)
- Bug fixes (if multi-file)
- Experiments (always — easy to discard)
- Refactoring (always — easy to compare before/after)

## When NOT to Use

- Single-file documentation changes
- Config tweaks
- Commit message fixes

## Cleanup

Worktrees are cleaned up by `finishing-a-development-branch`:
```bash
git worktree remove .worktrees/feature/<name>
git branch -d feature/<name>  # only after merge
```

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Just a quick change, no branch needed" | Quick changes break things too. Isolate. |
| "Setting up worktree takes too long" | 30 seconds of setup vs hours of untangling conflicts. |
| "I'll create a branch later" | Later never comes. Start isolated. |
| "Main branch is fine for experiments" | Experiments on main = accidental commits = broken main. |
