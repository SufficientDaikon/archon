"""``archon catalog`` — browse and manage MCP server integrations (FR-CAT-030 through FR-CAT-038).

Provides subcommands: list, search, info, recommend, install, check.
"""

from __future__ import annotations

import os
from typing import Optional

import typer

from archon.core.catalog import (
    Catalog,
    McpServer,
    PLATFORM_CONFIGS,
    SUPPORTED_PLATFORMS,
    VALID_CATEGORIES,
    _server_to_dict,
    generate_platform_config,
    merge_into_config,
    check_dependencies,
    get_platform_config_path,
)
from archon.core.registry import Registry
from archon.core.platform import get_detected_platform_ids
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
)

# ── Typer sub-app (FR-CAT-030) ─────────────────────────────────

catalog_app = typer.Typer(
    help="Browse and manage MCP server integrations.",
    no_args_is_help=True,
)


# ── Helpers ─────────────────────────────────────────────────────


def _load_catalog_or_exit() -> Catalog:
    """Load the catalog or print error and exit."""
    try:
        cat = Catalog()
        cat.load()
        return cat
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)
    except Exception as exc:
        print_error(f"Failed to load MCP catalog: {exc}")
        raise typer.Exit(1)


# ── catalog list (FR-CAT-031) ──────────────────────────────────


@catalog_app.command("list")
def catalog_list_cmd(
    category: Optional[str] = typer.Option(
        None, "--category", "-c",
        help="Filter by category (core, development, database, research, design, ai, cloud, communication).",
    ),
) -> None:
    """List all available MCP servers in the catalog."""
    cat = _load_catalog_or_exit()

    if category and category not in VALID_CATEGORIES:
        print_error(
            f"Unknown category '{category}'. "
            f"Valid: {', '.join(VALID_CATEGORIES)}"
        )
        raise typer.Exit(1)

    servers = cat.list_servers(category=category)

    if is_json():
        print_json(json_envelope(
            command="catalog list",
            data={"servers": [_server_to_dict(s) for s in servers]},
        ))
        return

    if not servers:
        print_info("No servers in catalog.")
        return

    rows = []
    for s in servers:
        desc = (s.description[:55] + "…") if len(s.description) > 55 else s.description
        rows.append([s.name, s.category, desc])

    table = make_table(
        f"MCP Servers ({len(servers)})",
        [("Name", "bold"), ("Category", "cyan"), ("Description", "")],
        rows,
    )
    console.print()
    console.print(table)
    console.print()


# ── catalog search (FR-CAT-032) ────────────────────────────────


@catalog_app.command("search")
def catalog_search_cmd(
    query: str = typer.Argument(..., help="Search query (keyword, tag, or phrase)."),
) -> None:
    """Search MCP servers by keyword, tag, or description."""
    cat = _load_catalog_or_exit()

    results = cat.search(query)

    if is_json():
        print_json(json_envelope(
            command="catalog search",
            data={
                "query": query,
                "count": len(results),
                "servers": [_server_to_dict(s) for _, s in results],
            },
        ))
        return

    if not results:
        print_info(f"No results for '{query}'.")
        console.print("  Try a broader term, or run [bold]archon catalog list[/bold] to browse.")
        return

    console.print(f"\n[bold]Search results for[/bold] \"{query}\" ({len(results)} match{'es' if len(results) != 1 else ''}):\n")

    rows = []
    for _, s in results[:25]:
        desc = (s.description[:55] + "…") if len(s.description) > 55 else s.description
        tags_str = ", ".join(s.tags[:4])
        rows.append([s.name, s.category, tags_str, desc])

    table = make_table(
        "Results",
        [("Name", "bold"), ("Category", "cyan"), ("Tags", "dim"), ("Description", "")],
        rows,
    )
    console.print(table)
    console.print()


# ── catalog info (FR-CAT-033) ──────────────────────────────────


@catalog_app.command("info")
def catalog_info_cmd(
    server: str = typer.Argument(..., help="Server name (e.g., github, postgres)."),
) -> None:
    """Show detailed information about an MCP server."""
    cat = _load_catalog_or_exit()

    srv = cat.find_server(server)
    if not srv:
        similar = cat.similar_names(server)
        msg = f"Server '{server}' not found in catalog."
        if similar:
            msg += f" Did you mean: {', '.join(similar)}?"
        print_error(msg)
        raise typer.Exit(1)

    if is_json():
        print_json(json_envelope(
            command="catalog info",
            data=_server_to_dict(srv),
        ))
        return

    # Rich output — matching info.py pattern
    console.print()
    console.rule(f"[bold cyan]{srv.name}[/bold cyan]")
    console.print()
    console.print(f"  [bold]Name:[/bold]        {srv.name}")
    console.print(f"  [bold]Package:[/bold]     {srv.package}")
    console.print(f"  [bold]Category:[/bold]    {srv.category}")
    console.print(f"  [bold]Description:[/bold] {srv.description}")
    console.print(f"  [bold]Server Type:[/bold] {srv.server_type}")
    console.print(f"  [bold]Install:[/bold]     {srv.install_command}")

    if srv.tags:
        console.print(f"  [bold]Tags:[/bold]        {', '.join(srv.tags)}")

    if srv.docs_url:
        console.print(f"  [bold]Docs:[/bold]        {srv.docs_url}")

    if srv.required_env:
        console.print(f"\n  [bold]Required Environment Variables:[/bold]")
        for ev in srv.required_env:
            console.print(f"    • {ev.name} — {ev.description}")

    if srv.recommended_for:
        rec = srv.recommended_for
        if rec.skills or rec.agents or rec.bundles:
            console.print(f"\n  [bold]Recommended For:[/bold]")
            if rec.skills:
                console.print(f"    Skills:  {', '.join(rec.skills)}")
            if rec.agents:
                console.print(f"    Agents:  {', '.join(rec.agents)}")
            if rec.bundles:
                console.print(f"    Bundles: {', '.join(rec.bundles)}")

    if srv.args_template:
        console.print(f"\n  [bold]Args Template:[/bold] {' '.join(srv.args_template)}")

    console.print()


# ── catalog recommend (FR-CAT-034) ─────────────────────────────


@catalog_app.command("recommend")
def catalog_recommend_cmd() -> None:
    """Recommend MCP servers based on your installed skills and bundles."""
    cat = _load_catalog_or_exit()

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    result = cat.recommend(reg)

    required = result.get("required", [])
    recommended = result.get("recommended", [])

    if is_json():
        print_json(json_envelope(
            command="catalog recommend",
            data=result,
        ))
        return

    if not required and not recommended:
        print_info(
            "No skills installed with MCP dependencies. "
            "Install skills first to get MCP recommendations."
        )
        console.print("  Run [bold]archon install --all[/bold] to install skills.")
        return

    console.print()

    if required:
        console.print("[bold]Required by your skills:[/bold]")
        for item in required:
            srv = item["server"]
            name = srv.get("name", "?")
            desc = srv.get("description", "")
            refs = ", ".join(item.get("referenced_by", []))
            if item.get("in_catalog"):
                console.print(f"  • {name} — {desc} (used by: {refs})")
            else:
                console.print(f"  • {name} — [dim]not in catalog — configure manually[/dim] (used by: {refs})")
        console.print()

    if recommended:
        console.print("[bold]Also recommended:[/bold]")
        for item in recommended:
            srv = item["server"]
            name = srv.get("name", "?")
            desc = srv.get("description", "")
            refs = ", ".join(item.get("referenced_by", []))
            console.print(f"  • {name} — {desc} (used by: {refs})")
        console.print()


# ── catalog install (FR-CAT-035) ───────────────────────────────


@catalog_app.command("install")
def catalog_install_cmd(
    server: str = typer.Argument(..., help="Server name to install (e.g., github)."),
    platform: Optional[str] = typer.Option(
        None, "--platform", "-p",
        help="Target platform. Defaults to claude-code.",
    ),
) -> None:
    """Generate platform MCP config for a server."""
    cat = _load_catalog_or_exit()

    srv = cat.find_server(server)
    if not srv:
        similar = cat.similar_names(server)
        msg = f"Server '{server}' not found in catalog."
        if similar:
            msg += f" Did you mean: {', '.join(similar)}?"
        print_error(msg)
        raise typer.Exit(1)

    # Determine target platforms
    if platform:
        if platform not in PLATFORM_CONFIGS:
            print_error(
                f"Unknown platform '{platform}'. "
                f"Supported: {', '.join(SUPPORTED_PLATFORMS)}"
            )
            raise typer.Exit(1)
        target_platforms = [platform]
    else:
        detected = get_detected_platform_ids()
        target_platforms = [p for p in detected if p in PLATFORM_CONFIGS]
        if not target_platforms:
            print_error(
                "No supported platforms detected. "
                f"Use --platform to specify one of: {', '.join(SUPPORTED_PLATFORMS)}"
            )
            raise typer.Exit(1)

    results: list[dict] = []

    for pid in target_platforms:
        try:
            status = merge_into_config(srv, pid)
            config_path = get_platform_config_path(pid)
            results.append({
                "platform": pid,
                "status": status,
                "config_path": str(config_path),
            })
        except ValueError as exc:
            results.append({
                "platform": pid,
                "status": "error",
                "error": str(exc),
            })
        except PermissionError:
            results.append({
                "platform": pid,
                "status": "error",
                "error": f"Permission denied writing to {get_platform_config_path(pid)}",
            })
        except OSError as exc:
            results.append({
                "platform": pid,
                "status": "error",
                "error": str(exc),
            })

    if is_json():
        print_json(json_envelope(
            command="catalog install",
            data={
                "server": srv.name,
                "results": results,
                "install_command": srv.install_command,
            },
        ))
        return

    # Rich output
    console.print()
    for r in results:
        pid = r["platform"]
        status = r["status"]
        if status == "added":
            print_success(f"Added '{srv.name}' to {pid} config ({r['config_path']})")
        elif status == "already_configured":
            print_info(f"Server '{srv.name}' is already configured for {pid}.")
        elif status == "error":
            print_error(f"{pid}: {r.get('error', 'Unknown error')}")

    # Print install command
    print_info(f"Install the server package: {srv.install_command}")

    # Warn about unset env vars
    for ev in srv.required_env:
        if not os.environ.get(ev.name):
            print_warning(f"Set environment variable {ev.name}: {ev.description}")

    console.print()


# ── catalog check (FR-CAT-036) ─────────────────────────────────


@catalog_app.command("check")
def catalog_check_cmd() -> None:
    """Audit MCP config against installed skills' dependencies."""
    cat = _load_catalog_or_exit()

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    missing = check_dependencies(cat, reg)

    if is_json():
        print_json(json_envelope(
            command="catalog check",
            data={
                "satisfied": len(missing) == 0,
                "missing_count": len(missing),
                "missing": [
                    {
                        "skill_name": m.skill_name,
                        "server_name": m.server_name,
                        "platforms_missing": m.platforms_missing,
                        "in_catalog": m.in_catalog,
                    }
                    for m in missing
                ],
            },
        ))
        return

    console.print()
    if not missing:
        print_success("All MCP dependencies satisfied ✓")
    else:
        console.print(f"[bold]MCP Dependency Audit[/bold] ({len(missing)} issue{'s' if len(missing) != 1 else ''}):\n")
        for m in missing:
            platforms_str = ", ".join(m.platforms_missing)
            console.print(
                f"  [yellow]⚠[/yellow] Skill '{m.skill_name}' requires MCP server "
                f"'{m.server_name}' but it is not configured ({platforms_str})"
            )
            if m.in_catalog:
                console.print(f"    → Run: archon catalog install {m.server_name}")
            else:
                console.print(f"    → Server '{m.server_name}' is not in the catalog — configure manually.")
    console.print()
