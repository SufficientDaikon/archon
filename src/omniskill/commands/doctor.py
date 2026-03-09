"""``omniskill doctor`` — health diagnostics (US-3, FR-023 through FR-027)."""

from __future__ import annotations

import typer

from omniskill.core.registry import Registry
from omniskill.core.platform import detect_platforms
from omniskill.core.config import is_initialized, load_config, get_install_records
from omniskill.utils.output import (
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

    return max(0, min(100, score))


def doctor_cmd() -> None:
    """Run health diagnostics and display a report."""

    issues: list[dict] = []

    # ── Initialization check ────────────────────────────────────
    initialized = is_initialized()
    if not initialized:
        issues.append({
            "severity": "error",
            "message": "OMNISKILL is not initialized.",
            "remediation": "Run: omniskill init",
        })

    # ── Registry check ──────────────────────────────────────────
    registry_ok = False
    skills_count = 0
    agents_count = 0
    bundles_count = 0
    pipelines_count = 0
    version = "unknown"

    try:
        reg = Registry()
        reg.load()
        registry_ok = True
        skills_count = len(reg.skills)
        agents_count = len(reg.agents)
        bundles_count = len(reg.bundles)
        pipelines_count = len(reg.pipelines)
        version = reg.version
    except FileNotFoundError:
        issues.append({
            "severity": "error",
            "message": "Registry (omniskill.yaml) not found.",
            "remediation": "Ensure OMNISKILL_ROOT is set or run from the omniskill directory.",
        })
    except Exception as exc:
        issues.append({
            "severity": "error",
            "message": f"Registry error: {exc}",
            "remediation": "Check omniskill.yaml for syntax errors.",
        })

    # ── Platform detection (FR-024) ─────────────────────────────
    platforms = detect_platforms()
    detected = [p for p in platforms if p.detected]

    if not detected:
        issues.append({
            "severity": "warning",
            "message": "No AI platforms detected.",
            "remediation": "Install at least one supported platform (Claude Code, Copilot CLI, Cursor, etc.).",
        })

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
                "remediation": f"Run: omniskill install --platform {p.id} --all",
            })
            status["healthy"] = False
        else:
            status["healthy"] = p.detected
        platform_statuses.append(status)

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
                    "bundles": bundles_count,
                    "pipelines": pipelines_count,
                },
                "platforms": platform_statuses,
                "installed_components": total_installed,
                "issues": issues,
            },
        ))
        return

    # ── Rich output ─────────────────────────────────────────────
    console.print()
    console.rule("[bold cyan]OMNISKILL Health Report[/bold cyan]")
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
    console.print(f"  Skills:    {skills_count}")
    console.print(f"  Agents:    {agents_count}")
    console.print(f"  Bundles:   {bundles_count}")
    console.print(f"  Pipelines: {pipelines_count}")
    console.print(f"  Installed: {total_installed} record(s)")
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
