"""Cross-platform path resolution for OMNISKILL CLI.

Resolves OMNISKILL_HOME, the framework root (where omniskill.yaml lives),
platform-specific config directories, and installation targets.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from platformdirs import user_config_dir, user_data_dir


def get_omniskill_home() -> Path:
    """Return the OMNISKILL user-config home directory.

    Resolution order:
      1. ``OMNISKILL_HOME`` environment variable
      2. ``~/.omniskill/`` (default)
    """
    env = os.environ.get("OMNISKILL_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".omniskill"


def get_config_path() -> Path:
    """Return the path to the user config file.

    Resolution order:
      1. ``OMNISKILL_CONFIG`` environment variable
      2. ``<omniskill_home>/config.yaml``
    """
    env = os.environ.get("OMNISKILL_CONFIG")
    if env:
        return Path(env).expanduser().resolve()
    return get_omniskill_home() / "config.yaml"


def get_state_path() -> Path:
    """Return the path to the install-state file."""
    return get_omniskill_home() / "state.yaml"


def get_omniskill_root() -> Path:
    """Return the OMNISKILL framework root (where omniskill.yaml lives).

    Resolution order:
      1. ``OMNISKILL_ROOT`` environment variable
      2. Walk upwards from this file's location to find ``omniskill.yaml``
      3. Current working directory if it contains ``omniskill.yaml``
    """
    # 1. Environment variable
    env = os.environ.get("OMNISKILL_ROOT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "omniskill.yaml").exists():
            return p

    # 2. Walk up from the package install location
    #    When installed as editable or in the repo, the package is at
    #    <repo>/src/omniskill/ so walking up 3 levels reaches the repo root.
    pkg_dir = Path(__file__).resolve().parent  # utils/
    for ancestor in [pkg_dir.parent, pkg_dir.parent.parent, pkg_dir.parent.parent.parent]:
        if (ancestor / "omniskill.yaml").exists():
            return ancestor

    # 3. Current working directory
    cwd = Path.cwd()
    if (cwd / "omniskill.yaml").exists():
        return cwd

    # Fallback — raise later when the registry is actually loaded
    return Path.home() / "omniskill"


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
