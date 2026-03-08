---
name: mcp-server-index
description: RAG-indexed registry of configured MCP servers, available tools, and dispatch rules for Godot development workflows.
---

# MCP Server Index

This skill is the source of truth for selecting MCP servers and tools in this environment.
Always consult this index before invoking MCP tools.

## Active MCP Servers

### godot-mcp
- Purpose: Godot runtime + project + scene operations.
- Config key: `godot-mcp`
- Typical use:
  - Run/stop project for validation.
  - Read runtime/debug output.
  - Programmatic scene and node operations.
- Preferred tasks: runtime testing, scene refactors, verification loops.

### context7
- Purpose: fast documentation retrieval.
- Config key: `context7`
- Typical use:
  - Pull current docs for Godot/GDScript/FastMCP/APIs.
- Preferred tasks: API lookups, syntax confirmation, library guidance.

### godot-asset-library
- Purpose: search and pull assets from official Godot Asset Library API.
- Config key: `godot-asset-library`
- Tools:
  - `get_categories`
  - `search_assets`
  - `get_asset`
  - `download_asset_zip`
- Preferred tasks: find existing addons/assets before building from scratch.

### kscript-knowledge
- Purpose: local RAG-like knowledge base for patterns, rules, references.
- Config key: `kscript-knowledge`
- Tools:
  - `add_entry`
  - `search_entries`
  - `get_entry`
  - `list_tags`
  - `stats`
- Preferred tasks: capture and retrieve reusable Godot/GDScript patterns.

### ragx-aipm
- Purpose: AI project management and planning utilities.
- Config key: `ragx-aipm`
- Preferred tasks: planning and task organization support.

## Dispatch Rules

1. Runtime errors / behavior mismatch -> `godot-mcp` first.
2. API uncertainty / docs lookup -> `context7`.
3. Need plugin/addon quickly -> `godot-asset-library` before custom implementation.
4. Reusable fix/pattern discovered -> store in `kscript-knowledge` via `add_entry`.
5. Multi-step roadmap -> `ragx-aipm`.

## Godot Workflow Policy

- Start with analysis + minimal wireframe.
- Use MCP calls intentionally and explain why each call is needed.
- Keep changes backward compatible.
- Validate with runtime checks when possible.
- Persist useful lessons into `kscript-knowledge`.