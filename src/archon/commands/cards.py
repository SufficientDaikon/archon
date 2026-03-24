"""``archon cards`` — view and manage agent cards (US-AC-001 through US-AC-004)."""

from __future__ import annotations

from typing import Optional

import typer

from archon.core.registry import Registry
from archon.utils.output import (
    console,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_verbose,
    is_json,
    json_envelope,
    print_json,
    make_table,
    make_panel,
)
from archon.utils.paths import get_archon_root


# ── Capability badge mapping ────────────────────────────────────

_CAPABILITY_BADGES: dict[str, str] = {
    "streaming": "⚡",
    "multi-turn": "🔄",
    "file-output": "📄",
    "self-evaluation": "🔍",
    "context-aware": "🧠",
}

_COST_TIER_STYLES: dict[str, str] = {
    "fast": "green",
    "standard": "cyan",
    "premium": "magenta",
}


# ── Validation logic ────────────────────────────────────────────

_ALLOWED_COST_TIERS = {"fast", "standard", "premium"}
_REQUIRED_CAPABILITIES = {"streaming", "multi-turn", "file-output", "self-evaluation", "context-aware"}


def _validate_card(agent_name: str, card_data: dict | None) -> list[str]:
    """Validate a card dict and return a list of error strings."""
    errors: list[str] = []

    if card_data is None or not isinstance(card_data, dict):
        errors.append(f"{agent_name}: card section is empty or not an object")
        return errors

    # Capabilities
    caps = card_data.get("capabilities")
    if caps is None:
        errors.append(f"{agent_name}: card.capabilities: required field missing")
    elif not isinstance(caps, dict):
        errors.append(f"{agent_name}: card.capabilities: expected object, got {type(caps).__name__}")
    else:
        for cap_name in _REQUIRED_CAPABILITIES:
            if cap_name not in caps:
                errors.append(f"{agent_name}: card.capabilities.{cap_name}: required field missing")
            elif not isinstance(caps[cap_name], bool):
                errors.append(f"{agent_name}: card.capabilities.{cap_name}: expected boolean, got {type(caps[cap_name]).__name__}")

    # Skills provided
    skills = card_data.get("skills-provided")
    if skills is None:
        errors.append(f"{agent_name}: card.skills-provided: required field missing")
    elif not isinstance(skills, list):
        errors.append(f"{agent_name}: card.skills-provided: expected list, got {type(skills).__name__}")
    elif len(skills) < 1:
        errors.append(f"{agent_name}: card.skills-provided: 0 items < minimum 1")
    else:
        for i, skill in enumerate(skills):
            if not isinstance(skill, dict):
                errors.append(f"{agent_name}: card.skills-provided[{i}]: expected object, got {type(skill).__name__}")
                continue
            for req_field in ("id", "name", "description"):
                if req_field not in skill:
                    errors.append(f"{agent_name}: card.skills-provided[{i}].{req_field}: required field missing")

    # Input modes
    in_modes = card_data.get("input-modes")
    if in_modes is None:
        errors.append(f"{agent_name}: card.input-modes: required field missing")
    elif not isinstance(in_modes, list):
        errors.append(f"{agent_name}: card.input-modes: expected list, got {type(in_modes).__name__}")
    elif len(in_modes) < 1:
        errors.append(f"{agent_name}: card.input-modes: 0 items < minimum 1")

    # Output modes
    out_modes = card_data.get("output-modes")
    if out_modes is None:
        errors.append(f"{agent_name}: card.output-modes: required field missing")
    elif not isinstance(out_modes, list):
        errors.append(f"{agent_name}: card.output-modes: expected list, got {type(out_modes).__name__}")
    elif len(out_modes) < 1:
        errors.append(f"{agent_name}: card.output-modes: 0 items < minimum 1")

    # Cost tier
    cost_tier = card_data.get("cost-tier")
    if cost_tier is None:
        errors.append(f"{agent_name}: card.cost-tier: required field missing")
    elif cost_tier not in _ALLOWED_COST_TIERS:
        errors.append(f"{agent_name}: card.cost-tier: '{cost_tier}' not in allowed values [fast, standard, premium]")

    # Avg tokens
    avg_tokens = card_data.get("avg-tokens")
    if avg_tokens is None:
        errors.append(f"{agent_name}: card.avg-tokens: required field missing")
    elif not isinstance(avg_tokens, dict):
        errors.append(f"{agent_name}: card.avg-tokens: expected object, got {type(avg_tokens).__name__}")
    else:
        for token_field in ("input", "output"):
            val = avg_tokens.get(token_field)
            if val is None:
                errors.append(f"{agent_name}: card.avg-tokens.{token_field}: required field missing")
            elif isinstance(val, bool):
                errors.append(f"{agent_name}: card.avg-tokens.{token_field}: expected integer, got boolean")
            elif isinstance(val, float):
                errors.append(f"{agent_name}: card.avg-tokens.{token_field}: expected integer, got float")
            elif not isinstance(val, int):
                errors.append(f"{agent_name}: card.avg-tokens.{token_field}: expected integer, got {type(val).__name__}")
            elif val < 0:
                errors.append(f"{agent_name}: card.avg-tokens.{token_field}: must be ≥ 0")

    # Quality metrics (optional)
    qm = card_data.get("quality-metrics")
    if qm is not None and isinstance(qm, dict):
        for float_field in ("completeness", "last-eval-score"):
            if float_field in qm:
                fv = qm[float_field]
                if not isinstance(fv, (int, float)):
                    errors.append(f"{agent_name}: card.quality-metrics.{float_field}: expected float, got {type(fv).__name__}")
                elif fv < 0.0:
                    errors.append(f"{agent_name}: card.quality-metrics.{float_field}: {fv} below minimum 0.0")
                elif fv > 1.0:
                    errors.append(f"{agent_name}: card.quality-metrics.{float_field}: {fv} exceeds maximum 1.0")
        if "eval-count" in qm:
            ec = qm["eval-count"]
            if isinstance(ec, bool):
                errors.append(f"{agent_name}: card.quality-metrics.eval-count: expected integer, got boolean")
            elif not isinstance(ec, int):
                errors.append(f"{agent_name}: card.quality-metrics.eval-count: expected integer, got {type(ec).__name__}")
            elif ec < 0:
                errors.append(f"{agent_name}: card.quality-metrics.eval-count: must be ≥ 0")

    return errors


# ── Display helpers ─────────────────────────────────────────────

def _badges_str(capabilities: dict[str, bool]) -> str:
    """Build a string of emoji badges for true capabilities."""
    badges = []
    for cap_name, emoji in _CAPABILITY_BADGES.items():
        if capabilities.get(cap_name, False):
            badges.append(emoji)
    return " ".join(badges) if badges else "—"


def _show_summary_table(reg: Registry) -> None:
    """Display the Rich summary table of all agents (FR-AC-021)."""
    rows: list[list[str]] = []
    for agent in sorted(reg.agents, key=lambda a: a.name):
        reg.load_agent_manifest(agent)
        name = agent.name
        role = agent.role or "—"

        if agent.card is not None:
            badges = _badges_str(agent.card.capabilities)
            tier = agent.card.cost_tier
            tier_style = _COST_TIER_STYLES.get(tier, "")
            tier_display = f"[{tier_style}]{tier}[/{tier_style}]" if tier_style else tier
        else:
            badges = "—"
            tier_display = "[dim]no card[/dim]"

        rows.append([name, role, badges, tier_display])

    table = make_table(
        "Agent Cards",
        [("Name", "bold"), ("Role", ""), ("Capabilities", ""), ("Cost Tier", "")],
        rows,
    )
    console.print()
    console.print(table)
    console.print()


def _show_detail_panel(agent_obj: object, reg: Registry) -> None:
    """Display a Rich panel with full card details for one agent (FR-AC-024)."""
    reg.load_agent_manifest(agent_obj)

    lines: list[str] = []
    lines.append(f"[bold]{agent_obj.name}[/bold]  v{agent_obj.version}")
    lines.append(f"[dim]Role:[/dim] {agent_obj.role}")
    lines.append(f"[dim]Description:[/dim] {agent_obj.description}")
    lines.append("")

    if agent_obj.card is None:
        lines.append("[yellow]No card data available.[/yellow]")
    else:
        card = agent_obj.card

        # Capabilities
        lines.append("[bold cyan]Capabilities[/bold cyan]")
        for cap_name, emoji in _CAPABILITY_BADGES.items():
            val = card.capabilities.get(cap_name, False)
            icon = "✓" if val else "✗"
            style = "green" if val else "red"
            lines.append(f"  {emoji} {cap_name}: [{style}]{icon}[/{style}]")
        lines.append("")

        # Skills provided
        lines.append("[bold cyan]Skills Provided[/bold cyan]")
        for skill in card.skills_provided:
            lines.append(f"  • [bold]{skill.get('name', '?')}[/bold] ({skill.get('id', '?')})")
            lines.append(f"    {skill.get('description', '')}")
            tags = skill.get("tags", [])
            if tags:
                lines.append(f"    Tags: {', '.join(tags)}")
        lines.append("")

        # I/O modes
        lines.append(f"[bold cyan]Input Modes:[/bold cyan]  {', '.join(card.input_modes)}")
        lines.append(f"[bold cyan]Output Modes:[/bold cyan] {', '.join(card.output_modes)}")
        lines.append("")

        # Cost tier
        tier_style = _COST_TIER_STYLES.get(card.cost_tier, "")
        lines.append(f"[bold cyan]Cost Tier:[/bold cyan] [{tier_style}]{card.cost_tier}[/{tier_style}]")

        # Avg tokens
        if card.avg_tokens:
            lines.append(f"[bold cyan]Avg Tokens:[/bold cyan] input={card.avg_tokens.get('input', '?')}, output={card.avg_tokens.get('output', '?')}")
        lines.append("")

        # Quality metrics
        if card.quality_metrics:
            lines.append("[bold cyan]Quality Metrics[/bold cyan]")
            for k, v in card.quality_metrics.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append("[dim]Quality Metrics: not yet evaluated[/dim]")

        # Handoff targets (from manifest)
        manifest = agent_obj._manifest or {}
        handoff = manifest.get("handoff-targets") or manifest.get("handoff")
        if handoff:
            lines.append("")
            lines.append("[bold cyan]Handoff Targets[/bold cyan]")
            if isinstance(handoff, list):
                for h in handoff:
                    lines.append(f"  → {h.get('agent', '?')}: {h.get('condition', '')}")
            elif isinstance(handoff, dict):
                next_agent = handoff.get("next-agent", "?")
                lines.append(f"  → {next_agent}")

    panel = make_panel("\n".join(lines), title=f"Agent Card: {agent_obj.name}", border_style="cyan")
    console.print()
    console.print(panel)
    console.print()


# ── Main command ────────────────────────────────────────────────

def cards_cmd(
    agent_name: Optional[str] = typer.Argument(None, help="Agent name to show details for."),
    validate: bool = typer.Option(False, "--validate", help="Validate all agent cards against the schema."),
    json_export: bool = typer.Option(False, "--json", help="Output agent cards as JSON."),
) -> None:
    """View and manage agent cards — capability metadata for every agent."""

    try:
        root = get_archon_root()
        reg = Registry(root=root)
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    # ── Validate mode ───────────────────────────────────────────
    if validate:
        import yaml as _yaml

        all_errors: list[str] = []
        agent_results: list[dict] = []

        for agent in sorted(reg.agents, key=lambda a: a.name):
            reg.load_agent_manifest(agent)
            manifest = agent._manifest or {}
            card_data = manifest.get("card")

            if card_data is None or (isinstance(card_data, dict) and not card_data):
                if is_json() or json_export:
                    agent_results.append({"name": agent.name, "status": "warning", "issues": ["card section missing (recommended)"]})
                else:
                    console.print(f"  [yellow]⚠[/yellow] {agent.name}: card section missing (recommended)")
                continue

            errors = _validate_card(agent.name, card_data)
            if errors:
                all_errors.extend(errors)
                if is_json() or json_export:
                    agent_results.append({"name": agent.name, "status": "failed", "issues": errors})
                else:
                    console.print(f"  [red]✗[/red] {agent.name}")
                    for e in errors:
                        console.print(f"      [red]{e}[/red]")
            else:
                if is_json() or json_export:
                    agent_results.append({"name": agent.name, "status": "passed", "issues": []})
                else:
                    console.print(f"  [green]✓[/green] {agent.name}")

        if is_json() or json_export:
            print_json(json_envelope(
                command="cards --validate",
                status="error" if all_errors else "success",
                data={"results": agent_results, "total_errors": len(all_errors)},
            ))
        else:
            console.print()
            if all_errors:
                print_error(f"{len(all_errors)} validation error(s) found.")
            else:
                print_success("All agent cards are valid.")
            console.print()

        if all_errors:
            raise typer.Exit(2)
        return

    # ── JSON export mode ────────────────────────────────────────
    if is_json() or json_export:
        cards_data: list[dict] = []
        for agent in sorted(reg.agents, key=lambda a: a.name):
            reg.load_agent_manifest(agent)
            card_dict = None
            if agent.card is not None:
                card_dict = {
                    "capabilities": agent.card.capabilities,
                    "skills-provided": agent.card.skills_provided,
                    "input-modes": agent.card.input_modes,
                    "output-modes": agent.card.output_modes,
                    "cost-tier": agent.card.cost_tier,
                    "avg-tokens": agent.card.avg_tokens,
                    "quality-metrics": agent.card.quality_metrics,
                }
            cards_data.append({
                "name": agent.name,
                "version": agent.version,
                "role": agent.role,
                "description": agent.description,
                "card": card_dict,
            })

        if agent_name:
            # Single agent JSON
            found = None
            for c in cards_data:
                if c["name"] == agent_name:
                    found = c
                    break
            if found is None:
                print_json(json_envelope(
                    command="cards",
                    status="error",
                    errors=[{"message": f"Agent not found: {agent_name}"}],
                ))
                raise typer.Exit(1)
            print_json(json_envelope(command="cards", data={"card": found}))
        else:
            print_json(json_envelope(command="cards", data={"cards": cards_data}))
        return

    # ── Single agent detail ─────────────────────────────────────
    if agent_name:
        agent_obj = reg.find_agent(agent_name)
        if agent_obj is None:
            print_error(f"Agent not found: {agent_name}")
            similar = reg.similar_names(agent_name)
            if similar:
                print_info(f"Did you mean: {', '.join(similar)}?")
            raise typer.Exit(1)
        _show_detail_panel(agent_obj, reg)
        return

    # ── Summary table ───────────────────────────────────────────
    _show_summary_table(reg)
