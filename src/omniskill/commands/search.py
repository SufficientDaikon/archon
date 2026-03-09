"""``omniskill search`` — fuzzy search across components (US-4, FR-031, FR-032)."""

from __future__ import annotations

import re

import typer

from omniskill.core.registry import Registry
from omniskill.utils.output import (
    console, print_error, print_info, is_json, json_envelope, print_json, make_table,
)


def _score(query: str, name: str, description: str, tags: list[str]) -> float:
    """Compute a simple relevance score for a component against *query*."""
    q = query.lower()
    words = set(re.split(r"[\s\-_]+", q))
    score = 0.0

    n = name.lower()
    d = description.lower()
    t_text = " ".join(tags).lower()

    # Exact name match
    if q == n:
        score += 100
    elif q in n:
        score += 50
    elif n in q:
        score += 30

    # Description match
    if q in d:
        score += 20

    # Tag matches
    for tag in tags:
        if q == tag.lower():
            score += 40
        elif q in tag.lower():
            score += 15

    # Word overlap
    for w in words:
        if w in n:
            score += 10
        if w in d:
            score += 5
        if w in t_text:
            score += 8

    return score


def search_cmd(
    query: str = typer.Argument(..., help="Search query (keyword, tag, or phrase)."),
) -> None:
    """Search across all skills, agents, bundles, and pipelines."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    hits: list[dict] = []

    # Search skills
    for sk in reg.skills:
        reg.load_skill_manifest(sk)
        s = _score(query, sk.name, sk.description, sk.tags)
        if s > 0:
            hits.append({
                "name": sk.name,
                "type": "skill",
                "version": sk.version,
                "description": sk.description,
                "tags": sk.tags,
                "score": s,
            })

    # Search agents
    for ag in reg.agents:
        reg.load_agent_manifest(ag)
        s = _score(query, ag.name, ag.description, [])
        if s > 0:
            hits.append({
                "name": ag.name,
                "type": "agent",
                "version": ag.version,
                "description": ag.description,
                "tags": [],
                "score": s,
            })

    # Search bundles
    for bnd in reg.bundles:
        reg.load_bundle_manifest(bnd)
        s = _score(query, bnd.name, bnd.description, bnd.skills)
        if s > 0:
            hits.append({
                "name": bnd.name,
                "type": "bundle",
                "version": bnd.version,
                "description": bnd.description,
                "tags": bnd.skills,
                "score": s,
            })

    # Search pipelines
    for pl in reg.pipelines:
        reg.load_pipeline_manifest(pl)
        s = _score(query, pl.name, pl.description, [pl.trigger])
        if s > 0:
            hits.append({
                "name": pl.name,
                "type": "pipeline",
                "version": pl.version,
                "description": pl.description,
                "tags": [pl.trigger],
                "score": s,
            })

    # Sort by relevance (FR-032)
    hits.sort(key=lambda h: -h["score"])

    if is_json():
        # Strip score from output
        for h in hits:
            del h["score"]
        print_json(json_envelope(command="search", data={"query": query, "count": len(hits), "results": hits}))
        return

    if not hits:
        print_info(f"No results for '{query}'.")
        console.print("  Try a broader term, or run [bold]omniskill list[/bold] to browse.")
        return

    console.print(f"\n[bold]Search results for[/bold] \"{query}\" ({len(hits)} match{'es' if len(hits) != 1 else ''}):\n")

    rows = []
    for h in hits[:25]:  # Cap at 25 results
        desc = (h["description"][:55] + "…") if len(h["description"]) > 55 else h["description"]
        rows.append([h["name"], h["type"], h["version"], desc])

    table = make_table(
        "Results",
        [("Name", "bold"), ("Type", "cyan"), ("Version", ""), ("Description", "")],
        rows,
    )
    console.print(table)
    console.print()
