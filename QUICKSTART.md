# OMNISKILL Quick Start Guide

## Installation & Setup

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install pyyaml
```

### Step 1: Detect Your Platforms

```bash
python scripts/install.py --detect
```

This will show which AI coding platforms are installed on your system.

### Step 2: Validate Repository

```bash
# Validate all skills and bundles
python scripts/validate.py --all

# Check for conflicts
python scripts/doctor.py
```

### Step 3: Install Skills

```bash
# Install all skills to all detected platforms
python scripts/install.py --all

# OR install to specific platform
python scripts/install.py --platform copilot-cli --all

# OR install specific skill
python scripts/install.py --skill godot-best-practices

# OR install specific bundle
python scripts/install.py --bundle godot-kit
```

---

## Common Commands

### Health Check

```bash
# Full diagnostic
python scripts/doctor.py

# Check platforms only
python scripts/doctor.py --platforms

# Check for conflicts
python scripts/doctor.py --conflicts
```

### Validation

```bash
# Validate everything
python scripts/validate.py --all

# Validate specific skill
python scripts/validate.py skills/godot-gdscript

# Check for duplicate triggers
python scripts/validate.py --check-triggers
```

### Updates

```bash
# Check for updates
python scripts/update.py --check

# Apply all updates
python scripts/update.py --apply

# Update specific skill
python scripts/update.py --apply godot-gdscript

# Rollback if something breaks
python scripts/update.py --rollback godot-gdscript
```

### Migration (from legacy formats)

```bash
# Migrate single skill
python scripts/migrate.py legacy-skill/ --output-dir migrated/

# Batch migrate
python scripts/migrate.py --auto-detect old-skills-dir/
```

---

## Supported Platforms

| Platform    | Installation Location  | Type    |
| ----------- | ---------------------- | ------- |
| Copilot CLI | `~/.copilot/skills/`   | Global  |
| Claude Code | `~/.claude/skills/`    | Global  |
| Cursor      | `.cursor/rules/*.mdc`  | Project |
| Windsurf    | `.windsurfrules`       | Project |
| Antigravity | `.antigravity/skills/` | Project |

**Global platforms:** Installed once per user, available in all projects.
**Project platforms:** Installed per project directory.

---

## Troubleshooting

### Windows Encoding Issues

If you see Unicode errors, set UTF-8 encoding:

**PowerShell:**

```powershell
$env:PYTHONIOENCODING="utf-8"
python scripts/doctor.py
```

**Command Prompt:**

```cmd
set PYTHONIOENCODING=utf-8
python scripts/doctor.py
```

### "No platforms detected"

- Install at least one supported AI coding platform
- For project platforms (Cursor/Windsurf), run from your project root
- Check directory permissions

### "Skill not found"

- Verify skill exists: `ls skills/`
- Check exact spelling (case-sensitive)
- Run `python scripts/doctor.py` to list available skills

### Installation fails

- Check write permissions on platform directories
- Verify skill supports the target platform (check manifest.yaml)
- Run with Python verbose mode: `python -v scripts/install.py ...`

---

## Directory Structure

```
omniskill/
├── skills/              # Individual skills
│   ├── godot-gdscript/
│   │   ├── SKILL.md
│   │   ├── manifest.yaml
│   │   └── examples/
│   └── ...
├── bundles/             # Skill bundles (kits)
│   ├── godot-kit/
│   │   ├── bundle.yaml
│   │   └── meta-skill/
│   └── ...
├── agents/              # Formal agents
├── pipelines/           # Multi-agent workflows
├── adapters/            # Platform adapters
├── scripts/             # Operational tools
└── schemas/             # Validation schemas
```

---

## What's Next?

### Create Your Own Skill

1. Copy a template: `cp -r skills/template skills/my-skill`
2. Edit `SKILL.md` and `manifest.yaml`
3. Validate: `python scripts/validate.py skills/my-skill`
4. Install: `python scripts/install.py --skill my-skill`

### Explore Bundles

```bash
# See available bundles
ls bundles/

# Install a full kit
python scripts/install.py --bundle godot-kit
```

### Keep Skills Updated

```bash
# Check for updates weekly
python scripts/update.py --check

# Apply updates
python scripts/update.py --apply
```

---

## Getting Help

- **Documentation:** See `docs/` directory
- **Scripts Help:** Run any script with `--help` flag
- **Adapters:** See `adapters/README.md`
- **Schemas:** See `schemas/` for validation rules

---

## Status

✅ **Phase 1-6 Complete**

- Skills, bundles, agents, pipelines ✅
- Cross-platform adapters ✅
- Core operational scripts ✅

🚧 **Coming Soon:**

- Phase 7: Testing & CI/CD
- Phase 8: Web UI & marketplace
- Phase 9: Analytics & telemetry

---

**OMNISKILL** - Write once, run everywhere. 🚀
