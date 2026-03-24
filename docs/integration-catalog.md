# Integration Catalog

The **MCP Server Integration Catalog** is a curated collection of Model Context Protocol (MCP) servers that integrate with Archon skills, agents, and bundles. It provides a single place to discover, configure, and manage MCP servers across AI coding platforms.

## Overview

Archon skills and agents can declare `mcp-dependencies` in their manifests — MCP servers they need to function. The Integration Catalog:

- **Discovers** which MCP servers exist and what they do
- **Recommends** servers based on your installed skills and bundles
- **Generates** platform-specific MCP configuration files automatically
- **Audits** whether required servers are actually configured

## Quick Start

```bash
# Browse available servers
archon catalog list

# Search for a server
archon catalog search database

# Install a server for your platform
archon catalog install github --platform copilot-cli
```

## Server Entry Format

Each server in `catalog/mcp-servers.yaml` has this structure:

```yaml
- name: github                          # Unique kebab-case ID
  package: "@modelcontextprotocol/server-github"  # npm/pip package
  category: development                 # Category for grouping
  description: "GitHub integration — repos, issues, PRs, code search"
  install-command: "npx -y @modelcontextprotocol/server-github"
  server-type: stdio                    # stdio or sse
  args-template: ["npx", "-y", "@modelcontextprotocol/server-github"]
  required-env:
    - name: GITHUB_TOKEN
      description: "Personal access token with repo scope"
  recommended-for:
    skills: [backend-development]
    agents: [implementer-agent]
    bundles: [web-dev-kit]
  tags: [git, github, version-control, code-review]
  docs-url: "https://github.com/modelcontextprotocol/servers/tree/main/src/github"
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string (kebab-case) | Unique server identifier |
| `package` | string | Package name (npm or pip) |
| `category` | string | One of: `core`, `development`, `database`, `research`, `design`, `ai`, `cloud`, `communication` |
| `description` | string (10–300 chars) | Human-readable purpose |
| `install-command` | string | Shell command to install the server |
| `tags` | list[string] | At least one searchable tag |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `required-env` | list of `{name, description}` | Environment variables needed |
| `recommended-for` | `{skills, agents, bundles}` | Archon components that benefit |
| `docs-url` | string | Documentation URL |
| `server-type` | `"stdio"` (default) or `"sse"` | Connection type |
| `args-template` | list[string] | Default args for config generation |

## CLI Reference

### `archon catalog list`

List all available MCP servers in the catalog.

```bash
archon catalog list                     # All servers
archon catalog list --category database # Filter by category
archon catalog list --json              # JSON output
```

### `archon catalog search <query>`

Search servers by keyword, tag, or description. Results are scored by relevance.

```bash
archon catalog search git       # Find git-related servers
archon catalog search database  # Find database servers
```

Scoring priority: name match > tag match > description match.

### `archon catalog info <server>`

Show full details of a specific server including environment variables, recommendations, and install command.

```bash
archon catalog info github
archon catalog info postgres
```

If the server name is misspelled, fuzzy suggestions are shown.

### `archon catalog recommend`

Get personalized recommendations based on your installed skills and bundles.

```bash
archon catalog recommend
```

Shows two sections:
- **Required by your skills** — servers needed by `mcp-dependencies` in skill manifests
- **Also recommended** — servers whose `recommended-for` matches your installed components

### `archon catalog install <server>`

Generate platform MCP config and merge it into the config file.

```bash
archon catalog install github                       # All detected platforms
archon catalog install github --platform copilot-cli # Specific platform
archon catalog install postgres --platform claude-code
```

Supported platforms: `copilot-cli`, `claude-code`, `cursor`.

### `archon catalog check`

Audit your MCP config against installed skills' dependencies.

```bash
archon catalog check
archon catalog check --json
```

Reports any skills with unmet `mcp-dependencies`.

## Platform Config Formats

The `catalog install` command generates platform-specific JSON config:

### Copilot CLI (`~/.copilot/mcp-config.json`)

```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE" }
    }
  }
}
```

### Claude Code (`~/.claude/mcp.json`)

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE" }
    }
  }
}
```

### Cursor (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN_HERE" }
    }
  }
}
```

## How Recommendations Work

The `recommend` command uses two strategies:

1. **Dependency scanning** — Loads all installed skills' `manifest.yaml` files and collects their `mcp-dependencies` lists. Each dependency name is matched against catalog server names.

2. **Reverse matching** — Each catalog server has a `recommended-for` field listing skills, agents, and bundles that benefit from it. The system checks which of these are installed in your registry.

## Adding Custom Servers

To add a server to the catalog:

1. Edit `catalog/mcp-servers.yaml`
2. Add a new entry following the format above
3. Ensure `name` is unique and kebab-case
4. Run `archon validate` to check the entry
5. Run `archon catalog info <name>` to verify

## Troubleshooting

### "MCP catalog not found"

Ensure you're running from the Archon root directory, or set the `Archon_ROOT` environment variable.

### "Existing config is not valid JSON"

The platform config file has syntax errors. Fix it manually or delete it and re-run the install command.

### Environment variable warnings

When `catalog install` generates config, it checks if required environment variables are set. If not, placeholder values like `YOUR_GITHUB_TOKEN_HERE` are used. Set the actual values in your shell profile.

### "Server already configured"

Running `catalog install` for a server that's already in the config is a no-op — it exits cleanly without modifying the file.
