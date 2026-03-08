# Creating Agents

## What's an Agent?

An agent is an **orchestration layer** — a defined persona that uses skills, tools, and handoff protocols to accomplish specific types of tasks. Agents are the building blocks of pipelines.

## Agent Structure

```
agents/my-agent/
├── AGENT.md               # Full agent definition
└── agent-manifest.yaml    # Metadata, bindings, contracts
```

## Creating an Agent

### Step 1: Define agent-manifest.yaml

```yaml
name: my-task-agent
version: 1.0.0
role: "Task Specialist"
description: "Handles [type of task] with [approach]"

persona:
  tone: "professional, thorough"
  style: "methodical, step-by-step"
  identity: "specialist in [domain]"

skill-bindings:
  - skill: relevant-skill
    trigger: "when user asks to do X"

tool-access: [filesystem, github]

handoff-targets:
  - agent: next-agent
    condition: "when task is complete"
    artifact: "output file path"

guardrails:
  - "Never skip validation"

input-contract:
  type: "task description"
  format: "free text"

output-contract:
  type: "completed artifact"
  format: "depends on task"
```

### Step 2: Write AGENT.md

See [agents/\_template/AGENT.md](../agents/_template/AGENT.md) for the full template with all required sections.

### Step 3: Validate

```bash
python scripts/validate.py agents/my-task-agent
```

## Self-Customization

Use the AI-guided approach:

> "Follow the add-agent skill to create an agent for [task type]"

The `add-agent` skill provides step-by-step guidance for defining personas, skill bindings, and handoff protocols.

## Special Agent Pattern: The Routing Agent

The **complexity-router** is a special type of agent that runs before other agents. It:

1. Classifies incoming tasks: trivial → simple → moderate → complex → expert
2. Routes to the optimal model tier (fast/cheap → standard → premium)
3. Selects the appropriate skill/agent/pipeline
4. Has P0 priority (runs first on every request)

See `skills/complexity-router/resources/routing-table.md` for the full routing logic.

## Existing Agents

See the [agents directory](../agents/) for all available agents.
