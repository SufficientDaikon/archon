# Platform Guide

## Supported Platforms

OMNISKILL supports 5 AI coding assistant platforms through adapters.

## Claude Code

**Target**: `~/.claude/skills/`
**Format**: Each skill becomes a `SKILL.md` file in a skill directory.

```bash
python scripts/install.py --platform claude-code
```

## GitHub Copilot CLI

**Target**: `~/.copilot/skills/`
**Format**: Each skill becomes a `SKILL.md` file with optional front-matter.

```bash
python scripts/install.py --platform copilot-cli
```

## Cursor

**Target**: `.cursor/rules/` (project-level) or global rules
**Format**: Each skill becomes a `.mdc` rule file.

```bash
python scripts/install.py --platform cursor
```

## Windsurf

**Target**: `.windsurfrules` or rules directory
**Format**: Skills are compiled into rule format.

```bash
python scripts/install.py --platform windsurf
```

## Antigravity

**Target**: `.antigravity/skills/`
**Format**: Each skill becomes a skill file in the expected format.

```bash
python scripts/install.py --platform antigravity
```

## Multi-Platform Install

```bash
# Auto-detect all installed platforms
python scripts/install.py

# Install for specific platforms
python scripts/install.py --platform claude-code --platform cursor
```

## Platform Overrides

Skills can have platform-specific behavior via `overrides/`:

```
skills/my-skill/overrides/
├── cursor.md       # Cursor-specific additions
└── windsurf.md     # Windsurf-specific additions
```

Overrides are merged with the base `SKILL.md` during adapter transformation.
