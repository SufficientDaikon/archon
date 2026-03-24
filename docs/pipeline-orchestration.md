# Archon v2.0 — Pipeline Orchestration Guide

## Overview

Pipelines are multi-step workflows that chain agents together to accomplish complex tasks. The `PipelineExecutor` in `src/archon/core/pipeline_engine.py` manages execution, state, failure recovery, and artifact validation.

---

## Running Pipelines

### CLI Usage

```bash
# Run the SDD pipeline
archon pipeline run sdd-pipeline --project ./myapp

# Run the UX pipeline with a specific target
archon pipeline run ux-pipeline --project ./myapp --target "dashboard redesign"

# Resume a paused pipeline
archon pipeline resume sdd-pipeline-abc123

# Check pipeline status
archon pipeline status sdd-pipeline-abc123

# List all pipeline runs
archon pipeline list
```

### Trigger Phrases

Pipelines also activate via natural language:

| Phrase | Pipeline |
|--------|----------|
| "build feature X from scratch" | sdd-pipeline |
| "design feature X" | ux-pipeline |
| "fix bug X" | debug-pipeline |
| "create a new skill for X" | skill-factory |
| "build product X end-to-end" | full-product |

---

## Pipeline YAML Format

Each pipeline is defined in `pipelines/<name>.yaml`:

```yaml
name: sdd-pipeline
description: Spec-Driven Development — from idea to reviewed implementation
version: 2.0.0

steps:
  - id: write-spec
    agent: spec-writer
    description: Transform requirements into implementable specification
    expected_artifacts:
      - path: artifacts/spec.md
        required_sections:
          - "## User Stories"
          - "## Acceptance Criteria"
          - "## Technical Architecture"
          - "## Error Handling"
        min_word_count: 500
    on-failure: halt

  - id: curate-spec-context
    agent: context-curator
    description: Curate spec output for implementer consumption
    inputs:
      - from: write-spec
        artifact: artifacts/spec.md
    on-failure: halt

  - id: implement
    agent: implementer
    description: Build from spec, section by section
    inputs:
      - from: curate-spec-context
        artifact: artifacts/curated-context.md
    expected_artifacts:
      - path: artifacts/implementation/
        type: directory
    on-failure: loop
    loop-target: implement
    max-iterations: 3

  - id: curate-impl-context
    agent: context-curator
    description: Curate implementation output for reviewer
    inputs:
      - from: implement
        artifact: artifacts/implementation/
      - from: write-spec
        artifact: artifacts/spec.md
    on-failure: halt

  - id: review
    agent: reviewer
    description: Verify implementation against spec
    inputs:
      - from: curate-impl-context
        artifact: artifacts/curated-context.md
    expected_artifacts:
      - path: artifacts/review-report.html
        required_sections:
          - "Compliance Summary"
          - "Issues Found"
          - "Recommendations"
    on-failure: halt
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique step identifier |
| `agent` | Yes | Which agent executes this step |
| `description` | Yes | Human-readable step purpose |
| `inputs` | No | Artifacts from previous steps |
| `expected_artifacts` | No | What this step must produce |
| `on-failure` | Yes | `halt`, `skip`, or `loop` |
| `loop-target` | If loop | Which step to loop back to |
| `max-iterations` | If loop | Maximum retry attempts |

---

## State Management

### PipelineState Class

The `PipelineState` class tracks everything about a running pipeline:

```python
class PipelineState:
    pipeline_id: str          # Unique run identifier
    pipeline_name: str        # e.g., "sdd-pipeline"
    status: str               # pending|validating|executing|completed|failed|cancelled|paused
    current_step: str         # ID of the currently executing step
    started_at: datetime
    updated_at: datetime
    
    # Accumulated state — grows, never shrinks
    decisions: list[str]      # Design decisions made during execution
    constraints: list[str]    # Constraints discovered or imposed
    tech_stack: list[str]     # Technologies selected
    
    # Step results
    step_results: dict[str, StepResult]
    
    # Artifacts produced
    artifacts: dict[str, ArtifactMetadata]
    
    # Thinking traces for audit
    thinking_traces: list[ThinkingTrace]
    
    # Deviation log
    deviations: list[Deviation]
```

### The Accumulated State Pattern

A critical design principle: **accumulated state grows, never shrinks.**

```python
# CORRECT — state accumulates
state.decisions.append("Using PostgreSQL for relational data")
state.decisions.append("Redis for session store")
state.tech_stack.append("PostgreSQL")
state.tech_stack.append("Redis")

# WRONG — never remove accumulated state
state.decisions.remove("Using PostgreSQL")  # FORBIDDEN
state.tech_stack = []                       # FORBIDDEN
```

This ensures that:
- Later steps have full context of all prior decisions
- The reviewer can verify every decision was implemented
- Pipeline resumption has complete history
- Audit trails are never broken

### State Persistence

State is written to disk after every step:

```
~/.copilot/.archon/pipeline-states/
    └── sdd-pipeline-abc123.json
```

```json
{
  "pipeline_id": "sdd-pipeline-abc123",
  "pipeline_name": "sdd-pipeline",
  "status": "executing",
  "current_step": "implement",
  "started_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:15:00Z",
  "decisions": [
    "REST API with Express.js",
    "PostgreSQL with Prisma ORM",
    "JWT-free session auth with Redis"
  ],
  "constraints": [
    "Must support 1000 concurrent users",
    "Response time < 200ms for all endpoints"
  ],
  "tech_stack": ["Node.js", "Express", "PostgreSQL", "Prisma", "Redis"],
  "step_results": {
    "write-spec": {
      "status": "completed",
      "duration_ms": 12000,
      "artifact_path": "artifacts/spec.md"
    },
    "curate-spec-context": {
      "status": "completed",
      "duration_ms": 3000,
      "artifact_path": "artifacts/curated-context.md"
    }
  },
  "thinking_traces": ["..."],
  "deviations": []
}
```

---

## Artifact Validation

Every step with `expected_artifacts` is validated by the `ArtifactValidator` after completion.

### Validation Checks

```python
class ArtifactValidator:
    def validate(self, step, artifacts):
        for expected in step.expected_artifacts:
            # 1. Existence check
            assert expected.path.exists(), \
                f"Missing artifact: {expected.path}"
            
            # 2. Type check
            if expected.type == "directory":
                assert expected.path.is_dir()
                assert len(list(expected.path.iterdir())) > 0
            
            # 3. Required sections (for markdown/HTML)
            if expected.required_sections:
                content = expected.path.read_text()
                for section in expected.required_sections:
                    assert section in content, \
                        f"Missing section: {section}"
            
            # 4. Minimum word count
            if expected.min_word_count:
                words = len(content.split())
                assert words >= expected.min_word_count, \
                    f"Too short: {words} words, need {expected.min_word_count}"
```

### Validation Failure

If validation fails, the step is marked as `failed` and the `on-failure` strategy determines what happens next.

---

## Failure Handling

### Strategy: halt

Pipeline stops immediately. Human must investigate and either fix the issue manually or cancel the pipeline.

```yaml
on-failure: halt
```

Use for: critical steps where partial output is dangerous (spec writing, final review).

### Strategy: skip

Step is marked as `skipped`. The next step receives whatever context is available. A warning is logged.

```yaml
on-failure: skip
```

Use for: optional enhancement steps where the pipeline can proceed without them.

### Strategy: loop

Step retries, targeting `loop-target` (usually itself). The agent receives the failure reason and previous output as additional context.

```yaml
on-failure: loop
loop-target: implement
max-iterations: 3
```

The loop provides the agent with:
1. The original inputs
2. The failed output
3. The validation error message
4. Instruction: "Fix the issues identified above"

### The 3-Fix Escape Hatch

If a looping step fails `max-iterations` times (default: 3), the pipeline does NOT loop forever. Instead:

1. The step is marked as `failed`
2. All 3 attempts and their errors are collected
3. The pipeline halts with a diagnostic:

```
ESCAPE HATCH TRIGGERED
Step: implement
Attempts: 3/3
Errors:
  Attempt 1: Missing required section "Error Handling"
  Attempt 2: Missing required section "Error Handling"
  Attempt 3: Test failures in auth.test.js (3 failing)
Recommendation: Review spec section on error handling — it may be ambiguous
```

This prevents infinite loops while giving the agent a fair chance to self-correct.

---

## Resuming Paused Pipelines

Pipelines pause when:
- A deviation is detected and awaits human decision
- The escape hatch triggers
- A `halt` failure strategy fires
- The user manually pauses

### Resume Command

```bash
archon pipeline resume sdd-pipeline-abc123
```

### What Happens on Resume

1. The `PipelineExecutor` loads state from disk
2. It identifies the step where execution stopped
3. If the step was `failed`, it re-runs from that step
4. If the step was `paused` (deviation), it checks for a resolution in the state file
5. Accumulated state is preserved — all prior decisions, constraints, and tech stack are intact

### Manual State Editing

Because state files are human-readable JSON, you can manually edit them before resuming:

```bash
# Open the state file
code ~/.copilot/.archon/pipeline-states/sdd-pipeline-abc123.json

# Edit: resolve a deviation, adjust constraints, etc.
# Then resume
archon pipeline resume sdd-pipeline-abc123
```

---

## Context Curation Between Steps

The `context-curator` agent runs between major steps to prevent context bloat.

### The Problem

Without curation, each step receives all output from all previous steps. By step 5, the context window is full of irrelevant detail from step 1.

### The Solution

The context-curator:
1. Receives the full output of the previous step
2. Identifies what the next agent actually needs
3. Produces a curated summary with only relevant information
4. Preserves critical details (decisions, constraints, schema definitions)
5. Drops implementation noise (debug logs, intermediate attempts)

### Curation Rules

```
ALWAYS KEEP:
  - Design decisions and their rationale
  - Schema definitions and data models
  - API contracts and interfaces
  - Constraints and non-functional requirements
  - Unresolved issues and open questions

ALWAYS DROP:
  - Intermediate debugging output
  - Failed attempts (unless instructive)
  - Verbose logging
  - Redundant explanations
  - Thinking traces (available separately if needed)
```

### Pipeline Flow with Curation

```
spec-writer
    │
    ▼ (full spec output: ~3000 words)
context-curator
    │
    ▼ (curated for implementer: ~800 words)
implementer
    │
    ▼ (full implementation output: ~5000 words)
context-curator
    │
    ▼ (curated for reviewer: ~1200 words — spec excerpts + code summary)
reviewer
    │
    ▼ (review report)
```

Each curation step reduces token usage by 60-80% while preserving all decision-critical information.

---

## Quick Reference

```bash
# Run a pipeline
archon pipeline run <name> --project <path>

# Check status
archon pipeline status <pipeline-id>

# Resume paused pipeline
archon pipeline resume <pipeline-id>

# List all runs
archon pipeline list

# Cancel a running pipeline
archon pipeline cancel <pipeline-id>
```

### Pipeline YAML Cheat Sheet

```yaml
steps:
  - id: step-name              # Unique ID
    agent: agent-name           # Which agent
    description: "..."          # What it does
    inputs:                     # What it needs
      - from: previous-step
        artifact: path/to/file
    expected_artifacts:          # What it must produce
      - path: output/path
        required_sections: []
        min_word_count: 500
    on-failure: halt|skip|loop  # What to do on failure
    loop-target: step-name      # Where to loop back
    max-iterations: 3           # Max retries
```
