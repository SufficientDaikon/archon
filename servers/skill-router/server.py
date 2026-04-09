"""Skill Router MCP Server — semantic skill discovery via TF-IDF routing.

Indexes skill files from ~/.claude/skill-library/ and exposes tools for
finding, listing, and loading skills on demand. Cross-references manifest.yaml
from ~/.claude/skills/ for rich metadata (tags, triggers, priority).

Zero LLM calls — pure text matching with weighted term scoring.

Usage:
    python server.py                      # stdio transport (default)
    python server.py --skills-dir PATH    # custom skills library directory
    python server.py --manifests-dir PATH # custom manifests directory
"""

from __future__ import annotations

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastmcp import FastMCP, Context

from indexer import SkillIndex, SkillEntry


# ── Configuration ────────────────────────────────────────────────

DEFAULT_SKILLS_DIR = Path.home() / ".claude" / "skill-library"
DEFAULT_MANIFESTS_DIR = Path.home() / ".claude" / "skills"


def _get_dir(flag: str, default: Path) -> Path:
    """Get directory from CLI args or default."""
    for i, arg in enumerate(sys.argv):
        if arg == flag and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return default


# ── Lifespan (index on startup) ─────────────────────────────────

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Build the skill index on server startup."""
    skills_dir = _get_dir("--skills-dir", DEFAULT_SKILLS_DIR)
    manifests_dir = _get_dir("--manifests-dir", DEFAULT_MANIFESTS_DIR)
    index = SkillIndex(skills_dir=skills_dir, manifests_dir=manifests_dir)
    index.build()
    yield {"index": index, "skills_dir": skills_dir}


# ── Server ───────────────────────────────────────────────────────

mcp = FastMCP(
    "skill-router",
    description="Semantic skill discovery for Archon. Find the right skill for any task.",
    lifespan=app_lifespan,
)


# ── Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def find_skill(task: str, top_k: int = 3, ctx: Context = None) -> str:
    """Find the best-matching skill(s) for a task description.

    Searches the skill library using TF-IDF keyword matching.
    Returns skill names, match scores, descriptions, and full content
    for the top matches so you can adopt the skill immediately.

    Args:
        task: Natural language description of what you need to do.
              Example: "build an Astro page with React islands"
        top_k: Number of top matches to return (default 3, max 5)
    """
    index: SkillIndex = ctx.fastmcp_context.lifespan_context["index"]
    top_k = min(top_k, 5)

    results = index.search(task, top_k=top_k)
    if not results:
        return json.dumps({
            "matches": [],
            "message": "No matching skills found. Try different keywords.",
        }, indent=2)

    matches = []
    for skill, score in results:
        content = index.get_skill_content(skill)
        matches.append({
            "name": skill.name,
            "filename": skill.filename,
            "description": skill.description,
            "category": skill.category,
            "priority": skill.priority,
            "score": round(score, 3),
            "size": skill.size_category,
            "content": content,
        })

    return json.dumps({
        "query": task,
        "matches": matches,
        "total_skills_indexed": len(index.skills),
    }, indent=2)


@mcp.tool()
async def list_skills(category: str | None = None, ctx: Context = None) -> str:
    """List all available skills in the library.

    Args:
        category: Optional filter — one of: web, design, backend, testing,
                  gamedev, mobile, mcp, ops, forge, workflow, general.
                  If omitted, returns all skills.
    """
    index: SkillIndex = ctx.fastmcp_context.lifespan_context["index"]
    skills = index.by_category(category)

    if not skills:
        msg = f"No skills in category '{category}'." if category else "No skills indexed."
        return json.dumps({"skills": [], "message": msg})

    by_cat: dict[str, list[dict]] = {}
    for s in skills:
        entry = {
            "name": s.name,
            "filename": s.filename,
            "description": s.description,
            "priority": s.priority,
            "size": s.size_category,
            "tags": s.tags,
        }
        by_cat.setdefault(s.category, []).append(entry)

    return json.dumps({
        "total": len(skills),
        "categories": by_cat,
    }, indent=2)


@mcp.tool()
async def get_skill(name: str, ctx: Context = None) -> str:
    """Get the full content of a specific skill by name or filename.

    Args:
        name: Skill name (e.g. "frontend-design") or
              filename (e.g. "frontend-design.md")
    """
    index: SkillIndex = ctx.fastmcp_context.lifespan_context["index"]
    skill = index.get_skill(name)

    if not skill:
        # Fuzzy fallback: search with the name as a query
        results = index.search(name, top_k=1)
        if results:
            skill = results[0][0]
        else:
            return json.dumps({
                "error": f"Skill '{name}' not found.",
                "available": [s.name for s in index.skills],
            })

    content = index.get_skill_content(skill)
    return json.dumps({
        "name": skill.name,
        "filename": skill.filename,
        "description": skill.description,
        "category": skill.category,
        "priority": skill.priority,
        "tags": skill.tags,
        "size": skill.size_category,
        "content": content,
    }, indent=2)


@mcp.tool()
async def rebuild_index(ctx: Context = None) -> str:
    """Re-index all skills in the library.

    Call this after adding, removing, or modifying skill files.
    """
    index: SkillIndex = ctx.fastmcp_context.lifespan_context["index"]
    skills_dir: Path = ctx.fastmcp_context.lifespan_context["skills_dir"]

    old_count = len(index.skills)
    index.skills_dir = skills_dir
    index.build()
    new_count = len(index.skills)

    return json.dumps({
        "status": "rebuilt",
        "previous_count": old_count,
        "current_count": new_count,
        "skills_dir": str(skills_dir),
    })


# ── Resources ────────────────────────────────────────────────────

@mcp.resource("skill://index")
async def skill_index_resource(ctx: Context = None) -> str:
    """Full skill index metadata — names, descriptions, categories, priorities, sizes."""
    index: SkillIndex = ctx.fastmcp_context.lifespan_context["index"]
    return json.dumps({
        "total": len(index.skills),
        "skills": [
            {
                "name": s.name,
                "filename": s.filename,
                "description": s.description,
                "category": s.category,
                "priority": s.priority,
                "tags": s.tags,
                "size": s.size_category,
                "size_bytes": s.size_bytes,
            }
            for s in index.skills
        ],
    }, indent=2)


@mcp.resource("skill://categories")
async def categories_resource(ctx: Context = None) -> str:
    """Category listing with skill counts."""
    index: SkillIndex = ctx.fastmcp_context.lifespan_context["index"]
    cats: dict[str, int] = {}
    for s in index.skills:
        cats[s.category] = cats.get(s.category, 0) + 1
    return json.dumps(cats, indent=2)


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
