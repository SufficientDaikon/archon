# Getting Started with OMNISKILL

## Prerequisites

- **Git** installed
- **Python 3.8+** installed
- At least one supported AI coding assistant:
  - Claude Code
  - GitHub Copilot CLI
  - Cursor
  - Windsurf
  - Antigravity

## Installation

### Full Install (all bundles, all detected platforms)

```bash
git clone https://github.com/tahaa/omniskill.git
cd omniskill
python scripts/install.py
```

### Install a Specific Bundle

```bash
python scripts/install.py --bundle web-dev-kit
python scripts/install.py --bundle godot-kit
```

### Install for a Specific Platform

```bash
python scripts/install.py --platform claude-code
python scripts/install.py --platform cursor
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

## Next Steps

- [Creating Skills](creating-skills.md) — Deep dive into skill authoring
- [Creating Bundles](creating-bundles.md) — Group skills into installable kits
- [Creating Agents](creating-agents.md) — Define formal agent definitions
- [Platform Guide](platform-guide.md) — Platform-specific setup details
