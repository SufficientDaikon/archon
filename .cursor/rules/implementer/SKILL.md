---
name: implementer
description: >-
  Use when implementing features from a specification. Triggers on tasks involving
  spec-driven implementation, building from requirements, task breakdown execution,
  TDD from acceptance criteria, or when the user asks to "implement the spec",
  "build from spec", or "execute the implementation plan".
---

# Implementer Skill

This skill implements features faithfully from comprehensive specifications, following the Spec-Driven Development methodology where code serves the specification.

## When to Use This Skill

- User has an approved specification and wants to implement it
- User asks to "implement", "build", "code", or "execute" from a spec
- User needs to translate acceptance criteria into working code
- User needs task breakdown and systematic implementation

## Implementation Pipeline

### Step 1: Read & Analyze the Spec
1. Read the ENTIRE spec — don't skim
2. List all user stories with priorities
3. List all functional requirements
4. Identify key entities and their relationships
5. Note non-functional requirements and constraints
6. Check for any `[NEEDS CLARIFICATION]` markers — resolve with user first

### Step 2: Create Task Breakdown
Generate `tasks.md` using this format:

```markdown
# Implementation Tasks: [Feature Name]

**Spec**: [path to spec]
**Created**: [date]

## Phase 1: Setup
- [ ] T001 Initialize project structure per spec requirements
- [ ] T002 Configure dependencies and build tools
- [ ] T003 Create ignore files (.gitignore, etc.)

## Phase 2: Foundation
- [ ] T004 [P] Create [Entity] model in [path]
- [ ] T005 [P] Create [Entity] model in [path]
- [ ] T006 Set up storage/database layer in [path]

## Phase 3: User Story 1 (P1) — [Title]
**Goal**: [What this story delivers]
**Test**: [How to verify independently]

- [ ] T007 [US1] Write acceptance tests in [path]
- [ ] T008 [US1] Implement [component] in [path]
- [ ] T009 [US1] Implement [component] in [path]
- [ ] T010 [US1] Wire integration in [path]

## Phase 4: User Story 2 (P2) — [Title]
...

## Phase N: Polish & Cross-Cutting
- [ ] T0XX Implement error handling per spec edge cases
- [ ] T0XX Add input validation per FR requirements
- [ ] T0XX Create README documentation
```

### Step 3: Implement Systematically

For each phase:

1. **Before coding**: Re-read the relevant spec section
2. **Write tests first**: Convert Given/When/Then → test cases
3. **Implement**: Write minimal code to pass the tests
4. **Verify**: Run tests, check behavior matches spec
5. **Mark done**: Update tasks.md with `[X]`
6. **Checkpoint**: Confirm this phase works before moving on

### Step 4: Handle Deviations

When spec conflicts with reality:

```markdown
## DEVIATION: [Title]
- **Spec says**: [requirement]
- **Reality**: [what happened]
- **Proposed alternative**: [solution]
- **Impact**: [effect on feature]
```

1. STOP and document the deviation
2. Ask user for approval before proceeding
3. Log for the reviewer agent

### Step 5: Generate Completion Report

When done, create a completion report:

```markdown
# Implementation Completion Report

## Summary
- Total tasks: [N]
- Completed: [N]
- Deviations: [N]

## User Stories Implemented
- [X] US1 (P1): [title] — [status]
- [X] US2 (P2): [title] — [status]

## Requirements Coverage
- [X] FR-001: [description]
- [X] FR-002: [description]

## Deviations
[List any deviations]

## Files Created/Modified
[File list with descriptions]
```

## Task ID Format

```
- [ ] T001 [P] [US1] Description with exact file path
```

| Component | Required | Description |
|-----------|----------|-------------|
| `- [ ]` | Yes | Markdown checkbox |
| `T001` | Yes | Sequential task ID |
| `[P]` | No | Parallel-safe marker |
| `[US1]` | For story tasks | User story reference |
| Description | Yes | Clear action + file path |

## Implementation Rules

### DO:
- Follow the spec literally — it's your contract
- Write tests before code (from acceptance scenarios)
- Implement P1 stories first, then P2, then P3
- Verify at each checkpoint
- Track progress in tasks.md
- Report deviations immediately
- Use existing project patterns
- Keep it simple

### DON'T:
- Add features not in the spec
- "Improve" the spec silently
- Skip tests
- Over-engineer
- Move to next story before current one passes
- Ignore non-functional requirements
- Guess when you should ask

## Handoff

After implementation, tell the user:
1. Completion report location
2. Test results summary
3. Any deviations logged
4. Recommend: "Use the **reviewer agent** to verify spec compliance"
