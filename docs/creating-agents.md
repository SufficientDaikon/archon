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
  - rule: "Never skip validation"
    severity: critical
    on-violation: halt
  - rule: "Always document assumptions"
    severity: major
    on-violation: warn
  - rule: "Prefer explicit over implicit"
    severity: minor
    on-violation: log

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

| Agent | Role | Key Skills |
|-------|------|------------|
| spec-writer-agent | Specification Architect | spec-writer, prompt-architect |
| implementer-agent | Implementation Engineer | implementer |
| reviewer-agent | Compliance Reviewer | reviewer |
| debugger-agent | Debug Investigator | systematic-debugging |
| ux-research-agent | UX Researcher | ux-research |
| ui-design-agent | Visual Designer | ui-visual-design, frontend-design |
| qa-master-agent | QA Engineer | e2e-testing-patterns, qa-test-planner |
| context-curator-agent | Context Architect | context-curator |
| dissector-agent | Codebase Analyst | dissector |
| **security-reviewer-agent** | Security Reviewer | security-review, security-awareness synapse |

## v2.0: Guardrails Enforcement

In v2.0, guardrails are **enforced at runtime**, not just documented. Every guardrail has three fields:

| Field | Values | Meaning |
| --- | --- | --- |
| `rule` | Free text | The constraint the agent must follow |
| `severity` | `critical`, `major`, `minor` | How serious a violation is |
| `on-violation` | `halt`, `warn`, `log` | What happens when the rule is broken |

### Severity Levels

- **critical** — Violation stops execution immediately. The agent must not proceed.
- **major** — Violation generates a warning. The agent should address it before continuing.
- **minor** — Violation is logged for audit. The agent can continue.

### The Anti-Rationalization Synapse

All agents automatically load the **anti-rationalization** core synapse, which prevents agents from rationalizing their way around guardrails. It includes:

- **10 Iron Laws** — Absolute rules that cannot be bent
- **Forbidden phrases** — Language patterns that signal rule-bending
- **Rationalization tables** — Common excuse patterns and their corrections

### Example: Spec Writer Guardrails

```yaml
guardrails:
  - rule: "Never assume requirements — ask or mark as TBD"
    severity: critical
    on-violation: halt
  - rule: "Every section must have acceptance criteria"
    severity: critical
    on-violation: halt
  - rule: "Use precise language — no ambiguous terms"
    severity: major
    on-violation: warn
  - rule: "Include error handling for every user flow"
    severity: major
    on-violation: warn
```
