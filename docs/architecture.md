# Archon v3.0 — 6-Layer Architecture

## Overview

Archon is built as a 6-layer stack where each layer has a single responsibility and strict boundaries. Control flows top-down (bootstrap → agents → skills), data flows bottom-up (artifacts → pipelines → users). v3.0 adds Layer 6 for runtime contracts, policy enforcement, and replay determinism.

```
┌─────────────────────────────────────────────────┐
│  Layer 6: RUNTIME CONTRACTS (v3)                │
│  Sessions, policy engine, telemetry, replay     │
├─────────────────────────────────────────────────┤
│  Layer 4: ARTIFACT LAYER                        │
│  Pipeline outputs, validated JSON, audit trails  │
├─────────────────────────────────────────────────┤
│  Layer 3: PIPELINE LAYER                        │
│  sdd │ ux │ debug │ skill-factory │ full-product │
├─────────────────────────────────────────────────┤
│  Layer 2: SKILL LAYER                           │
│  83 skills, each with manifest.yaml             │
├─────────────────────────────────────────────────┤
│  Layer 1: AGENT LAYER                           │
│  9 agents with guardrails & manifests           │
├─────────────────────────────────────────────────┤
│  Layer 0: BOOTSTRAP & DISCIPLINE                │
│  Hooks, synapses, anti-rationalization          │
└─────────────────────────────────────────────────┘
```

---

## Layer 0: Bootstrap & Discipline

**Directory:** `hooks/`

Layer 0 fires before any agent starts. It establishes the cognitive discipline that prevents agents from going off-rails.

### Hook System

| Hook | File | Fires When |
|------|------|------------|
| Session Start | `hooks/session_start.py` | Agent session begins |
| Pre-Step | `hooks/pre_step.py` | Before each pipeline step |
| Post-Step | `hooks/post_step.py` | After each pipeline step |
| On Failure | `hooks/on_failure.py` | Any step fails |
| On Deviation | `hooks/on_deviation.py` | Agent deviates from spec |

### Bootstrap Sequence

When any Archon session starts, the following sequence executes:

```
session_start hook
    │
    ├─► Load core synapses from synapses/
    │     ├── anti-rationalization.md
    │     ├── sequential-thinking.md
    │     └── metacognition.md
    │
    ├─► Inject anti-rationalization rules
    │     └── 10 Iron Laws activated
    │
    ├─► Inject sequential thinking protocol
    │     └── [THINKING] blocks required for complex tasks
    │
    └─► Inject metacognition synapse
          └── Complexity scaling activated
```

The bootstrap is non-negotiable — no agent can bypass it. The `session_start.py` hook validates that all required synapses exist and are syntactically valid before allowing the session to proceed.

### Why Layer 0 Exists

Without discipline enforcement, AI agents will:
- Skip steps they consider "unnecessary"
- Rationalize incomplete work as complete
- Deviate from specifications mid-task

Layer 0 prevents all three by making discipline a system property, not a suggestion.

---

## Layer 1: Agent Layer

**Directory:** `agents/`

Nine specialized agents, each with a single role and an `agent-manifest.yaml` that defines its guardrails.

| Agent | Role | Primary Skill Dependencies |
|-------|------|---------------------------|
| `spec-writer` | Specification Architect | spec-writer skill |
| `implementer` | Implementation Engineer | implementer skill |
| `reviewer` | Compliance Reviewer | reviewer skill |
| `debugger` | Root-Cause Investigator | systematic-debugging |
| `ux-research` | UX Researcher | ux-research |
| `ui-design` | Visual Designer | ui-visual-design, frontend-design |
| `qa-master` | QA Engineer | qa-test-planner, e2e-testing-patterns |
| `context-curator` | Pipeline Handoff Curator | context-curator |
| `dissector` | Codebase Analyst | dissector skill |

### Agent Manifest Structure

Each agent's `agent-manifest.yaml` contains:

```yaml
name: implementer
role: Implementation Engineer
guardrails:
  must-do:
    - Follow spec section by section
    - Write tests before implementation
    - Verify each section compiles before proceeding
  must-not:
    - Skip sections marked as required
    - Add features not in the spec
    - Modify existing tests without justification
  on-violation: halt-and-report
skills:
  - implementer
  - systematic-debugging
triggers:
  - "implement the spec"
  - "build from spec"
```

### Agent ↔ Skill Relationship

Agents invoke skills; skills are never invoked directly by users. This separation ensures that skills always run within the guardrail context of an agent.

```
User Request
    │
    ▼
Agent (guardrails active)
    │
    ├─► Skill A (focused capability)
    ├─► Skill B (focused capability)
    └─► Skill C (focused capability)
    │
    ▼
Validated Output
```

---

## Layer 2: Skill Layer

**Directory:** `skills/`

48+ skills, each a self-contained capability with a `manifest.yaml`. Skills contain the actual domain knowledge — how to write React components, how to debug GDScript, how to design wireframes.

### Skill Manifest Format

```yaml
name: react-best-practices
description: React development guidelines with hooks, patterns, and optimization
version: 1.0.0
triggers:
  - React component
  - React hooks
  - React performance
platforms:
  - claude-code
```

### Skill Bundles

Skills are grouped into installable bundles for common workflows:

```
godot-kit      → 5 Godot skills
web-dev-kit    → 5 web development skills
ux-design-kit  → 7 UX/UI skills
django-kit     → 4 Django skills
sdd-kit        → 6 spec-driven development skills
testing-kit    → 4 testing skills
mobile-kit     → 2 mobile skills
meta-kit       → 5 meta/tooling skills
```

Install a bundle: `python scripts/install.py --bundle web-dev-kit`

---

## Layer 3: Pipeline Layer

**Directory:** `pipelines/`

Five orchestrated workflows that chain agents together with context curation between steps.

### Pipeline State Machine

```
          ┌──────────┐
          │ pending   │
          └────┬──────┘
               │ validate
          ┌────▼──────┐
          │ validating │
          └────┬──────┘
               │ execute
          ┌────▼──────┐     ┌──────────┐
          │ executing  ├────►│  paused  │
          └────┬──────┘     └────┬─────┘
               │                 │ resume
          ┌────▼─────────────────▼─────┐
          │        step loop           │
          └────┬──────┬──────┬─────────┘
               │      │      │
          ┌────▼──┐ ┌─▼────┐ ┌▼─────────┐
          │completed│ │failed│ │cancelled │
          └────────┘ └──────┘ └──────────┘
```

### Pipeline Execution

The `PipelineExecutor` in `src/archon/core/pipeline_engine.py` drives all pipelines. Each step:

1. Runs `pre_step.py` hook (validates prerequisites)
2. Invokes the designated agent
3. Runs `post_step.py` hook (validates outputs)
4. Curates context for the next step via `context-curator`

### Available Pipelines

| Pipeline | Steps |
|----------|-------|
| **sdd** | spec-writer → context-curator → implementer → context-curator → reviewer |
| **ux** | research → context-curator → wireframe → context-curator → visual → review → handoff |
| **debug** | debugger → context-curator → implementer → tester → reviewer |
| **skill-factory** | prompt → spec → context-curator → implement → validate → review |
| **full-product** | ux-pipeline → context-curator → sdd-pipeline → testing |

---

## Layer 4: Artifact Layer

Pipeline outputs are validated and persisted as structured artifacts.

### Artifact Validation

The `ArtifactValidator` checks every pipeline output against its schema:
- `expected_artifacts` — which files must exist
- `required_sections` — which headings must appear
- `min_word_count` — minimum content length

### Persistence

Pipeline state is persisted at:
```
~/.claude/.archon/pipeline-states/
    ├── sdd-pipeline-<id>.json
    ├── ux-pipeline-<id>.json
    └── ...
```

Each state file is human-readable JSON containing:
- Current step and status
- Accumulated decisions, constraints, and tech stack
- Artifact paths and validation results
- Thinking traces for audit

### Why JSON?

Artifacts are JSON (not binary) so that:
1. Humans can inspect pipeline state at any time
2. Agents can resume from any checkpoint
3. Version control can track changes
4. Debugging is straightforward — `cat` the state file

---

## Cognitive Synapses

Synapses are cross-cutting cognitive capabilities that enhance how agents think, independent of what task they perform. They layer structured reasoning on top of any agent interaction.

### Synapse Types

| Type | Behavior | Examples |
|------|----------|----------|
| **Core** | Auto-injected into every agent; fires on every task | metacognition, anti-rationalization, sequential-thinking |
| **Cross-cutting** | Fires for specific task types based on context | security-awareness, pattern-recognition |
| **Optional** | Fires only when explicitly bound to an agent | risk-assessment, domain-specific synapses |

Core synapses fire always. Cross-cutting synapses fire for specific task types. Optional synapses fire when bound to an agent via its manifest.

### Built-in Synapses

- **metacognition** — plan before acting, monitor confidence, reflect on quality
- **anti-rationalization** — detect and block excuse-making that skips steps
- **sequential-thinking** — decompose, reason step-by-step, validate, synthesize
- **security-awareness** — evaluate security implications of decisions and code
- **pattern-recognition** — identify recurring patterns, anti-patterns, and architectural smells

---

## DDE (Dissect-Develop-Evolve) Pipeline Framework

The DDE framework defines an 8-stage pipeline for turning existing codebases into Archon skills and upgrading existing skills.

### DDE Stages

```
DISSECT → CATALOG → DIFF → SPECIFY → IMPLEMENT → VALIDATE → REGISTER → COMPOSE
```

| Stage | Purpose |
|-------|---------|
| **DISSECT** | Analyze a codebase or domain to extract patterns, conventions, and knowledge |
| **CATALOG** | Organize extracted knowledge into structured categories |
| **DIFF** | Compare against existing skills to identify gaps and overlaps |
| **SPECIFY** | Write a formal skill specification from the cataloged knowledge |
| **IMPLEMENT** | Build the skill (SKILL.md, manifest.yaml, resources) |
| **VALIDATE** | Run validation against Archon schemas and quality gates |
| **REGISTER** | Add the skill to the registry and assign to bundles |
| **COMPOSE** | Wire the skill into agents, pipelines, and bundles |

### DDE Pipelines

Two pipelines use the DDE framework:

| Pipeline | Purpose | Stages Used |
|----------|---------|-------------|
| **dissect-to-skill** | Create a new skill from an existing codebase | All 8 stages |
| **skill-upgrade** | Upgrade an existing skill with new patterns | DISSECT → CATALOG → DIFF → IMPLEMENT → VALIDATE |

---

## Cross-Layer Data Flow

```
User: "build feature X from scratch"
    │
    ▼
Layer 0: Bootstrap fires, synapses loaded
    │
    ▼
Layer 3: Pipeline engine selects sdd-pipeline
    │
    ├─► Layer 1: spec-writer agent activated
    │       └─► Layer 2: spec-writer skill invoked
    │              └─► Layer 4: spec artifact produced
    │
    ├─► Layer 1: context-curator curates handoff
    │
    ├─► Layer 1: implementer agent activated
    │       └─► Layer 2: implementer skill invoked
    │              └─► Layer 4: code artifact produced
    │
    ├─► Layer 1: context-curator curates handoff
    │
    └─► Layer 1: reviewer agent activated
            └─► Layer 2: reviewer skill invoked
                   └─► Layer 4: review report produced
```

Every transition between agents passes through the context-curator to ensure only relevant context propagates forward — preventing context bloat and token waste.

---

## Layer 6: Runtime Contracts (v3.0)

**Directory:** `src/archon/core/` (new v3 modules)

Layer 6 wraps the entire runtime with enforced contracts — no tool executes without a policy decision, no session transitions without state machine validation, and no completion claim without evidence.

### Session Lifecycle

The `SessionManager` (`session_manager.py`) enforces an 8-state lifecycle:

```
created → active → waiting_tool → active
                 → waiting_permission → active
                 → idle → active
                 → error → recovering → active
                 → archived (terminal)
```

Invalid transitions raise `InvalidTransitionError`. Every event is logged with a correlation ID that links sessions to pipeline traces.

### Central Policy Engine

The `PolicyEngine` (`policy_engine.py`) gates every tool invocation:

1. **Schema validation** — tool arguments checked against registered schemas
2. **Permission rules** — evaluated in order, first match wins
3. **Trust tier precedence** — builtin > verified > community > untrusted
4. **Decision artifact** — machine-readable `PolicyDecision` with rationale

Default action is **deny** — tools must have an explicit allow rule. Denied decisions are queryable and replayable from the audit log.

### Telemetry & Replay

The `TelemetryCollector` (`telemetry.py`) normalizes all events to versioned envelopes:

```
TelemetryEnvelope:
  envelope_id: tel-xxxxxxxxxxxx
  schema_version: 3.0.0
  event_type: policy_decision | session_start | ...
  correlation_id: corr-xxxxxxxxxxxx
  source: {component, session_id, pipeline_name, step_name}
  payload: {...}
  retention_class: standard | audit
```

The `ReplayHarness` captures session snapshots and compares checksums for determinism — timestamps are excluded from the checksum so structure-only comparison works across environments.

### MCP Trust Routing

The `MCPConnectorManager` (`agent_mcp.py`) routes to MCP servers by capability and trust:

- Connectors register with trust tier and capabilities
- Routing selects the highest-trust healthy connector for a capability
- Unhealthy connectors are excluded automatically
- Routing is deterministic (same inputs → same output)

### v3 Schemas

Six new contract schemas (`schemas/`) define the wire format:

| Schema | Purpose |
|--------|---------|
| `session.schema.yaml` | Session lifecycle states and transitions |
| `tool-invocation.schema.yaml` | Tool call with required policy decision |
| `permission.schema.yaml` | Permission rules with trust tiers |
| `hook-event.schema.yaml` | Normalized hook bus events |
| `telemetry-envelope.schema.yaml` | Versioned telemetry format |
| `context-handoff.schema.yaml` | Phase handoff with pinned constraints and evidence |

### Release Gates

The `ReleaseGateValidator` (`migration.py`) validates 6 hard gates before any release:

1. **SchemaAndContracts** — all v3 schemas present and version 3.x
2. **PolicyAndSecurity** — policy engine and permission schema present
3. **ReplayDeterminism** — telemetry module and replay tests present
4. **ContextIntegrity** — handoff schema enforces pinned_constraints and evidence_links
5. **PromptQuality** — prompt files present, schema validator functional
6. **MigrationReadiness** — migration dry-run passes with zero blockers

All 6 must pass, and the weighted score must reach 90+ for a GO recommendation.
