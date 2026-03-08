# Pipelines

Multi-agent workflow definitions for OMNISKILL.

| Pipeline                              | Description              | Trigger                        |
| ------------------------------------- | ------------------------ | ------------------------------ |
| [sdd-pipeline](sdd-pipeline.yaml)     | Spec-Driven Development  | "build feature X from scratch" |
| [ux-pipeline](ux-pipeline.yaml)       | Full UX Design Lifecycle | "design feature X"             |
| [debug-pipeline](debug-pipeline.yaml) | Systematic Bug Fixing    | "fix bug X"                    |
| [skill-factory](skill-factory.yaml)   | Create New Skills        | "create a new skill for X"     |
| [full-product](full-product.yaml)     | End-to-End Product Dev   | "build product X end-to-end"   |

## How Pipelines Work

Pipelines define ordered sequences of agent steps. Each step:

1. Receives input (from the user or a previous step)
2. Invokes a specific agent
3. Produces output passed to the next step
4. Handles failure (halt, loop back, skip, or retry)

Pipelines are **resumable** — if interrupted, they save state and can continue from the last completed step.

## Schema

See [`schemas/pipeline.schema.yaml`](../schemas/pipeline.schema.yaml) for the full pipeline definition schema.
