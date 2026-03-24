# Rationalization Tables — Complete Reference

## TDD Rationalizations

| # | Rationalization | Counter-Argument | Iron Law |
|---|----------------|-----------------|----------|
| 1 | "This function is too simple to test" | Simple functions have edge cases. Write the test. | #1 |
| 2 | "I'll write tests after the code works" | How do you know it works without tests? | #1 |
| 3 | "The existing tests cover this" | Do they? Run them and verify. | #7 |
| 4 | "Manual testing is faster" | Manual testing isn't repeatable or documented. | #3 |
| 5 | "Mocking is too complex for this" | Complexity in mocking reveals coupling in design. | #1 |
| 6 | "Tests slow down development" | Bugs slow down development more. | #1 |
| 7 | "100% coverage is unrealistic" | Nobody asked for 100%. Cover the behavior. | #1 |

## Debugging Rationalizations

| # | Rationalization | Counter-Argument | Iron Law |
|---|----------------|-----------------|----------|
| 1 | "I know what the bug is" | Then prove it. Run the diagnostic. | #2 |
| 2 | "Let me just try this fix" | Trying fixes without diagnosis creates new bugs. | #2 |
| 3 | "It worked on my machine" | Prove it works in the target environment. | #7 |
| 4 | "The error message is misleading" | Maybe. Investigate properly first. | #2 |
| 5 | "This is probably a race condition" | "Probably" means you don't know. Prove it. | #2 |
| 6 | "The third-party library has a bug" | Maybe. But verify your usage first. | #7 |

## Verification Rationalizations

| # | Rationalization | Counter-Argument | Iron Law |
|---|----------------|-----------------|----------|
| 1 | "I just ran this 5 minutes ago" | 5 minutes ago is not now. Run it again. | #3 |
| 2 | "The CI will catch it" | CI is a safety net, not primary verification. | #3 |
| 3 | "I visually inspected the output" | Eyes miss things. Use automated checks. | #7 |
| 4 | "The types guarantee correctness" | Types prevent some errors, not all. | #3 |
| 5 | "Code review will catch issues" | You're the first line of defense. | #3 |
| 6 | "It compiled, so it's correct" | Compilation ≠ correctness. | #3 |

## Planning Rationalizations

| # | Rationalization | Counter-Argument | Iron Law |
|---|----------------|-----------------|----------|
| 1 | "We don't need a spec for this" | Everything has requirements. Document them. | #5 |
| 2 | "The requirements are obvious" | Obvious to whom? Write them down. | #5 |
| 3 | "Let's start coding and figure it out" | Figure it out first. Then code. | #5 |
| 4 | "This is just a prototype" | Prototypes become production. Build it right. | #5 |
| 5 | "We can always rewrite it" | Rewrites cost 3x. Build it right. | #5 |
| 6 | "The deadline doesn't allow planning" | Skipping planning guarantees missing the deadline. | #5 |

## Scope Rationalizations

| # | Rationalization | Counter-Argument | Iron Law |
|---|----------------|-----------------|----------|
| 1 | "The user probably doesn't need this" | You don't decide scope. The spec does. | #6 |
| 2 | "This feature is gold-plating" | If it's in the spec, it's required. | #6 |
| 3 | "Let's ship this and add it later" | "Later" means "never" unless it's tracked. | #6 |
| 4 | "This is out of scope" | Only the spec defines scope. | #6 |
| 5 | "Close enough is good enough" | "Close" is not "correct". | #6 |
