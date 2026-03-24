# Archon v2.0 — Guardrails Guide

## Overview

Guardrails are the enforcement mechanism that prevents AI agents from deviating, rationalizing, or cutting corners. They operate at three levels: system-wide (synapses), per-agent (manifests), and per-step (hooks).

---

## Anti-Rationalization Synapse

**File:** `synapses/anti-rationalization.md`

The anti-rationalization synapse is injected at session start and remains active for the entire session. It defines absolute behavioral constraints.

### The 10 Iron Laws

| # | Law | Enforcement |
|---|-----|-------------|
| 1 | **Never skip a required step** | Pre-step hook validates step completion |
| 2 | **Never claim work is done when it isn't** | Post-step hook validates artifacts exist |
| 3 | **Never modify the spec without explicit approval** | Deviation hook triggers STOP protocol |
| 4 | **Never rationalize a shortcut** | Forbidden phrase detection |
| 5 | **Never add unrequested features** | Reviewer checks spec compliance |
| 6 | **Never ignore test failures** | Post-step hook checks exit codes |
| 7 | **Never proceed past a failed validation** | Pipeline engine enforces gate |
| 8 | **Never silently drop requirements** | Artifact validator checks required sections |
| 9 | **Never substitute a simpler problem** | Thinking trace audits reasoning chain |
| 10 | **Never claim inability without evidence** | Must show 3 distinct attempts before reporting failure |

### Forbidden Phrases

The synapse maintains a rationalization detection table. If an agent generates any of these patterns, the deviation protocol fires:

| Forbidden Pattern | What It Really Means | Correct Action |
|-------------------|---------------------|----------------|
| "This should be sufficient" | Incomplete work | Complete the work fully |
| "For brevity, I'll skip..." | Skipping required content | Do not skip anything |
| "This is left as an exercise" | Avoiding implementation | Implement it |
| "In a real scenario, you would..." | Hypothetical instead of actual | Do the actual work |
| "Due to complexity, I'll simplify..." | Unauthorized scope reduction | Follow the spec exactly |
| "I'll focus on the key parts" | Cherry-picking easy sections | Address all sections |
| "This is straightforward, so..." | Skipping validation | Validate anyway |
| "Time constraints require..." | Invented deadline pressure | No time constraints exist |

### How Detection Works

The `pre_step.py` hook scans agent output for forbidden phrases using pattern matching. On detection:

1. The output is flagged with `RATIONALIZATION_DETECTED`
2. The deviation protocol fires (see below)
3. The agent must redo the step without the rationalization

---

## Hook System

### pre_step.py — Prerequisite Validation

Runs before each pipeline step. Validates:

```python
def validate_prerequisites(step, state):
    # 1. Previous step completed successfully
    assert state.previous_step.status == "completed"
    
    # 2. Required artifacts from previous step exist
    for artifact in step.required_inputs:
        assert artifact.path.exists(), f"Missing: {artifact.path}"
    
    # 3. Required sections present in input artifacts
    for section in step.required_sections:
        assert section in artifact.content
    
    # 4. Agent guardrails loaded
    assert step.agent.guardrails is not None
    
    # 5. No unresolved deviations from previous steps
    assert len(state.unresolved_deviations) == 0
```

If any check fails, the step does not execute. The pipeline enters `paused` state with a diagnostic message.

### post_step.py — Output Validation

Runs after each pipeline step. Validates:

```python
def validate_outputs(step, state, result):
    # 1. Expected artifacts were produced
    for artifact in step.expected_artifacts:
        assert artifact.path.exists()
    
    # 2. Artifacts meet minimum quality
    for artifact in step.expected_artifacts:
        assert word_count(artifact) >= step.min_word_count
    
    # 3. Required sections present
    for section in step.required_sections:
        assert section in artifact.content
    
    # 4. No forbidden phrases in output
    assert no_rationalization_detected(result.output)
    
    # 5. Thinking trace captured (if required)
    if step.requires_thinking_trace:
        assert result.thinking_trace is not None
```

### on_failure.py — Failure Handling

When a step fails, this hook determines the recovery action based on the pipeline's `on-failure` configuration:

| Action | Behavior |
|--------|----------|
| `halt` | Pipeline stops. Human intervention required. |
| `skip` | Step is skipped. Next step receives partial context. |
| `loop` | Step retries up to `max-iterations` times. |

### on_deviation.py — Deviation Detection

Monitors for spec deviations during execution. Triggers when:
- Agent output contradicts a spec requirement
- Agent adds functionality not in the spec
- Agent modifies a file outside its declared scope

---

## Deviation Protocol: STOP → DOCUMENT → ASK → LOG

When a deviation is detected, the following protocol executes unconditionally:

### Step 1: STOP

The agent halts immediately. No further output is generated. The current step is marked as `paused`.

### Step 2: DOCUMENT

The deviation is recorded in structured format:

```yaml
deviation:
  timestamp: "2025-01-15T10:30:00Z"
  agent: implementer
  step: implement-auth-module
  type: spec-deviation  # or: rationalization, scope-creep, skip-attempt
  description: "Agent attempted to use JWT instead of spec-required session tokens"
  spec_reference: "Section 3.2: Authentication MUST use server-side sessions"
  agent_output_excerpt: "Using JWT would be more scalable..."
```

### Step 3: ASK

The pipeline presents the deviation to the user with options:
- **Approve deviation** — spec is updated, agent continues with new direction
- **Reject deviation** — agent must redo the step following the original spec
- **Pause pipeline** — human investigates further

### Step 4: LOG

Regardless of the decision, the deviation and its resolution are logged to the pipeline state file for audit.

---

## Writing Guardrails in Agent Manifests

Each agent's `agent-manifest.yaml` includes a `guardrails` section with three required fields.

### Structure

```yaml
guardrails:
  must-do:
    - "Requirement the agent MUST follow"
    - "Another mandatory behavior"
  must-not:
    - "Behavior the agent MUST NOT exhibit"
    - "Another forbidden behavior"
  on-violation: halt-and-report  # or: warn, retry, escalate
```

### must-do Rules

Positive requirements. The agent is checked against these after each step.

```yaml
# Example: spec-writer agent
guardrails:
  must-do:
    - Include acceptance criteria for every user story
    - Define error handling for every endpoint
    - Specify database schema with types and constraints
    - Include non-functional requirements section
```

### must-not Rules

Negative constraints. The agent's output is scanned for violations.

```yaml
# Example: implementer agent
guardrails:
  must-not:
    - Add features not specified in the spec
    - Skip error handling
    - Use deprecated APIs without spec approval
    - Commit code that doesn't compile
```

### on-violation Strategies

| Strategy | Behavior |
|----------|----------|
| `halt-and-report` | Stop execution, report violation to user |
| `warn` | Log warning, continue execution |
| `retry` | Redo the step (up to 3 times) |
| `escalate` | Pass to reviewer agent for judgment |

### Composing Guardrails

Guardrails compose hierarchically:
1. **System guardrails** (10 Iron Laws) — always active, cannot be overridden
2. **Agent guardrails** (manifest) — active when that agent runs
3. **Step guardrails** (pipeline YAML) — active for a specific step

A violation at any level triggers the deviation protocol.

---

## Schema Reference

### guardrails.schema.yaml

**File:** `schemas/guardrails.schema.yaml`

```yaml
type: object
required: [must-do, must-not, on-violation]
properties:
  must-do:
    type: array
    items:
      type: string
    minItems: 1
    description: Positive requirements the agent must follow
  must-not:
    type: array
    items:
      type: string
    minItems: 1
    description: Behaviors the agent must not exhibit
  on-violation:
    type: string
    enum: [halt-and-report, warn, retry, escalate]
    description: Action taken when a guardrail is violated
  context:
    type: object
    description: Optional additional context for guardrail evaluation
    properties:
      severity:
        type: string
        enum: [critical, warning, info]
      scope:
        type: array
        items:
          type: string
        description: File patterns this guardrail applies to
```

### Validation

Guardrails are validated at two points:
1. **Install time** — `python scripts/validate.py` checks all manifests against the schema
2. **Runtime** — `pre_step.py` re-validates before each step executes

---

## Quick Reference

```
System Level:   10 Iron Laws (always on, never overridden)
                    │
Agent Level:    agent-manifest.yaml guardrails section
                    │
Step Level:     Pipeline YAML step-specific constraints
                    │
Detection:      pre_step.py (before) + post_step.py (after)
                    │
Response:       STOP → DOCUMENT → ASK → LOG
```
