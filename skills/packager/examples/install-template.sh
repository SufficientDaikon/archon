#!/bin/bash
# {{PACKAGE_NAME}} Installer — macOS/Linux
# Run: chmod +x install.sh && ./install.sh

set -e

COPILOT_DIR="$HOME/.copilot"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FORCE=false
DRY_RUN=false

# Parse flags
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --force) FORCE=true ;;
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║  {{PACKAGE_NAME}} Installer          ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Create directories
for dir in agents skills sdd/prompts sdd/templates sdd/specs sdd/reports; do
  mkdir -p "$COPILOT_DIR/$dir"
done

INSTALLED=0

# Install agents
if [ -d "$SCRIPT_DIR/agents" ]; then
  for file in "$SCRIPT_DIR/agents"/*.agent.md; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    dest="$COPILOT_DIR/agents/$name"
    if [ -f "$dest" ] && [ "$FORCE" = false ]; then
      echo "  ⚠  $name already exists (use --force to overwrite)"
    else
      echo "  ✅ Installing agent: $name"
      [ "$DRY_RUN" = false ] && cp "$file" "$dest"
      INSTALLED=$((INSTALLED + 1))
    fi
  done
fi

# Install skills
if [ -d "$SCRIPT_DIR/skills" ]; then
  for dir in "$SCRIPT_DIR/skills"/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    dest="$COPILOT_DIR/skills/$name"
    if [ -d "$dest" ] && [ "$FORCE" = false ]; then
      echo "  ⚠  Skill '$name' already exists (use --force to overwrite)"
    else
      echo "  ✅ Installing skill: $name"
      [ "$DRY_RUN" = false ] && cp -r "$dir" "$dest"
      INSTALLED=$((INSTALLED + 1))
    fi
  done
fi

# Install prompts
if [ -d "$SCRIPT_DIR/prompts" ]; then
  for file in "$SCRIPT_DIR/prompts"/*.md; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    echo "  ✅ Installing prompt: $name"
    [ "$DRY_RUN" = false ] && cp "$file" "$COPILOT_DIR/sdd/prompts/$name"
    INSTALLED=$((INSTALLED + 1))
  done
fi

# Install templates
if [ -d "$SCRIPT_DIR/templates" ]; then
  for file in "$SCRIPT_DIR/templates"/*; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    echo "  ✅ Installing template: $name"
    [ "$DRY_RUN" = false ] && cp "$file" "$COPILOT_DIR/sdd/templates/$name"
    INSTALLED=$((INSTALLED + 1))
  done
fi

echo ""
echo "  ── Installation Complete ──"
echo ""
if [ "$DRY_RUN" = true ]; then
  echo "  (DRY RUN — no files were actually copied)"
fi
echo "  Installed to: $COPILOT_DIR"
echo "  Items installed: $INSTALLED"
echo ""
echo "  Next: Open a Copilot CLI session and try:"
echo "    /skills              — verify skills are loaded"
echo "    @{{AGENT_NAME}} hello — invoke an agent"
echo ""
