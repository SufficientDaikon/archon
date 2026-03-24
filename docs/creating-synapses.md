# Creating Synapses

> Build cognitive capabilities that enhance agent reasoning. Synapses add structured thinking layers — planning, monitoring, and reflection — that fire automatically during task execution.

## 🧬 Synapse Anatomy

Every Archon synapse lives in its own directory under `synapses/` and follows this structure:

```
synapses/my-synapse/
├── SYNAPSE.md          — Instructions the AI agent follows
├── manifest.yaml       — Metadata, firing phases, type
└── resources/          — Rubrics, templates, heuristics
```

> **Skills vs Synapses:** Skills define *what* an agent does (task-specific instructions). Synapses define *how* an agent thinks (cognitive enhancements that layer on top of any task).

## 🏷️ Core vs Optional Types

Every synapse has a `synapse-type` that determines how it binds to agents:

### Core Synapses

Core synapses are **auto-injected into all agents**. They fire for every task, scaling effort to complexity. Use core for fundamental cognitive capabilities every agent benefits from.

```yaml
synapse-type: core
# Auto-injected — every agent gets this synapse
```

### Optional Synapses

Optional synapses are **bound per-agent**. They only fire when explicitly included in an agent's configuration. Use optional for specialized cognitive patterns relevant to specific roles.

```yaml
synapse-type: optional
# Only fires when an agent explicitly binds this synapse
```

> ⚠️ **Choose Wisely:** Core synapses add overhead to *every* agent interaction. Only mark a synapse as core if it genuinely benefits all agents. When in doubt, start with optional.

## Step 1: SYNAPSE.md

This is the instruction file the AI agent reads. **Required sections:**

### 🎭 Identity

Who is this synapse? What cognitive capability does it provide?

```markdown
# My Synapse

## Identity

**Name:** My Synapse
**Type:** core | optional
**Version:** 1.0.0
**Author:** your-name

Describe the cognitive capability this synapse provides.
What aspect of thinking does it enhance? Why does it matter?
```

### 🎯 When Active

When does this synapse fire? Core synapses fire for every agent task. Optional synapses fire only when bound.

```markdown
## When Active

- **Activation:** always-on | binding-activated
- **Phases:** 3 firing phases

Describe the conditions under which this synapse activates
and how it scales effort to task complexity.
```

### 🔥 Firing Phases

The core of a synapse — structured phases that fire at specific points during task execution. Each phase has timing, instructions, and an output format.

```markdown
## Firing Phases

### Phase 1 — PLAN (Pre-Fire)

**Timing:** Before starting ANY task.

**Instructions:**

1. Step one of this phase
2. Step two of this phase

**Output Format:**

### 🧠 My Synapse — PLAN
- **Dimension 1:** [value]
- **Dimension 2:** [value]
```

### 📏 Rules

DO and DON'T lists — guardrails for the synapse behavior.

```markdown
## Rules

### DO:
- Be honest about uncertainty
- Scale monitoring effort to task complexity
- Justify every rating with evidence

### DON'T:
- Skip phases when under time pressure
- Hide uncertainty to appear more capable
- Produce output longer than the actual task
```

### 📦 Output Format

Describe the internal reasoning artifacts this synapse produces. These are **thinking artifacts**, not work artifacts.

```markdown
## Output Format

This synapse produces internal reasoning artifacts:

| Phase | Artifact | Purpose |
|-------|----------|---------|
| PLAN  | Planning assessment | Ensures readiness before work |
| MONITOR | Confidence tags | Communicates certainty |
| REFLECT | Reflection summary | Self-assessment for quality |

These artifacts are embedded in the agent's output stream.
```

### 🤝 Resources

Reference table of supporting materials the synapse can consult.

```markdown
## Resources

| Resource | Type | Description |
|----------|------|-------------|
| resources/rubric.md | rubric | Calibrated scale with criteria |
| resources/template.md | template | Structured output template |
| resources/heuristic.md | heuristic | Detection heuristics |
```

## Step 2: manifest.yaml

The manifest declares everything about your synapse except the instructions themselves:

```yaml
name: my-synapse
version: 1.0.0
description: "What cognitive capability this synapse provides"
author: your-name
synapse-type: core   # core | optional
license: MIT

firing-phases:
  - name: PLAN
    timing: pre-task
    description: "Assess complexity and select strategy"

  - name: MONITOR
    timing: active
    description: "Track confidence and detect stuck loops"

  - name: REFLECT
    timing: post-task
    description: "Self-score quality and capture lessons"

tags:
  - reasoning
  - metacognition

# Optional: Supporting reference materials
resources:
  - path: resources/rubric.md
    type: rubric
    load: always
    description: "Calibrated confidence scale"

  - path: resources/template.md
    type: template
    load: always
    description: "Structured output template"

# Optional: Restrict to specific platforms
# platforms:
#   - claude-code
#   - copilot-cli
#   - cursor
#   - windsurf
#   - antigravity
```

### Manifest Field Reference

#### Required Fields

- **`name`** — Unique kebab-case identifier (`^[a-z][a-z0-9-]*$`)
- **`version`** — Semantic version (`MAJOR.MINOR.PATCH`)
- **`description`** — Human-readable purpose (10–200 characters)
- **`author`** — Creator identifier
- **`synapse-type`** — `core` (auto-injected) or `optional` (per-agent binding)
- **`firing-phases`** — List of phase objects (at least one required), each with `name`, `timing`, and `description`
- **`tags`** — Categorization tags for discovery (at least one)

#### Optional Fields

- **`license`** — License identifier (defaults to MIT)
- **`platforms`** — Supported platforms: `claude-code`, `copilot-cli`, `cursor`, `windsurf`, `antigravity` (defaults to all)
- **`resources`** — List of resource objects with `path`, `type` (`rubric`, `template`, `heuristic`, `reference`, `cheat-sheet`), `load` (`always` or `on-demand`), and optional `description`

## 🔥 Firing Phase Design

Firing phases are the heart of a synapse. Each phase fires at a specific point relative to task execution:

### Pre-Task Phases

Fire **before** the agent starts working. Use for planning, readiness assessment, strategy selection, and risk prediction.

```yaml
- name: PLAN
  timing: pre-task
  description: "Assess complexity, inventory knowledge, select strategy"
```

### Active Phases

Fire **during** task execution at major decision points. Use for confidence tagging, progress checking, stuck detection, and assumption tracking.

```yaml
- name: MONITOR
  timing: active
  description: "Tag confidence on decisions, detect stuck loops"
```

### Post-Task Phases

Fire **after** the agent completes work. Use for quality self-scoring, lessons learned, gap disclosure, and reflection.

```yaml
- name: REFLECT
  timing: post-task
  description: "Self-score quality, capture lessons, disclose gaps"
```

> 💡 **Phase Design Tips:**
> - **Not all three timings are required** — a synapse can have just a pre-task phase, or just active + post-task
> - **Scale to complexity** — phases should be lightweight for routine tasks, detailed for complex ones
> - **Define clear output formats** — each phase should produce a structured, recognizable output block
> - **Keep phases independent** — each phase should work even if a previous phase was skipped

## Step 3: Resources (Optional but Recommended)

Add reference materials the synapse can consult during firing phases:

```
resources/
├── confidence-rubric.md    — Calibrated scale with evidence criteria
├── reflection-template.md  — Structured template for post-task output
└── stuck-detection.md      — Heuristics for recognizing stuck loops
```

Declare resources in your manifest:

```yaml
resources:
  - path: resources/confidence-rubric.md
    type: rubric
    load: always
    description: "Calibrated confidence scale with evidence criteria"
  - path: resources/reflection-template.md
    type: template
    load: always
  - path: resources/stuck-detection.md
    type: heuristic
    load: always
```

### Resource Types

- **`rubric`** — Scoring scales with criteria for each level
- **`template`** — Structured output templates the synapse fills in
- **`heuristic`** — Decision-making rules and detection patterns
- **`reference`** — General reference materials for the domain
- **`cheat-sheet`** — Quick-reference guides for common patterns

## Step 4: Validate

Run the validation script to ensure your synapse is well-formed:

```bash
$ python scripts/validate.py synapses/my-synapse
```

The validator checks:

- **manifest.yaml completeness** and schema compliance against `schemas/synapse-manifest.schema.yaml`
- **SYNAPSE.md required sections** are present: Identity, When Active, Firing Phases, Rules, Output Format
- **Firing phase timings** are valid (`pre-task`, `active`, `post-task`)
- **Resources exist** and are accessible
- **Name uniqueness** across all synapses

> ⚠️ **Common Validation Errors:**
> - Missing required sections in SYNAPSE.md
> - Invalid `synapse-type` (must be `core` or `optional`)
> - Invalid `timing` value in firing phases
> - Referenced resources don't exist
> - Invalid YAML syntax in manifest

## 🛠️ Tutorial: Create a New Synapse

Follow these steps to create a synapse from scratch. We'll build a "risk-assessment" synapse that helps agents evaluate and mitigate risks during task execution.

### 1. Copy the Template

```bash
$ cp -r synapses/_template synapses/risk-assessment
```

### 2. Edit manifest.yaml

```yaml
# synapses/risk-assessment/manifest.yaml
name: risk-assessment
version: 1.0.0
description: "Structured risk evaluation — identify, score, and mitigate risks before and during task execution"
author: your-name
synapse-type: optional
license: MIT

firing-phases:
  - name: IDENTIFY
    timing: pre-task
    description: "Scan the task for potential risks and failure modes"

  - name: EVALUATE
    timing: active
    description: "Score risks as they materialize during execution"

  - name: REVIEW
    timing: post-task
    description: "Assess which risks materialized and document mitigations"

tags:
  - risk
  - safety
  - quality

resources:
  - path: resources/risk-matrix.md
    type: rubric
    load: always
    description: "Probability × impact scoring matrix"
```

### 3. Write SYNAPSE.md

```markdown
# Risk Assessment Synapse

## Identity

**Name:** Risk Assessment
**Type:** Optional
**Version:** 1.0.0
**Author:** your-name

Structured risk evaluation for agent tasks. Identifies potential
failure modes, scores their likelihood and impact, and tracks
mitigations throughout execution.

## When Active

- **Activation:** Binding-activated (optional synapse)
- **Phases:** 3 firing phases — IDENTIFY, EVALUATE, REVIEW

## Firing Phases

### Phase 1 — IDENTIFY (Pre-Fire)

**Timing:** Before starting the task.

**Instructions:**

1. List all potential failure modes
2. Score each risk: probability (1-5) × impact (1-5)
3. Identify the top 3 risks by score
4. Propose a mitigation for each top risk

**Output Format:**

### ⚠️ Risk Assessment — IDENTIFY
| Risk | Probability | Impact | Score | Mitigation |
|------|-------------|--------|-------|------------|
| ...  | ...         | ...    | ...   | ...        |

### Phase 2 — EVALUATE (Active-Fire)

**Timing:** At each major decision point.

**Instructions:**

1. Check if any identified risk is materializing
2. If yes, activate the planned mitigation
3. Log any new risks discovered during execution

### Phase 3 — REVIEW (Post-Fire)

**Timing:** After completing the task.

**Instructions:**

1. Which risks materialized? Were mitigations effective?
2. Any surprise risks not identified in Phase 1?
3. Lessons learned for future risk identification

## Rules

### DO:
- Be specific about failure modes
- Use the probability × impact matrix from resources
- Update risk scores as new information emerges

### DON'T:
- List vague, generic risks
- Ignore low-probability high-impact risks
- Skip the review phase

## Output Format

| Phase | Artifact | Purpose |
|-------|----------|---------|
| IDENTIFY | Risk register | Catalogues risks before work begins |
| EVALUATE | Risk alerts | Flags materializing risks mid-task |
| REVIEW | Risk report | Post-mortem on risk management |

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| resources/risk-matrix.md | rubric | Probability × impact scoring matrix |
```

### 4. Add Resources

Create the supporting resource files referenced in your manifest:

```markdown
# resources/risk-matrix.md — Risk Scoring Matrix

## Probability Scale
- 1 = Very unlikely (< 5%)
- 2 = Unlikely (5–20%)
- 3 = Possible (20–50%)
- 4 = Likely (50–80%)
- 5 = Very likely (> 80%)

## Impact Scale
- 1 = Negligible — cosmetic issues only
- 2 = Minor — small rework needed
- 3 = Moderate — significant rework
- 4 = Major — blocks progress or causes failures
- 5 = Critical — data loss, security breach, or complete failure

## Risk Score = Probability × Impact
- 1–5: Low risk (monitor)
- 6–12: Medium risk (mitigate)
- 13–25: High risk (address before proceeding)
```

### 5. Validate

```bash
$ python scripts/validate.py synapses/risk-assessment
```

✅ Your synapse is ready. If it's a core synapse, it will auto-inject into all agents. If optional, bind it to specific agents in their configuration.

## ✨ Best Practices

### 1. Start Optional

Begin with `synapse-type: optional` and test with specific agents before promoting to core. Core synapses add overhead to every interaction.

### 2. Design Clear Output Formats

Each firing phase should produce a recognizable, structured output block with an emoji prefix (e.g., `🧠`, `⚠️`) so users can identify synapse output at a glance.

### 3. Scale to Complexity

Synapses should be lightweight for routine tasks and detailed for complex ones. Include instructions for how the agent should gauge task complexity and adjust effort.

### 4. Keep Phases Independent

Each phase should function even if a previous phase was skipped or produced minimal output. Don't create hard dependencies between phases.

### 5. Provide Rich Resources

Rubrics, templates, and heuristics give the synapse concrete criteria to work with instead of relying on vague instructions.

### 6. Study the Metacognition Synapse

The built-in `synapses/metacognition/` synapse is the reference implementation. Study its SYNAPSE.md, manifest.yaml, and resources for patterns to follow.

## 📖 Example: Metacognition Synapse

The built-in metacognition synapse demonstrates all synapse patterns. It's a core synapse with three phases:

```yaml
# synapses/metacognition/manifest.yaml
name: metacognition
version: 1.0.0
description: "Structured self-awareness for agents — plan before acting, monitor confidence during execution, reflect on quality after completion"
author: tahaa
synapse-type: core
license: MIT

firing-phases:
  - name: PLAN
    timing: pre-task
    description: "Assess complexity, inventory knowledge, select strategy, define exit criteria"

  - name: MONITOR
    timing: active
    description: "Tag confidence on decisions, check progress, detect stuck loops, track assumptions"

  - name: REFLECT
    timing: post-task
    description: "Self-score quality, capture lessons learned, disclose known gaps and uncertainties"

tags:
  - metacognition
  - reasoning
  - self-awareness
  - core

resources:
  - path: resources/confidence-rubric.md
    type: rubric
    load: always
    description: "Calibrated confidence scale with evidence criteria for each level"

  - path: resources/reflection-template.md
    type: template
    load: always
    description: "Structured template for Phase 3 reflection output"

  - path: resources/stuck-detection.md
    type: heuristic
    load: always
    description: "Heuristics for recognizing stuck loops and when to pivot"
```

> ✅ **Pattern to Study:** The **metacognition** synapse demonstrates how to build a core synapse with all three firing phase timings, rich resource files, and clear output formats for each phase.

## 📖 Example: Security-Awareness Synapse

The **security-awareness** synapse is a cross-cutting synapse that fires for tasks involving code changes, infrastructure, or data handling:

```yaml
# synapses/security-awareness/manifest.yaml
name: security-awareness
version: 1.0.0
description: "Evaluate security implications of decisions, code changes, and architectural choices"
author: tahaa
synapse-type: cross-cutting
license: MIT

firing-phases:
  - name: THREAT-SCAN
    timing: pre-task
    description: "Identify potential security concerns in the task scope"

  - name: GUARD
    timing: active
    description: "Flag security-sensitive decisions as they occur"

  - name: AUDIT
    timing: post-task
    description: "Review completed work for security gaps and vulnerabilities"

tags:
  - security
  - cross-cutting
  - code-review

resources:
  - path: resources/owasp-checklist.md
    type: cheat-sheet
    load: always
    description: "OWASP top 10 quick-reference for common vulnerability patterns"
```

> **When it fires:** The security-awareness synapse activates for tasks that involve writing or modifying code, configuring infrastructure, handling user input, or managing authentication/authorization. It does not fire for pure documentation or design tasks.

## 📖 Example: Pattern-Recognition Synapse

The **pattern-recognition** synapse is a cross-cutting synapse that helps agents identify recurring patterns, anti-patterns, and architectural smells:

```yaml
# synapses/pattern-recognition/manifest.yaml
name: pattern-recognition
version: 1.0.0
description: "Identify recurring patterns, anti-patterns, and architectural smells in code and design"
author: tahaa
synapse-type: cross-cutting
license: MIT

firing-phases:
  - name: SCAN
    timing: pre-task
    description: "Survey the codebase or design for known patterns and anti-patterns"

  - name: MATCH
    timing: active
    description: "Flag pattern matches and anti-pattern detections during execution"

  - name: CATALOG
    timing: post-task
    description: "Summarize detected patterns with recommendations"

tags:
  - patterns
  - architecture
  - cross-cutting
  - code-quality

resources:
  - path: resources/pattern-catalog.md
    type: reference
    load: always
    description: "Catalog of common design patterns and their indicators"

  - path: resources/anti-pattern-heuristics.md
    type: heuristic
    load: always
    description: "Detection heuristics for code smells and anti-patterns"
```

> **When it fires:** The pattern-recognition synapse activates for tasks involving code review, architecture decisions, refactoring, and codebase analysis. It helps agents spot both positive patterns to preserve and anti-patterns to fix.
