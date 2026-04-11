# Platform Guide

## Supported Platform

Archon targets **Claude Code** as its sole platform.

## Claude Code

**Target**: `~/.claude/skills/`
**Format**: Each skill becomes a `SKILL.md` file in a skill directory.

### Installation

```bash
python scripts/install.py
```

### How It Works

1. On `archon init`, the CLI confirms your `~/.claude/` directory exists.
2. Configuration is saved to `~/.archon/config.yaml`.
3. On `archon install`, skills are deployed directly to `~/.claude/skills/`.
4. No adapter transformation is needed -- skills are authored natively for Claude Code.

### Verify

```bash
archon doctor
```

## SDK as an Alternative

For programmatic integration, use the Python SDK instead of CLI scripts:

```python
from sdk.archon import Archon

os = Archon()

# Install skills
os.install(bundle="web-dev-kit")

# Validate all artifacts
errors = os.validate()

# Health check
report = os.health_check()
```
