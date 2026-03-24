# Decomposition Patterns

## Feature Implementation Pattern
```
1. Understand requirements (read spec, clarify ambiguities)
2. Design approach (architecture, data flow, component interaction)
3. Set up environment (dependencies, config, test framework)
4. Write failing tests (acceptance criteria → test cases)
5. Implement core logic (minimum viable implementation)
6. Implement edge cases (error handling, boundary conditions)
7. Run full test suite (no regressions, all new tests pass)
8. Document changes (code comments, README, CHANGELOG)
```

## Bug Investigation Pattern
```
1. Reproduce the bug (exact steps → consistent failure)
2. Gather evidence (logs, stack traces, error messages)
3. Isolate scope (which component, which input, which condition)
4. Form hypothesis (what could cause this exact behavior)
5. Test hypothesis (debugging, logging, unit test)
6. Confirm root cause (hypothesis matches evidence)
7. Implement fix (minimal change addressing root cause)
8. Verify fix (original bug gone, no new issues)
9. Add regression test (prevent recurrence)
```

## Code Review Pattern
```
1. Read the specification (understand what was intended)
2. Check spec compliance (does code match spec requirements?)
3. Check architecture (right patterns, proper separation)
4. Check code quality (naming, structure, complexity)
5. Check test coverage (critical paths tested?)
6. Check edge cases (error handling, boundaries)
7. Summarize findings (pass/fail with details)
```

## Refactoring Pattern
```
1. Document current behavior (ensure tests exist)
2. Identify refactoring targets (code smells, complexity)
3. Plan transformation steps (order matters)
4. Execute each step independently
5. Run tests after EACH step (behavior preserved?)
6. Clean up (remove dead code, update docs)
7. Final verification (full test suite)
```

## Research Pattern
```
1. Define the question precisely
2. Identify information sources
3. Gather data from each source
4. Cross-reference findings
5. Identify contradictions or gaps
6. Form conclusion with confidence level
7. List assumptions and unknowns
```

## Architecture Design Pattern
```
1. Clarify requirements (functional + non-functional)
2. Identify constraints (technology, performance, team)
3. Survey existing patterns (what similar systems use)
4. Propose 2-3 approaches
5. Evaluate each against requirements + constraints
6. Select and justify choice
7. Document architecture (diagrams, decisions, rationale)
8. Identify risks and mitigations
```
