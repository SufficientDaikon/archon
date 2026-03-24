# Verification Before Completion — The Honesty Enforcer

> **Type:** Rigid (follow exactly)  
> **Trigger:** About to claim work is complete, fixed, passing, or done  
> **Born from:** 24 trust-breaking failures where unverified claims were made

## Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

## The Gate Function

Every time you are about to say "done", "fixed", "passes", or "complete":

### Step 1: IDENTIFY
What specific command or check proves this claim?
- Tests passing? → `pytest` / `npm test` / `cargo test`
- Build succeeding? → `npm run build` / `cargo build`
- Server running? → `curl localhost:PORT`
- File created? → `ls -la path/to/file`

### Step 2: RUN
Execute the FULL command. Not a subset. Not from memory. Fresh execution.
- Run the COMPLETE test suite, not just "the relevant tests"
- Build the FULL project, not just "the changed file"
- Check ALL endpoints, not just "the one I changed"

### Step 3: READ
Read the FULL output. Check the exit code.
- Scroll through ALL output, not just the summary
- Check for warnings, not just errors
- Verify the exit code is 0 (or expected non-zero)

### Step 4: VERIFY
Does the output ACTUALLY confirm your claim?
- "243 passed" → Yes, tests pass
- "243 passed, 2 skipped" → Why are 2 skipped? Investigate.
- "Build succeeded with warnings" → What warnings? Are they acceptable?
- No output → Something is wrong. Investigate.

### Step 5: ONLY THEN — Make the Claim
Now you can say "done" / "fixed" / "passes" — WITH the evidence:
- Include the command you ran
- Include the relevant output
- Include the exit code

## Forbidden Phrases

| Never Say | Why | Instead Say |
|-----------|-----|-------------|
| "Should pass now" | Unverified claim | "Running tests..." → [show output] |
| "Should work" | Unverified claim | "Verifying..." → [show evidence] |
| "Looks correct" | Visual inspection ≠ verification | "Running verification..." → [show result] |
| "I'm confident this fixes it" | Confidence ≠ evidence | "Test output confirms the fix: [output]" |
| "Tests should be passing" | "Should" is not "are" | "Test results: [actual output]" |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I just ran the tests a minute ago" | State changes between runs. Run again. |
| "I only changed one line" | One line can break everything. Verify. |
| "The change is trivial" | Trivial changes cause production outages. Verify. |
| "I can see it's correct" | Seeing ≠ verifying. Run the actual check. |
| "Testing would take too long" | Shipping bugs takes longer. Verify. |

## The Origin Story

This skill exists because of 24 documented failures where:
- Agent said "fixed" but tests still failed
- Agent said "passing" but hadn't run the suite
- Agent said "complete" but files were missing
- Agent said "working" but the build was broken

Each failure broke trust. This gate function prevents all of them.

## Integration

- **Last skill to fire** before any completion claim
- Works with **anti-rationalization synapse** to catch excuse-making
- Works with **metacognition synapse** to prevent premature confidence
- Pipeline engine runs this automatically at step completion
