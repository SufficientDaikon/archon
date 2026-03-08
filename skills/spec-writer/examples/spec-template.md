# Feature Specification: [FEATURE NAME]

**Created**: [DATE]
**Status**: Draft
**Source**: [Plan or description reference]

---

## 1. Project Overview

### What We're Building

[Clear, concise description of the feature/product]

### Why We're Building It

[Business value, user pain point being solved, opportunity]

### Who It's For

[Primary and secondary user personas]

---

## 2. User Scenarios & Stories

<!--
  Stories are PRIORITIZED as user journeys ordered by importance.
  Each story is INDEPENDENTLY TESTABLE — implementing just ONE
  delivers a viable MVP slice.

  P1 = Core value (the MVP)
  P2 = Important (enhances value significantly)
  P3 = Nice-to-have (polish and delight)
-->

### User Story 1 — [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why P1]

**Independent Test**: [How this can be tested standalone]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 — [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why P2]

**Independent Test**: [How this can be tested standalone]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 — [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why P3]

**Independent Test**: [How this can be tested standalone]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### Edge Cases

- What happens when [boundary condition]?
- How does the system handle [error scenario]?
- What if [unexpected user behavior]?

---

## 3. Functional Requirements

### Core Requirements

- **FR-001**: System MUST [specific capability]
- **FR-002**: System MUST [specific capability]
- **FR-003**: Users MUST be able to [key interaction]
- **FR-004**: System MUST [data requirement]
- **FR-005**: System MUST [behavior]

### Validation & Security

- **FR-0XX**: System MUST validate [input type] before processing
- **FR-0XX**: System MUST [security requirement]

### Data & Persistence

- **FR-0XX**: System MUST persist [data type] across sessions
- **FR-0XX**: System MUST [retention/cleanup policy]

---

## 4. Non-Functional Requirements _(include when relevant)_

### Performance

- **NFR-001**: [Response time, throughput, latency targets]

### Scalability

- **NFR-002**: [Concurrent users, data volume, growth targets]

### Security

- **NFR-003**: [Authentication, authorization, data protection]

### Accessibility

- **NFR-004**: [WCAG level, assistive technology support]

### Reliability

- **NFR-005**: [Uptime, recovery, data integrity]

---

## 5. Key Entities _(include when data is involved)_

### [Entity 1]

- **What it represents**: [description]
- **Key attributes**: [list without implementation types]
- **Relationships**: [how it relates to other entities]

### [Entity 2]

- **What it represents**: [description]
- **Key attributes**: [list]
- **Relationships**: [connections]

---

## 6. Success Criteria

### Measurable Outcomes

- **SC-001**: [User-facing measurable metric]
- **SC-002**: [Business measurable metric]
- **SC-003**: [Quality measurable metric]
- **SC-004**: [Adoption/satisfaction metric]

---

## 7. Assumptions & Dependencies

### Assumptions

- [Assumption 1 — what we're taking as given]
- [Assumption 2]

### Dependencies

- [Dependency 1 — external system, team, or resource]
- [Dependency 2]

---

## 8. Out of Scope

The following are explicitly **NOT** part of this feature:

- [Out of scope item 1]
- [Out of scope item 2]
- [Out of scope item 3]

---

## 9. Acceptance Checklist

### Spec Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] All mandatory sections completed
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable and technology-agnostic
- [ ] No more than 3 `[NEEDS CLARIFICATION]` markers remain
- [ ] Every user story has acceptance scenarios
- [ ] Edge cases identified for major flows
- [ ] Scope is clearly bounded
- [ ] All functional requirements trace to a user story
