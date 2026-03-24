"""Cross-platform path resolution for Archon CLI.

Resolves ARCHON_HOME, the framework root (where archon.yaml lives),
platform-specific config directories, and installation targets.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from platformdirs import user_config_dir, user_data_dir


def get_archon_home() -> Path:
    """Return the Archon user-config home directory.

    Resolution order:
      1. ``ARCHON_HOME`` environment variable
      2. ``~/.archon/`` (default)
    """
    env = os.environ.get("ARCHON_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".archon"


def get_config_path() -> Path:
    """Return the path to the user config file.

    Resolution order:
      1. ``ARCHON_CONFIG`` environment variable
      2. ``<archon_home>/config.yaml``
    """
    env = os.environ.get("ARCHON_CONFIG")
    if env:
        return Path(env).expanduser().resolve()
    return get_archon_home() / "config.yaml"


def get_state_path() -> Path:
    """Return the path to the install-state file."""
    return get_archon_home() / "state.yaml"


def get_archon_root() -> Path:
    """Return the Archon framework root (where archon.yaml lives).

    Resolution order:
      1. ``ARCHON_ROOT`` environment variable
      2. Walk upwards from this file's location to find ``archon.yaml``
      3. Current working directory if it contains ``archon.yaml``
    """
    # 1. Environment variable
    env = os.environ.get("ARCHON_ROOT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "archon.yaml").exists():
            return p

    # 2. Walk up from the package install location
    #    When installed as editable or in the repo, the package is at
    #    <repo>/src/archon/ so walking up 3 levels reaches the repo root.
    pkg_dir = Path(__file__).resolve().parent  # utils/
    for ancestor in [pkg_dir.parent, pkg_dir.parent.parent, pkg_dir.parent.parent.parent]:
        if (ancestor / "archon.yaml").exists():
            return ancestor

    # 3. Current working directory
    cwd = Path.cwd()
    if (cwd / "archon.yaml").exists():
        return cwd

    # Fallback — raise later when the registry is actually loaded
    return Path.home() / "archon"


def get_platform_target(platform_id: str) -> Optional[Path]:
    """Return the installation target directory for a given platform.

    These are the *default* paths. The user config may override them.
    """
    home = Path.home()
    cwd = Path.cwd()

    targets: dict[str, Path] = {
        "claude-code": home / ".claude" / "skills",
        "copilot-cli": home / ".copilot" / "skills",
        "cursor": cwd / ".cursor" / "rules",
        "windsurf": cwd,  # single file: .windsurfrules
        "antigravity": cwd / ".antigravity" / "skills",
    }
    return targets.get(platform_id)
