# Archon Scripts

Core operational scripts for managing the Archon framework.

## Overview

This directory contains Python scripts that provide the operational backbone for Archon:

- **install.py** - Install skills and bundles to platforms
- **validate.py** - Validate skills, bundles, and manifests
- **doctor.py** - Health checker and diagnostics
- **migrate.py** - Migrate skills from other formats
- **update.py** - Update manager for keeping skills current

---

## Scripts

### install.py

**Purpose:** Main installer for deploying skills and bundles to AI coding platforms.

**Features:**

- Auto-detects installed platforms (Copilot CLI, Claude Code, Cursor, Windsurf, Antigravity)
- Installs individual skills or entire bundles
- Supports platform-specific overrides
- Bulk installation with `--all` flag

**Usage:**

```bash
# Detect platforms
python scripts/install.py --detect

# Install all skills to all detected platforms
python scripts/install.py --all

# Install to specific platform
python scripts/install.py --platform copilot-cli --all

# Install specific skill
python scripts/install.py --skill godot-best-practices

# Install specific bundle
python scripts/install.py --bundle godot-kit
```

**Exit Codes:**

- `0` - Success
- `1` - Failure (no platforms, install errors)

---

### validate.py

**Purpose:** Validates skills, bundles, agents, and pipelines against schemas.

**Features:**

- Validates manifest.yaml against schema definitions
- Checks SKILL.md for required sections
- Detects duplicate triggers across skills
- Validates bundle dependencies
- Checks for circular dependencies
- Reports pass/fail with specific errors

**Usage:**

```bash
# Validate everything
python scripts/validate.py --all

# Validate all skills
python scripts/validate.py --skills

# Validate all bundles
python scripts/validate.py --bundles

# Validate specific skill
python scripts/validate.py skills/godot-gdscript

# Check for trigger conflicts
python scripts/validate.py --check-triggers
```

**Exit Codes:**

- `0` - All validations passed
- `1` - One or more validations failed

---

### doctor.py

**Purpose:** Health checker that diagnoses platform installations and identifies issues.

**Features:**

- Lists all detected platforms
- Shows installed skills per platform
- Checks for trigger conflicts
- Identifies broken references (missing skills in bundles)
- Calculates overall health score (0-100)
- Provides actionable recommendations

**Usage:**

```bash
# Full health check
python scripts/doctor.py

# List platforms only
python scripts/doctor.py --platforms

# Check conflicts only
python scripts/doctor.py --conflicts

# Check broken references only
python scripts/doctor.py --references
```

**Health Score:**

- 🟢 90-100: Excellent
- 🟡 70-89: Good
- 🟠 50-69: Fair
- 🔴 0-49: Poor

**Exit Codes:**

- `0` - Health score >= 50
- `1` - Health score < 50 or specific checks failed

---

### migrate.py

**Purpose:** Migrates skills from various formats to Archon format.

**Features:**

- Auto-detects skill format
- Supports multiple source formats:
  - Copilot CLI (SKILL.md)
  - Cursor (.mdc files)
  - Generic markdown
- Extracts metadata using heuristics
- Creates proper Archon structure (SKILL.md + manifest.yaml)
- Batch migration with `--auto-detect`

**Usage:**

```bash
# Migrate single skill
python scripts/migrate.py legacy-skill/ --output-dir migrated/

# Auto-detect and migrate all subdirectories
python scripts/migrate.py --auto-detect legacy-skills/

# Force specific format
python scripts/migrate.py old-skill/ --format cursor

# Specify output directory
python scripts/migrate.py skill/ --output-dir skills/
```

**Supported Formats:**

- `copilot-cli` - Copilot CLI SKILL.md format
- `cursor` - Cursor .mdc format with front-matter
- `generic-md` - Generic markdown files

**Exit Codes:**

- `0` - All migrations succeeded
- `1` - One or more migrations failed

---

### update.py

**Purpose:** Manages skill and bundle updates from the repository.

**Features:**

- Checks for available updates
- Compares installed vs. repository versions
- Applies updates with automatic backup
- Rollback support for failed updates
- Supports multiple platforms (Copilot CLI, Claude Code)

**Usage:**

```bash
# Check for available updates
python scripts/update.py --check

# Apply all updates
python scripts/update.py --apply

# Update specific skill
python scripts/update.py --apply godot-gdscript

# Rollback to previous version
python scripts/update.py --rollback godot-gdscript

# Specify platform
python scripts/update.py --check --platform claude-code
```

**Version Comparison:**
Uses semantic versioning (MAJOR.MINOR.PATCH) to determine if updates are available.

**Backup Location:**

- Copilot CLI: `~/.copilot/skills/.backups/`
- Claude Code: `~/.claude/skills/.backups/`

**Exit Codes:**

- `0` - Success
- `1` - Update or rollback failed

---

## Common Workflows

### Initial Setup

```bash
# 1. Validate all skills
python scripts/validate.py --all

# 2. Check system health
python scripts/doctor.py

# 3. Install skills to detected platforms
python scripts/install.py --all
```

### Adding a New Skill

```bash
# 1. Create skill in skills/ directory
# 2. Validate it
python scripts/validate.py skills/my-new-skill

# 3. Install it
python scripts/install.py --skill my-new-skill
```

### Maintaining Skills

```bash
# 1. Check for conflicts
python scripts/doctor.py --conflicts

# 2. Check for updates
python scripts/update.py --check

# 3. Apply updates
python scripts/update.py --apply
```

### Migrating Legacy Skills

```bash
# 1. Migrate from old format
python scripts/migrate.py --auto-detect legacy-skills/

# 2. Validate migrated skills
python scripts/validate.py --skills

# 3. Move to skills/ directory
mv migrated/* skills/

# 4. Install
python scripts/install.py --all
```

---

## Requirements

### Python Version

- Python 3.8 or higher

### Dependencies

```bash
pip install pyyaml
```

### System Requirements

- Write access to platform directories:
  - `~/.copilot/` (Copilot CLI)
  - `~/.claude/` (Claude Code)
  - `.cursor/` (Cursor, project-level)
  - `.windsurfrules` (Windsurf, project-level)
  - `.antigravity/` (Antigravity, project-level)

---

## Error Handling

All scripts follow these conventions:

1. **Exit Codes:**
   - `0` = Success
   - `1` = Failure

2. **Output Format:**
   - ✅ Success messages
   - ❌ Error messages
   - ⚠️ Warning messages
   - 🔍 Informational messages

3. **Error Recovery:**
   - `update.py` creates automatic backups
   - Failed operations are rolled back when possible
   - Detailed error messages for debugging

---

## Development

### Adding a New Script

1. Create `scripts/new-script.py`
2. Follow existing script structure:
   - Use argparse for CLI args
   - Include docstring with usage examples
   - Implement `main()` function
   - Use `if __name__ == "__main__"` block
3. Add to this README
4. Test with various edge cases

### Testing Scripts

```bash
# Test in a safe environment
# Create test directory
mkdir test-archon
cd test-archon

# Copy skills and scripts
cp -r ../skills .
cp -r ../scripts .

# Test validation
python scripts/validate.py --all

# Test installation (dry run by inspecting code)
# (Add --dry-run flag to scripts for safe testing)
```

---

## Troubleshooting

### "No platforms detected"

- Ensure at least one supported platform is installed
- For project-level platforms (Cursor, Windsurf), run from project root
- Check permissions on platform directories

### "Skill not found"

- Verify skill exists in `skills/` directory
- Check spelling of skill name
- Run `python scripts/doctor.py` to list available skills

### "Validation failed"

- Check manifest.yaml syntax (YAML format)
- Ensure all required fields are present
- Verify SKILL.md has required sections
- Run with verbose output for details

### "Update failed"

- Check for sufficient disk space
- Verify write permissions
- Review backup in `.backups/` directory
- Try rollback with `--rollback`

---

## See Also

- [Archon README](../README.md) - Framework overview
- [Adapters Documentation](../adapters/README.md) - Platform adapters
- [Schema Definitions](../schemas/) - Validation schemas
- [Skills Directory](../skills/) - Available skills
- [Bundles Directory](../bundles/) - Skill bundles
