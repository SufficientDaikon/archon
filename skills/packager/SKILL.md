---
name: packager
description: >-
  Use when packaging, sharing, or publishing Archon agents, skills, templates,
  or SDD artifacts as shareable git repos. Triggers on tasks involving sharing,
  publishing, packaging, exporting, or distributing custom agents and skills.
  Also triggers when user says "package this", "share this", "make a repo for this",
  or "publish my agents".
---

# Packager Skill

This skill packages local Archon artifacts into shareable git repositories with professional README documentation and self-contained HTML documentation websites.

## When to Use This Skill

- User wants to share custom agents, skills, or templates
- User says "package", "share", "publish", "export", or "distribute"
- User wants to create a GitHub repo from their local Archon setup
- User wants documentation generated for their agents/skills

## Packaging Process

### Step 1: Determine Scope

Ask the user what to package. Common patterns:

| User Says | What to Package |
|-----------|----------------|
| "Package the SDD system" | All 3 agents + 3 skills + templates + prompts + guide |
| "Package the spec-writer" | 1 agent + 1 skill + its templates and examples |
| "Package all my agents" | All .agent.md files + their matching skills |
| "Package this skill" | 1 SKILL.md + templates/ + examples/ |
| "Package everything" | Full ~/.claude/ export (excluding session-state) |

### Step 2: Inventory Files

Scan these directories for the requested artifacts:

```
~/.claude/
├── agents/*.agent.md          -> Agent profiles
├── skills/*/SKILL.md          -> Skills
├── skills/*/templates/*       -> Skill templates
├── skills/*/examples/*        -> Skill examples
├── sdd/prompts/*              -> Reusable prompts
├── sdd/templates/*            -> Shared templates
├── sdd/SDD-GUIDE.md           -> System documentation
├── sdd/README.md              -> Artifact index
└── CLAUDE.md                  -> Global rules (extract relevant sections)
```

### Step 3: Create Repo Structure

```
{repo-name}/
├── README.md                  ← Comprehensive documentation
├── LICENSE                    ← MIT license
├── .gitignore                 ← OS/editor ignores
├── docs/
│   └── index.html             ← Self-contained documentation website
├── agents/                    ← Packaged agent profiles
├── skills/                    ← Packaged skills with templates
├── prompts/                   ← Packaged prompts
├── templates/                 ← Standalone templates
├── install.ps1                ← Windows installer
└── install.sh                 ← macOS/Linux installer
```

### Step 4: Generate README.md

Required sections (in order):

1. **Title** — `# {Package Name}` with one-line description
2. **Overview** — What this is, who it's for, what problem it solves (3-5 sentences)
3. **What's Included** — Table: File | Description | Required?
4. **Prerequisites** — Claude Code CLI installed, etc.
5. **Installation** — Numbered steps with `code blocks`
6. **Quick Start** — 3 commands or less to see it work
7. **Usage** — Per-component guide with prompt examples
8. **Architecture** — ASCII diagram of how pieces connect
9. **Customization** — How to modify for their needs
10. **Troubleshooting** — Common issues
11. **License** — MIT

Quality rules:
- Every command must be in a fenced code block with language tag
- Every step must show expected output
- Define all jargon (what IS an Archon agent? what IS a skill?)
- Write for someone who found this repo via Google

### Step 5: Generate HTML Documentation Website

Create `docs/index.html` — a self-contained, beautiful documentation site.

#### Required HTML Structure:

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Package Name} — Documentation</title>
  <!-- Prism.js for syntax highlighting (from CDN) -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
  <style>/* ALL CSS INLINE — see template */</style>
</head>
<body>
  <nav><!-- Sticky sidebar navigation --></nav>
  <main>
    <section id="hero"><!-- Title, description, quick-start --></section>
    <section id="what-is-this"><!-- Concept explanation --></section>
    <section id="whats-included"><!-- File tree visualization --></section>
    <section id="installation"><!-- Step-by-step guide --></section>
    <section id="usage"><!-- Per-component usage --></section>
    <section id="architecture"><!-- Visual diagrams --></section>
    <section id="prompts"><!-- Prompt examples in callout blocks --></section>
    <section id="customization"><!-- Config options --></section>
    <section id="troubleshooting"><!-- FAQ --></section>
  </main>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-powershell.min.js"></script>
  <script>/* Copy-to-clipboard, theme toggle, smooth scroll */</script>
</body>
</html>
```

#### HTML Design Requirements:

**Layout:**
- Max-width 900px content area, centered
- Sticky sidebar nav on desktop (collapses to hamburger on mobile)
- Generous padding and margins

**Typography:**
- System font stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- Code: "SF Mono", "Cascadia Code", "Fira Code", Consolas, monospace
- Base size: 16px, line-height: 1.7

**Colors (Light Theme):**
- Background: #ffffff
- Surface: #f8fafc
- Text: #1e293b
- Text secondary: #64748b
- Accent: #3b82f6 (blue)
- Success: #16a34a (green)
- Border: #e2e8f0

**Colors (Dark Theme):**
- Background: #0f172a
- Surface: #1e293b
- Text: #f1f5f9
- Text secondary: #94a3b8
- Accent: #60a5fa
- Border: #334155

**Code Blocks:**
- Dark background (#1e293b or Prism Tomorrow theme)
- Copy button (top-right corner, appears on hover)
- Language label (top-left)
- Horizontal scroll for long lines
- Line numbers for blocks > 5 lines

**Prompt Examples:**
- Styled as callout cards with left border accent
- "Copy prompt" button
- Monospace text but with a distinct background (e.g., blue-tinted)

**Step-by-Step Sections:**
- Numbered circles (CSS counters)
- Each step has: title, description, code block, expected output
- Visual connector line between steps

**File Tree:**
- Styled with indentation, folder/file icons (📁/📄)
- Optional: collapsible directories

### Step 6: Generate Install Scripts

**install.ps1 (Windows PowerShell):**
```powershell
# Install {Package Name}
# Copies agents, skills, and templates to ~/.claude/

$ClaudeDir = "$env:USERPROFILE\.claude"

# Create directories
@("agents", "skills", "sdd\prompts", "sdd\templates") | ForEach-Object {
    New-Item -ItemType Directory -Path "$ClaudeDir\$_" -Force | Out-Null
}

# Copy agents
Copy-Item -Path ".\agents\*" -Destination "$ClaudeDir\agents\" -Recurse -Force

# Copy skills
Get-ChildItem -Path ".\skills" -Directory | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination "$ClaudeDir\skills\$($_.Name)" -Recurse -Force
}

Write-Host "Installed successfully to $ClaudeDir" -ForegroundColor Green
```

**install.sh (macOS/Linux bash):**
```bash
#!/bin/bash
# Install {Package Name}

CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"/{agents,skills,sdd/{prompts,templates}}

cp -r ./agents/* "$CLAUDE_DIR/agents/" 2>/dev/null
cp -r ./skills/* "$CLAUDE_DIR/skills/" 2>/dev/null

echo "Installed successfully to $CLAUDE_DIR"
```

### Step 7: Generate Prompts Guide

For every agent/skill in the package, generate prompts organized by difficulty:

| Level | Color | Count | Purpose |
|-------|-------|-------|---------|
| 🟢 Getting Started | Green | 3+ | First thing a new user should try |
| 🔵 Common Workflows | Blue | 5+ | Day-to-day patterns |
| 🟣 Advanced | Purple | 3+ | Power-user patterns, chaining |

Each prompt MUST include:
1. A title explaining what it does
2. The full copy-paste prompt text (with `@agent-name` prefix)
3. A 1-2 sentence description of context
4. An "Expected Result" block showing what the user will see

These go in BOTH the README (as code blocks) and the HTML website (as interactive tutorial cards with filter tabs and copy buttons).

### Step 8: Sanitize, Init Git & Push to GitHub

1. **Sanitize paths**: Replace `C:\Users\tahaa\` → `~/` or relative paths
2. **Remove secrets**: Strip any API keys, tokens, or personal info
3. **Remove ephemeral files**: No session-state, no .specify/specs/ content
4. **Git init** + `.gitignore` + `LICENSE` (MIT)
5. `git add -A && git commit -m "Initial release: {description}"`
6. **Auto-push to GitHub** using `gh` CLI:
   ```powershell
   gh repo create {repo-name} --public --description "{desc}" --source=. --push
   ```
7. **Enable GitHub Pages**:
   ```powershell
   gh api repos/{owner}/{repo}/pages -X POST -f source.branch=main -f source.path=/docs
   ```

If `gh` is not available, generate a `push.ps1` script with manual instructions.

## Output Quality Checklist

Before declaring the package complete, verify:

- [ ] README has all 11 required sections
- [ ] HTML website loads in browser without errors
- [ ] Syntax highlighting works in HTML website
- [ ] Prompt tutorial section has 11+ prompts across 3 difficulty levels
- [ ] Every prompt has a copy button and expected result
- [ ] Install script paths are correct
- [ ] No hardcoded user-specific paths in packaged files
- [ ] No secrets or personal info in any file
- [ ] .gitignore exists and covers OS/editor files
- [ ] LICENSE file exists (MIT)
- [ ] Git repo initialized with initial commit
- [ ] Pushed to GitHub (or push script generated)
- [ ] GitHub Pages enabled (or instructions provided)

## Handoff

After packaging, tell the user:
1. **Local path**: Full path to the package directory
2. **GitHub URL**: `https://github.com/{owner}/{repo-name}`
3. **Docs site**: `https://{owner}.github.io/{repo-name}/`
4. **Preview command**: `start docs/index.html` (Windows) or `open docs/index.html` (macOS)
