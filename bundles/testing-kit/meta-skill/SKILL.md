# qa-master

**Meta-Skill Coordinator for QA and Testing**

## Purpose

Routes testing and QA requests to the appropriate specialized skill based on whether the focus is E2E test implementation, test planning, web application testing, or systematic debugging.

## Routing Logic

### 1. E2E Test Implementation → **e2e-testing-patterns**

**Trigger keywords:** Playwright, Cypress, E2E, end-to-end testing, test automation, test suite, flaky tests, page object model, test selectors, test patterns

**Use when:**
- Implementing E2E tests with Playwright or Cypress
- Building reliable test suites
- Fixing flaky tests
- Establishing E2E testing standards
- Creating page object models
- Improving test selector strategies
- Structuring E2E test architecture
- Learning E2E best practices

**Example requests:**
- "Write Playwright tests for checkout flow"
- "Fix flaky E2E tests"
- "Create a page object model"
- "Establish E2E testing standards"
- "Implement Cypress test suite"
- "Improve test selector reliability"

---

### 2. Test Planning & Documentation → **qa-test-planner**

**Trigger keywords:** test plan, test cases, test suite, manual testing, QA documentation, bug report, regression testing, test scenarios, acceptance testing

**Use when:**
- Creating comprehensive test plans
- Writing manual test cases
- Generating regression test suites
- Creating bug reports
- Planning test scenarios
- Documenting acceptance tests
- QA strategy and planning
- Test coverage analysis

**Example requests:**
- "Create a test plan for login feature"
- "Write manual test cases for checkout"
- "Generate regression test suite"
- "Create a bug report template"
- "Plan QA strategy for this sprint"
- "Document acceptance test scenarios"

---

### 3. Web Application Testing → **webapp-testing**

**Trigger keywords:** test webapp, local testing, browser testing, screenshot, browser logs, UI testing, verify frontend, debug UI behavior

**Use when:**
- Testing local web applications
- Verifying frontend functionality
- Debugging UI behavior
- Capturing browser screenshots
- Viewing browser logs
- Automated UI verification
- Testing running web servers
- Frontend integration testing

**Example requests:**
- "Test this local webapp on localhost:3000"
- "Verify the login button works"
- "Capture screenshot of the dashboard"
- "Check browser console logs"
- "Test UI functionality automatically"
- "Verify frontend integration"

---

### 4. Debugging & Root Cause Analysis → **systematic-debugging**

**Trigger keywords:** debug, bug, error, crash, investigate, root cause, troubleshooting, test failure, unexpected behavior, fix issue

**Use when:**
- Encountering any bug or error
- Test failures that need investigation
- Unexpected behavior in code
- Need root cause analysis
- Before attempting fixes
- Systematic investigation required
- Complex debugging scenarios

**Critical rule:** ALWAYS use systematic-debugging BEFORE proposing fixes. Never jump to solutions.

**Example requests:**
- "Debug why this test is failing"
- "Investigate this error"
- "Find root cause of crash"
- "Why is this feature not working?"
- "Troubleshoot this issue"
- "Analyze test failure"

---

## Multi-Skill Scenarios

### Complete Feature Testing
1. **qa-test-planner** → Create test plan and test cases
2. **e2e-testing-patterns** → Implement automated E2E tests
3. **webapp-testing** → Verify UI functionality
4. **systematic-debugging** → Debug any failures

### E2E Test Development
1. **qa-test-planner** → Define test scenarios
2. **e2e-testing-patterns** → Implement tests
3. **systematic-debugging** → Fix flaky tests

### Bug Investigation
1. **systematic-debugging** → Investigate root cause
2. **webapp-testing** → Verify fix locally (if webapp)
3. **e2e-testing-patterns** → Add regression test

### QA Process Setup
1. **qa-test-planner** → Establish test strategy
2. **e2e-testing-patterns** → Setup E2E framework
3. **systematic-debugging** → Debug framework issues

---

## Decision Tree

```
Is the request about...

├─ BUG, ERROR, OR TEST FAILURE?
│  └─ systematic-debugging (ALWAYS FIRST)
│
├─ IMPLEMENTING E2E TESTS (Playwright/Cypress)?
│  └─ e2e-testing-patterns
│
├─ TEST PLANNING OR DOCUMENTATION?
│  └─ qa-test-planner
│
└─ TESTING LOCAL WEBAPP OR UI VERIFICATION?
   └─ webapp-testing
```

---

## Critical Debugging Rule

**🚨 BEFORE PROPOSING ANY FIX:**

If the user reports:
- A bug
- An error
- A test failure
- Unexpected behavior
- Something "not working"

**YOU MUST:**
1. Route to **systematic-debugging** FIRST
2. Complete root cause investigation
3. THEN (and only then) proceed to fix

**NEVER:**
- Jump straight to a solution
- Propose fixes without investigation
- Skip root cause analysis

---

## Layer-Based Routing

### Planning Layer
**qa-test-planner** handles test strategy, plans, and documentation

### Implementation Layer
**e2e-testing-patterns** handles automated test implementation

### Execution Layer
**webapp-testing** handles live web application testing

### Investigation Layer
**systematic-debugging** handles all debugging and root cause analysis

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **Bug Investigation** | systematic-debugging | webapp-testing | e2e-testing-patterns |
| **E2E Test Writing** | e2e-testing-patterns | qa-test-planner | systematic-debugging |
| **Test Planning** | qa-test-planner | e2e-testing-patterns | - |
| **UI Verification** | webapp-testing | systematic-debugging | - |
| **Test Debugging** | systematic-debugging | e2e-testing-patterns | webapp-testing |
| **QA Strategy** | qa-test-planner | e2e-testing-patterns | - |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this a BUG, ERROR, or FAILURE?**
   - Yes → systematic-debugging (MANDATORY)
   - No → Continue

2. **Is this about PLANNING or DOCUMENTATION?**
   - Yes → qa-test-planner
   - No → Continue

3. **Is this about IMPLEMENTING E2E TESTS?**
   - Yes → e2e-testing-patterns
   - No → Continue

4. **Is this about TESTING A RUNNING WEBAPP?**
   - Yes → webapp-testing
   - No → qa-test-planner (default for unclear cases)

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "My test is failing" | systematic-debugging | Bug/failure requires investigation |
| "Write Playwright tests" | e2e-testing-patterns | E2E test implementation |
| "Create a test plan" | qa-test-planner | Test planning |
| "Test this webapp" | webapp-testing | Web app verification |
| "Debug this error" | systematic-debugging | Debugging required |
| "Fix flaky tests" | systematic-debugging → e2e-testing-patterns | Debug first, then fix |
| "Write test cases" | qa-test-planner | Test documentation |
| "Verify login works" | webapp-testing | UI functionality verification |
| "Setup E2E framework" | e2e-testing-patterns | E2E infrastructure |

---

## Testing Workflow Patterns

### Pattern 1: TDD (Test-Driven Development)
```
qa-test-planner (define acceptance criteria)
    ↓
e2e-testing-patterns (write failing test)
    ↓
[implementation happens]
    ↓
webapp-testing (verify it works)
```

### Pattern 2: Bug Fix Workflow
```
systematic-debugging (investigate root cause)
    ↓
[fix implementation]
    ↓
e2e-testing-patterns (add regression test)
    ↓
webapp-testing (verify fix)
```

### Pattern 3: QA Process
```
qa-test-planner (create test plan)
    ↓
e2e-testing-patterns (automate tests)
    ↓
webapp-testing (manual verification)
    ↓
systematic-debugging (investigate failures)
```

---

## Framework Detection

Auto-detect testing context:

- **Playwright files detected** (*.spec.ts, playwright.config.ts)
  → Use e2e-testing-patterns for test implementation

- **Cypress files detected** (*.cy.js, cypress.config.js)
  → Use e2e-testing-patterns for test implementation

- **Running webapp detected** (localhost:*, dev server)
  → Use webapp-testing for live testing

- **Test failure detected** (failing tests, error messages)
  → Use systematic-debugging FIRST

---

## Integration Points

### E2E + Debugging
- **e2e-testing-patterns** implements tests
- **systematic-debugging** investigates failures
- Coordinate: Debug before refactoring tests

### Planning + Implementation
- **qa-test-planner** defines what to test
- **e2e-testing-patterns** implements automated tests
- Coordinate: Test cases inform E2E test design

### Webapp Testing + Debugging
- **webapp-testing** identifies issues
- **systematic-debugging** investigates root cause
- Coordinate: Use webapp-testing to reproduce, systematic-debugging to analyze

---

## Quality Gates

Before marking testing work complete:

1. **Test plan created?** → qa-test-planner ✓
2. **E2E tests implemented?** → e2e-testing-patterns ✓
3. **Tests passing?** → webapp-testing or e2e-testing-patterns ✓
4. **Failures debugged?** → systematic-debugging ✓
5. **No flaky tests?** → e2e-testing-patterns ✓

---

## Common Anti-Patterns (Avoid)

- ❌ Proposing fixes without using systematic-debugging → ALWAYS debug first
- ❌ Using webapp-testing for E2E test implementation → Use e2e-testing-patterns
- ❌ Using e2e-testing-patterns for test planning → Use qa-test-planner
- ❌ Skipping systematic-debugging for "obvious" bugs → Always investigate

---

## Debugging First Principle

**The Golden Rule of QA-Master:**

```
IF (bug OR error OR failure OR "not working") {
  THEN {
    FIRST: systematic-debugging
    SECOND: implement fix
    THIRD: verify with appropriate testing skill
  }
}
```

**Never skip Step 1.**

---

## Tool-Specific Routing

| Tool/Framework | Routed To | Use Case |
|----------------|-----------|----------|
| **Playwright** | e2e-testing-patterns | E2E test implementation |
| **Cypress** | e2e-testing-patterns | E2E test implementation |
| **Manual Test Cases** | qa-test-planner | Test documentation |
| **Local Webapp** | webapp-testing | Live UI testing |
| **Browser DevTools** | webapp-testing | Console logs, screenshots |
| **Debugger** | systematic-debugging | Root cause analysis |

---

## Notes for AI Assistants

- **BUG/ERROR → ALWAYS systematic-debugging FIRST** (non-negotiable)
- **E2E tests → e2e-testing-patterns**
- **Test planning → qa-test-planner**
- **Live webapp → webapp-testing**
- **Never jump to solutions** — always investigate root cause
- **Chain systematic-debugging → fix → test** for bug workflows
- **Consult each SKILL.md** before applying testing knowledge
- **Use systematic-debugging as a gate** before any fix attempt
