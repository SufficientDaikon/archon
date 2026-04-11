# Getting Started with Archon

## Prerequisites

- **Git** installed
- **Python 3.8+** installed
- **Claude Code** installed (`~/.claude/` directory present)

## Installation

### Full Install

```bash
git clone https://github.com/SufficientDaikon/archon.git
cd archon
python scripts/install.py
```

### Install a Specific Bundle

```bash
python scripts/install.py --bundle web-dev-kit
python scripts/install.py --bundle godot-kit
```

### Verify Installation

```bash
python scripts/doctor.py
```

## Your First Skill

### Option A: Use the Skill Factory (recommended)

Tell your AI assistant:

> "Create a new skill for [your domain]"

This triggers the **skill-factory pipeline** which guides you through the entire process.

### Option B: Manual Creation

1. Copy the template: `cp -r skills/_template skills/my-skill`
2. Edit `skills/my-skill/manifest.yaml` — fill in name, description, triggers
3. Edit `skills/my-skill/SKILL.md` — define identity, workflow, rules
4. Validate: `python scripts/validate.py skills/my-skill`
5. Install: `python scripts/install.py --skill my-skill`

## Using Bundles

Bundles are domain kits that install multiple related skills at once:

```bash
# Install the web development kit
python scripts/install.py --bundle web-dev-kit

# This installs: frontend-design, react-best-practices,
# vercel-react-best-practices, web-design-guidelines, backend-development
# Plus the web-fullstack-expert meta-skill that composes them
```

## Using Pipelines

Pipelines are multi-agent workflows. Trigger them with natural language:

- **"Build feature X from scratch"** → SDD Pipeline (spec → implement → review)
- **"Design feature X"** → UX Pipeline (research → wireframe → visual → review)
- **"Fix bug X"** → Debug Pipeline (investigate → fix → test → review)
- **"Create a new skill for X"** → Skill Factory

Behind the scenes, every request passes through the **Complexity Router** which classifies your task (trivial → simple → moderate → complex → expert) and routes it to the optimal model tier and skill/agent/pipeline.

## Knowledge Sources

Archon can tap into external knowledge repositories:

- **GitHub repos** — Point to any public or private repository
- **Local directories** — Reference your project docs, specs, or notes
- **URLs** — Web documentation or API references
- **APIs** — Dynamic data sources

Knowledge sources use file-based search (grep/find/cat) — no vector databases or embeddings required. Configure sources in `templates/source-config.yaml` and sync them with:

```bash
python scripts/admin.py --sync
```

## Self-Customization

Archon includes AI-guided skills for extending itself:

- **`add-skill`** -- Tell your AI: "Follow the add-skill skill to create a skill for [domain]"
- **`add-bundle`** -- AI-guided bundle creation with checklists
- **`add-agent`** -- AI-guided agent creation
- **`rename-project`** -- Fork Archon and customize it for your organization

These skills provide step-by-step guidance and validation checks.

## Using the SDK

For programmatic access, use the Python SDK:

```python
from sdk.archon import Archon

os = Archon()

# List available skills
skills = os.list_skills()

# Route a task to the right skill/agent
route = os.route("Create a React component")

# Sync knowledge sources
os.sync_sources()

# Health check
report = os.health_check()
```

## Next Steps

- [Creating Skills](creating-skills.md) — Deep dive into skill authoring
- [Creating Bundles](creating-bundles.md) — Group skills into installable kits
- [Creating Agents](creating-agents.md) — Define formal agent definitions
- [Creating Pipelines](creating-pipelines.md) — Build multi-agent workflows
- [Creating Synapses](creating-synapses.md) — Custom cognitive capabilities
- [Architecture](architecture.md) — Understand the 5-Layer architecture
- [Guardrails](guardrails.md) — How guardrails enforce agent discipline
- [Sequential Thinking](sequential-thinking.md) — Chain-of-thought protocol
- [Pipeline Orchestration](pipeline-orchestration.md) — Real pipeline execution engine
- [Platform Guide](platform-guide.md) — Platform-specific setup details
- [Migration Guide (v2.0)](migration-v2.md) — Upgrading from v0.x to v2.0
- [FAQ](faq.md) — Common questions about new features

## v2.0 Features

### Guardrails Engine

Every agent in v2.0 has **enforced guardrails** — structured rules with severity levels and violation actions:

```yaml
guardrails:
  - rule: "Never assume requirements"
    severity: critical
    on-violation: halt
  - rule: "Always validate output"
    severity: major
    on-violation: warn
```

Guardrails are enforced by the hook system, not just documented. The anti-rationalization synapse prevents agents from rationalizing their way around rules.

### Sequential Thinking

The sequential-thinking synapse fires automatically for every agent, enforcing step-by-step reasoning:

1. **DECOMPOSE** — Break the task into numbered steps
2. **REASON** — Think through each step with evidence
3. **VALIDATE** — Check conclusions against evidence
4. **SYNTHESIZE** — Combine step conclusions into final answer

### Pipeline Execution

Pipelines are now real executable workflows:

```bash
archon pipeline run sdd-pipeline --project ./myapp
archon pipeline status
archon pipeline resume <state-id>
```

The pipeline engine handles failure recovery, context curation between steps, and persistent state.
