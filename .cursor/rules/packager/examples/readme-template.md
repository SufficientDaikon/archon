# {{PACKAGE_NAME}}

> {{ONE_LINE_DESCRIPTION}}

{{HERO_SUMMARY — 3 sentences explaining what this is, who it's for, and what problem it solves.}}

## Overview

```
{{ASCII_DIAGRAM — Show how the pieces connect}}
```

## What's Included

| File                         | Description           | Required |
| ---------------------------- | --------------------- | -------- |
| `agents/{{name}}.agent.md`   | {{description}}       | ✅       |
| `skills/{{name}}/SKILL.md`   | {{description}}       | ✅       |
| `skills/{{name}}/templates/` | {{description}}       | ✅       |
| `prompts/{{name}}.md`        | {{description}}       | Optional |
| `docs/index.html`            | Documentation website | Optional |
| `install.ps1`                | Windows installer     | ✅       |
| `install.sh`                 | macOS/Linux installer | ✅       |

## Prerequisites

- [GitHub Copilot](https://github.com/features/copilot) subscription (Individual, Business, or Enterprise)
- [VS Code Insiders](https://code.visualstudio.com/insiders/) with Copilot CLI enabled
- OR any editor with Copilot CLI agent support

## Installation

### Option 1: One-Click Installer (Recommended)

```bash
# Clone the repo
git clone https://github.com/{{GITHUB_USER}}/{{REPO_NAME}}.git
cd {{REPO_NAME}}

# Windows
.\install.ps1

# macOS/Linux
chmod +x install.sh && ./install.sh
```

### Option 2: Manual Installation

Copy the files to your Copilot CLI configuration directory:

```bash
# Copy agents
cp agents/*.agent.md ~/.copilot/agents/

# Copy skills
cp -r skills/* ~/.copilot/skills/

# Copy prompts (if any)
cp prompts/*.md ~/.copilot/sdd/prompts/

# Copy templates (if any)
cp templates/* ~/.copilot/sdd/templates/
```

### Verify Installation

Open a new Copilot CLI session and check:

```
{{VERIFY_COMMAND — e.g., /skills to see loaded skills, or @agent-name to invoke}}
```

You should see:

```
{{EXPECTED_OUTPUT}}
```

## Quick Start

The fastest way to see it working:

```
{{QUICK_START_PROMPT}}
```

## Usage

### {{Component 1 Name}}

{{Description of what this component does and when to use it.}}

**Invoke with:**

```
{{INVOCATION_COMMAND}}
```

**Example:**

```
{{EXAMPLE_PROMPT}}
```

**What it produces:**
{{Description of output}}

---

### {{Component 2 Name}}

{{Repeat pattern for each component}}

## Architecture

```
{{ASCII_ARCHITECTURE_DIAGRAM}}
```

### How It Works

{{Step-by-step explanation of the system flow.}}

### Key Concepts

| Concept      | Definition                                                                 |
| ------------ | -------------------------------------------------------------------------- |
| **Agent**    | A `.agent.md` file defining an AI persona with specific tools and workflow |
| **Skill**    | A `SKILL.md` file providing procedural knowledge, templates, and examples  |
| **Template** | A reusable output format referenced by skills                              |

## Customization

### Changing Agent Behavior

Edit `~/.copilot/agents/{{name}}.agent.md`. The file has two parts:

1. **YAML frontmatter** — name, description, available tools
2. **Markdown body** — identity, workflow, rules

### Adding Templates

Place new templates in `~/.copilot/skills/{{name}}/templates/` and reference them in the SKILL.md.

## Troubleshooting

| Problem           | Solution                                                                  |
| ----------------- | ------------------------------------------------------------------------- |
| Agent not found   | Ensure `.agent.md` is in `~/.copilot/agents/` with valid YAML frontmatter |
| Skill not loading | Skills auto-load by relevance. Use keywords from the skill description    |
| Templates missing | Check `~/.copilot/skills/{name}/templates/` exists                        |

## Documentation Website

Open `docs/index.html` in a browser for the full interactive documentation with syntax highlighting, copy-to-clipboard code blocks, and dark mode support.

To host on GitHub Pages:

1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Set Source to **Deploy from branch**, Branch to **main**, Folder to **/docs**
4. Save — your site will be live at `https://{{GITHUB_USER}}.github.io/{{REPO_NAME}}/`

## Contributing

1. Fork this repo
2. Edit agent/skill files
3. Test by copying to your `~/.copilot/` directory
4. Submit a PR with a description of changes

## License

MIT — see [LICENSE](LICENSE) for details.
