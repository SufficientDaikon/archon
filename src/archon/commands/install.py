"""``archon install`` — install skills, bundles, agents (US-2, FR-013 through FR-018)."""

from __future__ import annotations

from typing import Optional

import typer

from archon.core.registry import Registry
from archon.core.installer import (
    install_skill_to_platform,
    resolve_target_platforms,
)
from archon.core.platform import PlatformInfo
from archon.utils.output import (
    console, print_success, print_error, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json, get_progress,
)


def install_cmd(
    skill: Optional[str] = typer.Option(None, "--skill", "-s", help="Install a specific skill."),
    bundle: Optional[str] = typer.Option(None, "--bundle", "-b", help="Install a bundle of skills."),
    synapse: Optional[str] = typer.Option(None, "--synapse", help="Install a specific synapse."),
    all_flag: bool = typer.Option(False, "--all", "-a", help="Install all skills, agents, and synapses."),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Target a specific platform."),
    force: bool = typer.Option(False, "--force", "-f", help="Force reinstall even if up to date."),
) -> None:
    """Install skills, bundles, synapses, or agents to detected platform(s)."""

    if not skill and not bundle and not synapse and not all_flag:
        print_error("Specify --skill <name>, --bundle <name>, or --all.")
        print_info("Run [bold]archon list[/bold] to see available components.")
        raise typer.Exit(1)

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    targets = resolve_target_platforms(reg, platform)
    if not targets:
        print_error("No target platforms found. Run [bold]archon init[/bold] first or use --platform.")
        raise typer.Exit(1)

    results: list[dict] = []

    # ── Install a single skill ──────────────────────────────────
    if skill:
        sk = reg.find_skill(skill)
        if not sk:
            similar = reg.similar_names(skill)
            msg = f"Skill '{skill}' not found in the registry."
            if similar:
                msg += f" Did you mean: {', '.join(similar)}?"
            print_error(msg)
            if is_json():
                print_json(json_envelope(
                    command="install",
                    status="error",
                    errors=[{"code": "NOT_FOUND", "message": msg, "detail": skill, "remediation": "Run archon list skills"}],
                ))
            raise typer.Exit(1)

        reg.load_skill_manifest(sk)
        for plat in targets:
            ok = install_skill_to_platform(sk, reg, plat, force=force)
            results.append({"skill": sk.name, "platform": plat.id, "success": ok})
            if ok:
                print_success(f"Installed [bold]{sk.name}[/bold] v{sk.version} → {plat.name}")
            else:
                print_error(f"Failed to install {sk.name} to {plat.name}")

    # ── Install a bundle ────────────────────────────────────────
    elif bundle:
        bnd = reg.find_bundle(bundle)
        if not bnd:
            similar = reg.similar_names(bundle)
            msg = f"Bundle '{bundle}' not found."
            if similar:
                msg += f" Did you mean: {', '.join(similar)}?"
            print_error(msg)
            raise typer.Exit(1)

        if not is_json():
            console.print(f"\n[bold]Installing bundle:[/bold] {bnd.name} ({len(bnd.skills)} skills)")

        def _install_bundle_skills():
            for skill_name in bnd.skills:
                sk = reg.find_skill(skill_name)
                if not sk:
                    print_warning(f"  Skill '{skill_name}' in bundle not found in registry — skipping")
                    continue
                reg.load_skill_manifest(sk)
                for plat in targets:
                    ok = install_skill_to_platform(sk, reg, plat, force=force)
                    results.append({"skill": sk.name, "platform": plat.id, "success": ok})

        if is_json():
            _install_bundle_skills()
        else:
            with get_progress() as progress:
                task = progress.add_task(f"Installing {bnd.name}", total=len(bnd.skills) * len(targets))
                for skill_name in bnd.skills:
                    sk = reg.find_skill(skill_name)
                    if not sk:
                        print_warning(f"  Skill '{skill_name}' in bundle not found in registry — skipping")
                        progress.advance(task, len(targets))
                        continue
                    reg.load_skill_manifest(sk)
                    for plat in targets:
                        ok = install_skill_to_platform(sk, reg, plat, force=force)
                        results.append({"skill": sk.name, "platform": plat.id, "success": ok})
                        progress.advance(task)

            ok_count = sum(1 for r in results if r["success"])
            total = len(results)
            console.print(f"\n  {ok_count}/{total} installations succeeded.")

    # ── Install a single synapse ────────────────────────────────
    elif synapse:
        syn = reg.find_synapse(synapse)
        if not syn:
            similar = reg.similar_names(synapse)
            msg = f"Synapse '{synapse}' not found in the registry."
            if similar:
                msg += f" Did you mean: {', '.join(similar)}?"
            print_error(msg)
            raise typer.Exit(1)

        reg.load_synapse_manifest(syn)
        synapse_dir = reg.root / syn.path
        for plat in targets:
            ok = _install_synapse_to_platform(synapse_dir, syn, plat)
            results.append({"skill": syn.name, "platform": plat.id, "success": ok})
            if ok and not is_json():
                print_success(f"Installed synapse [bold]{syn.name}[/bold] v{syn.version} → {plat.name}")
            elif not ok and not is_json():
                print_error(f"Failed to install synapse {syn.name} to {plat.name}")

    # ── Install all ─────────────────────────────────────────────
    elif all_flag:
        total_tasks = len(reg.skills) * len(targets)
        if not is_json():
            console.print(f"\n[bold]Installing all {len(reg.skills)} skills to {len(targets)} platform(s)[/bold]")

        def _install_all_skills():
            for sk in reg.skills:
                reg.load_skill_manifest(sk)
                for plat in targets:
                    ok = install_skill_to_platform(sk, reg, plat, force=force)
                    results.append({"skill": sk.name, "platform": plat.id, "success": ok})

        if is_json():
            _install_all_skills()
        else:
            with get_progress() as progress:
                task = progress.add_task("Installing all", total=total_tasks)
                for sk in reg.skills:
                    reg.load_skill_manifest(sk)
                    for plat in targets:
                        ok = install_skill_to_platform(sk, reg, plat, force=force)
                        results.append({"skill": sk.name, "platform": plat.id, "success": ok})
                        progress.advance(task)

        ok_count = sum(1 for r in results if r["success"])
        if not is_json():
            console.print(f"\n  {ok_count}/{len(results)} installations succeeded.")

        # Also install all synapses
        if reg.synapses:
            if not is_json():
                console.print(f"\n[bold]Installing {len(reg.synapses)} synapse(s)[/bold]")
            for syn in reg.synapses:
                reg.load_synapse_manifest(syn)
                synapse_dir = reg.root / syn.path
                for plat in targets:
                    ok = _install_synapse_to_platform(synapse_dir, syn, plat)
                    results.append({"skill": syn.name, "platform": plat.id, "success": ok})
                    if ok and not is_json():
                        print_success(f"Installed synapse [bold]{syn.name}[/bold] → {plat.name}")

    # ── JSON output ─────────────────────────────────────────────
    if is_json():
        ok_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - ok_count
        print_json(json_envelope(
            command="install",
            status="success" if fail_count == 0 else "error",
            data={
                "installed": ok_count,
                "failed": fail_count,
                "results": results,
            },
            errors=[{"code": "INSTALL_FAILED", "message": f"{fail_count} installations failed"}] if fail_count else [],
        ))

    # Exit with 1 if any install failed
    if any(not r["success"] for r in results):
        raise typer.Exit(1)


def _install_synapse_to_platform(synapse_dir, synapse, platform) -> bool:
    """Install a synapse to a platform target directory."""
    try:
        target_base = platform.skills_target
        if not target_base:
            return False
        synapse_target = target_base / "_synapses" / synapse.name
        synapse_target.mkdir(parents=True, exist_ok=True)

        # Copy SYNAPSE.md
        src_md = synapse_dir / "SYNAPSE.md"
        if src_md.exists():
            import shutil
            shutil.copy2(src_md, synapse_target / "SYNAPSE.md")

        # Copy resources directory
        src_resources = synapse_dir / "resources"
        if src_resources.exists() and src_resources.is_dir():
            import shutil
            dst_resources = synapse_target / "resources"
            if dst_resources.exists():
                shutil.rmtree(dst_resources)
            shutil.copytree(src_resources, dst_resources)

        # Update _synapses-index.md
        index_path = target_base / "_synapses" / "_synapses-index.md"
        _update_synapse_index(index_path, synapse)

        return True
    except Exception:
        return False


def _update_synapse_index(index_path, synapse) -> None:
    """Create or update the _synapses-index.md file listing installed core synapses."""
    entries: dict[str, str] = {}

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        import re as _re
        for match in _re.finditer(r"^- \*\*(.+?)\*\*", content, _re.MULTILINE):
            entries[match.group(1)] = match.group(0)

    entries[synapse.name] = f"- **{synapse.name}** (v{synapse.version}, {synapse.synapse_type}) — {synapse.description}"

    lines = [
        "# Installed Synapses Index",
        "",
        "> Core synapses listed below should be injected into every agent interaction.",
        "> These provide cognitive enhancements (e.g., metacognition) that improve reasoning quality.",
        "",
    ]
    for name in sorted(entries):
        lines.append(entries[name])
    lines.append("")

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines), encoding="utf-8")
