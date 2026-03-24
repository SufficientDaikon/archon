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
