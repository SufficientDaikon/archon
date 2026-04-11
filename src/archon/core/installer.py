"""Installer — copies skill/agent files to platform directories.

Handles file copy, platform-specific adaptation, idempotency checks,
and installation recording (FR-013 through FR-022, FR-060, FR-066).
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import yaml

from archon.core.registry import Registry, Skill, Agent, Bundle
from archon.core.platform import PlatformInfo, detect_platforms, get_platform_info
from archon.core.config import record_install, get_install_records, remove_install_record
from archon.utils.output import print_success, print_error, print_warning, print_verbose


def _sanitize_path(name: str) -> str:
    """Prevent path traversal (FR-066)."""
    # Strip any ../ or absolute-path tricks
    safe = name.replace("..", "").replace("/", "").replace("\\", "")
    return safe or "unknown"


def install_skill_to_platform(
    skill: Skill,
    registry: Registry,
    platform: PlatformInfo,
    *,
    force: bool = False,
) -> bool:
    """Install a single skill to a single platform.

    Returns True on success.
    """
    source_dir = registry.root / skill.path
    if not source_dir.exists():
        print_error(f"Skill source not found: {source_dir}")
        return False

    target = platform.skills_target
    if target is None:
        print_warning(f"Platform '{platform.id}' has no skills target directory configured.")
        return False

    safe_name = _sanitize_path(skill.name)
    target_dir = target / safe_name

    # Idempotency check (FR-015)
    if target_dir.exists() and not force:
        # Check version
        installed_manifest = target_dir / "manifest.yaml"
        if installed_manifest.exists():
            try:
                with open(installed_manifest, "r", encoding="utf-8") as fh:
                    existing = yaml.safe_load(fh) or {}
                if existing.get("version") == skill.version:
                    print_verbose(f"  {skill.name} already installed at v{skill.version} on {platform.id} — skipped")
                    return True
                else:
                    old_ver = existing.get("version", "unknown")
                    print_verbose(f"  Upgrading {skill.name} {old_ver} → {skill.version} on {platform.id}")
            except Exception:
                pass
        # Remove old version for upgrade
        shutil.rmtree(target_dir, ignore_errors=True)

    # Ensure parent exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy skill files
    try:
        for item in source_dir.iterdir():
            if item.name.startswith("."):
                continue
            dest = target_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # Record installation (FR-067)
        record_install(
            component_name=skill.name,
            component_type="skill",
            version=skill.version,
            platform=platform.id,
            install_path=str(target_dir),
        )
        return True

    except PermissionError as exc:
        print_error(f"Permission denied writing to {target_dir}: {exc}")
        # Clean up partial install
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        return False
    except Exception as exc:
        print_error(f"Failed to install {skill.name} to {platform.id}: {exc}")
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        return False


def uninstall_skill_from_platform(
    skill_name: str,
    platform: PlatformInfo,
) -> bool:
    """Remove a skill from a platform. Returns True if files were removed."""
    if platform.skills_target is None:
        return False
    target_dir = platform.skills_target / _sanitize_path(skill_name)
    if not target_dir.exists():
        return False
    try:
        shutil.rmtree(target_dir)
        remove_install_record(skill_name, platform.id)
        return True
    except Exception as exc:
        print_error(f"Failed to remove {skill_name} from {platform.id}: {exc}")
        return False


def resolve_target_platforms(
    registry: Registry,
    platform_filter: str | None = None,
) -> list[PlatformInfo]:
    """Determine which platforms to target.

    If *platform_filter* is given, return only that platform (even if not
    detected). Otherwise return all detected platforms.
    """
    all_platforms = detect_platforms()
    if platform_filter:
        for p in all_platforms:
            if p.id == platform_filter:
                return [p]
        # Unknown platform
        print_error(
            f"Platform '{platform_filter}' not recognized. "
            f"Valid platforms: {', '.join(p.id for p in all_platforms)}"
        )
        return []
    return [p for p in all_platforms if p.detected]
