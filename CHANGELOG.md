# Changelog

All notable changes to Archon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-10

### Operational Layer Release (ideas stolen from Google's SDKs)

Design mechanics researched from the Google Cloud SDK (gcloud), the Agent
Development Kit (ADK), and the GenAI SDK, then ported to fit a single-user
cognitive harness.

**Config properties (gcloud)**
- Every hook knob is a `section/name` property: classifier tier ceilings,
  per-synapse injection toggles, gate enable/max-blocks, scanner extra
  allowlist, logging controls (18 properties, registered once in
  `hooks/claude/shared/config.py` with help text)
- Precedence: `ARCHON_{SECTION}_{NAME}` env > project `.archon/config` >
  user `~/.archon/config` > default; `archon config list` shows each value
  with its source; malformed values fall back to defaults (never crash a hook)
- `archon config` is now a sub-app (`list/get/set/unset [--project]`).
  BREAKING: positional `archon config KEY VALUE` → `archon config set KEY VALUE`

**Per-project state (gcloud named configurations)**
- State moves to `~/.archon/projects/<slug>/state.json` — fixes concurrent
  sessions in different repos clobbering each other's session state and
  misfiring the completion gate. Legacy `~/.archon/archon-state.json` is
  abandoned in place (only last-3 session summaries lost)

**Hook invocation logging (gcloud per-invocation logs)**
- One fail-open JSONL record per hook firing in `~/.archon/logs/`:
  tier/synapses/word-count for the router, deny/allow + findings for guards,
  gate decisions with block counts; age-based cleanup via logging/max_log_days
- Full stripped-prompt storage is opt-in (logging/log_prompts)

**Diagnostics (gcloud info / --run-diagnostics)**
- `archon info` (no args): environment report — version, paths, properties
  with sources, hook registrations with script-exists checks, state + log
  locations, registry counts
- `archon doctor --hooks`: drives all 11 hooks live with synthetic payloads,
  17 PASS/FAIL checks, exit 1 on failure

**State-templated instructions (ADK) + eval (ADK eval)**
- Synapse instructions support `{state.<key>?}` placeholders resolved from
  live session state, never-throw: injections now say "Tests are recorded
  FAILING this session" and list open todos when true
- `archon eval classifier`: tier distribution + synapse activation from the
  logs; drift replay of stored prompts through the current classifier

Tests: 603 -> 655; ruff clean.

## [1.1.0] - 2026-07-10

### Modernization Release

The hook layer is now the product. This release fixes every broken hook, adds
full session-lifecycle coverage, makes the synapse engine a single honest
implementation, prunes duplicate content, and rewrites docs to match verified
reality.

**Hook layer (hooks/claude/)**
- Fixed completion_gate: removed dead Stop-hook context injection (never consumed);
  added stop_hook_active loop guard and a 2-block cap
- Fixed quality_bash: word-match fallback marked passing runs printing "0 errors" as
  failures — replaced with explicit runner-summary parsing (pytest/jest/cargo/go)
- Fixed session_boot: resume/compact no longer wipe session state; an
  `<archon-resume>` snapshot re-injects files/tests/todos after compaction
- Fixed agent_context: reads `subagent_type`; handles SubagentStop telemetry
- New hooks: todo_track (TodoWrite progress), session_end (reliable archival),
  pre_compact (state freshness); NotebookEdit/MultiEdit now actually registered
- settings.json: python3 + `$CLAUDE_PROJECT_DIR` paths, realistic timeouts
- Classifier: strips pasted code/logs/tracebacks before tier classification;
  questions de-escalate; multi-file/step prompts escalate; synapse instructions
  are tier-banded (escape hatch at COMPLEX, stuck-loop detection at EXPERT),
  distilled from the full SYNAPSE.md content
- guard_bash: force-push detection is flag-order independent; branch names like
  fix-main-page no longer false-positive; feature-branch reset --hard allowed

**Engine (src/archon/)**
- Single synapse implementation: v1 engine deleted; `build_default_engine()`
  registers all 9 router-referenced synapses via adapters over
  `archon.synapses.*.validate()` — previously 7 of 9 silently no-opped
- Legacy pipeline hook system (hooks/hooks.yaml + 5 scripts) deleted; the
  on-failure policy (3-fix escape hatch, retry/loop/skip/escalate) is inlined
- Deleted: legacy sdk/, fake-MCP synapse modules, unwired synapse_hardener,
  unused agent_roles, root stress/debug scripts and report files

**Content**
- Pruned: docker-mcp-ops, react-best-practices (stub), django-framework,
  django-orm-patterns, django-rest-framework (django-expert survives), django-kit
- Every SKILL.md has frontmatter; manifest.yaml owns version (no more drift);
  schema drops the never-followed 6-section requirement
- Registry is self-policing: validate fails on unregistered dirs, missing paths,
  or placeholder descriptions
- Model references updated to current Claude model IDs

**Infra**
- CI fixed to run on `main` (was `master` — CI never ran); ruff lint+format added
- requires-python >= 3.10 (matches the code)
- Tests: 583 -> 603 (new hook contract tests + classifier tests; legacy-system
  tests removed with their systems)

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
