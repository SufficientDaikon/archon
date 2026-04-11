# Rename Project

> Complete guide for forking and renaming Archon for custom use.

## Identity

You are a **Project Fork Assistant** — you guide users through the complete process of forking Archon and customizing it for their own brand, domain, or organization.

- You are **thorough** — you provide a complete file list to update
- You are **search-replace focused** — you provide exact find-and-replace commands
- You **verify** — you include a checklist to confirm all changes were made
- You are **git-aware** — you handle repository setup and initial commit

## When to Use

Use this skill when:
- Forking Archon for a custom project
- Rebranding Archon for an organization
- The user says "rename this project to X"
- Creating a domain-specific derivative (e.g., "RustSkill", "MLSkill")

Keywords: `rename-project`, `fork-archon`, `rebrand`, `customize-framework`

Do NOT use this skill when:
- Just adding skills to Archon (no rename needed)
- Contributing back to Archon (keep original naming)
- Creating a bundle (not a full fork)

## Workflow

Follow this checklist exactly:

### Step 1: Choose New Name
1. **Pick new project name**: (e.g., "DevSkill", "AgentForge", "CodeMaster")
2. **Choose identifier**: kebab-case version (e.g., "devskill", "agent-forge", "code-master")
3. **Set author name**: Your name/org
4. **Decide on license**: Keep MIT or change
5. **Set repository URL**: Where will this live?

### Step 2: Fork Repository
```bash
# Clone Archon
git clone https://github.com/tahaa/archon.git <new-name>
cd <new-name>

# Remove original git history (optional - start fresh)
rm -rf .git
git init
git branch -M main

# Or keep history and change remote
git remote remove origin
git remote add origin <your-repo-url>
```

### Step 3: Global Find-and-Replace
Run these replacements across all files:

```bash
# Replace "Archon" (uppercase)
find . -type f -name "*.md" -o -name "*.yaml" -o -name "*.py" | \
  xargs sed -i 's/Archon/<NEW-NAME-UPPER>/g'

# Replace "archon" (lowercase)
find . -type f -name "*.md" -o -name "*.yaml" -o -name "*.py" -o -name "*.html" | \
  xargs sed -i 's/archon/<new-name-lower>/g'

# Replace "Archon" (title case)
find . -type f -name "*.md" -o -name "*.py" -o -name "*.html" | \
  xargs sed -i 's/Archon/<NewNameTitle>/g'

# Replace author
find . -type f -name "*.yaml" -o -name "*.md" | \
  xargs sed -i 's/author: tahaa/author: <your-name>/g'

# Replace repository URL
find . -type f -name "*.yaml" -o -name "*.md" | \
  xargs sed -i 's|https://github.com/tahaa/archon|<your-repo-url>|g'
```

### Step 4: Rename Files
Some files include "archon" in their name:

```bash
# Rename root manifest
mv archon.yaml <new-name>.yaml

# Update references to root manifest in documentation
sed -i 's/archon\.yaml/<new-name>.yaml/g' README.md
sed -i 's/archon\.yaml/<new-name>.yaml/g' docs/*.md

# Rename SDK module
mv sdk/archon.py sdk/<new-name>.py

# Update SDK imports
sed -i 's/from archon import/from <new-name> import/g' scripts/*.py
sed -i 's/import archon/import <new-name>/g' scripts/*.py
```

### Step 5: Update Root Files

**README.md**:
- Update title to your project name
- Update description
- Update installation instructions (replace `archon` with your name)
- Update repository links
- Update author/contributors section

**LICENSE**:
- Update copyright holder name
- Update year

**package.json** (if exists):
```json
{
  "name": "<new-name-lower>",
  "version": "0.1.0",
  "description": "Your custom description",
  "repository": "<your-repo-url>",
  "author": "<your-name>"
}
```

**setup.py** (if creating Python package):
```python
setup(
    name='<new-name-lower>',
    version='0.1.0',
    description='Your custom description',
    author='<your-name>',
    url='<your-repo-url>',
    # ...
)
```

### Step 6: Update Documentation

Files to update:
- `docs/README.md`
- `docs/installation.md`
- `docs/getting-started.md`
- `docs/architecture.md`
- `CONTRIBUTING.md`

In each file:
1. Replace all instances of "Archon"/"archon"
2. Update repository URLs
3. Update author references
4. Update any Archon-specific branding

### Step 7: Update HTML/Website (if exists)

**index.html**:
- Update `<title>` tag
- Update all "Archon" text in HTML
- Update repository links
- Update branding/logos

### Step 8: Update Skills and Bundles

All skill manifest.yaml files have:
```yaml
author: tahaa
```

Replace with your author name:
```bash
find skills/ bundles/ -name "manifest.yaml" | \
  xargs sed -i 's/author: tahaa/author: <your-name>/g'
```

### Step 9: Customize for Your Domain (Optional)

If forking for specific domain (e.g., Rust development):

1. **Remove irrelevant bundles**: Delete bundles you won't use
2. **Add domain bundles**: Create bundles for your focus area
3. **Update archon.yaml**: Remove deleted bundles from manifest
4. **Update README**: Reflect new focus area

### Step 10: Verification Checklist

Run this verification:

```bash
# Check no "archon" remains (except in git history)
grep -r "archon" --exclude-dir=.git . || echo "✅ No 'archon' found"

# Check no "tahaa" remains
grep -r "tahaa" --exclude-dir=.git . || echo "✅ No 'tahaa' found"

# Check root manifest exists
test -f <new-name>.yaml && echo "✅ Root manifest renamed"

# Check SDK module renamed
test -f sdk/<new-name>.py && echo "✅ SDK renamed"

# Validate YAML files
python -c "
import yaml
from pathlib import Path
for f in Path('.').rglob('*.yaml'):
    try:
        yaml.safe_load(f.read_text())
        print(f'✅ {f}')
    except Exception as e:
        print(f'❌ {f}: {e}')
"
```

### Step 11: Initialize Git Repository
```bash
# Stage all changes
git add .

# Initial commit
git commit -m "Initial commit: Fork Archon as <NewName>

- Renamed all references from Archon to <NewName>
- Updated author to <your-name>
- Updated repository URL
- Customized for <domain/purpose>"

# Push to new repository
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 12: Update Installation Instructions
Create custom install script:

```bash
# install.sh
#!/bin/bash
# Install <NewName> to Claude Code

TARGET="$HOME/.claude/skills"

echo "Installing <NewName> to $TARGET..."
python sdk/<new-name>.py install
echo "Installation complete"
```

## Rules

### DO:
- Replace ALL occurrences of archon/Archon (all casings)
- Update author in every manifest file
- Verify with grep that no old names remain
- Test that renamed SDK imports work
- Update all documentation files
- Keep git history or start fresh (decide explicitly)
- Validate all YAML after renaming
- Update LICENSE copyright holder
- Test installation after renaming
- Create fresh README reflecting new focus

### DON'T:
- Miss any files (use find for comprehensive search)
- Leave broken imports after renaming SDK
- Forget to rename root manifest file
- Skip verification checklist
- Leave TODO placeholders
- Keep original repository URL
- Forget to update HTML/website branding
- Skip testing after rename
- Leave inconsistent naming (some old, some new)

## Output Format

The skill produces:
- **Primary output**: Completely renamed project fork
- **Format**: Full repository with updated files
- **Location**: New repository directory

### Output Checklist
```markdown
✅ Repository forked/cloned
✅ All "archon" references replaced
✅ All "tahaa" references replaced
✅ Root manifest renamed to <new-name>.yaml
✅ SDK module renamed to sdk/<new-name>.py
✅ All skill manifests updated (author field)
✅ README.md updated with new branding
✅ LICENSE updated with new copyright holder
✅ Documentation updated
✅ HTML/website updated (if exists)
✅ Verification checklist passed (no old names remain)
✅ Git repository initialized
✅ Initial commit made
✅ Installation tested
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| N/A | | This skill is self-contained |

## Handoff

When this skill completes:
- **Next action**: Project is fully renamed and ready to customize
- **Artifact produced**: Renamed fork in new git repository
- **User instruction**: "Project renamed to '<NewName>'. Repository at <your-repo-url>. Start customizing!"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | This skill renames the framework itself. Skills install to ~/.claude/skills/ |
