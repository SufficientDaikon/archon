# Adapters

Cross-platform adapters that transform the universal OMNISKILL format into platform-native skill files.

## Supported Platforms

| Platform           | Adapter                      | Target Location        | Status         |
| ------------------ | ---------------------------- | ---------------------- | -------------- |
| Claude Code        | [claude-code/](claude-code/) | `~/.claude/skills/`    | 🔄 In Progress |
| GitHub Copilot CLI | [copilot-cli/](copilot-cli/) | `~/.copilot/skills/`   | 🔄 In Progress |
| Cursor             | [cursor/](cursor/)           | `.cursor/rules/`       | 🔄 In Progress |
| Windsurf           | [windsurf/](windsurf/)       | `.windsurfrules`       | 🔄 In Progress |
| Antigravity        | [antigravity/](antigravity/) | `.antigravity/skills/` | 🔄 In Progress |

## How Adapters Work

1. Read the skill's `SKILL.md` and `manifest.yaml`
2. Apply any platform-specific overrides from `overrides/`
3. Transform into the platform's native format
4. Write to the platform's expected location

## Adding a New Adapter

Create a new directory under `adapters/` with an adapter script that:

1. Accepts a skill path as input
2. Reads the universal format
3. Outputs the platform-native format
4. Writes to the correct location
