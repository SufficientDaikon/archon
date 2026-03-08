<div align="center">

# 🧠 OMNISKILL

### Universal AI Agent & Skills Framework

**One repo. One format. Every platform. Best-in-class.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/skills-48-blue)]()
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
| 🧠 **Complexity Router** | Smart routing — classifies tasks by complexity, routes to optimal model/agent |
| 📚 **Knowledge Sources** | Pluggable knowledge base — GitHub repos, local dirs, URLs. File-based search, no vector DB |
| 🔧 **Self-Customization** | AI-assisted skills that guide agents to create new skills, bundles, agents, and adapters |
| 🎭 **Prompt Library**   | Organized prompt templates — router, system, personas (expert, quick, teacher) |
| 🐍 **Python SDK**       | Programmatic access — `from sdk.omniskill import OmniSkill` |
| 🏭 **Skill Factory**    | AI-powered pipeline to create new skills that meet quality standards    |
| 🔌 **Cross-Platform**   | Adapters for Claude Code, Copilot CLI, Cursor, Windsurf, Antigravity    |
| 📖 **Rich Resources**   | Cheat sheets, style guides, decision trees bundled with skills          |
| 🧪 **Validation**       | Schema-based validation for every skill, bundle, agent, and pipeline    |
| 🔄 **Self-Improving**   | Uses its own pipelines to improve its own skills                        |
| 🩺 **Admin Dashboard**  | Comprehensive health checks, stats, and diagnostics via CLI             |

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
├── skills/           # 48 individual skills (SKILL.md + manifest.yaml)
│   ├── _template/    # Skill template for new skills
│   ├── complexity-router/  # 🧠 Smart task routing (NEW)
│   ├── knowledge-sources/  # 📚 External knowledge management (NEW)
│   ├── add-skill/    # 🔧 AI-assisted skill creation (NEW)
│   ├── add-bundle/   # 🔧 AI-assisted bundle creation (NEW)
│   ├── add-agent/    # 🔧 AI-assisted agent creation (NEW)
│   ├── add-adapter/  # 🔧 AI-assisted adapter creation (NEW)
│   ├── rename-project/ # 🔧 Fork & rename OMNISKILL (NEW)
│   └── ...           # 41 domain skills
├── bundles/          # Domain bundles (bundle.yaml + meta-skill)
├── agents/           # Agent definitions (AGENT.md + agent-manifest.yaml)
├── pipelines/        # Multi-agent workflow definitions
├── prompts/          # 🎭 Prompt library — router, system, personas (NEW)
│   ├── router.md     # Complexity classification prompts
│   ├── system.md     # Master system prompt
│   ├── shared.md     # Shared utilities & formatting
│   └── personas/     # Expert, Quick, Teacher personas
├── sdk/              # 🐍 Python SDK (NEW)
│   └── omniskill.py  # Programmatic framework access
├── adapters/         # Cross-platform adapters (5 platforms)
├── scripts/          # install, doctor, validate, migrate, update, admin
├── schemas/          # YAML validation schemas
└── docs/             # Beautiful HTML documentation site
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

## 🧪 Validation & Admin

```bash
python scripts/validate.py skills/my-skill     # Validate one skill
python scripts/validate.py bundles/my-kit       # Validate one bundle
python scripts/validate.py --all                # Validate everything
python scripts/admin.py --stats                 # Show framework statistics
python scripts/admin.py --report                # Generate full health report
```

---

## 🧠 Complexity Router

Every incoming task is automatically classified by complexity and routed to the optimal model/agent:

| Complexity | Model Tier | Routing |
| --- | --- | --- |
| **Trivial** | Fast (Haiku) | Direct answer, no skill needed |
| **Simple** | Fast + Skill | Single skill activation |
| **Moderate** | Standard + Resources | Skill with reference materials |
| **Complex** | Premium + Agent | Multi-skill agent orchestration |
| **Expert** | Premium + Pipeline | Full multi-agent pipeline |

Cost optimization happens automatically — no manual rules to maintain.

---

## 📚 Knowledge Sources

Plug any source into your knowledge base — no vector DB, no embeddings needed. File-based search with `grep`/`find`/`cat`.

```yaml
# sources config example
sources:
  - id: my-docs
    type: github
    repo: owner/repo
    branch: main
    content-path: docs
  - id: local-notes
    type: local
    path: ~/notes
  - id: reference
    type: url
    url: https://docs.example.com
```

---

## 🔧 AI-Assisted Self-Customization

OMNISKILL includes skills that guide AI agents through customizing the framework itself:

| Skill | Purpose |
| --- | --- |
| `add-skill` | Step-by-step guide to create a new skill |
| `add-bundle` | Create a new domain bundle with meta-skill |
| `add-agent` | Define a new agent with skill bindings |
| `add-adapter` | Add support for a new AI platform |
| `rename-project` | Fork & fully rename OMNISKILL for custom use |

Just tell your AI assistant: *"Follow the add-skill skill to create a new skill for [domain]"*

---

## 🎭 Prompt Library

Organized prompt templates in `prompts/`:

| Prompt | Purpose |
| --- | --- |
| `router.md` | Complexity classification system prompt |
| `system.md` | Master OMNISKILL agent identity prompt |
| `shared.md` | Response formatting, citations, error handling |
| `personas/expert.md` | Deep, thorough analysis persona |
| `personas/quick.md` | Concise, fast response persona |
| `personas/teacher.md` | Step-by-step explanatory persona |

---

## 🐍 Python SDK

```python
from sdk.omniskill import OmniSkill

os = OmniSkill()
os.list_skills(tags=["web"])          # Filter skills by tag
os.route("build a React dashboard")  # Complexity routing
os.install(platform="cursor")        # Install to platform
os.sync_sources()                    # Sync knowledge sources
os.health_check()                    # Comprehensive diagnostics
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
