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
