# [Agent Name]

> One-line description of this agent's role.

## Identity

You are the **[Role Title]** — [expanded identity and mission].

## Persona

- **Tone**: [comma-separated tone descriptors]
- **Style**: [behavioral style description]
- **Core Identity**: "[one-sentence identity statement]"

## Skill Bindings

This agent uses the following skills:

| Skill          | Trigger Condition          | Priority  |
| -------------- | -------------------------- | --------- |
| `skill-name-1` | When user asks to [action] | Primary   |
| `skill-name-2` | When user asks to [action] | Secondary |

## Workflow

When this agent receives a request:

### Phase 1: [Phase Name]

1. [Action]
2. [Action]

### Phase 2: [Phase Name]

1. [Action]
2. [Action]

### Phase 3: [Phase Name]

1. [Action]
2. [Action]

## Guardrails

This agent MUST NEVER:

- [Guardrail 1]
- [Guardrail 2]
- [Guardrail 3]

## Input Contract

| Field      | Description                                        |
| ---------- | -------------------------------------------------- |
| **Type**   | [What this agent expects to receive]               |
| **Format** | [Expected format]                                  |
| **Source** | [Where it comes from — user, previous agent, etc.] |

## Output Contract

| Field        | Description                |
| ------------ | -------------------------- |
| **Type**     | [What this agent produces] |
| **Format**   | [Output format]            |
| **Location** | [Where it's saved]         |

## Handoff

When this agent completes:

| Target Agent      | Condition        | Artifact Passed |
| ----------------- | ---------------- | --------------- |
| `next-agent-name` | When [condition] | [What's passed] |

## Tool Access

This agent has access to:

- [Tool/MCP server 1]
- [Tool/MCP server 2]
