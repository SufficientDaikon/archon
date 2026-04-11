"""``archon doctor`` — health diagnostics (US-3, FR-023 through FR-027)."""

from __future__ import annotations

import typer

from archon.core.registry import Registry
from archon.core.platform import detect_platforms
from archon.core.config import is_initialized, load_config, get_install_records
from archon.utils.output import (
    console, print_success, print_error, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json, make_table,
)


def _compute_health(
    *,
    initialized: bool,
    platforms_detected: int,
    registry_ok: bool,
    skills_count: int,
    issues: list[dict],
    catalog_issues: int = 0,
) -> int:
    """Compute health score 0-100 (FR-023)."""
    score = 100

    if not initialized:
        score -= 25
    if not registry_ok:
        score -= 30
    if platforms_detected == 0:
        score -= 20

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    score -= min(len(errors) * 10, 30)
    score -= min(len(warnings) * 3, 15)

    # Catalog issues capped at 5 points (FR-CAT-043)
    score -= min(catalog_issues, 5)

    return max(0, min(100, score))


def doctor_cmd() -> None:
    """Run health diagnostics and display a report."""

    issues: list[dict] = []

    # ── Initialization check ────────────────────────────────────
    initialized = is_initialized()
    if not initialized:
        issues.append({
            "severity": "error",
            "message": "Archon is not initialized.",
            "remediation": "Run: archon init",
        })

    # ── Registry check ──────────────────────────────────────────
    registry_ok = False
    skills_count = 0
    agents_count = 0
    bundles_count = 0
    pipelines_count = 0
    synapses_count = 0
    version = "unknown"

    try:
        reg = Registry()
        reg.load()
        registry_ok = True
        skills_count = len(reg.skills)
        agents_count = len(reg.agents)
        bundles_count = len(reg.bundles)
        pipelines_count = len(reg.pipelines)
        synapses_count = len(reg.synapses)
        version = reg.version
    except FileNotFoundError:
        issues.append({
            "severity": "error",
            "message": "Registry (archon.yaml) not found.",
            "remediation": "Ensure ARCHON_ROOT is set or run from the Archon directory.",
        })
    except Exception as exc:
        issues.append({
            "severity": "error",
            "message": f"Registry error: {exc}",
            "remediation": "Check archon.yaml for syntax errors.",
        })

    # ── Agent card checks (FR-AC-037 through FR-AC-039) ─────────
    agents_with_cards = 0
    if registry_ok:
        for agent in reg.agents:
            reg.load_agent_manifest(agent)
            if agent.card is not None:
                agents_with_cards += 1
        missing_cards = agents_count - agents_with_cards
        if missing_cards > 0:
            issues.append({
                "severity": "warning",
                "message": f"{missing_cards} agent(s) missing card section in manifest.",
                "remediation": "Add card: section to agent-manifest.yaml. See: archon docs agent-cards",
            })

        # Check agent-cards.json staleness
        agent_cards_path = reg.root / "agent-cards.json"
        if agent_cards_path.exists():
            try:
                import re as _re
                from archon.core.agent_cards import generate_agent_cards
                expected = generate_agent_cards(reg.root, reg)
                actual = agent_cards_path.read_text(encoding="utf-8")
                expected_cmp = _re.sub(r'"generated":\s*"[^"]+"', '"generated": ""', expected)
                actual_cmp = _re.sub(r'"generated":\s*"[^"]+"', '"generated": ""', actual)
                if expected_cmp != actual_cmp:
                    issues.append({
                        "severity": "info",
                        "message": "agent-cards.json is stale.",
                        "remediation": "Regenerate with: archon generate agent-cards",
                    })
            except Exception:
                pass  # Don't let card check break doctor

    # ── Platform detection (FR-024) ─────────────────────────────
    platforms = detect_platforms()
    detected = [p for p in platforms if p.detected]

    if not detected:
        issues.append({
            "severity": "warning",
            "message": "No AI platforms detected.",
            "remediation": "Install Claude Code and ensure ~/.claude/ exists, then run: archon init",
        })

    # ── MCP Catalog checks (FR-CAT-040 through FR-CAT-044) ─────
    catalog_ok = False
    catalog_entries = 0
    catalog_missing_deps = 0
    catalog_missing_details: list[dict] = []
    catalog_issue_count = 0

    if registry_ok:
        try:
            from archon.core.catalog import Catalog, check_dependencies
            cat = Catalog(root=reg.root)
            cat.load()
            catalog_ok = True
            catalog_entries = len(cat.servers)

            # Check missing MCP dependencies across platforms
            missing_deps = check_dependencies(cat, reg)
            catalog_missing_deps = len(missing_deps)
            for md in missing_deps:
                detail = {
                    "skill": md.skill_name,
                    "server": md.server_name,
                    "platforms": md.platforms_missing,
                    "in_catalog": md.in_catalog,
                }
                catalog_missing_details.append(detail)
                issues.append({
                    "severity": "warning",
                    "message": f"Skill '{md.skill_name}' requires MCP server '{md.server_name}' but it is not configured.",
                    "remediation": f"Run: archon catalog install {md.server_name}",
                })
                catalog_issue_count += 1
        except FileNotFoundError:
            issues.append({
                "severity": "info",
                "message": "MCP catalog not found or invalid.",
                "remediation": "Ensure catalog/mcp-servers.yaml exists in the Archon root.",
            })
            catalog_issue_count += 2
        except Exception:
            issues.append({
                "severity": "info",
                "message": "MCP catalog not found or invalid.",
                "remediation": "Ensure catalog/mcp-servers.yaml exists and is valid YAML.",
            })
            catalog_issue_count += 2

    # Per-platform checks
    platform_statuses: list[dict] = []
    for p in platforms:
        status: dict = {
            "id": p.id,
            "name": p.name,
            "detected": p.detected,
            "scope": p.scope,
            "installed_skills": len(p.installed_skills),
        }
        if p.detected and p.skills_target and not p.skills_target.exists():
            issues.append({
                "severity": "info",
                "message": f"{p.name}: skills directory does not exist yet ({p.skills_target})",
                "remediation": f"Run: archon install --platform {p.id} --all",
            })
            status["healthy"] = False
        else:
            status["healthy"] = p.detected
        platform_statuses.append(status)

    # ── Virtuoso Engine checks ────────────────────────────────────
    virtuoso_ok = False
    virtuoso_version = "not installed"
    synapses_installed = 0
    agent_library_count = 0

    for p in detected:
        if p.skills_target:
            # Check Virtuoso SKILL.md
            virtuoso_skill = p.skills_target / "virtuoso" / "SKILL.md"
            if virtuoso_skill.exists():
                virtuoso_ok = True
                content = virtuoso_skill.read_text(encoding="utf-8")
                import re as _re_v
                ver_match = _re_v.search(r'version="([^"]+)"', content)
                if ver_match:
                    virtuoso_version = ver_match.group(1)
            else:
                issues.append({
                    "severity": "warning",
                    "message": f"Virtuoso engine not installed for {p.name}.",
                    "remediation": "Run: archon init --force",
                })

            # Check synapses
            synapses_dir = p.skills_target / "_synapses"
            if synapses_dir.exists():
                synapses_installed = sum(
                    1 for d in synapses_dir.iterdir()
                    if d.is_dir() and not d.name.startswith("_") and (d / "SYNAPSE.md").exists()
                )
            if synapses_installed < 5:
                issues.append({
                    "severity": "warning",
                    "message": f"Only {synapses_installed}/5 synapses installed.",
                    "remediation": "Run: archon init --force",
                })
            break  # Only check first detected platform

    # Check agent-library
    from pathlib import Path as _Path
    agent_library = _Path.home() / ".claude" / "agent-library"
    if agent_library.exists():
        agent_library_count = sum(1 for f in agent_library.glob("*.md") if not f.name.startswith("_"))

    # Check agent-router MCP
    agent_router_ok = False
    try:
        import json as _json
        settings_path = _Path.home() / ".claude" / "settings.json"
        if settings_path.exists():
            settings = _json.loads(settings_path.read_text(encoding="utf-8"))
            mcp_servers = settings.get("mcpServers", {})
            if "agent-router" in mcp_servers:
                agent_router_ok = True
    except Exception:
        pass

    if not agent_router_ok and agent_library_count > 0:
        issues.append({
            "severity": "info",
            "message": "Agent-router MCP server not registered but agent-library exists.",
            "remediation": "Register agent-router in ~/.claude/settings.json mcpServers.",
        })

    # ── Installation records check ──────────────────────────────
    records = get_install_records()
    total_installed = len(records)

    # ── Compute score ───────────────────────────────────────────
    score = _compute_health(
        initialized=initialized,
        platforms_detected=len(detected),
        registry_ok=registry_ok,
        skills_count=skills_count,
        issues=issues,
        catalog_issues=catalog_issue_count,
    )

    # ── JSON output ─────────────────────────────────────────────
    if is_json():
        print_json(json_envelope(
            command="doctor",
            data={
                "health_score": score,
                "initialized": initialized,
                "framework_version": version,
                "registry": {
                    "ok": registry_ok,
                    "skills": skills_count,
                    "agents": agents_count,
                    "agents_with_cards": agents_with_cards,
                    "bundles": bundles_count,
                    "pipelines": pipelines_count,
                    "synapses": synapses_count,
                    "mcp_catalog": {
                        "ok": catalog_ok,
                        "entries": catalog_entries,
                        "missing_dependencies": catalog_missing_deps,
                        "missing_details": catalog_missing_details,
                    },
                },
                "virtuoso": {
                    "installed": virtuoso_ok,
                    "version": virtuoso_version,
                    "synapses_installed": synapses_installed,
                    "agent_library_count": agent_library_count,
                    "agent_router_registered": agent_router_ok,
                },
                "platforms": platform_statuses,
                "installed_components": total_installed,
                "issues": issues,
            },
        ))
        return

    # ── Rich output ─────────────────────────────────────────────
    console.print()
    console.rule("[bold cyan]Archon Health Report[/bold cyan]")
    console.print()

    # Score display
    if score >= 90:
        score_style = "bold green"
        status_text = "EXCELLENT"
    elif score >= 70:
        score_style = "bold yellow"
        status_text = "GOOD"
    elif score >= 50:
        score_style = "bold dark_orange"
        status_text = "FAIR"
    else:
        score_style = "bold red"
        status_text = "POOR"

    console.print(f"  Health Score: [{score_style}]{score}/100 — {status_text}[/{score_style}]")
    console.print(f"  Framework Version: {version}")
    console.print()

    # Platform table (FR-024)
    plat_rows = []
    for ps in platform_statuses:
        det = "✅ Detected" if ps["detected"] else "❌ Not found"
        health = "🟢" if ps.get("healthy") else "⚪"
        plat_rows.append([ps["name"], ps["id"], det, str(ps["installed_skills"]), health])

    table = make_table(
        "Platforms",
        [("Name", "bold"), ("ID", ""), ("Status", ""), ("Skills", "cyan"), ("Health", "")],
        plat_rows,
    )
    console.print(table)
    console.print()

    # Component inventory (FR-027)
    console.print("[bold]Component Inventory:[/bold]")
    console.print(f"  Skills:      {skills_count}")
    console.print(f"  Agents:      {agents_count}")
    console.print(f"  Agent Cards: {agents_with_cards}/{agents_count}")
    console.print(f"  Bundles:     {bundles_count}")
    console.print(f"  Pipelines:   {pipelines_count}")
    console.print(f"  Synapses:    {synapses_count}")
    console.print(f"  MCP Catalog: {catalog_entries} server(s)" + (" ✓" if catalog_ok else " (not loaded)"))
    console.print(f"  Installed:   {total_installed} record(s)")
    console.print()

    # Virtuoso Engine status
    console.print("[bold]Virtuoso Engine:[/bold]")
    if virtuoso_ok:
        console.print(f"  🧠 Engine:       v{virtuoso_version} ✓")
    else:
        console.print("  ❌ Engine:       not installed")
    console.print(f"  🧠 Synapses:     {synapses_installed}/5")
    console.print(f"  📚 Agent Library: {agent_library_count} agent(s)")
    console.print(f"  🔌 Agent Router: {'✓ registered' if agent_router_ok else '❌ not registered'}")
    console.print()

    # Issues (FR-025, FR-026)
    if issues:
        console.print("[bold]Issues:[/bold]")
        for issue in issues:
            sev = issue["severity"]
            if sev == "error":
                icon = "[red]✗[/red]"
            elif sev == "warning":
                icon = "[yellow]⚠[/yellow]"
            else:
                icon = "[cyan]ℹ[/cyan]"
            console.print(f"  {icon} [{sev}]{issue['message']}[/{sev}]")
            console.print(f"    → {issue['remediation']}")
        console.print()
    else:
        print_success("No issues detected!")
        console.print()
