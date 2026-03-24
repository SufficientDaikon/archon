# DDE: Dissection-Driven Enhancement

> A repeatable methodology for extracting production patterns from real codebases and integrating them into the Archon framework.

## Overview

DDE (Dissection-Driven Enhancement) is the methodology used to systematically improve Archon skills by studying real, production-grade codebases. Rather than writing skills from theoretical knowledge alone, DDE grounds every rule, workflow step, and code pattern in evidence from analyzed repositories.

## The 8-Step DDE Loop

```
DISSECT --> CATALOG --> DIFF --> SPECIFY --> IMPLEMENT --> VALIDATE --> REGISTER --> COMPOSE
   |                                                                                    |
   +------------------------------------------------------------------------------------+
                              (repeat for next codebase)
```

### Step 1: DISSECT
**Input**: A production codebase (source repo URL or local path)
**Tool**: `dissector-agent` (13-phase autonomous analysis)
**Output**: Dissection document set (architecture overview, patterns catalog, code examples)

The dissector-agent performs:
1. Repository structure analysis
2. Dependency graph extraction
3. Architecture pattern identification
4. Design pattern cataloging (with confidence levels)
5. Code example extraction
6. Anti-pattern identification
7. Performance pattern analysis
8. Security pattern analysis

### Step 2: CATALOG
**Input**: Dissection documents
**Output**: Pattern inventory with frequency, location, and confidence

Catalog every pattern found in the dissection:
- **Pattern name**: e.g., "Guard Chain", "Cursor Pagination", "Soft Deletion"
- **Frequency**: How many times it appears (e.g., "61/61 API routes")
- **Confidence**: High/Medium/Low based on consistency of implementation
- **Code locations**: Specific files and line ranges
- **Dependencies**: What other patterns it relies on

### Step 3: DIFF
**Input**: Pattern inventory + current Archon skill catalog
**Output**: Gap analysis report

Compare cataloged patterns against existing skills:
- **Missing skills**: Patterns with no corresponding Archon skill
- **Incomplete skills**: Existing skills that don't cover the discovered pattern
- **Contradicted skills**: Existing skills whose rules conflict with production evidence
- **Confirmed skills**: Existing skills validated by production usage

Priority scoring:
- P0 (Critical): Pattern found in >80% of codebase, no skill exists
- P1 (High): Pattern found in >50%, skill exists but incomplete
- P2 (Medium): Pattern found in <50%, would improve existing skill
- P3 (Low): Pattern is niche or codebase-specific

### Step 4: SPECIFY
**Input**: Gap analysis report (P0 and P1 items)
**Output**: SDD-compliant specification for each new/upgraded skill

For each gap, create an SDD spec:
- **Identity**: Who is the agent persona?
- **Workflow**: What are the ordered steps?
- **Rules**: What are the DOs and DON'Ts (with evidence)?
- **Output Template**: What does the generated code look like?
- **Acceptance Criteria**: How do we verify the skill is correct?

Use the `spec-writer-agent` for spec generation.

### Step 5: IMPLEMENT
**Input**: SDD specifications
**Output**: SKILL.md + manifest.yaml + resources/ for each skill

Implementation follows the 9-section template:
1. **Identity** — Agent persona with 3 traits
2. **When to Use** — Trigger conditions and anti-conditions
3. **Workflow** — 5-7 ordered steps
4. **Rules** — 5-6 DOs, 5-6 DON'Ts
5. **Output Format** — File structure template
6. **Resources** — Reference docs and code examples
7. **Handoff** — Next agent, artifact description, user instruction
8. **Platform Notes** — Per-platform behavior
9. **manifest.yaml** — Triggers, tags, composes, platforms

Use the `implementer-agent` for skill authoring.

### Step 6: VALIDATE
**Input**: Implemented skills
**Output**: Compliance report (gold/silver/bronze/stub)

Run the compliance checker:
```bash
python scripts/skill-compliance-check.py --skill <skill-name>
```

Acceptance criteria:
- All new skills must score **gold** (9/9 sections)
- All upgraded skills must score **gold** (9/9 sections)
- manifest.yaml must have triggers, platforms, and tags
- Resource files must exist and be referenced

Use the `reviewer-agent` for quality review.

### Step 7: REGISTER
**Input**: Validated skills
**Output**: Updated archon.yaml

Register each skill in the root manifest:
- Add to `skills:` list (alphabetical order)
- Add to relevant `bundles:` (e.g., web-dev-kit, prompts-chat-kit)
- Update version numbers for upgraded skills
- Add `composes:` relationships in manifest.yaml

### Step 8: COMPOSE
**Input**: Registered skills
**Output**: Updated bundle manifests + composition graph

Connect skills into a system:
- `composes:` — Skills that work together (e.g., guard-chain composes error-handling-architecture)
- `extends:` — Skills that build on another (e.g., prisma-orm-patterns extends backend-development)
- Bundle grouping — Skills that are typically installed together

## Quality Gates

Each step has a quality gate that must pass before proceeding:

| Step | Gate | Metric |
|------|------|--------|
| DISSECT | Completeness | All 13 dissector phases completed |
| CATALOG | Coverage | Every pattern has frequency + confidence |
| DIFF | Prioritization | Every gap has a P0-P3 priority |
| SPECIFY | SDD Compliance | Spec has all required sections |
| IMPLEMENT | Template Compliance | 9/9 sections present |
| VALIDATE | Gold Standard | Compliance checker returns gold |
| REGISTER | Manifest Valid | archon.yaml parses correctly |
| COMPOSE | Graph Connected | No orphan skills in bundles |

## Example: prompts.chat DDE Cycle

**Source**: https://github.com/f/prompts.chat
**Dissection size**: 280KB across 19 documents

### Patterns Cataloged
| Pattern | Frequency | Confidence | Action |
|---------|-----------|------------|--------|
| Guard Chain | 61/61 routes | High | New skill (P0) |
| Cursor Pagination (perPage+1) | All list endpoints | High | New skill (P0) |
| Soft Deletion | All models | High | Integrated into prisma-orm-patterns |
| Error Taxonomy | All routes | High | New skill (P0) |
| Plugin Registry | Core architecture | High | Already existed (plugin-system) |
| Fluent Builder | SDK/API | High | Already existed (fluent-builder) |
| Provider Composition | React app | High | Integrated into react-best-practices upgrade |
| Server Components First | React app | High | Integrated into react-best-practices upgrade |
| React Compiler | Build config | High | Integrated into react-best-practices upgrade |

### Skills Created
- `guard-chain` (new, P0)
- `error-handling-architecture` (new, P0)
- `prisma-orm-patterns` (new, P0)

### Skills Upgraded
- `react-best-practices` v1.0 -> v2.0 (23 lines -> 137 lines, full 9-section)
- `backend-development` v1.0 -> v2.0 (topic-organized -> 9-section format)
- `e2e-testing-patterns` v1.0 -> v2.0 (code-heavy -> 9-section with patterns)

## Running DDE on a New Codebase

```bash
# 1. Run the dissector agent on a codebase
# (use dissector-agent with the target repo)

# 2. Catalog patterns from dissection output
# (manual or assisted by dissector-agent)

# 3. Run gap analysis against current skills
python scripts/skill-compliance-check.py

# 4. Create specs for missing/incomplete skills
# (use spec-writer-agent)

# 5. Implement skills from specs
# (use implementer-agent following 9-section template)

# 6. Validate skill compliance
python scripts/skill-compliance-check.py --skill <new-skill>

# 7. Register in archon.yaml
# (add to skills list, bundles, update versions)

# 8. Connect composition graph
# (add composes/extends to manifest.yaml files)
```
