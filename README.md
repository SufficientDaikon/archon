<div align="center">

# 🧠 OMNISKILL

### Universal AI Agent & Skills Framework

**One repo. One format. Every platform. Best-in-class.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/skills-41-blue)]()
[![Bundles](https://img.shields.io/badge/bundles-8-green)]()
[![Platforms](https://img.shields.io/badge/platforms-5-purple)]()

_Write skills once. Run them on Claude Code, Copilot CLI, Cursor, Windsurf, and Antigravity._

</div>

---

## What is OMNISKILL?

OMNISKILL is a **universal framework** for AI coding assistant skills, agents, and workflows. It solves the fragmentation problem: instead of maintaining separate skill files for every AI tool, you write once in a universal format and deploy everywhere.

### Key Features

| Feature                 | Description                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| 🎯 **Universal Skills** | Single format works on 5+ AI platforms                                  |
| 📦 **Bundles**          | Install domain kits (Godot, Web Dev, UX, Django...) as one unit         |
| 🤖 **Formal Agents**    | Agents with personas, skill bindings, guardrails, and handoff protocols |
| 🔄 **Pipelines**        | Multi-agent workflows (spec → implement → review)                       |
| 🏭 **Skill Factory**    | AI-powered pipeline to create new skills that meet quality standards    |
| 🔌 **Cross-Platform**   | Adapters for Claude Code, Copilot CLI, Cursor, Windsurf, Antigravity    |
| 📚 **Rich Resources**   | Cheat sheets, style guides, decision trees bundled with skills          |
| 🧪 **Validation**       | Schema-based validation for every skill, bundle, agent, and pipeline    |
| 🔄 **Self-Improving**   | Uses its own pipelines to improve its own skills                        |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/SufficientDaikon/omniskill.git
cd omniskill
```

### 2. Install for your platform

```bash
python scripts/install.py              # Auto-detects platforms
python scripts/install.py --platform claude-code   # Specific platform
python scripts/install.py --bundle web-dev-kit     # Specific bundle only
```

### 3. Verify

```bash
python scripts/doctor.py               # Check installation health
```

---

## 📦 Bundles

| Bundle            | Skills   | Description                                            |
| ----------------- | -------- | ------------------------------------------------------ |
| **godot-kit**     | 5 skills | Complete Godot 4 / GDScript development                |
| **web-dev-kit**   | 5 skills | Frontend, React, backend, design guidelines            |
| **ux-design-kit** | 7 skills | Full UX pipeline: research → wireframe → visual → test |
| **django-kit**    | 4 skills | Django framework, ORM, REST APIs                       |
| **sdd-kit**       | 5 skills | Spec-Driven Development: spec → implement → review     |
| **testing-kit**   | 4 skills | E2E testing, QA planning, debugging                    |
| **mobile-kit**    | 2 skills | Mobile design, Capacitor best practices                |
| **meta-kit**      | 5 skills | Skill creation, discovery, packaging, prompts          |

---

## 🔄 Pipelines

| Pipeline           | Flow                                             | Trigger                        |
| ------------------ | ------------------------------------------------ | ------------------------------ |
| **sdd-pipeline**   | spec-writer → implementer → reviewer             | "build feature X from scratch" |
| **ux-pipeline**    | research → wireframe → visual → review → handoff | "design feature X"             |
| **debug-pipeline** | debug → implement → test → review                | "fix bug X"                    |
| **skill-factory**  | prompt → spec → implement → validate → review    | "create a new skill for X"     |
| **full-product**   | ux-pipeline → sdd-pipeline → testing             | "build product X end-to-end"   |

---

## 📁 Directory Structure

```
omniskill/
├── skills/           # All individual skills (SKILL.md + manifest.yaml)
│   └── _template/    # Skill template for new skills
├── bundles/          # Domain bundles (bundle.yaml + meta-skill)
├── agents/           # Agent definitions (AGENT.md + agent-manifest.yaml)
│   └── _template/    # Agent template
├── pipelines/        # Multi-agent workflow definitions
├── prompts/          # Categorized prompt library
├── adapters/         # Cross-platform adapters (5 platforms)
├── scripts/          # install, doctor, validate, migrate, update
├── schemas/          # YAML validation schemas
└── docs/             # Extended documentation
```

---

## 🎯 Skill Format

Every skill follows the OMNISKILL universal format:

```
skills/my-skill/
├── SKILL.md           # Instructions (Identity, Workflow, Rules, Output, Handoff)
├── manifest.yaml      # Metadata (name, version, triggers, platforms, tags)
├── resources/         # Reference materials (cheat sheets, style guides)
├── examples/          # Sample interactions
├── templates/         # Output templates
├── tests/             # Validation test cases
└── overrides/         # Platform-specific overrides
```

**manifest.yaml** declares triggers, supported platforms, dependencies, and resources.
**SKILL.md** contains the actual instructions the AI agent follows.

See [`skills/_template/`](skills/_template/) for the full template.

---

## 🤖 Agent Format

Every agent follows the OMNISKILL agent format:

```
agents/my-agent/
├── AGENT.md               # Full agent definition (Identity, Persona, Workflow, Guardrails)
└── agent-manifest.yaml    # Metadata (skill bindings, handoffs, I/O contracts)
```

See [`agents/_template/`](agents/_template/) for the full template.

---

## 🔌 Supported Platforms

| Platform           | Adapter                 | Target Location        |
| ------------------ | ----------------------- | ---------------------- |
| Claude Code        | `adapters/claude-code/` | `~/.claude/skills/`    |
| GitHub Copilot CLI | `adapters/copilot-cli/` | `~/.copilot/skills/`   |
| Cursor             | `adapters/cursor/`      | `.cursor/rules/`       |
| Windsurf           | `adapters/windsurf/`    | `.windsurfrules`       |
| Antigravity        | `adapters/antigravity/` | `.antigravity/skills/` |

---

## 🧪 Validation

```bash
python scripts/validate.py skills/my-skill     # Validate one skill
python scripts/validate.py bundles/my-kit       # Validate one bundle
python scripts/validate.py --all                # Validate everything
```

---

## 📖 Documentation

**🌐 [Browse the Full Documentation Site →](https://sufficientdaikon.github.io/omniskill/docs/getting-started.html)**

| Guide | Description |
| --- | --- |
| [Getting Started](https://sufficientdaikon.github.io/omniskill/docs/getting-started.html) | Installation, setup, your first skill |
| [Creating Skills](https://sufficientdaikon.github.io/omniskill/docs/creating-skills.html) | Skill anatomy, manifest, SKILL.md authoring |
| [Creating Bundles](https://sufficientdaikon.github.io/omniskill/docs/creating-bundles.html) | Domain kits with meta-skill routing |
| [Creating Agents](https://sufficientdaikon.github.io/omniskill/docs/creating-agents.html) | Agent personas, skill bindings, handoffs |
| [Creating Pipelines](https://sufficientdaikon.github.io/omniskill/docs/creating-pipelines.html) | Multi-agent workflows with branching |
| [Platform Guide](https://sufficientdaikon.github.io/omniskill/docs/platform-guide.html) | Claude Code, Copilot, Cursor, Windsurf, Antigravity |
| [Architecture](https://sufficientdaikon.github.io/omniskill/docs/architecture.html) | Layered design, data flow, validation |
| [FAQ](https://sufficientdaikon.github.io/omniskill/docs/faq.html) | Common questions answered |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills, bundles, agents, and pipelines.

---

## License

MIT © tahaa
