"""Core generation logic for agent-cards.json.

Produces a machine-readable JSON index of all agent cards in the Archon
framework, suitable for consumption by web UIs, LLM orchestrators, and
IDE extensions.

Public API
----------
- :func:`generate_agent_cards` — JSON string of all agent cards
- :func:`write_agent_cards` — generate and write agent-cards.json to disk
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from archon.core.registry import Registry


# ── Public API ──────────────────────────────────────────────────


def generate_agent_cards(root: Path, registry: Registry | None = None) -> str:
    """Generate the ``agent-cards.json`` content as a JSON string.

    Args:
        root: Path to the Archon repository root.
        registry: Pre-loaded Registry instance.  If *None*, one is created
            and loaded automatically.

    Returns:
        Pretty-printed JSON string containing all agent card data.
    """
    reg = _ensure_registry(root, registry)
    agents_data: list[dict[str, Any]] = []

    for agent in sorted(reg.agents, key=lambda a: a.name):
        reg.load_agent_manifest(agent)
        agents_data.append(_build_card_entry(root, agent, reg))

    index: dict[str, Any] = {
        "$schema": "archon-agent-cards-v1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "framework_version": reg.version,
        "agents": agents_data,
    }

    return json.dumps(index, indent=2, ensure_ascii=False)


def write_agent_cards(
    root: Path,
    output_dir: Path | None = None,
    registry: Registry | None = None,
) -> dict[str, Any]:
    """Generate and write ``agent-cards.json`` to disk.

    Args:
        root: Archon repository root.
        output_dir: Directory to write the file to.  Defaults to *root*.
        registry: Pre-loaded Registry instance.

    Returns:
        A dict with keys ``path``, ``size``, ``agent_count``.
    """
    out = output_dir or root
    out.mkdir(parents=True, exist_ok=True)

    reg = _ensure_registry(root, registry)
    content = generate_agent_cards(root, reg)

    file_path = out / "agent-cards.json"
    file_path.write_text(content, encoding="utf-8", newline="\n")

    # Count agents from the JSON
    data = json.loads(content)
    agent_count = len(data.get("agents", []))

    return {
        "path": file_path,
        "size": file_path.stat().st_size,
        "agent_count": agent_count,
    }



def write_a2a_cards(
    root: Path,
    registry: Registry | None = None,
) -> Path:
    """Generate A2A AgentCard JSON files conforming to schema version 0.2.1.

    Writes:
    - ``<root>/.well-known/agent.json`` — combined array of all agent cards
    - ``<root>/.well-known/agents/<name>.json`` — per-agent card

    Args:
        root: Archon repository root.
        registry: Pre-loaded Registry instance. If None, one is created.

    Returns:
        Path to the combined ``.well-known/agent.json`` file.
    """
    reg = _ensure_registry(root, registry)

    well_known = root / ".well-known"
    per_agent_dir = well_known / "agents"
    per_agent_dir.mkdir(parents=True, exist_ok=True)

    # Resolve base URL from environment variable or fall back to localhost.
    # Set ARCHON_A2A_BASE_URL in production deployments.
    import os
    base_url = os.environ.get("ARCHON_A2A_BASE_URL", "http://localhost:8000").rstrip("/")

    all_cards: list[dict[str, Any]] = []

    for agent in sorted(reg.agents, key=lambda a: a.name):
        reg.load_agent_manifest(agent)
        skills_provided = []
        if agent.card and agent.card.skills_provided:
            for sk in agent.card.skills_provided:
                if isinstance(sk, dict):
                    skills_provided.append({
                        "id": sk.get("id", sk.get("name", "")),
                        "name": sk.get("name", ""),
                        "description": sk.get("description", ""),
                    })

        card: dict[str, Any] = {
            "schemaVersion": "0.2.1",
            "name": agent.name,
            "description": agent.description or "",
            "url": f"{base_url}/agents/{agent.name}",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
            },
            "skills": skills_provided,
        }

        # Write per-agent card
        per_card_path = per_agent_dir / f"{agent.name}.json"
        per_card_path.write_text(
            json.dumps(card, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        all_cards.append(card)

    # Write combined card
    combined_path = well_known / "agent.json"
    combined_path.write_text(
        json.dumps(all_cards, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return combined_path

# ── Private helpers ─────────────────────────────────────────────


def _ensure_registry(root: Path, registry: Registry | None) -> Registry:
    """Return *registry* if provided, else create and load one."""
    if registry is not None:
        registry.ensure_loaded()
        return registry
    reg = Registry(root=root)
    reg.load()
    return reg


def _build_card_entry(root: Path, agent: Any, registry: Registry) -> dict[str, Any]:
    """Build the card entry dict for a single agent.

    The card value uses hyphenated keys matching the YAML manifest format.
    """
    entry: dict[str, Any] = {
        "name": agent.name,
        "version": agent.version,
        "role": agent.role,
        "description": agent.description,
        "path": agent.path,
    }

    if agent.card is not None:
        entry["card"] = {
            "capabilities": agent.card.capabilities,
            "skills-provided": agent.card.skills_provided,
            "input-modes": agent.card.input_modes,
            "output-modes": agent.card.output_modes,
            "cost-tier": agent.card.cost_tier,
            "avg-tokens": agent.card.avg_tokens,
            "quality-metrics": agent.card.quality_metrics,
        }
    else:
        entry["card"] = None

    return entry
