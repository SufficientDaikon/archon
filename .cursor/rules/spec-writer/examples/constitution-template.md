# Project Constitution

> Governing principles for spec-driven development in this project.
> Created with the SDD Agent System.

---

## Article I: Specification First

Every feature MUST begin as a specification. No code shall be written without an approved spec.

- Specifications define WHAT and WHY, never HOW
- Specs are technology-agnostic unless explicitly constrained
- Code is generated FROM specs, not the other way around

## Article II: Testable Requirements

Every functional requirement MUST be independently testable.

- Use Given/When/Then format for acceptance scenarios
- Every FR must trace to at least one user story
- Success criteria must be measurable without implementation knowledge

## Article III: Incremental Delivery

Features are delivered incrementally by user story priority.

- P1 stories form the MVP — they ship first
- Each story is independently testable and deployable
- No story depends on a lower-priority story

## Article IV: Deviation Protocol

When implementation conflicts with the spec, STOP and document.

- No silent divergence from the spec
- All deviations require explicit approval
- Deviations are logged for the reviewer agent

## Article V: Quality Gates

Nothing ships without passing the review gate.

- The reviewer agent compares implementation to spec
- Compliance score must be 80%+ for conditional approval
- Critical findings block deployment

## Article VI: Simplicity

Prefer the simplest solution that meets the spec.

- No over-engineering or "might need later" features
- No unnecessary abstractions or indirection
- If the spec doesn't require it, don't build it

## Article VII: Documentation as Artifact

The spec IS the documentation.

- Specs are versioned alongside code
- When features change, specs update first
- The review report serves as the quality record

---

## Customization

Modify this constitution to match your project's specific constraints:

- Add technology-specific articles (e.g., "All APIs must be RESTful")
- Add compliance requirements (e.g., "WCAG 2.1 AA minimum")
- Add team conventions (e.g., "All PRs require spec review before code review")
