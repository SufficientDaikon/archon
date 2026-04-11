# Creating Pipelines

## What's a Pipeline?

A pipeline defines a **multi-agent workflow** — an ordered sequence of agent steps where each step's output feeds into the next. Pipelines support branching, loops, and resumability.

## Pipeline Format

```yaml
name: my-pipeline
version: 1.0.0
description: "What this pipeline accomplishes"
trigger: "natural language pattern *"

steps:
  - name: step-one
    agent: first-agent
    input: "what this step receives"
    output: "what this step produces"
    on-failure: halt

  - name: step-two
    agent: second-agent
    input: "output from step:step-one"
    output: "final result"
    on-failure: loop
    loop-target: step-one
    max-iterations: 3

resumable: true
```

## The Complexity Router Pre-Step

Before any pipeline executes, the **complexity-router** automatically runs as a pre-step:

1. **Classification** — Analyzes the request complexity
2. **Model Selection** — Chooses the optimal model tier
3. **Pipeline Selection** — Determines if this is the right pipeline or if a simpler/more complex one should be used

This routing happens transparently. The router uses signals from:
- Task scope and dependencies
- Required domain expertise
- Expected output complexity
- Time constraints

See `skills/complexity-router/resources/complexity-signals.md` for the full classification criteria.

## Step Configuration

### on-failure options

- `halt` — Stop the pipeline; report failure
- `loop` — Go back to `loop-target` step (requires `max-iterations`)
- `skip` — Skip this step; continue to next
- `retry` — Retry this step (uses `max-iterations`)

### Input References

Use `step:name` to reference output from a previous step:

- `"Spec from step:specify"` — uses the specify step's output
- `"Code from step:implement AND spec from step:specify"` — multiple inputs

## Existing Pipelines

See the [pipelines directory](../pipelines/) for all available pipelines.

| Pipeline | Description | Trigger |
|----------|-------------|---------|
| sdd-pipeline | Spec-Driven Development | "build feature X from scratch" |
| ux-pipeline | Full UX Design Lifecycle | "design feature X" |
| debug-pipeline | Systematic Bug Fixing | "fix bug X" |
| skill-factory | Create New Skills | "create a new skill for X" |
| full-product | End-to-End Product Dev | "build product X end-to-end" |
| **dissect-to-skill** | Extract skills from existing codebases via DDE stages (DISSECT → CATALOG → DIFF → SPECIFY → IMPLEMENT → VALIDATE → REGISTER → COMPOSE) | "dissect codebase X into a skill" |
| **skill-upgrade** | Upgrade existing skills with new patterns via DDE stages (DISSECT → CATALOG → DIFF → IMPLEMENT → VALIDATE) | "upgrade skill X with new patterns" |

## v2.0: Pipeline Execution Engine

In v2.0, pipelines are **actually executed** by the `PipelineExecutor` engine. This replaces the v0.x approach where pipelines were just YAML documentation of intended workflows.

### Running a Pipeline

```bash
# Via CLI
archon pipeline run sdd-pipeline --project ./myapp

# Via SDK
from sdk.archon import Archon
os = Archon()
os.execute_pipeline("sdd-pipeline", project_name="myapp")
```

### Pipeline State Machine

The engine manages pipeline state through these transitions:

```
pending → validating → executing → completed
                         ↓
                    failed / paused / cancelled
```

- **pending** — Pipeline loaded, not yet started
- **validating** — Checking prerequisites and schema compliance
- **executing** — Running steps sequentially
- **completed** — All steps finished successfully
- **failed** — A step failed with `on-failure: halt`
- **paused** — Execution paused (can be resumed)
- **cancelled** — Manually cancelled

### State Persistence

Pipeline state is saved as JSON to `~/.claude/.archon/pipeline-states/`. This enables:

- **Resumability** — `archon pipeline resume <state-id>`
- **Audit trail** — Every step, decision, and deviation is recorded
- **Accumulated state** — Decisions, constraints, and tech_stack grow across steps (never shrink)

### Context Curation Between Steps

The **context-curator** agent runs between pipeline steps to create focused context briefs:

1. Summarizes the previous step's output
2. Filters to only what the next agent needs
3. Applies token budget constraints
4. Generates a structured context brief

This prevents context pollution — each agent gets a clean, focused input rather than the entire accumulated history.

### Artifact Validation

The `ArtifactValidator` checks outputs between steps:

- **`validate_exists(path)`** — File must exist
- **`validate_sections(path, headings)`** — Required Markdown sections
- **`validate_min_content(path, words)`** — Minimum content length
- **`validate_schema(path, schema)`** — JSON/YAML schema compliance
- **`validate_compliance_score(report, threshold)`** — Score gate

### CLI Commands

```bash
archon pipeline run <name> --project <dir>   # Execute a pipeline
archon pipeline status [state-id]             # Show current status
archon pipeline resume <state-id>             # Resume paused pipeline
archon pipeline list                          # List all active pipelines
archon pipeline cancel <state-id>             # Cancel with cleanup
```
