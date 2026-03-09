# CLI Guide for OMNISKILL

Complete command-line reference for the `omniskill` CLI — installation, commands, configuration, and workflows.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Global Flags](#global-flags)
- [Command Reference](#command-reference)
  - [omniskill init](#omniskill-init)
  - [omniskill install](#omniskill-install)
  - [omniskill uninstall](#omniskill-uninstall)
  - [omniskill doctor](#omniskill-doctor)
  - [omniskill validate](#omniskill-validate)
  - [omniskill list](#omniskill-list)
  - [omniskill search](#omniskill-search)
  - [omniskill info](#omniskill-info)
  - [omniskill pipeline](#omniskill-pipeline)
  - [omniskill update](#omniskill-update)
  - [omniskill migrate](#omniskill-migrate)
  - [omniskill admin](#omniskill-admin)
  - [omniskill config](#omniskill-config)
- [Exit Codes](#exit-codes)
- [Configuration](#configuration)
- [Platform Detection](#platform-detection)
- [JSON Output](#json-output)
- [Shell Completions](#shell-completions)
- [Common Workflows](#common-workflows)
- [Next Steps](#next-steps)

---

## Installation

### From PyPI (Recommended)

```bash
pip install omniskill
```

### From Source

```bash
git clone https://github.com/SufficientDaikon/omniskill.git
cd omniskill
pip install -e .
```

### Verify Installation

```bash
omniskill --version
# omniskill v1.0.0
```

---

## Quick Start

Get up and running in 60 seconds:

```bash
# 1. Initialize OMNISKILL in your environment
omniskill init

# 2. Install the default bundle for your detected platforms
omniskill install --all

# 3. Verify everything is healthy
omniskill doctor
```

That's it — your AI coding assistants now have access to all OMNISKILL skills, agents, and pipelines.

---

## Global Flags

These flags work with every command:

| Flag        | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `--json`    | Output results as structured JSON (see [JSON Output](#json-output)) |
| `--quiet`   | Suppress all non-essential output; only show errors                 |
| `--verbose` | Show detailed debug-level output                                    |
| `--version` | Print the OMNISKILL version and exit                                |

**Examples:**

```bash
# Machine-readable output for CI pipelines
omniskill doctor --json

# Silent operation for scripts
omniskill install --all --quiet

# Debug a failing install
omniskill install --skill react-best-practices --verbose

# Check the installed version
omniskill --version
```

---

## Command Reference

### `omniskill init`

Initialize OMNISKILL in the current environment. Creates the `~/.omniskill/` config directory, detects installed platforms, and writes a default `config.yaml`.

**Usage:**

```bash
omniskill init [--platform <name>]
```

**Options:**

| Option              | Description                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `--platform <name>` | Skip auto-detection and initialize for a specific platform (`claude-code`, `copilot-cli`, `cursor`, `windsurf`, `antigravity`) |

**Example:**

```bash
$ omniskill init
✓ Detected platforms: claude-code, copilot-cli, cursor
✓ Created ~/.omniskill/config.yaml
✓ OMNISKILL initialized successfully

$ omniskill init --platform cursor
✓ Initialized for platform: cursor
✓ Created ~/.omniskill/config.yaml
```

---

### `omniskill install`

Install skills, bundles, or everything to one or more platforms.

**Usage:**

```bash
omniskill install [--skill <name>] [--bundle <name>] [--all] [--platform <name>] [--force]
```

**Options:**

| Option              | Description                                        |
| ------------------- | -------------------------------------------------- |
| `--skill <name>`    | Install a single skill by name                     |
| `--bundle <name>`   | Install a bundle (domain kit) by name              |
| `--all`             | Install all available skills and bundles           |
| `--platform <name>` | Target a specific platform (default: all detected) |
| `--force`           | Overwrite existing installations without prompting |

**Examples:**

```bash
# Install a single skill
$ omniskill install --skill react-best-practices
✓ Installed react-best-practices to claude-code
✓ Installed react-best-practices to copilot-cli
✓ Installed react-best-practices to cursor
Installed 1 skill to 3 platforms

# Install a bundle
$ omniskill install --bundle web-dev-kit
✓ Installing web-dev-kit (5 skills + 1 meta-skill)...
  ✓ frontend-design
  ✓ react-best-practices
  ✓ vercel-react-best-practices
  ✓ web-design-guidelines
  ✓ backend-development
  ✓ web-fullstack-expert (meta-skill)
Installed 6 skills to 3 platforms

# Install everything
$ omniskill install --all
✓ Installing 42 skills, 6 bundles to 3 platforms...
Done in 4.2s

# Force reinstall to a specific platform
$ omniskill install --skill godot-best-practices --platform cursor --force
✓ Installed godot-best-practices to cursor (overwritten)
```

---

### `omniskill uninstall`

Remove an installed skill or bundle from one or more platforms.

**Usage:**

```bash
omniskill uninstall <name> [--platform <name>] [--force]
```

**Options:**

| Option              | Description                                             |
| ------------------- | ------------------------------------------------------- |
| `<name>`            | **(Required)** Name of the skill or bundle to uninstall |
| `--platform <name>` | Uninstall from a specific platform only (default: all)  |
| `--force`           | Skip confirmation prompt                                |

**Example:**

```bash
$ omniskill uninstall godot-best-practices
⚠ This will remove godot-best-practices from 3 platforms. Continue? [y/N] y
✓ Removed godot-best-practices from claude-code
✓ Removed godot-best-practices from copilot-cli
✓ Removed godot-best-practices from cursor
Uninstalled 1 skill from 3 platforms

$ omniskill uninstall web-dev-kit --platform cursor --force
✓ Removed web-dev-kit (6 skills) from cursor
```

---

### `omniskill doctor`

Run a comprehensive health check on your OMNISKILL installation. Checks config files, platform connections, skill integrity, and version status.

**Usage:**

```bash
omniskill doctor [--json]
```

**Options:**

| Option   | Description                       |
| -------- | --------------------------------- |
| `--json` | Output results as structured JSON |

**Example:**

```bash
$ omniskill doctor
OMNISKILL Doctor v1.0.0
──────────────────────────────

Configuration
  ✓ Config file exists          ~/.omniskill/config.yaml
  ✓ Config file valid           YAML syntax OK

Platforms
  ✓ claude-code                 ~/.claude/AGENTS.md found
  ✓ copilot-cli                 ~/.copilot/ found
  ✓ cursor                      ~/.cursor/rules/ found
  ✗ windsurf                    Not detected
  ✗ antigravity                 Not detected

Skills
  ✓ 42 skills installed         0 conflicts detected
  ✓ 6 bundles installed         All meta-skills present
  ✓ All manifests valid         0 schema errors

Version
  ✓ Up to date                  v1.0.0 (latest)

──────────────────────────────
Result: 11 passed, 2 skipped, 0 failed
```

---

### `omniskill validate`

Validate a skill, bundle, agent, or pipeline against the OMNISKILL schema. Use this before committing or opening a PR to catch errors early.

**Usage:**

```bash
omniskill validate [path] [--json]
```

**Options:**

| Option   | Description                                                             |
| -------- | ----------------------------------------------------------------------- |
| `[path]` | Path to a skill/bundle/agent/pipeline directory (default: validate all) |
| `--json` | Output results as structured JSON                                       |

**Example:**

```bash
# Validate a specific skill
$ omniskill validate skills/my-new-skill
Validating skills/my-new-skill...
  ✓ manifest.yaml              Schema valid
  ✓ SKILL.md                   All required sections present
  ✓ Triggers                   No conflicts with existing skills
  ✓ Resources                  All referenced files exist
Result: PASS (4/4 checks)

# Validate everything
$ omniskill validate
Validating 42 skills, 6 bundles, 8 agents, 4 pipelines...
  ✓ 42 skills valid
  ✓ 6 bundles valid
  ✓ 8 agents valid
  ✓ 4 pipelines valid
Result: PASS (60/60 checks)

# Validate with JSON output for CI
$ omniskill validate skills/broken-skill --json
{
  "status": "fail",
  "command": "validate",
  "version": "1.0.0",
  "data": {
    "path": "skills/broken-skill",
    "checks": 4,
    "passed": 2,
    "failed": 2,
    "errors": [
      "manifest.yaml: missing required field 'description'",
      "SKILL.md: missing section '## When to Use'"
    ]
  },
  "errors": []
}
```

---

### `omniskill list`

List installed skills, agents, bundles, or pipelines.

**Usage:**

```bash
omniskill list [skills|agents|bundles|pipelines] [--json]
```

**Options:**

| Option      | Description                                        |
| ----------- | -------------------------------------------------- |
| `skills`    | List only skills (default if no sub-command given) |
| `agents`    | List only agents                                   |
| `bundles`   | List only bundles                                  |
| `pipelines` | List only pipelines                                |
| `--json`    | Output results as structured JSON                  |

**Example:**

```bash
$ omniskill list skills
OMNISKILL Skills (42 installed)
───────────────────────────────
  backend-development          v1.0.0   [web, api, database]
  capacitor-best-practices     v1.0.0   [mobile, capacitor]
  django-expert                v1.0.0   [python, django]
  frontend-design              v1.0.0   [web, ui, css]
  godot-best-practices         v1.0.0   [gamedev, godot]
  react-best-practices         v1.0.0   [web, react]
  ...

$ omniskill list bundles
OMNISKILL Bundles (6 installed)
───────────────────────────────
  godot-kit                    5 skills    Godot game development
  web-dev-kit                  5 skills    Full-stack web development
  django-kit                   4 skills    Django web framework
  mobile-kit                   3 skills    Mobile app development
  ux-design-kit                6 skills    UX/UI design pipeline
  devops-kit                   3 skills    DevOps and infrastructure

$ omniskill list agents --json
{
  "status": "ok",
  "command": "list",
  "version": "1.0.0",
  "data": {
    "type": "agents",
    "count": 8,
    "items": [
      { "name": "spec-writer", "version": "1.0.0", "description": "Transforms plans into specs" },
      { "name": "implementer", "version": "1.0.0", "description": "Implements from specifications" }
    ]
  },
  "errors": []
}
```

---

### `omniskill search`

Search the OMNISKILL registry for skills, bundles, agents, or pipelines by keyword.

**Usage:**

```bash
omniskill search <query> [--json]
```

**Options:**

| Option    | Description                                                                |
| --------- | -------------------------------------------------------------------------- |
| `<query>` | **(Required)** Search term — matches name, description, tags, and triggers |
| `--json`  | Output results as structured JSON                                          |

**Example:**

```bash
$ omniskill search react
Search results for "react" (4 matches)
───────────────────────────────────────
  react-best-practices         skill    React hooks, patterns, and optimization
  vercel-react-best-practices  skill    Next.js and React performance from Vercel
  frontend-design              skill    Production-grade frontend interfaces
  web-dev-kit                  bundle   Includes react-best-practices + 4 more

$ omniskill search "game dev"
Search results for "game dev" (3 matches)
─────────────────────────────────────────
  godot-best-practices         skill    Godot 4.x GDScript best practices
  godot-gdscript-patterns      skill    Master Godot 4 GDScript patterns
  godot-kit                    bundle   Complete Godot game development kit
```

---

### `omniskill info`

Show detailed information about a skill, bundle, agent, or pipeline.

**Usage:**

```bash
omniskill info <name> [--json]
```

**Options:**

| Option   | Description                                |
| -------- | ------------------------------------------ |
| `<name>` | **(Required)** Name of the item to inspect |
| `--json` | Output results as structured JSON          |

**Example:**

```bash
$ omniskill info react-best-practices
react-best-practices
━━━━━━━━━━━━━━━━━━━━
  Type:         skill
  Version:      1.0.0
  Author:       omniskill-team
  License:      MIT
  Platforms:    claude-code, copilot-cli, cursor, windsurf, antigravity
  Tags:         web, react, hooks, performance
  Priority:     P2
  Description:  React development guidelines with hooks, component patterns,
                state management, and performance optimization.

  Triggers:
    Keywords:   "react component", "react hooks", "use state"
    Patterns:   "create * react *", "optimize react *"

  Dependencies: none
  Bundle:       web-dev-kit

  Installed:    Yes (3 platforms)
```

---

### `omniskill pipeline`

Run or check the status of multi-agent pipelines.

**Usage:**

```bash
omniskill pipeline run <name> [--project <name>]
omniskill pipeline status [--project <name>]
```

**Sub-commands:**

| Sub-command  | Description                                    |
| ------------ | ---------------------------------------------- |
| `run <name>` | Start a pipeline by name                       |
| `status`     | Show the status of running/completed pipelines |

**Options:**

| Option             | Description                                    |
| ------------------ | ---------------------------------------------- |
| `--project <name>` | Associate the pipeline run with a project name |

**Example:**

```bash
# Run the SDD pipeline
$ omniskill pipeline run sdd --project my-feature
✓ Starting SDD pipeline for project "my-feature"
  Phase 1/3: spec-writer        ▶ Running...
  Phase 2/3: implementer        ○ Pending
  Phase 3/3: reviewer           ○ Pending

# Check pipeline status
$ omniskill pipeline status --project my-feature
Pipeline: sdd (my-feature)
──────────────────────────
  Phase 1/3: spec-writer        ✓ Complete    (2m 14s)
  Phase 2/3: implementer        ▶ Running     (1m 03s)
  Phase 3/3: reviewer           ○ Pending

$ omniskill pipeline status
Active Pipelines
────────────────
  sdd (my-feature)              Phase 2/3    implementer     Running
  ux-lifecycle (redesign)       Phase 5/7    ui-design       Running
```

---

### `omniskill update`

Check for and apply updates to OMNISKILL.

**Usage:**

```bash
omniskill update [--check]
```

**Options:**

| Option    | Description                                  |
| --------- | -------------------------------------------- |
| `--check` | Only check for updates without applying them |

**Example:**

```bash
# Check for updates
$ omniskill update --check
Current version: v1.0.0
Latest version:  v1.1.0
Update available! Run `omniskill update` to install.

# Apply the update
$ omniskill update
Updating OMNISKILL v1.0.0 → v1.1.0...
  ✓ Downloaded v1.1.0
  ✓ Updated CLI
  ✓ Migrated config (no changes needed)
  ✓ Re-validated installed skills
Update complete! Run `omniskill doctor` to verify.
```

---

### `omniskill migrate`

Migrate legacy OMNISKILL skill files (pre-v1.0) to the current format.

**Usage:**

```bash
omniskill migrate <path> [--in-place]
```

**Options:**

| Option       | Description                                                     |
| ------------ | --------------------------------------------------------------- |
| `<path>`     | **(Required)** Path to the skill or directory to migrate        |
| `--in-place` | Overwrite original files instead of creating `.migrated` copies |

**Example:**

```bash
# Preview migration (creates .migrated copies)
$ omniskill migrate skills/old-skill
Migrating skills/old-skill...
  ✓ manifest.yaml → manifest.yaml.migrated    Added 'platforms' field
  ✓ SKILL.md → SKILL.md.migrated              Added 'When to Use' section
Migration preview complete. Review .migrated files, then run with --in-place.

# Apply migration in place
$ omniskill migrate skills/old-skill --in-place
Migrating skills/old-skill (in-place)...
  ✓ manifest.yaml              Added 'platforms' field
  ✓ SKILL.md                   Added 'When to Use' section
Migration complete! Run `omniskill validate skills/old-skill` to verify.
```

---

### `omniskill admin`

Administrative utilities — sync knowledge sources, rebuild indexes, and manage the registry.

**Usage:**

```bash
omniskill admin
```

Running `omniskill admin` opens an interactive admin menu:

```bash
$ omniskill admin
OMNISKILL Admin
───────────────
  1. Sync knowledge sources
  2. Rebuild skill index
  3. Clear platform caches
  4. Export installation report
  5. Reset configuration

Select an option [1-5]:
```

> **Tip:** For non-interactive use, pipe a selection: `echo 1 | omniskill admin`

---

### `omniskill config`

Read or write OMNISKILL configuration values.

**Usage:**

```bash
omniskill config [key] [value] [--list]
```

**Options:**

| Option    | Description                                               |
| --------- | --------------------------------------------------------- |
| `[key]`   | Configuration key to read or set (dot-notation supported) |
| `[value]` | New value to assign to the key                            |
| `--list`  | Show all configuration key-value pairs                    |

**Example:**

```bash
# List all config values
$ omniskill config --list
home             = ~/.omniskill
platforms        = claude-code, copilot-cli, cursor
default_bundle   = web-dev-kit
auto_update      = true
json_output      = false

# Read a single value
$ omniskill config platforms
claude-code, copilot-cli, cursor

# Set a value
$ omniskill config auto_update false
✓ Set auto_update = false
```

---

## Exit Codes

| Code | Meaning                                                                              |
| ---- | ------------------------------------------------------------------------------------ |
| `0`  | **Success** — command completed without errors                                       |
| `1`  | **Error** — command failed (runtime error, missing dependency, etc.)                 |
| `2`  | **Validation failure** — one or more checks failed (used by `validate` and `doctor`) |

Use exit codes in CI/CD scripts:

```bash
omniskill validate || echo "Validation failed!"
```

---

## Configuration

### Config File

OMNISKILL stores configuration in `~/.omniskill/config.yaml`:

```yaml
# ~/.omniskill/config.yaml
home: ~/.omniskill
platforms:
  - claude-code
  - copilot-cli
  - cursor
default_bundle: web-dev-kit
auto_update: true
json_output: false
log_level: info
```

### Environment Variables

Environment variables override config file values:

| Variable             | Description                                     | Default           |
| -------------------- | ----------------------------------------------- | ----------------- |
| `OMNISKILL_HOME`     | Override the OMNISKILL home directory           | `~/.omniskill`    |
| `OMNISKILL_PLATFORM` | Force a specific platform (skip auto-detection) | _(auto-detected)_ |

**Example:**

```bash
# Use a custom home directory
OMNISKILL_HOME=/opt/omniskill omniskill doctor

# Force a specific platform
OMNISKILL_PLATFORM=cursor omniskill install --all
```

---

## Platform Detection

OMNISKILL auto-detects installed AI coding assistants by checking for platform-specific files and directories:

| Platform        | Detection Method                                              |
| --------------- | ------------------------------------------------------------- |
| **Claude Code** | Checks for `~/.claude/` directory and `AGENTS.md`             |
| **Copilot CLI** | Checks for `~/.copilot/` directory                            |
| **Cursor**      | Checks for `~/.cursor/rules/` directory                       |
| **Windsurf**    | Checks for `~/.windsurf/` or `~/.codeium/windsurf/` directory |
| **Antigravity** | Checks for `~/.antigravity/` directory                        |

### How It Works

1. On `omniskill init`, the CLI scans your system for each platform's indicator files.
2. Detected platforms are saved to `~/.omniskill/config.yaml`.
3. On `omniskill install`, skills are deployed to each detected platform using the appropriate adapter.
4. Each adapter knows how to transform a universal OMNISKILL skill into the platform's native format.

### Override Detection

Use `--platform` to target a specific platform:

```bash
omniskill install --all --platform claude-code
```

Or set the `OMNISKILL_PLATFORM` environment variable:

```bash
export OMNISKILL_PLATFORM=cursor
omniskill install --all
```

---

## JSON Output

When the `--json` flag is passed, all commands output a structured JSON envelope:

```json
{
  "status": "ok",
  "command": "doctor",
  "version": "1.0.0",
  "data": {
    "checks_passed": 11,
    "checks_failed": 0,
    "checks_skipped": 2,
    "platforms": ["claude-code", "copilot-cli", "cursor"]
  },
  "errors": []
}
```

### Envelope Fields

| Field     | Type                            | Description                               |
| --------- | ------------------------------- | ----------------------------------------- |
| `status`  | `"ok"` \| `"fail"` \| `"error"` | Overall result                            |
| `command` | `string`                        | The command that was executed             |
| `version` | `string`                        | OMNISKILL CLI version                     |
| `data`    | `object`                        | Command-specific payload                  |
| `errors`  | `array`                         | List of error messages (empty on success) |

### Error Envelope

On failure, the envelope looks like:

```json
{
  "status": "error",
  "command": "install",
  "version": "1.0.0",
  "data": null,
  "errors": ["Skill 'nonexistent-skill' not found in registry"]
}
```

---

## Shell Completions

Enable tab-completion for your shell:

```bash
# Install completions (auto-detects bash, zsh, fish, PowerShell)
omniskill --install-completion

# Then restart your shell or source the completion file
source ~/.bashrc   # bash
source ~/.zshrc    # zsh
```

After installation, you can tab-complete commands, options, skill names, and bundle names:

```bash
$ omniskill ins<TAB>
install

$ omniskill install --sk<TAB>
--skill

$ omniskill install --skill react<TAB>
react-best-practices
```

---

## Common Workflows

### Install a Bundle

```bash
omniskill install --bundle web-dev-kit
omniskill doctor
```

### Validate Before a PR

```bash
# Validate all skills, bundles, agents, and pipelines
omniskill validate
# Exit code 0 = all good, 2 = validation failure
```

### Check Installation Health

```bash
omniskill doctor --json | jq '.data.checks_failed'
# 0
```

### Search for Skills

```bash
omniskill search "django"
omniskill info django-expert
omniskill install --skill django-expert
```

### Run a Pipeline

```bash
omniskill pipeline run sdd --project new-feature
omniskill pipeline status --project new-feature
```

### Update OMNISKILL

```bash
omniskill update --check
omniskill update
omniskill doctor
```

---

## Next Steps

- **[Getting Started](getting-started.md)** — First-time setup and installation guide
- **[Creating Skills](creating-skills.md)** — Author your own custom skills
- **[Creating Bundles](creating-bundles.md)** — Package skills into installable domain kits
- **[Creating Agents](creating-agents.md)** — Define formal agent definitions
- **[Creating Pipelines](creating-pipelines.md)** — Build multi-agent workflows
- **[Platform Guide](platform-guide.md)** — Platform-specific setup and configuration
- **[Architecture](architecture.md)** — How the complexity router and knowledge system work
- **[FAQ](faq.md)** — Common questions and troubleshooting
