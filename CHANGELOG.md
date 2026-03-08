# Changelog

All notable changes to OMNISKILL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
