# sdd-pipeline-expert

**Meta-Skill Coordinator for Spec-Driven Development Lifecycle**

## Purpose

Orchestrates the complete Spec-Driven Development (SDD) lifecycle from specification writing through implementation and compliance review, ensuring every phase follows the spec-driven methodology.

## SDD Lifecycle Phases

The SDD process follows a rigorous, phase-gated workflow:

```
1. SPECIFICATION → spec-writer
2. IMPLEMENTATION → implementer
3. COMPLIANCE REVIEW → reviewer
4. (Loop if non-compliant) → Back to implementer
5. DESIGN HANDOFF → design-handoff (for UI/UX artifacts)
6. DESIGN REVIEW → design-review (for design quality gates)
```

---

## Routing Logic

### 1. Phase 1: Specification Writing → **spec-writer**

**Trigger keywords:** spec, specification, requirements, user story, acceptance criteria, write spec, create spec, requirements engineering, feature description, plan to spec

**Use when:**
- Transforming high-level plans into detailed specs
- Writing comprehensive specifications
- Creating user stories with acceptance criteria
- Defining requirements
- Turning feature descriptions into implementable specs
- Establishing architectural requirements
- Defining API contracts
- Creating testable acceptance criteria

**Deliverable:** Comprehensive Specification Document (markdown)

**Example requests:**
- "Turn this plan into a spec"
- "Write a specification for user authentication"
- "Create a spec from these requirements"
- "Define acceptance criteria for this feature"
- "Document API specification for REST endpoints"

---

### 2. Phase 2: Implementation → **implementer**

**Trigger keywords:** implement, build, code, develop, execute, implement the spec, build from spec, code from specification, TDD, test-driven

**Use when:**
- Implementing features from a specification
- Building from approved specs
- Executing spec-driven implementation
- Writing tests based on acceptance criteria
- Following specification section-by-section
- Verifying implementation against spec
- Test-Driven Development from specs

**Input:** Specification document
**Deliverable:** Implemented code with tests

**Example requests:**
- "Implement this specification"
- "Build the feature from the spec"
- "Execute this implementation plan"
- "Code the system based on these requirements"
- "Implement section 3 of the spec"

---

### 3. Phase 3: Compliance Review → **reviewer**

**Trigger keywords:** review, compliance, verify, audit, check against spec, compliance review, spec compliance, implementation review, validate implementation

**Use when:**
- Reviewing implementation against specification
- Verifying spec compliance
- Auditing completed implementation
- Comparing code to requirements
- Generating compliance reports
- Identifying gaps and deviations
- Quality gate validation

**Input:** Specification + Implementation
**Deliverable:** HTML/CSS Compliance Report

**Example requests:**
- "Review this implementation against the spec"
- "Verify spec compliance"
- "Check if the code matches the requirements"
- "Generate a compliance report"
- "Audit implementation for gaps"

---

### 4. Design Handoff Management → **design-handoff**

**Trigger keywords:** handoff, lifecycle state, design artifact, artifact format, inter-agent communication, handoff protocol, lifecycle management

**Use when:**
- Managing design artifact handoffs between agents
- Tracking lifecycle state of design artifacts
- Formatting handoff artifacts
- Coordinating between design agents
- Managing quality gate transitions
- Ensuring proper artifact format standards

**Deliverable:** Formatted handoff artifact with lifecycle metadata

**Example requests:**
- "Prepare this design for handoff"
- "Format this artifact for the next agent"
- "Manage lifecycle state transition"
- "Coordinate handoff from wireframe to visual design"
- "Track design artifact lifecycle"

---

### 5. Design Quality Review → **design-review**

**Trigger keywords:** design review, design critique, heuristic evaluation, design quality, design compliance, accessibility audit, design standards

**Use when:**
- Reviewing design artifacts for quality
- Conducting design critiques
- Heuristic evaluation of designs
- Checking design compliance
- Assessing visual quality
- Accessibility compliance audits
- Design system consistency checks

**Deliverable:** Design Review Report with scores and feedback

**Example requests:**
- "Review this design for quality"
- "Critique this wireframe"
- "Evaluate design compliance"
- "Audit accessibility of this design"
- "Check design system consistency"

---

## Core SDD Workflow (Sequential)

### Standard SDD Pipeline
```
spec-writer (create spec)
    ↓
implementer (build from spec)
    ↓
reviewer (verify compliance)
    ↓
IF non-compliant → implementer (fix gaps)
    ↓
reviewer (re-verify)
    ↓
DONE
```

### Design-Focused SDD Pipeline
```
spec-writer (design spec)
    ↓
implementer (create design)
    ↓
design-review (quality gate)
    ↓
IF issues → implementer (fix)
    ↓
design-handoff (prepare for next phase)
    ↓
NEXT PHASE
```

---

## Multi-Phase Scenarios

### Feature Development (Full SDD)
1. **spec-writer** → Write comprehensive spec
2. **implementer** → Implement feature with tests
3. **reviewer** → Verify compliance
4. **implementer** (if needed) → Fix gaps
5. **reviewer** → Final sign-off

### UI/UX Development
1. **spec-writer** → UX specification
2. **implementer** → Build UI components
3. **design-review** → Quality audit
4. **reviewer** → Spec compliance check
5. **design-handoff** → Prepare for production

### API Development
1. **spec-writer** → API specification (OpenAPI)
2. **implementer** → Build API endpoints
3. **reviewer** → Verify API matches spec
4. **implementer** → Fix deviations
5. **reviewer** → Final approval

---

## Decision Tree

```
What phase are you in?

├─ NEED SPECIFICATION?
│  └─ spec-writer
│
├─ HAVE SPEC, NEED IMPLEMENTATION?
│  └─ implementer
│
├─ HAVE IMPLEMENTATION, NEED COMPLIANCE CHECK?
│  └─ reviewer
│
├─ DESIGN ARTIFACT HANDOFF?
│  └─ design-handoff
│
└─ DESIGN QUALITY REVIEW?
   └─ design-review
```

---

## State-Based Routing

Track the current state of work:

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **Idea/Plan** | Create spec | spec-writer |
| **Spec Approved** | Implement | implementer |
| **Implementation Complete** | Review compliance | reviewer |
| **Non-compliant** | Fix issues | implementer |
| **Compliant** | DONE or Handoff | design-handoff (if design) |
| **Design Created** | Quality review | design-review |
| **Design Approved** | Handoff | design-handoff |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **New Feature** | spec-writer | implementer | reviewer |
| **From Spec** | implementer | reviewer | - |
| **Verify Code** | reviewer | implementer | - |
| **Design Handoff** | design-handoff | design-review | - |
| **Design Quality** | design-review | reviewer | - |
| **Fix Gaps** | implementer | reviewer | - |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Do we have a spec?**
   - No → spec-writer
   - Yes → Continue

2. **Do we have implementation?**
   - No → implementer
   - Yes → Continue

3. **Has compliance been verified?**
   - No → reviewer
   - Yes → DONE or design-handoff

4. **Is this a design artifact?**
   - Yes → design-review or design-handoff
   - No → Follow standard SDD flow

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "Write a spec for login feature" | spec-writer | Creating specification |
| "Implement this spec" | implementer | Spec-driven implementation |
| "Review code against spec" | reviewer | Compliance verification |
| "Fix compliance gaps" | implementer | Re-implementation |
| "Prepare design for handoff" | design-handoff | Lifecycle management |
| "Review wireframe quality" | design-review | Design quality gate |
| "Turn this plan into a spec" | spec-writer | Requirements engineering |
| "Build from specification" | implementer | Implementation phase |

---

## Quality Gates

The SDD pipeline enforces quality gates:

### Gate 1: Spec Completeness
- **Checked by:** spec-writer (self-evaluation)
- **Criteria:** All requirements defined, acceptance criteria clear, architecture specified
- **Pass → Proceed to implementer**

### Gate 2: Implementation Compliance
- **Checked by:** reviewer
- **Criteria:** Code matches spec, tests pass, acceptance criteria met
- **Pass → DONE**
- **Fail → Back to implementer**

### Gate 3: Design Quality (if applicable)
- **Checked by:** design-review
- **Criteria:** Accessibility, consistency, visual quality, UX compliance
- **Pass → design-handoff**
- **Fail → Back to implementer**

---

## Looping and Iteration

The SDD pipeline supports iteration:

```
spec-writer (v1 spec)
    ↓
implementer (v1 implementation)
    ↓
reviewer (finds gaps)
    ↓
spec-writer (update spec) [OPTIONAL: only if spec was incomplete]
    ↓
implementer (fix gaps)
    ↓
reviewer (re-verify)
    ↓
DONE
```

**Key principle:** The spec is the source of truth. If reviewer finds issues, determine if:
1. **Implementation didn't follow spec** → implementer fixes
2. **Spec was unclear/incomplete** → spec-writer updates, then implementer re-implements

---

## Input/Output Contracts

### spec-writer
- **Input:** High-level plan, feature description, requirements
- **Output:** Specification document (markdown)

### implementer
- **Input:** Specification document
- **Output:** Implemented code + tests

### reviewer
- **Input:** Specification + Implementation
- **Output:** HTML Compliance Report

### design-handoff
- **Input:** Design artifact + lifecycle metadata
- **Output:** Formatted handoff artifact

### design-review
- **Input:** Design artifact
- **Output:** Design review report with scores

---

## Integration Notes

### When to combine skills:

**Spec → Implement → Review (Standard)**
- Always chain these three in sequence
- Never skip reviewer after implementer

**Design Pipeline**
- implementer → design-review → design-handoff
- Or: spec-writer → implementer → design-review

### When NOT to combine:

- Don't call reviewer before implementer
- Don't skip spec-writer and go straight to implementer (unless spec already exists)
- Don't use design-handoff for non-design artifacts

---

## Compliance Report Interpretation

After **reviewer** generates a report:

- **GREEN (90-100% compliance)** → DONE ✅
- **YELLOW (70-89% compliance)** → Minor fixes needed → implementer
- **RED (< 70% compliance)** → Major gaps → implementer (possibly spec-writer if spec unclear)

---

## Notes for AI Assistants

- **Always start with spec-writer** unless spec already exists
- **Never skip reviewer** after implementation
- **Use reviewer to validate**, not to modify code (reviewer is read-only)
- **Chain skills sequentially** — SDD is a pipeline, not parallel
- **Track state** — know where you are in the pipeline
- **Enforce quality gates** — don't proceed if gates fail
- **Loop as needed** — iteration is expected
- **Consult each SKILL.md** before applying skill knowledge
- **Treat spec as source of truth** — implementation must match spec
