"""Platform detection and management.

Detects installed AI coding platforms by checking known filesystem markers
(FR-059) and provides metadata about each platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PlatformInfo:
    """Metadata about a single detected platform."""

    id: str
    name: str
    detected: bool = False
    marker_path: Optional[Path] = None
    skills_target: Optional[Path] = None
    scope: str = "global"  # "global" or "project"
    installed_skills: list[str] = field(default_factory=list)


# ── Detection markers (FR-059) ──────────────────────────────────

PLATFORM_DEFS: list[dict] = [
    {
        "id": "claude-code",
        "name": "Claude Code",
        "markers_home": [".claude"],
        "markers_cwd": [],
        "scope": "global",
        "skills_dir": ".claude/skills",
    },
    {
        "id": "copilot-cli",
        "name": "Copilot CLI",
        "markers_home": [".copilot"],
        "markers_cwd": [],
        "scope": "global",
        "skills_dir": ".copilot/skills",
    },
    {
        "id": "cursor",
        "name": "Cursor",
        "markers_home": [".cursor"],
        "markers_cwd": [".cursor", ".cursorrules"],
        "scope": "project",
        "skills_dir": ".cursor/rules",
    },
    {
        "id": "windsurf",
        "name": "Windsurf",
        "markers_home": [".windsurf"],
        "markers_cwd": [".windsurfrules", ".windsurf"],
        "scope": "project",
        "skills_dir": None,  # uses .windsurfrules file
    },
    {
        "id": "antigravity",
        "name": "Antigravity",
        "markers_home": [".antigravity"],
        "markers_cwd": [".antigravity"],
        "scope": "project",
        "skills_dir": ".antigravity/skills",
    },
]


def detect_platforms(cwd: Path | None = None) -> list[PlatformInfo]:
    """Detect all installed AI coding platforms.

    Checks both ``~`` (home) and the current working directory for
    platform markers.  Returns a :class:`PlatformInfo` for every
    *known* platform — ``detected`` is ``True`` only when a marker is found.
    """
    home = Path.home()
    cwd = cwd or Path.cwd()
    results: list[PlatformInfo] = []

    for pdef in PLATFORM_DEFS:
        detected = False
        marker_path: Optional[Path] = None

        # Check home-directory markers
        for marker in pdef["markers_home"]:
            p = home / marker
            if p.exists():
                detected = True
                marker_path = p
                break

        # Check cwd markers
        if not detected:
            for marker in pdef["markers_cwd"]:
                p = cwd / marker
                if p.exists():
                    detected = True
                    marker_path = p
                    break

        # Determine skills target
        skills_target: Optional[Path] = None
        if pdef["skills_dir"]:
            if pdef["scope"] == "global":
                skills_target = home / pdef["skills_dir"]
            else:
                skills_target = cwd / pdef["skills_dir"]

        # Count installed skills
        installed: list[str] = []
        if detected and skills_target and skills_target.exists():
            for item in skills_target.iterdir():
                if item.is_dir():
                    if (item / "SKILL.md").exists() or (item / "manifest.yaml").exists():
                        installed.append(item.name)
                elif item.suffix in (".md", ".mdc"):
                    installed.append(item.stem)

        results.append(PlatformInfo(
            id=pdef["id"],
            name=pdef["name"],
            detected=detected,
            marker_path=marker_path,
            skills_target=skills_target,
            scope=pdef["scope"],
            installed_skills=installed,
        ))

    return results


def get_detected_platform_ids(cwd: Path | None = None) -> list[str]:
    """Return only the IDs of detected platforms."""
    return [p.id for p in detect_platforms(cwd) if p.detected]


def get_platform_info(platform_id: str, cwd: Path | None = None) -> PlatformInfo | None:
    """Get info for a specific platform."""
    for p in detect_platforms(cwd):
        if p.id == platform_id:
            return p
    return None
