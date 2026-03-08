---
name: reviewer
description: >-
  Use when reviewing implementation output against a specification for compliance.
  Generates a comprehensive HTML/CSS report comparing code to spec requirements.
  Triggers on tasks involving spec compliance review, implementation verification,
  quality auditing, or when user asks to "review against spec" or "verify implementation".
---

# Reviewer Skill

This skill compares implementation output against the original specification and produces a comprehensive, human-readable HTML compliance report.

## When to Use This Skill

- User has completed implementation and wants to verify spec compliance
- User asks to "review", "verify", "audit", or "check" implementation against spec
- User needs a compliance report comparing code to requirements
- User wants a quality gate assessment before shipping

## Review Process

### Step 1: Gather Inputs
Required:
1. **The specification file** (spec.md or equivalent)
2. **The project directory** (implemented code)

Optional but helpful:
3. **tasks.md** (implementation task tracker)
4. **Completion report** from the implementer
5. **Deviation log** from the implementer

### Step 2: Systematic Audit

Perform EACH of these audits:

#### A. User Story Coverage
For EACH story in the spec:
| Check | How to Verify |
|-------|---------------|
| Implemented? | Search codebase for story-related components |
| Acceptance scenarios satisfied? | Check each Given/When/Then against code behavior |
| Tests exist? | Search test files for story-related tests |
| Tests pass? | Run the test suite if possible |

Score: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL / ⬜ MISSING

#### B. Functional Requirements Coverage
For EACH FR-XXX:
- Find the code that implements it (file + line)
- Verify correctness against the spec wording
- Check if a test covers it

Score: ✅ IMPLEMENTED / ⚠️ PARTIAL / ❌ INCORRECT / ⬜ MISSING

#### C. Non-Functional Requirements
For EACH NFR:
- Find evidence in code (caching, validation, error handling, etc.)
- Assess whether it's measurably met

Score: ✅ MET / ⚠️ PARTIALLY / ❌ NOT MET / ⬜ NOT ADDRESSED

#### D. Success Criteria
For EACH SC-XXX:
- Is it verifiable with the current implementation?
- What evidence supports it?

Score: ✅ VERIFIABLE / ⚠️ LIKELY / ❌ UNLIKELY / ⬜ NOT ADDRESSED

#### E. Edge Cases
For EACH edge case in the spec:
- Is it handled in code? (find the handler)
- Is the handling correct?

Score: ✅ HANDLED / ⚠️ PARTIAL / ❌ UNHANDLED

### Step 3: Calculate Scores

**Per-item scoring**:
- ✅ = 1.0 points
- ⚠️ = 0.5 points
- ❌ = 0.0 points
- ⬜ = 0.0 points

**Overall compliance** = (total points / total possible) × 100%

**Verdict**:
- 95-100%: **APPROVED** — Ship it
- 80-94%: **APPROVED WITH CONDITIONS** — Minor fixes needed
- 60-79%: **NEEDS REVISION** — Significant gaps
- Below 60%: **REJECTED** — Major rework required

### Step 4: Generate HTML Report

Use the template at `templates/report-template.html` as the base.

The report MUST include:
1. **Executive Summary** — Score, verdict, key stats
2. **User Story Matrix** — Visual coverage table
3. **Requirements Traceability** — FR → Code → Test mapping
4. **Success Criteria Dashboard** — Visual status indicators
5. **Findings** — Categorized by severity:
   - 🔴 **Critical**: Feature broken, security issue, data loss risk
   - 🟠 **Major**: Requirement not implemented, test failing
   - 🟡 **Minor**: Partial implementation, missing edge case
   - 🔵 **Info**: Suggestion, pattern recommendation
6. **Deviations** — Analysis of any implementation deviations
7. **Verdict & Recommendations** — Overall assessment

### Step 5: Save & Report

1. Save HTML report as `review-report.html` in the project root
2. Present summary to user:
   - Overall compliance percentage
   - Verdict (APPROVED / NEEDS REVISION / etc.)
   - Critical findings count
   - Top 3 issues to address (if any)

## Rules

### DO:
- Check EVERY requirement — no sampling
- Include file paths and line numbers as evidence
- Credit good patterns alongside issues
- Be specific and actionable in recommendations
- Generate a self-contained HTML file (inline CSS, no external deps)

### DON'T:
- Be vague ("some issues found" — name them)
- Penalize for spec issues (that's spec-writer's domain)
- Include opinions not grounded in the spec
- Skip non-functional or edge case checks
- Generate report without reading ALL code
