# The 10 Iron Laws — Quick Reference

## Law 1: No Production Code Without a Failing Test First
- Write the test that defines the expected behavior
- Watch it fail (proves the test is valid)
- Write the minimum code to pass
- **Escape:** Only for pure documentation, config, or non-executable artifacts

## Law 2: No Fixes Without Root Cause Investigation
- Reproduce the bug first
- Form a hypothesis about the cause
- Gather evidence (logs, stack traces, debugger)
- Confirm root cause before writing any fix code
- **Escape:** Only for literal typos or syntax errors visible on inspection

## Law 3: No Completion Claims Without Fresh Verification Evidence
- "Fresh" means run right now, not 5 minutes ago
- Evidence must be terminal output, test results, or screenshots
- "I believe" and "I think" are not evidence
- **Escape:** None. This law has no exceptions.

## Law 4: Never Reverse Review Order
- **FIRST:** Spec compliance — does the code do what the spec says?
- **SECOND:** Code quality — is the code well-written?
- Quality without compliance is waste (beautifully wrong code)
- **Escape:** None. Always spec compliance first.

## Law 5: No Implementation Without Approved Design
- Design = spec, wireframe, architecture doc, or explicit user approval
- "Start coding and figure it out" violates this law
- Quick tasks still need explicit confirmation of requirements
- **Escape:** Bug fixes with clear reproduction steps serve as implicit spec

## Law 6: SPEC IS LAW
- The specification is the contract between designer and implementer
- Implementing something different (even if "better") is a violation
- Deviations require the Deviation Protocol
- **Escape:** Only via the explicit Deviation Protocol (STOP → DOCUMENT → ASK → LOG)

## Law 7: VERIFY, DON'T TRUST
- Past results don't prove current state
- Other agents' claims need fresh verification
- Your own claims need fresh verification
- **Escape:** None. Always verify.

## Law 8: DEVIATE LOUDLY
- Silent deviations are violations regardless of intent
- "I changed this because it's better" without approval = violation
- Every deviation must be documented BEFORE implementation
- **Escape:** None. Deviations are always loud.

## Law 9: INCREMENTAL PROOF
- Each step must be verified before building on it
- Don't build step 3 assuming steps 1-2 are correct — prove them
- Cascading assumptions create cascading failures
- **Escape:** None. Prove each step.

## Law 10: SAVE GLOBALLY
- Decisions made in one phase apply to ALL subsequent phases
- Constraints, tech stack choices, and design decisions persist
- Context must never shrink — only grow
- **Escape:** None. Everything is persistent.
