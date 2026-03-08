# Changelog

All notable changes to OMNISKILL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-08

### Added

- **Context Curator agent** (`agents/context-curator-agent/`) — Universal context management agent for multi-agent pipeline handoffs with validation, budget tracking, smart chunking, and dashboard generation
- **Context Curator skill** (`skills/context-curator/`) — Procedural skill with context brief templates, pipeline state JSON schema, filtering rules, compression strategies, and dashboard generation procedures
- Context Curator added to **sdd-kit** bundle (now 6 skills)
- Pipeline state persistence across sessions via JSON state files
- HTML pipeline progress dashboards (self-contained, print-friendly)
- Context budget awareness with token estimation and progressive compression

### Changed

- **sdd-pipeline** v1.1.0 — Added context-curator steps between spec-writer → implementer and implementer → reviewer transitions
- **ux-pipeline** v1.1.0 — Added context-curator steps between research → wireframe and wireframe → visual-design transitions
- **debug-pipeline** v1.1.0 — Added context-curator step between investigate → fix transition
- **skill-factory** v1.1.0 — Added context-curator step between specify → implement transition
- **full-product** v1.1.0 — Added context-curator steps between ux-design → specify, specify → implement, and implement → review transitions
- All curator steps use `on-failure: skip` for backward compatibility (pipelines work without curator)

## [0.1.0] - 2026-03-08

### Added

- Initial repository scaffolding and directory structure
- Universal skill format: `SKILL.md` + `manifest.yaml`
- Universal agent format: `AGENT.md` + `agent-manifest.yaml`
- YAML validation schemas for skills, bundles, agents, and pipelines
- Skill template (`skills/_template/`) with full directory structure
- Agent template (`agents/_template/`) with full directory structure
- Root manifest (`omniskill.yaml`) registering all components
- 8 bundle definitions: godot-kit, web-dev-kit, ux-design-kit, django-kit, sdd-kit, testing-kit, mobile-kit, meta-kit
- 5 pipeline definitions: sdd-pipeline, ux-pipeline, debug-pipeline, skill-factory, full-product
- Cross-platform adapter stubs for: Claude Code, Copilot CLI, Cursor, Windsurf, Antigravity
- Comprehensive README with catalog and quick-start guide
- Contributing guidelines
- MIT License
