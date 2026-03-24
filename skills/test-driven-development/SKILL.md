# Test-Driven Development — The Iron Law

> **Type:** Rigid (NO exceptions)  
> **Trigger:** Any feature implementation or bugfix, BEFORE writing production code  
> **Applies to:** Every agent that writes code

## Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

## The Cycle: Red → Green → Refactor

### RED Phase
1. Write ONE failing test that describes the desired behavior
2. Run the test
3. **VERIFY it FAILS** — if it passes, your test is wrong or the feature already exists
4. Read the failure message — it should describe what's missing

### GREEN Phase
1. Write the MINIMAL code to make the test pass
2. No extra features, no "while I'm here" additions
3. Run ALL tests (not just the new one)
4. **VERIFY ALL pass** — if others broke, fix before continuing

### REFACTOR Phase
1. Clean up: remove duplication, improve names, extract helpers
2. Run ALL tests after EVERY refactor change
3. **Keep green** — if any test fails during refactor, revert immediately
4. Don't add features during refactor — that's a new RED cycle

### REPEAT
Next behavior → new failing test → minimal code → refactor

## What "Delete" Means

If you wrote production code before the test:

1. **DELETE IT** — not "save for reference", not "I'll adapt it"
2. Don't look at it while writing the test
3. Start fresh: write the test first, THEN write the code
4. Delete means delete

## The 11-Entry Rationalization Table

| # | Excuse | Reality |
|---|--------|---------|
| 1 | "Too simple to test" | Simple code breaks too. Test takes 30 seconds. Write it. |
| 2 | "I'll test after" | Tests that pass immediately prove nothing about your code. |
| 3 | "Already manually tested" | Manual ≠ systematic. No record, can't re-run, can't automate. |
| 4 | "Deleting X hours of work is wasteful" | Sunk cost fallacy. The code was written without design. |
| 5 | "TDD is dogmatic/purist" | TDD IS pragmatic. It finds bugs before commit, not after deploy. |
| 6 | "I just need to make a small fix" | Small fixes break things. Test proves the fix works AND nothing broke. |
| 7 | "The test framework isn't set up" | Set it up. That's step 0 before any code. |
| 8 | "I know this works" | You know what you THINK works. Tests prove what ACTUALLY works. |
| 9 | "Time pressure — we need this shipped" | Untested code ships bugs. Bug-fixing is slower than TDD. |
| 10 | "Legacy code doesn't have tests" | Write a characterization test first. Then change. |
| 11 | "It's just a config change" | Config changes break systems. Test the expected behavior. |

## Red Flags

- Writing an implementation file before a test file
- A test that passes on first run (test is likely wrong)
- "Let me just get this working, then add tests"
- Tests that don't assert meaningful behavior
- Skipping the REFACTOR phase
- Running only the new test, not the full suite

## Framework Detection

Auto-detect and use the project's test framework:
| Language | Framework | Command |
|----------|-----------|---------|
| Python | pytest | `pytest` |
| JavaScript | jest/vitest | `npm test` |
| TypeScript | jest/vitest | `npm test` |
| Go | testing | `go test ./...` |
| Rust | cargo test | `cargo test` |
| Ruby | rspec | `rspec` |

## Integration

- **writing-plans** generates TDD-sized tasks (test → implement → verify)
- **subagent-driven-development** enforces TDD per task
- **verification-before-completion** ensures tests actually ran and passed
- **anti-rationalization synapse** catches TDD-skipping excuses
