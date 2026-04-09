"""Agent Router MCP Server — semantic agent discovery via TF-IDF routing.

Indexes agent files from ~/.claude/agent-library/ and exposes tools for
finding, listing, and loading agents on demand. Zero LLM calls — pure
text matching with weighted term scoring.

Usage:
    python server.py                    # stdio transport (default)
    python server.py --agents-dir PATH  # custom agents directory
"""

from __future__ import annotations

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastmcp import FastMCP, Context

from indexer import AgentIndex, AgentEntry


# ── Configuration ────────────────────────────────────────────────

DEFAULT_AGENTS_DIR = Path.home() / ".claude" / "agent-library"


def _get_agents_dir() -> Path:
    """Get agents directory from CLI args or default."""
    for i, arg in enumerate(sys.argv):
        if arg == "--agents-dir" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return DEFAULT_AGENTS_DIR


# ── Lifespan (index on startup) ─────────────────────────────────

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Build the agent index on server startup."""
    agents_dir = _get_agents_dir()
    index = AgentIndex(agents_dir=agents_dir)
    index.build()
    yield {"index": index, "agents_dir": agents_dir}


# ── Server ───────────────────────────────────────────────────────

mcp = FastMCP(
    "agent-router",
    description="Semantic agent discovery for Archon. Find the right agent for any task.",
    lifespan=app_lifespan,
)


# ── Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def find_agent(task: str, top_k: int = 3, ctx: Context = None) -> str:
    """Find the best-matching agent(s) for a task description.

    Searches the agent library using TF-IDF keyword matching.
    Returns agent names, match scores, descriptions, and full content
    for the top matches so you can adopt the persona immediately.

    Args:
        task: Natural language description of what you need to do.
              Example: "audit smart contracts for reentrancy vulnerabilities"
        top_k: Number of top matches to return (default 3, max 5)
    """
    index: AgentIndex = ctx.fastmcp_context.lifespan_context["index"]
    top_k = min(top_k, 5)

    results = index.search(task, top_k=top_k)
    if not results:
        return json.dumps({
            "matches": [],
            "message": "No matching agents found. Try different keywords.",
        }, indent=2)

    matches = []
    for agent, score in results:
        content = index.get_agent_content(agent)
        matches.append({
            "name": agent.name,
            "filename": agent.filename,
            "description": agent.description,
            "category": agent.category,
            "score": round(score, 3),
            "size": agent.size_category,
            "content": content,
        })

    return json.dumps({
        "query": task,
        "matches": matches,
        "total_agents_indexed": len(index.agents),
    }, indent=2)


@mcp.tool()
async def list_agents(category: str | None = None, ctx: Context = None) -> str:
    """List all available agents in the library.

    Args:
        category: Optional filter — one of: engineering, design, testing, game, niche, orchestration.
                  If omitted, returns all agents.
    """
    index: AgentIndex = ctx.fastmcp_context.lifespan_context["index"]
    agents = index.by_category(category)

    if not agents:
        msg = f"No agents in category '{category}'." if category else "No agents indexed."
        return json.dumps({"agents": [], "message": msg})

    # Group by category
    by_cat: dict[str, list[dict]] = {}
    for a in agents:
        entry = {
            "name": a.name,
            "filename": a.filename,
            "description": a.description,
            "size": a.size_category,
        }
        by_cat.setdefault(a.category, []).append(entry)

    return json.dumps({
        "total": len(agents),
        "categories": by_cat,
    }, indent=2)


@mcp.tool()
async def get_agent(name: str, ctx: Context = None) -> str:
    """Get the full content of a specific agent by name or filename.

    Args:
        name: Agent display name (e.g. "Frontend Developer") or
              filename (e.g. "engineering-frontend-developer" or
              "engineering-frontend-developer.md")
    """
    index: AgentIndex = ctx.fastmcp_context.lifespan_context["index"]
    agent = index.get_agent(name)

    if not agent:
        # Fuzzy fallback: search with the name as a query
        results = index.search(name, top_k=1)
        if results:
            agent = results[0][0]
        else:
            return json.dumps({
                "error": f"Agent '{name}' not found.",
                "available": [a.name for a in index.agents],
            })

    content = index.get_agent_content(agent)
    return json.dumps({
        "name": agent.name,
        "filename": agent.filename,
        "description": agent.description,
        "category": agent.category,
        "size": agent.size_category,
        "content": content,
    }, indent=2)


@mcp.tool()
async def rebuild_index(ctx: Context = None) -> str:
    """Re-index all agents in the library.

    Call this after adding, removing, or modifying agent files.
    """
    index: AgentIndex = ctx.fastmcp_context.lifespan_context["index"]
    agents_dir: Path = ctx.fastmcp_context.lifespan_context["agents_dir"]

    old_count = len(index.agents)
    index.agents_dir = agents_dir
    index.build()
    new_count = len(index.agents)

    return json.dumps({
        "status": "rebuilt",
        "previous_count": old_count,
        "current_count": new_count,
        "agents_dir": str(agents_dir),
    })


# ── Resources ────────────────────────────────────────────────────

@mcp.resource("agent://index")
async def agent_index_resource(ctx: Context = None) -> str:
    """Full agent index metadata — names, descriptions, categories, sizes."""
    index: AgentIndex = ctx.fastmcp_context.lifespan_context["index"]
    return json.dumps({
        "total": len(index.agents),
        "agents": [
            {
                "name": a.name,
                "filename": a.filename,
                "description": a.description,
                "category": a.category,
                "size": a.size_category,
                "size_bytes": a.size_bytes,
            }
            for a in index.agents
        ],
    }, indent=2)


@mcp.resource("agent://categories")
async def categories_resource(ctx: Context = None) -> str:
    """Category listing with agent counts."""
    index: AgentIndex = ctx.fastmcp_context.lifespan_context["index"]
    cats: dict[str, int] = {}
    for a in index.agents:
        cats[a.category] = cats.get(a.category, 0) + 1
    return json.dumps(cats, indent=2)


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
