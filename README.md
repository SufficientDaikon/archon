<div align="center">

# Archon

### The Virtuoso Engine for AI Agents

**One framework. Every platform. Enforced discipline.**

[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/skills-83-blue)]()
[![Agents](https://img.shields.io/badge/agents-10-orange)]()
[![Synapses](https://img.shields.io/badge/synapses-5-blueviolet)]()
[![Pipelines](https://img.shields.io/badge/pipelines-8-red)]()
[![Tests](https://img.shields.io/badge/tests-513-success)]()
[![Platforms](https://img.shields.io/badge/platforms-5-purple)]()

*Your AI agents are winging it. Archon makes them disciplined.*

</div>

---

Archon is the universal AI agent skills framework that solves three problems no one else does: **skills that transfer across platforms** without rewrites, **cognitive synapses** that make agents plan before they code, and **guardrails with Iron Laws** that agents cannot rationalize away.

83 skills. 10 agents. 5 cognitive synapses. 8 resumable pipelines. 513 tests. MIT licensed. Works on Claude Code, Cursor, Copilot CLI, Windsurf, and Antigravity.

```bash
pip install archon && archon init && archon doctor
```

---

## Why Archon

Most AI frameworks give you plumbing. Archon gives you **curriculum**.

| Problem | Everyone Else | Archon |
| --- | --- | --- |
| Skills lock you into one platform | Rewrite for each AI tool | Write once, deploy on 5 platforms |
| Agents guess instead of think | No structured reasoning | Cognitive synapses enforce PLAN-before-ACT |
| No quality enforcement | "Best effort" outputs | Iron Laws + guardrails agents cannot bypass |
| Pipelines break and don't recover | Manual restart from scratch | Resumable state machine with failure recovery |
| Skills are flat instruction files | One markdown blob | 6-section structure with resources, tests, templates |

---

## The Virtuoso Architecture

Archon uses a 6-layer architecture. Each layer builds on the one below. Skills at the base, runtime contracts at the top.

| Layer | Purpose |
| --- | --- |
| **Skills & Knowledge** | 83 skills, 14 bundles, prompt library, knowledge sources |
| **Agents & Personas** | 10 agents with formal personas, handoff contracts, quality gates |
| **Synapses & Cognition** | 5 cognitive synapses that shape HOW agents reason |
| **Pipelines & Orchestration** | 8 pipelines with execution, context curation, failure recovery |
| **Guardrails & Hooks** | 5 lifecycle hooks enforcing discipline at runtime |
| **Runtime Contracts** | Session state machine, policy engine, telemetry, MCP trust routing |

```
archon/
  skills/        83 skills (SKILL.md + manifest.yaml + resources)
  bundles/       14 domain bundles (bundle.yaml + meta-skill)
  agents/        10 agent definitions (AGENT.md + agent-manifest.yaml)
  pipelines/     8 multi-agent workflows
  synapses/      5 cognitive synapses (SYNAPSE.md + manifest.yaml)
  hooks/         5 lifecycle hooks
  src/           Core engine (session, policy, telemetry, replay)
  sdk/           Python SDK
  adapters/      5 platform adapters
  schemas/       15 validation schemas
  tests/         513 automated tests
```

---

## Quick Start

```bash
git clone https://github.com/SufficientDaikon/archon.git
cd archon
pip install -e .
archon init          # Detect your AI platforms
archon doctor        # Verify everything works
```

Install skills to your platform:

```bash
archon install --all                          # All 83 skills
archon install --bundle godot-kit             # Just Godot skills
archon install --skill backend-development    # Single skill
```

Run a pipeline:

```bash
archon pipeline run sdd-pipeline --project ./myapp
```

This triggers the full Spec-Driven Development flow: **spec-writer -> context-curator -> implementer -> context-curator -> reviewer** with automatic failure recovery.

---

## Cognitive Synapses

Synapses are what make Archon different. They shape HOW agents think, not what they do.

| Synapse | Phases | What It Does |
| --- | --- | --- |
| **Metacognition** | PLAN -> MONITOR -> REFLECT | Agents plan before acting and tag confidence levels |
| **Anti-Rationalization** | DETECT -> CHALLENGE -> ENFORCE | 10 Iron Laws prevent agents from making excuses |
| **Sequential Thinking** | DECOMPOSE -> REASON -> VALIDATE -> SYNTHESIZE | Step-by-step task decomposition |
| **Security Awareness** | SCAN -> FLAG | Injects OWASP checks during code tasks |
| **Pattern Recognition** | DETECT -> SUGGEST -> APPLY | Surfaces matching skills for detected patterns |

**Core** synapses fire automatically for every agent. Agents don't get to opt out.

---

## Agents

| Agent | Role | Primary Skills |
| --- | --- | --- |
| spec-writer-agent | Specification Architect | spec-writer, prompt-architect |
| implementer-agent | Implementation Engineer | implementer |
| reviewer-agent | Compliance Reviewer | reviewer |
| debugger-agent | Debug Investigator | systematic-debugging |
| context-curator-agent | Context Architect | context-curator |
| dissector-agent | Codebase Analyst | knowledge-sources |
| ux-research-agent | UX Researcher | ux-research |
| ui-design-agent | Visual Designer | ui-visual-design, frontend-design |
| qa-master-agent | QA Engineer | e2e-testing-patterns, qa-test-planner |
| security-reviewer-agent | Security Auditor | guard-chain, error-handling-architecture |

Every agent has `guardrail-enforcement: strict`, formal skill bindings, and handoff protocols.

---

## Bundles

| Bundle | Skills | Domain |
| --- | --- | --- |
| **godot-kit** | 5 | Godot 4 / GDScript |
| **web-dev-kit** | 10 | Frontend, React, RSC, i18n, backend |
| **ux-design-kit** | 7 | Research -> wireframe -> visual -> test |
| **django-kit** | 4 | Django framework, ORM, REST APIs |
| **sdd-kit** | 6 | Spec-Driven Development |
| **testing-kit** | 5 | Unit, E2E, QA, debugging |
| **mobile-kit** | 2 | Mobile design, Capacitor |
| **meta-kit** | 5 | Skill creation, discovery, packaging |
| **prompts-chat-kit** | 17 | Plugin system, quality gates, webhooks, SDK |
| **security-kit** | 4 | Guard chain, webhooks, error handling, logging |
| **data-layer-kit** | 4 | Prisma ORM, singletons, deduplication |
| **devops-kit** | 2 | Docker, structured logging |

---

## Pipelines

| Pipeline | Trigger | Flow |
| --- | --- | --- |
| **sdd-pipeline** | "build feature X from scratch" | spec -> curate -> implement -> curate -> review |
| **ux-pipeline** | "design feature X" | research -> wireframe -> visual -> review -> handoff |
| **debug-pipeline** | "fix bug X" | debug -> curate -> implement -> test -> review |
| **skill-factory** | "create a new skill for X" | prompt -> spec -> implement -> validate -> review |
| **full-product** | "build product X end-to-end" | ux-pipeline -> sdd-pipeline -> testing |
| **dissect-to-skill** | "dissect codebase X into skills" | dissect -> diff -> specify -> implement -> validate |
| **skill-upgrade** | "upgrade skill X" | assess -> specify -> rewrite -> verify |

Pipelines are **resumable**. If interrupted, they save state and continue from the last completed step.

---

## Supported Platforms

| Platform | Target |
| --- | --- |
| Claude Code | `~/.claude/skills/` |
| GitHub Copilot CLI | `~/.copilot/skills/` |
| Cursor | `.cursor/rules/` |
| Windsurf | `.windsurfrules` |
| Antigravity | `.antigravity/skills/` |

Write once, install everywhere.

---

## Documentation

| Guide | Description |
| --- | --- |
| [Getting Started](docs/getting-started.md) | Installation, setup, your first skill |
| [Creating Skills](docs/creating-skills.md) | Skill anatomy, manifest, SKILL.md authoring |
| [Creating Bundles](docs/creating-bundles.md) | Domain kits with meta-skill routing |
| [Creating Agents](docs/creating-agents.md) | Agent personas, skill bindings, handoffs |
| [Creating Pipelines](docs/creating-pipelines.md) | Multi-agent workflows with branching |
| [Creating Synapses](docs/creating-synapses.md) | Custom cognitive capabilities |
| [Architecture](docs/architecture.md) | 6-Layer design, data flow, validation |
| [Guardrails](docs/guardrails.md) | Guardrails engine, Iron Laws, deviation protocol |
| [CLI Guide](docs/cli-guide.md) | Full CLI command reference |
| [Platform Guide](docs/platform-guide.md) | Platform-specific setup details |
| [FAQ](docs/faq.md) | Common questions answered |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills, bundles, agents, pipelines, synapses, and hooks.

---

## License

MIT -- [Ahmed Taha](https://github.com/SufficientDaikon)
