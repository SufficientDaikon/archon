# Claude Plugin Scaffold Reference

> Extracted from prompts.chat `plugins/claude/prompts.chat/` directory.

## Complete Directory Structure

```
plugins/claude/my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── agents/
│   └── task-manager.md
├── commands/
│   └── search.md
└── skills/
    ├── index.json
    └── auto-lookup/
        └── SKILL.md
```

## 1. Plugin Manifest (`.claude-plugin/plugin.json`)

```json
{
  "name": "my-plugin",
  "description": "A Claude Code plugin for managing AI prompts",
  "version": "1.0.0",
  "author": "your-name",
  "features": {
    "mcp": true,
    "agents": true,
    "commands": true,
    "skills": true
  },
  "activation": {
    "onLoad": true,
    "triggers": ["prompt", "ai"]
  }
}
```

## 2. MCP Configuration (`.mcp.json`)

```json
{
  "mcpServers": {
    "my-plugin": {
      "command": "npx",
      "args": ["-y", "my-plugin-mcp-server"],
      "env": {
        "API_URL": "https://api.example.com",
        "API_KEY": "${MY_PLUGIN_API_KEY}"
      }
    }
  }
}
```

## 3. Agent Definition (`agents/task-manager.md`)

```markdown
# Task Manager Agent

You are the **Task Manager** for my-plugin. You help users search, create,
and manage resources through the MCP tools available to you.

## Available Tools

- `search_items` — Search for items by query
- `get_item` — Get a single item by ID
- `save_item` — Create or update an item
- `delete_item` — Remove an item

## Workflow

1. When the user asks to find something, use `search_items`
2. When the user wants details, use `get_item`
3. When the user wants to create/edit, use `save_item`
4. Always confirm destructive actions before using `delete_item`

## Guardrails

- Never delete without explicit user confirmation
- Always show search results before acting on them
- Redact any API keys or secrets in output
```

## 4. Slash Command (`commands/search.md`)

```markdown
# /search

Search for items in the plugin's database.

## Usage

/search [query]

## Examples

- `/search react hooks` — Find items related to React hooks
- `/search` — Browse all items

## Behavior

1. Call the `search_items` MCP tool with the user's query
2. Display results in a formatted list
3. Allow the user to select an item for details
```

## 5. Skills Registry (`skills/index.json`)

```json
{
  "skills": [
    {
      "name": "auto-lookup",
      "path": "skills/auto-lookup",
      "triggers": {
        "filePatterns": ["*.md", "*.txt"],
        "keywords": ["prompt", "template"]
      },
      "autoActivate": true
    }
  ]
}
```

## 6. Auto-Activating Skill (`skills/auto-lookup/SKILL.md`)

```markdown
# Auto-Lookup

> Automatically suggests relevant items when the user works with prompt files.

## Activation

This skill activates when:
- The user opens or edits a `.md` or `.txt` file
- The file contains keywords: "prompt", "template", "instruction"

## Behavior

1. Detect the current file's content topic
2. Search the plugin's database for related items
3. Suggest relevant items as inline completions or side panel
```

## 7. MCP Server Implementation (TypeScript)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-plugin",
  version: "1.0.0",
});

server.tool(
  "search_items",
  "Search for items by query",
  { query: z.string().describe("Search query"), limit: z.number().optional().default(10) },
  async ({ query, limit }) => {
    const results = await fetch(`${process.env.API_URL}/search?q=${query}&limit=${limit}`);
    const data = await results.json();
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

server.tool(
  "get_item",
  "Get a single item by ID",
  { id: z.string().describe("Item ID") },
  async ({ id }) => {
    const result = await fetch(`${process.env.API_URL}/items/${id}`);
    const data = await result.json();
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```
