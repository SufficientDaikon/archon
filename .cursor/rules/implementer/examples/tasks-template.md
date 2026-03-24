# Implementation Tasks: [FEATURE NAME]

**Spec**: [path-to-spec]
**Created**: [DATE]
**Status**: In Progress

---

## Phase 1: Setup

> Project initialization and configuration

- [ ] T001 Initialize project structure per implementation plan
- [ ] T002 Install and configure dependencies
- [ ] T003 Set up build/dev tooling (linting, formatting, build scripts)
- [ ] T004 Create ignore files (.gitignore, etc.) for tech stack

**Checkpoint**: Project builds/runs in empty state ☐

---

## Phase 2: Foundation

> Blocking prerequisites that all user stories depend on

- [ ] T005 [P] Create [Entity1] model/schema in [path]
- [ ] T006 [P] Create [Entity2] model/schema in [path]
- [ ] T007 Set up storage/database layer in [path]
- [ ] T008 Create shared types/constants in [path]
- [ ] T009 Implement auth/authorization if specified in [path]

**Checkpoint**: Foundation compiles, basic tests pass ☐

---

## Phase 3: User Story 1 (P1) — [Title]

> **Goal**: [What this story delivers to users]
> **Independent Test**: [How to verify this story works standalone]

### Tests

- [ ] T010 [US1] Write acceptance tests from scenarios in [path]

### Implementation

- [ ] T011 [US1] Implement [core component] in [path]
- [ ] T012 [US1] Implement [service/logic] in [path]
- [ ] T013 [US1] Implement [interface/endpoint/UI] in [path]
- [ ] T014 [US1] Wire integration between layers in [path]

**Checkpoint**: US1 acceptance tests pass, story works end-to-end ☐

---

## Phase 4: User Story 2 (P2) — [Title]

> **Goal**: [What this story delivers]
> **Independent Test**: [How to verify]

### Tests

- [ ] T015 [US2] Write acceptance tests in [path]

### Implementation

- [ ] T016 [P] [US2] Implement [component] in [path]
- [ ] T017 [US2] Implement [component] in [path]

**Checkpoint**: US2 acceptance tests pass ☐

---

## Phase 5: User Story 3 (P3) — [Title]

> **Goal**: [What this story delivers]
> **Independent Test**: [How to verify]

### Tests

- [ ] T018 [US3] Write acceptance tests in [path]

### Implementation

- [ ] T019 [P] [US3] Implement [component] in [path]

**Checkpoint**: US3 acceptance tests pass ☐

---

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T0XX Implement error handling per spec edge cases in [paths]
- [ ] T0XX Add input validation per FR requirements in [paths]
- [ ] T0XX Performance optimization per NFR targets
- [ ] T0XX Create README and API documentation
- [ ] T0XX Final integration test run

**Checkpoint**: All tests pass, all requirements verified ☐

---

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3-N (Stories, in order)
                                        → Phase Final (Polish)
```

## Progress Tracking

| Phase      | Status | Tasks  | Done  | Remaining |
| ---------- | ------ | ------ | ----- | --------- |
| Setup      | ☐      | 4      | 0     | 4         |
| Foundation | ☐      | 5      | 0     | 5         |
| US1 (P1)   | ☐      | 5      | 0     | 5         |
| US2 (P2)   | ☐      | 3      | 0     | 3         |
| US3 (P3)   | ☐      | 2      | 0     | 2         |
| Polish     | ☐      | 5      | 0     | 5         |
| **Total**  |        | **24** | **0** | **24**    |
