# Archon MCP Server Catalog

This directory contains the curated catalog of MCP (Model Context Protocol) servers supported by the Archon framework.

## Files

- **`mcp-servers.yaml`** — The catalog data file containing all server entries.

## Catalog Entry Format

Each server entry in `mcp-servers.yaml` has these fields:

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string (kebab-case) | Unique server identifier |
| `package` | string | npm/pip package name |
| `category` | string | One of: `core`, `development`, `database`, `research`, `design`, `ai`, `cloud`, `communication` |
| `description` | string (10–300 chars) | Human-readable purpose |
| `install-command` | string | Shell command to install the server |
| `tags` | list[string] | At least one searchable tag |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `required-env` | list of `{name, description}` | Environment variables needed |
| `recommended-for` | `{skills, agents, bundles}` | Archon components that benefit from this server |
| `docs-url` | string | Documentation URL |
| `server-type` | string | `"stdio"` (default) or `"sse"` |
| `args-template` | list[string] | Default args for platform config generation |

## Validation

Validate the catalog against its schema:

```bash
archon validate
archon catalog check
```

## Adding a Server

1. Add a new entry to `mcp-servers.yaml` following the format above.
2. Run `archon validate` to verify the entry.
3. Run `archon catalog list` to confirm it appears.

See [docs/integration-catalog.md](../docs/integration-catalog.md) for full documentation.
