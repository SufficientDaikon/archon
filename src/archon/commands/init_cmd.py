"""``archon init`` — first-time setup (US-1, FR-009 through FR-012).

Detects platforms, creates configuration, and installs the Virtuoso Engine
(cognitive kernel + all synapses) to detected platforms.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from archon.core.config import (
    is_initialized, load_config, save_config, VALID_KEYS,
)
from archon.core.platform import detect_platforms
from archon.core.virtuoso import install_virtuoso, get_virtuoso_xml_path
from archon.utils.output import (
    console, print_success, print_warning, print_info, print_error,
    is_json, json_envelope, print_json,
)
from archon.utils.paths import get_archon_home, get_config_path, get_archon_root


def init_cmd(
    platform: Optional[str] = typer.Option(
        None, "--platform", "-p",
        help="Configure for a specific platform only.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config."),
) -> None:
    """Initialize Archon — detect platforms and create configuration."""

    home_dir = get_archon_home()
    config_path = get_config_path()

    # FR-012: Detect existing configuration
    if is_initialized() and not force:
        if is_json():
            print_json(json_envelope(
                command="init",
                status="error",
                errors=[{
                    "code": "ALREADY_INITIALIZED",
                    "message": f"Archon is already initialized at {home_dir}",
                    "detail": str(config_path),
                    "remediation": "Use --force to reinitialize.",
                }],
            ))
            raise typer.Exit(1)
        print_warning(f"Archon is already initialized at [bold]{home_dir}[/bold]")
        print_info("Use [bold]--force[/bold] to reinitialize, or edit the config directly.")
        raise typer.Exit(1)

    # Create home directory
    home_dir.mkdir(parents=True, exist_ok=True)

    # FR-010: Detect platforms
    platforms = detect_platforms()
    detected = [p for p in platforms if p.detected]

    # FR-011: Filter to specific platform if requested
    if platform:
        detected = [p for p in platforms if p.id == platform]
        if not detected:
            valid_ids = ", ".join(p.id for p in platforms)
            print_error(f"Unknown platform '{platform}'. Valid platforms: {valid_ids}")
            raise typer.Exit(1)

    # Build config
    cfg = dict(VALID_KEYS)
    if detected:
        cfg["default_platform"] = detected[0].id

    # FR-009: Save configuration
    save_config(cfg)

    # ── Install Virtuoso Engine ──────────────────────────────────
    archon_root = get_archon_root()
    virtuoso_results: dict = {"installed": False, "synapses": 0}

    if detected:
        virtuoso_xml = get_virtuoso_xml_path(archon_root)
        if virtuoso_xml.exists():
            for p in detected:
                if p.skills_target is not None:
                    # Determine the platform's parent dir for CLAUDE.md
                    claude_dir = p.skills_target.parent
                    ok = install_virtuoso(archon_root, p.skills_target, claude_dir)
                    if ok:
                        virtuoso_results["installed"] = True
        else:
            if not is_json():
                print_warning("Virtuoso engine not found — skipping cognitive kernel install.")
                print_info(f"Expected at: {virtuoso_xml}")

    # ── Output ──────────────────────────────────────────────────

    if is_json():
        print_json(json_envelope(
            command="init",
            data={
                "home": str(home_dir),
                "config": str(config_path),
                "platforms_detected": [
                    {"id": p.id, "name": p.name, "scope": p.scope}
                    for p in detected
                ],
                "default_platform": cfg["default_platform"],
                "virtuoso": virtuoso_results,
            },
        ))
        return

    console.print()
    console.rule("[bold cyan]Archon Initialization[/bold cyan]")
    console.print()
    print_success(f"Configuration created at [bold]{config_path}[/bold]")
    console.print()

    if detected:
        console.print("[bold]Detected Platforms:[/bold]")
        for p in detected:
            icon = "🟢"
            console.print(f"  {icon} [bold]{p.name}[/bold] ({p.id}) — {p.scope}")
            if p.installed_skills:
                console.print(f"     {len(p.installed_skills)} skill(s) already installed")

        if virtuoso_results["installed"]:
            console.print()
            console.print("[bold]Virtuoso Engine:[/bold]")
            console.print("  🧠 Cognitive kernel installed (skills/virtuoso/SKILL.md)")
            console.print("  🧠 5 synapses installed (skills/_synapses/)")
    else:
        print_warning("No AI platforms detected.")
        console.print("  Supported platforms: claude-code, copilot-cli, cursor, windsurf, antigravity")
        console.print("  Install a platform, then run [bold]archon init[/bold] again,")
        console.print("  or specify one with [bold]archon init --platform <name>[/bold].")

    console.print()
    console.print("[muted]Next steps:[/muted]")
    console.print("  archon list            — browse available skills")
    console.print("  archon install --all   — install everything")
    console.print("  archon doctor          — health check")
    console.print()
