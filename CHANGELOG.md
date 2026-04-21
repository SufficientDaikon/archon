## [1.0.0-production] - 2026-04-21

### Production Hardening Release

**Synapse Engine v2**
- Production-hardened `synapse_engine_v2.py` with async trigger firing
- Formal decision types: `halt`, `warn`, `allow`
- Wired into pipeline execution at pre-execution phase
- Per-step synapse validation with blocking decisions

**Complete Synapse Module (src/archon/synapses/)**
- All 12 synapses now fully operational: anti_rationalization, code_quality, completeness, consistency, metacognition, mcp_client, pattern_recognition, security_awareness, sequential_thinking, trust_verification, code_quality_mcp, security_awareness_mcp
- `metacognition.py` expanded from 6-line stub to 108-line full validator (plan, reasoning, reflection, confidence checks)
- `trust_verification.py` contradiction detection fixed (was silent pass)
- `synapses/__init__.py` exports all 12 (was only 3)

**Testing Enforcement**
- CI now runs `pytest tests/` — 362 test suite is guarded on every commit
- Added `[project.optional-dependencies][dev]` with pytest, pytest-asyncio, pytest-cov
- New test suite: test_anticrationalization, test_code_quality, test_completeness, test_consistency, test_metacognition, test_pattern_recognition, test_security_awareness, test_trust_verification, test_synapses_executable

**MCP Servers**
- `servers/file-ops/` — File operations MCP server (Python)
- `servers/forge/` — Forge MCP server
- `file-ops-rs/` — Rust daemon with rate limiting + metrics

**Quality**
- All build artifacts properly gitignored
- `.gitignore` entries for file-ops-rs/target/ and servers/forge/target/
- Comprehensive release notes and changelog

---

# Changelog

All notable changes to Archon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Claude Code Hooks Architecture** — 8 lifecycle hooks that transform Archon's 5 synapses from passive documents into active enforced behavior
  - `session_boot.py` (SessionStart): Project detection, git state, boot context injection
  - `prompt_router.py` (UserPromptSubmit): Complexity classification, skill routing, synapse activation
  - `guard_bash.py` (PreToolUse/Bash): Blocks dangerous commands (rm -rf, force push, fork bombs)
  - `guard_write.py` (PreToolUse/Write|Edit|NotebookEdit): Secret scanning with env-var false-positive prevention
  - `quality_write.py` (PostToolUse/Write|Edit|NotebookEdit): Tracks modified files in session state
  - `quality_bash.py` (PostToolUse/Bash): Tracks test/build pass/fail results
  - `completion_gate.py` (Stop): Blocks session completion when tests or build failed
  - `agent_context.py` (SubagentStart): Role-specific context slicing for subagents
- **Shared modules** for hooks: `state.py` (atomic JSON state), `classifier.py` (complexity tiers), `scanner.py` (secret/command detection)
- **archon-adversarial-review skill** — PRISM-A protocol for independent framework auditing with 9 probe vectors

### Changed

- Stripped multi-platform support — Archon is now Claude Code only (model floor: Opus 4.6)
- Removed platform-specific adapters (Copilot CLI, Cursor, Windsurf, Antigravity)

## [1.0.0] - 2026-03-24

### The Virtuoso Engine for AI Agents

Archon v1.0.0 is the Virtuoso Engine for AI Agents — Claude Code only.

**Core Framework**

- 98 universal skills in a standardized format (SKILL.md + manifest.yaml + resources)
- 16 domain bundles (Godot, Web Dev, UX, Django, SDD, Testing, Mobile, Meta, Prompts, Security, Data Layer, DevOps, Windows, Orchestration, GitHub, Teaching)
- 17 agents with personas, skill bindings, guardrails, and handoff protocols
- 8 resumable multi-agent pipelines with failure recovery and context curation
- 5 cognitive synapses (metacognition, anti-rationalization, sequential-thinking, security-awareness, pattern-recognition)

**Architecture**

- 6-layer architecture: Skills -> Agents -> Synapses -> Pipelines -> Guardrails -> Runtime
- Session state machine with policy engine
- MCP agent-router for on-demand agent discovery

**Platform**

- Claude Code (model floor: Opus 4.6)
- Python SDK with programmatic access to all framework capabilities
