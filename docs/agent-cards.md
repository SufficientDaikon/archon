# Agent Cards

> Machine-readable metadata cards for every Archon agent — enabling discovery, selection, and programmatic consumption.

---

## What are Agent Cards?

Every Archon agent carries a structured **Agent Card** in its `agent-manifest.yaml`. The card describes the agent's capabilities, input/output modalities, cost tier, token estimates, and quality metrics in a machine-readable format.

Agent Cards enable:

- **Discovery** — External systems (web UIs, LLM routers, IDE extensions) can find agents and their capabilities from a single JSON index.
- **Selection** — When multiple agents could handle a task, card metadata (capabilities, cost-tier, quality-metrics) enables automated or user-assisted agent selection.
- **Observability** — Token usage estimates and quality metrics per agent enable cost optimization and continuous improvement.
- **Ecosystem** — A standardized card format makes agents portable across frameworks that adopt the same schema.

---

## Card Schema

Each card contains the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `capabilities` | object | ✅ | Boolean flags for agent capabilities |
| `capabilities.streaming` | boolean | ✅ | Supports streaming output |
| `capabilities.multi-turn` | boolean | ✅ | Supports multi-turn conversations |
| `capabilities.file-output` | boolean | ✅ | Produces file artifacts |
| `capabilities.self-evaluation` | boolean | ✅ | Validates own output quality |
| `capabilities.context-aware` | boolean | ✅ | Uses prior context from the pipeline |
| `skills-provided` | list | ✅ | Skills this agent provides (min 1) |
| `skills-provided[].id` | string | ✅ | Unique kebab-case skill identifier |
| `skills-provided[].name` | string | ✅ | Human-readable skill name |
| `skills-provided[].description` | string | ✅ | What this skill does |
| `skills-provided[].tags` | list[string] | ❌ | Categorization tags |
| `input-modes` | list[string] | ✅ | MIME types the agent accepts (min 1) |
| `output-modes` | list[string] | ✅ | MIME types the agent produces (min 1) |
| `cost-tier` | string | ✅ | One of: `fast`, `standard`, `premium` |
| `avg-tokens` | object | ✅ | Token usage estimates |
| `avg-tokens.input` | integer | ✅ | Average input tokens (≥ 0) |
| `avg-tokens.output` | integer | ✅ | Average output tokens (≥ 0) |
| `quality-metrics` | object \| null | ❌ | Evaluation metrics (null = not yet evaluated) |
| `quality-metrics.completeness` | float | ❌ | Fraction of requirements addressed (0.0–1.0) |
| `quality-metrics.last-eval-score` | float | ❌ | Score from most recent evaluation (0.0–1.0) |
| `quality-metrics.eval-count` | integer | ❌ | Number of evaluations completed |

---

## Example Card

```yaml
card:
  capabilities:
    streaming: false
    multi-turn: true
    file-output: true
    self-evaluation: true
    context-aware: true
  skills-provided:
    - id: requirements-engineering
      name: Requirements Engineering
      description: "Transforms ambiguous ideas into crystal-clear, testable specifications"
      tags: [specification, requirements, acceptance-criteria]
  input-modes:
    - "text/plain"
    - "text/markdown"
  output-modes:
    - "text/markdown"
  cost-tier: standard
  avg-tokens:
    input: 2000
    output: 8000
  quality-metrics: null
```

---

## Generating `agent-cards.json`

The `agent-cards.json` file is an auto-generated JSON index of all agent cards. It contains every agent's name, version, role, description, path, and full card data.

### CLI Command (recommended)

```bash
# Generate agent-cards.json at the repo root
archon generate agent-cards

# Write to a custom directory
archon generate agent-cards --output ./dist/

# JSON output (for scripting)
archon --json generate agent-cards
```

### Standalone Script

Works without the `archon` package installed — only requires Python 3.10+ and PyYAML:

```bash
python scripts/generate-agent-cards.py
python scripts/generate-agent-cards.py --output ./dist/
```

---

## CLI Reference

### View all agent cards

```bash
archon cards
```

Displays a Rich table with columns: Name, Role, Capabilities (emoji badges), Cost Tier (colored).

### View a single agent card

```bash
archon cards spec-writer-agent
```

Displays a detailed Rich panel with all card fields.

### Export as JSON

```bash
archon cards --json
```

Outputs a JSON envelope with all card data.

### Validate cards

```bash
archon cards --validate
```

Validates every agent's card section against the schema. Exits with code 0 on success, code 2 on failure.

### Check freshness

```bash
archon validate --check-agent-cards
```

Checks whether `agent-cards.json` is up to date with current manifests.

---

## Using Cards Programmatically

The generated `agent-cards.json` file can be consumed by any tool that reads JSON:

```json
{
  "$schema": "archon-agent-cards-v1",
  "generated": "2025-01-01T00:00:00+00:00",
  "framework_version": "0.2.0",
  "agents": [
    {
      "name": "spec-writer-agent",
      "version": "1.0.0",
      "role": "Specification Architect",
      "description": "...",
      "path": "agents/spec-writer-agent",
      "card": {
        "capabilities": { "streaming": false, "multi-turn": true, ... },
        "skills-provided": [...],
        "input-modes": ["text/plain", "text/markdown"],
        "output-modes": ["text/markdown"],
        "cost-tier": "standard",
        "avg-tokens": { "input": 2000, "output": 8000 },
        "quality-metrics": null
      }
    }
  ]
}
```

### Python

```python
import json
with open("agent-cards.json") as f:
    data = json.load(f)
for agent in data["agents"]:
    if agent["card"] and agent["card"]["cost-tier"] == "fast":
        print(f"Fast agent: {agent['name']}")
```

### JavaScript

```javascript
const cards = await fetch("agent-cards.json").then(r => r.json());
const premiumAgents = cards.agents.filter(
  a => a.card?.["cost-tier"] === "premium"
);
```

---

## Adding Cards to Your Agent

1. Open your agent's `agent-manifest.yaml`
2. Add a `card:` section at the end (see the [template](../agents/_template/agent-manifest.yaml))
3. Fill in accurate values based on your agent's actual capabilities
4. Run `archon cards --validate` to verify

The card section is **optional** — agents without it continue to work normally. However, cards are recommended for discoverability and programmatic consumption.
