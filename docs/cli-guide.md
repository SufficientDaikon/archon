# CLI Guide for Archon

Complete command-line reference for the `archon` CLI — installation, commands, configuration, and workflows.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Global Flags](#global-flags)
- [Command Reference](#command-reference)
  - [archon init](#archon-init)
  - [archon install](#archon-install)
  - [archon uninstall](#archon-uninstall)
  - [archon doctor](#archon-doctor)
  - [archon validate](#archon-validate)
  - [archon list](#archon-list)
  - [archon search](#archon-search)
  - [archon info](#archon-info)
  - [archon pipeline](#archon-pipeline)
  - [archon update](#archon-update)
  - [archon migrate](#archon-migrate)
  - [archon admin](#archon-admin)
  - [archon config](#archon-config)
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
pip install archon
```

### From Source

```bash
git clone https://github.com/SufficientDaikon/archon.git
cd archon
pip install -e .
```

### Verify Installation

```bash
archon --version
# archon v1.0.0
```

---

## Quick Start

Get up and running in 60 seconds:

```bash
# 1. Initialize Archon in your environment
archon init

# 2. Install the default bundle
archon install --all

# 3. Verify everything is healthy
archon doctor
```

That's it -- your Claude Code environment now has access to all Archon skills, agents, and pipelines.

---

## Global Flags

These flags work with every command:

| Flag        | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `--json`    | Output results as structured JSON (see [JSON Output](#json-output)) |
| `--quiet`   | Suppress all non-essential output; only show errors                 |
| `--verbose` | Show detailed debug-level output                                    |
| `--version` | Print the Archon version and exit                                |

**Examples:**

```bash
# Machine-readable output for CI pipelines
archon doctor --json

# Silent operation for scripts
archon install --all --quiet

# Debug a failing install
archon install --skill react-best-practices --verbose

# Check the installed version
archon --version
```

---

## Command Reference

### `archon init`

Initialize Archon in the current environment. Creates the `~/.archon/` config directory, detects installed platforms, and writes a default `config.yaml`.

**Usage:**

```bash
archon init [--platform <name>]
```

**Options:**

| Option              | Description                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `--platform <name>` | Specify the target platform (default: `claude-code`) |

**Example:**

```bash
$ archon init
✓ Detected platform: claude-code
✓ Created ~/.archon/config.yaml
✓ Archon initialized successfully
```

---

### `archon install`

Install skills, bundles, or everything to one or more platforms.

**Usage:**

```bash
archon install [--skill <name>] [--bundle <name>] [--all] [--platform <name>] [--force]
```

**Options:**

| Option              | Description                                        |
| ------------------- | -------------------------------------------------- |
| `--skill <name>`    | Install a single skill by name                     |
| `--bundle <name>`   | Install a bundle (domain kit) by name              |
| `--all`             | Install all available skills and bundles           |
| `--platform <name>` | Target platform (default: `claude-code`) |
| `--force`           | Overwrite existing installations without prompting |

**Examples:**

```bash
# Install a single skill
$ archon install --skill react-best-practices
✓ Installed react-best-practices to claude-code
Installed 1 skill

# Install a bundle
$ archon install --bundle web-dev-kit
✓ Installing web-dev-kit (5 skills + 1 meta-skill)...
  ✓ frontend-design
  ✓ react-best-practices
  ✓ vercel-react-best-practices
  ✓ web-design-guidelines
  ✓ backend-development
  ✓ web-fullstack-expert (meta-skill)
Installed 6 skills

# Install everything
$ archon install --all
✓ Installing 83 skills, 13 bundles...
Done in 4.2s

# Force reinstall a skill
$ archon install --skill godot-best-practices --force
✓ Installed godot-best-practices to claude-code (overwritten)
```

---

### `archon uninstall`

Remove an installed skill or bundle from one or more platforms.

**Usage:**

```bash
archon uninstall <name> [--platform <name>] [--force]
```

**Options:**

| Option              | Description                                             |
| ------------------- | ------------------------------------------------------- |
| `<name>`            | **(Required)** Name of the skill or bundle to uninstall |
| `--platform <name>` | Uninstall from a specific platform (default: `claude-code`) |
| `--force`           | Skip confirmation prompt                                |

**Example:**

```bash
$ archon uninstall godot-best-practices
⚠ This will remove godot-best-practices. Continue? [y/N] y
✓ Removed godot-best-practices from claude-code
Uninstalled 1 skill

$ archon uninstall web-dev-kit --force
✓ Removed web-dev-kit (6 skills) from claude-code
```

---

### `archon doctor`

Run a comprehensive health check on your Archon installation. Checks config files, platform connections, skill integrity, and version status.

**Usage:**

```bash
archon doctor [--json]
```

**Options:**

| Option   | Description                       |
| -------- | --------------------------------- |
| `--json` | Output results as structured JSON |

**Example:**

```bash
$ archon doctor
Archon Doctor v1.0.0
──────────────────────────────

Configuration
  ✓ Config file exists          ~/.archon/config.yaml
  ✓ Config file valid           YAML syntax OK

Platforms
  ✓ claude-code                 ~/.claude/AGENTS.md found

Skills
  ✓ 83 skills installed         0 conflicts detected
  ✓ 13 bundles installed        All meta-skills present
  ✓ All manifests valid         0 schema errors

Version
  ✓ Up to date                  v1.0.0 (latest)

──────────────────────────────
Result: 10 passed, 0 skipped, 0 failed
```

---

### `archon validate`

Validate a skill, bundle, agent, or pipeline against the Archon schema. Use this before committing or opening a PR to catch errors early.

**Usage:**

```bash
archon validate [path] [--json]
```

**Options:**

| Option   | Description                                                             |
| -------- | ----------------------------------------------------------------------- |
| `[path]` | Path to a skill/bundle/agent/pipeline directory (default: validate all) |
| `--json` | Output results as structured JSON                                       |

**Example:**

```bash
# Validate a specific skill
$ archon validate skills/my-new-skill
Validating skills/my-new-skill...
  ✓ manifest.yaml              Schema valid
  ✓ SKILL.md                   All required sections present
  ✓ Triggers                   No conflicts with existing skills
  ✓ Resources                  All referenced files exist
Result: PASS (4/4 checks)

# Validate everything
$ archon validate
Validating 83 skills, 13 bundles, 10 agents, 7 pipelines...
  ✓ 83 skills valid
  ✓ 13 bundles valid
  ✓ 10 agents valid
  ✓ 7 pipelines valid
Result: PASS (113/113 checks)

# Validate with JSON output for CI
$ archon validate skills/broken-skill --json
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

### `archon list`

List installed skills, agents, bundles, or pipelines.

**Usage:**

```bash
archon list [skills|agents|bundles|pipelines] [--json]
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
$ archon list skills
Archon Skills (83 installed)
───────────────────────────────
  backend-development          v1.0.0   [web, api, database]
  capacitor-best-practices     v1.0.0   [mobile, capacitor]
  django-expert                v1.0.0   [python, django]
  frontend-design              v1.0.0   [web, ui, css]
  godot-best-practices         v1.0.0   [gamedev, godot]
  react-best-practices         v1.0.0   [web, react]
  ...

$ archon list bundles
Archon Bundles (13 installed)
───────────────────────────────
  godot-kit                    5 skills    Godot game development
  web-dev-kit                  5 skills    Full-stack web development
  django-kit                   4 skills    Django web framework
  mobile-kit                   3 skills    Mobile app development
  ux-design-kit                6 skills    UX/UI design pipeline
  devops-kit                   3 skills    DevOps and infrastructure

$ archon list agents --json
{
  "status": "ok",
  "command": "list",
  "version": "1.0.0",
  "data": {
    "type": "agents",
    "count": 10,
    "items": [
      { "name": "spec-writer", "version": "1.0.0", "description": "Transforms plans into specs" },
      { "name": "implementer", "version": "1.0.0", "description": "Implements from specifications" }
    ]
  },
  "errors": []
}
```

---

### `archon search`

Search the Archon registry for skills, bundles, agents, or pipelines by keyword.

**Usage:**

```bash
archon search <query> [--json]
```

**Options:**

| Option    | Description                                                                |
| --------- | -------------------------------------------------------------------------- |
| `<query>` | **(Required)** Search term — matches name, description, tags, and triggers |
| `--json`  | Output results as structured JSON                                          |

**Example:**

```bash
$ archon search react
Search results for "react" (4 matches)
───────────────────────────────────────
  react-best-practices         skill    React hooks, patterns, and optimization
  vercel-react-best-practices  skill    Next.js and React performance from Vercel
  frontend-design              skill    Production-grade frontend interfaces
  web-dev-kit                  bundle   Includes react-best-practices + 4 more

$ archon search "game dev"
Search results for "game dev" (3 matches)
─────────────────────────────────────────
  godot-best-practices         skill    Godot 4.x GDScript best practices
  godot-gdscript-patterns      skill    Master Godot 4 GDScript patterns
  godot-kit                    bundle   Complete Godot game development kit
```

---

### `archon info`

Show detailed information about a skill, bundle, agent, or pipeline.

**Usage:**

```bash
archon info <name> [--json]
```

**Options:**

| Option   | Description                                |
| -------- | ------------------------------------------ |
| `<name>` | **(Required)** Name of the item to inspect |
| `--json` | Output results as structured JSON          |

**Example:**

```bash
$ archon info react-best-practices
react-best-practices
━━━━━━━━━━━━━━━━━━━━
  Type:         skill
  Version:      1.0.0
  Author:       archon-team
  License:      MIT
  Platforms:    claude-code
  Tags:         web, react, hooks, performance
  Priority:     P2
  Description:  React development guidelines with hooks, component patterns,
                state management, and performance optimization.

  Triggers:
    Keywords:   "react component", "react hooks", "use state"
    Patterns:   "create * react *", "optimize react *"

  Dependencies: none
  Bundle:       web-dev-kit

  Installed:    Yes
```

---

### `archon pipeline`

Run or check the status of multi-agent pipelines.

**Usage:**

```bash
archon pipeline run <name> [--project <name>]
archon pipeline status [--project <name>]
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
$ archon pipeline run sdd --project my-feature
✓ Starting SDD pipeline for project "my-feature"
  Phase 1/3: spec-writer        ▶ Running...
  Phase 2/3: implementer        ○ Pending
  Phase 3/3: reviewer           ○ Pending

# Check pipeline status
$ archon pipeline status --project my-feature
Pipeline: sdd (my-feature)
──────────────────────────
  Phase 1/3: spec-writer        ✓ Complete    (2m 14s)
  Phase 2/3: implementer        ▶ Running     (1m 03s)
  Phase 3/3: reviewer           ○ Pending

$ archon pipeline status
Active Pipelines
────────────────
  sdd (my-feature)              Phase 2/3    implementer     Running
  ux-lifecycle (redesign)       Phase 5/7    ui-design       Running
```

---

### `archon update`

Check for and apply updates to Archon.

**Usage:**

```bash
archon update [--check]
```

**Options:**

| Option    | Description                                  |
| --------- | -------------------------------------------- |
| `--check` | Only check for updates without applying them |

**Example:**

```bash
# Check for updates
$ archon update --check
Current version: v1.0.0
Latest version:  v1.1.0
Update available! Run `archon update` to install.

# Apply the update
$ archon update
Updating Archon v1.0.0 → v1.1.0...
  ✓ Downloaded v1.1.0
  ✓ Updated CLI
  ✓ Migrated config (no changes needed)
  ✓ Re-validated installed skills
Update complete! Run `archon doctor` to verify.
```

---

### `archon migrate`

Migrate legacy Archon skill files (pre-v1.0) to the current format.

**Usage:**

```bash
archon migrate <path> [--in-place]
```

**Options:**

| Option       | Description                                                     |
| ------------ | --------------------------------------------------------------- |
| `<path>`     | **(Required)** Path to the skill or directory to migrate        |
| `--in-place` | Overwrite original files instead of creating `.migrated` copies |

**Example:**

```bash
# Preview migration (creates .migrated copies)
$ archon migrate skills/old-skill
Migrating skills/old-skill...
  ✓ manifest.yaml → manifest.yaml.migrated    Added 'platforms' field
  ✓ SKILL.md → SKILL.md.migrated              Added 'When to Use' section
Migration preview complete. Review .migrated files, then run with --in-place.

# Apply migration in place
$ archon migrate skills/old-skill --in-place
Migrating skills/old-skill (in-place)...
  ✓ manifest.yaml              Added 'platforms' field
  ✓ SKILL.md                   Added 'When to Use' section
Migration complete! Run `archon validate skills/old-skill` to verify.
```

---

### `archon admin`

Administrative utilities — sync knowledge sources, rebuild indexes, and manage the registry.

**Usage:**

```bash
archon admin
```

Running `archon admin` opens an interactive admin menu:

```bash
$ archon admin
Archon Admin
───────────────
  1. Sync knowledge sources
  2. Rebuild skill index
  3. Clear platform caches
  4. Export installation report
  5. Reset configuration

Select an option [1-5]:
```

> **Tip:** For non-interactive use, pipe a selection: `echo 1 | archon admin`

---

### `archon config`

Read or write Archon configuration values.

**Usage:**

```bash
archon config [key] [value] [--list]
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
$ archon config --list
home             = ~/.archon
platforms        = claude-code
default_bundle   = web-dev-kit
auto_update      = true
json_output      = false

# Read a single value
$ archon config platforms
claude-code

# Set a value
$ archon config auto_update false
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
archon validate || echo "Validation failed!"
```

---

## Configuration

### Config File

Archon stores configuration in `~/.archon/config.yaml`:

```yaml
# ~/.archon/config.yaml
home: ~/.archon
platforms:
  - claude-code
default_bundle: web-dev-kit
auto_update: true
json_output: false
log_level: info
```

### Environment Variables

Environment variables override config file values:

| Variable             | Description                                     | Default           |
| -------------------- | ----------------------------------------------- | ----------------- |
| `Archon_HOME`     | Override the Archon home directory           | `~/.archon`    |
| `Archon_PLATFORM` | Force a specific platform (skip auto-detection) | _(auto-detected)_ |

**Example:**

```bash
# Use a custom home directory
Archon_HOME=/opt/archon archon doctor

# Force a specific platform
Archon_PLATFORM=claude-code archon install --all
```

---

## Platform Detection

Archon targets Claude Code. On initialization it confirms your `~/.claude/` directory exists.

| Platform        | Detection Method                                  |
| --------------- | ------------------------------------------------- |
| **Claude Code** | Checks for `~/.claude/` directory and `AGENTS.md` |

### How It Works

1. On `archon init`, the CLI checks for the `~/.claude/` directory.
2. The platform is saved to `~/.archon/config.yaml`.
3. On `archon install`, skills are deployed directly to `~/.claude/skills/`.

### Override Detection

Use the `Archon_PLATFORM` environment variable if needed:

```bash
export Archon_PLATFORM=claude-code
archon install --all
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
    "platforms": ["claude-code"]
  },
  "errors": []
}
```

### Envelope Fields

| Field     | Type                            | Description                               |
| --------- | ------------------------------- | ----------------------------------------- |
| `status`  | `"ok"` \| `"fail"` \| `"error"` | Overall result                            |
| `command` | `string`                        | The command that was executed             |
| `version` | `string`                        | Archon CLI version                     |
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
archon --install-completion

# Then restart your shell or source the completion file
source ~/.bashrc   # bash
source ~/.zshrc    # zsh
```

After installation, you can tab-complete commands, options, skill names, and bundle names:

```bash
$ archon ins<TAB>
install

$ archon install --sk<TAB>
--skill

$ archon install --skill react<TAB>
react-best-practices
```

---

## Common Workflows

### Install a Bundle

```bash
archon install --bundle web-dev-kit
archon doctor
```

### Validate Before a PR

```bash
# Validate all skills, bundles, agents, and pipelines
archon validate
# Exit code 0 = all good, 2 = validation failure
```

### Check Installation Health

```bash
archon doctor --json | jq '.data.checks_failed'
# 0
```

### Search for Skills

```bash
archon search "django"
archon info django-expert
archon install --skill django-expert
```

### Run a Pipeline

```bash
archon pipeline run sdd --project new-feature
archon pipeline status --project new-feature
```

### Update Archon

```bash
archon update --check
archon update
archon doctor
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
