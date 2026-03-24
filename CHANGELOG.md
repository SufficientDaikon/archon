# Changelog

All notable changes to Archon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-24

### The Virtuoso Engine for AI Agents

Archon v1.0.0 is the universal AI agent skills framework with enforced discipline.

**Core Framework**
- 83 universal skills in a standardized format (SKILL.md + manifest.yaml + resources)
- 14 domain bundles (Godot, Web Dev, UX, Django, SDD, Testing, Mobile, Meta, Prompts, Security, Data Layer, DevOps)
- 10 formal agents with personas, skill bindings, guardrails, and handoff protocols
- 8 resumable multi-agent pipelines with failure recovery and context curation
- 5 cognitive synapses (metacognition, anti-rationalization, sequential-thinking, security-awareness, pattern-recognition)
- 5 lifecycle hooks enforcing discipline at runtime

**Architecture**
- 6-layer architecture: Skills -> Agents -> Synapses -> Pipelines -> Guardrails -> Runtime
- Session state machine with policy engine and telemetry
- MCP trust routing and agent card system
- 15 validation schemas

**Platform Support**
- Claude Code, Copilot CLI, Cursor, Windsurf, Antigravity
- Platform-specific adapters with write-once-deploy-everywhere model

**Developer Experience**
- Full CLI: init, install, doctor, validate, search, info, pipeline, admin, cards
- Python SDK with programmatic access to all framework capabilities
- 513 automated tests
- GitHub Actions CI (Python 3.9, 3.12, 3.13)
