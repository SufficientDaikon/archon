---
name: spec-writer
description: >-
  Use when transforming plans, ideas, or feature descriptions into comprehensive
  implementable specifications. Triggers on tasks involving requirements engineering,
  spec creation, user story writing, acceptance criteria definition, or when the user
  asks to "write a spec", "create a specification", or "turn this plan into a spec".
---

# Spec Writer Skill

This skill transforms high-level plans into comprehensive, implementable specifications following the Spec-Driven Development (SDD) methodology.

## When to Use This Skill

- User provides a plan, idea, or feature description and needs a spec
- User asks to "write a spec", "specify", "create requirements"
- User has a rough plan that needs to be formalized
- User needs acceptance criteria, user stories, or requirements

## Specification Output Structure

Every spec you produce MUST follow this structure. Use the template at `templates/spec-template.md` as the output format.

### Required Sections (always include):
1. **Project Overview** — What, why, and for whom
2. **User Scenarios & Stories** — Prioritized, independently testable
3. **Functional Requirements** — Numbered, testable, unambiguous
4. **Success Criteria** — Measurable, technology-agnostic

### Conditional Sections (include when relevant):
5. **Non-Functional Requirements** — Performance, security, scalability
6. **Key Entities & Data Model** — When data is involved
7. **Edge Cases & Error Handling** — Always for user-facing features
8. **Assumptions & Dependencies** — When they exist
9. **Out of Scope** — When scope boundaries matter

## Process

### Step 1: Parse the Plan
Extract from the user's input:
- **Actors**: Who uses this? (users, admins, systems, APIs)
- **Actions**: What do they do? (CRUD, workflows, interactions)
- **Data**: What data is involved? (entities, relationships, attributes)
- **Constraints**: What limits exist? (performance, security, platform)
- **Goals**: What does success look like?

### Step 2: Clarify Ambiguities
For CRITICAL ambiguities only (max 5 questions):
- Prioritize: scope > security > UX > technical
- Make informed defaults for everything else
- Document defaults in the Assumptions section

### Step 3: Write User Stories
Format each story as:
```markdown
### User Story N - [Title] (Priority: PN)

[Plain language description]

**Why this priority**: [Value explanation]
**Independent Test**: [How to test this story alone]

**Acceptance Scenarios**:
1. **Given** [state], **When** [action], **Then** [outcome]
2. **Given** [state], **When** [action], **Then** [outcome]
```

Priority Guide:
- **P1**: Core value — the MVP. If only one story ships, it's this one.
- **P2**: Important — significantly enhances value
- **P3**: Nice-to-have — polish and delight

### Step 4: Write Requirements
Format: `FR-001: System MUST [specific, testable capability]`

Rules:
- Every requirement is independently testable
- Use MUST for mandatory, SHOULD for recommended, MAY for optional
- No implementation details (no "using React", "via REST API", etc.)
- Every requirement traces to at least one user story

### Step 5: Define Success Criteria
Format: `SC-001: [Measurable, technology-agnostic metric]`

Good: "Users complete signup in under 2 minutes"
Bad: "API responds in under 200ms" (too technical)

### Step 6: Validate
Run through this checklist:
- [ ] No tech stack or implementation details
- [ ] All requirements testable
- [ ] Success criteria measurable
- [ ] ≤3 NEEDS CLARIFICATION markers
- [ ] Every story has acceptance scenarios
- [ ] Edge cases identified
- [ ] Scope bounded (in + out)

## File Output

Save the spec to one of these locations (in priority order):
1. `.specify/specs/[feature-name]/spec.md` (if .specify/ exists)
2. `specs/[feature-name]/spec.md` (if specs/ exists)
3. `[feature-name]-spec.md` (fallback, project root)

## Examples of Good vs Bad

### Good Requirement
> FR-003: System MUST allow users to reset their password via email verification within 5 minutes of request

### Bad Requirement
> FR-003: Implement password reset using SendGrid API with JWT tokens

### Good Success Criterion
> SC-002: 95% of users successfully complete their first task within 3 minutes

### Bad Success Criterion
> SC-002: Redis cache hit rate above 80%

## Handoff Instructions

After completing the spec, inform the user:
1. The spec file location
2. A summary of stories and their priorities
3. Any remaining NEEDS CLARIFICATION items
4. Recommend: "Review the spec, then use the **implementer agent** to build it"
