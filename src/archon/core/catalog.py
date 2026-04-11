"""MCP Server Integration Catalog — core module (FR-CAT-010 through FR-CAT-021).

Loads, queries, and reasons about the curated MCP server catalog.
Provides platform-specific config generation and dependency checking.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from archon.utils.paths import get_archon_root


# ── Data classes ────────────────────────────────────────────────


VALID_CATEGORIES: list[str] = sorted([
    "core", "development", "database", "research",
    "design", "ai", "cloud", "communication",
])
"""Sorted list of allowed MCP server categories."""


@dataclass
class EnvVar:
    """An environment variable required by an MCP server."""
    name: str
    description: str


@dataclass
class RecommendedFor:
    """Which Archon components benefit from an MCP server."""
    skills: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    bundles: list[str] = field(default_factory=list)


@dataclass
class McpServer:
    """A single MCP server catalog entry (FR-CAT-002 through FR-CAT-004)."""
    name: str
    package: str
    category: str
    description: str
    install_command: str
    tags: list[str]
    required_env: list[EnvVar] = field(default_factory=list)
    recommended_for: RecommendedFor | None = None
    docs_url: str = ""
    server_type: str = "stdio"
    args_template: list[str] = field(default_factory=list)


@dataclass
class MissingDependency:
    """A skill's MCP dependency that is not configured on a platform."""
    skill_name: str
    server_name: str
    platforms_missing: list[str] = field(default_factory=list)
    in_catalog: bool = False


# ── Platform config formats (FR-CAT-018) ───────────────────────


PLATFORM_CONFIGS: dict[str, dict[str, str]] = {
    "claude-code": {
        "path": "~/.claude/mcp.json",
        "root_key": "mcpServers",
    },
}

SUPPORTED_PLATFORMS: list[str] = sorted(PLATFORM_CONFIGS.keys())


# ── Catalog class (FR-CAT-011 through FR-CAT-016) ──────────────


class Catalog:
    """Loads and queries the MCP server catalog."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or get_archon_root()
        self.servers: list[McpServer] = []
        self._loaded = False

    def load(self) -> None:
        """Parse ``catalog/mcp-servers.yaml`` and populate server list (FR-CAT-011)."""
        catalog_path = self.root / "catalog" / "mcp-servers.yaml"
        if not catalog_path.exists():
            raise FileNotFoundError(
                f"MCP catalog not found at {catalog_path}. "
                "Ensure you are running from the Archon root or set ARCHON_ROOT."
            )

        with open(catalog_path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

        seen_names: set[str] = set()
        for entry in raw.get("servers", []):
            name = entry.get("name", "")
            if name in seen_names:
                # Duplicate name — silently use last one (dict behavior), but log
                self.servers = [s for s in self.servers if s.name != name]
            seen_names.add(name)

            # Parse required-env
            env_list: list[EnvVar] = []
            for ev in entry.get("required-env", []):
                if isinstance(ev, dict):
                    env_list.append(EnvVar(
                        name=ev.get("name", ""),
                        description=ev.get("description", ""),
                    ))

            # Parse recommended-for
            rec_data = entry.get("recommended-for")
            rec_for: RecommendedFor | None = None
            if isinstance(rec_data, dict):
                rec_for = RecommendedFor(
                    skills=rec_data.get("skills", []),
                    agents=rec_data.get("agents", []),
                    bundles=rec_data.get("bundles", []),
                )

            server = McpServer(
                name=name,
                package=entry.get("package", ""),
                category=entry.get("category", ""),
                description=entry.get("description", ""),
                install_command=entry.get("install-command", ""),
                tags=entry.get("tags", []),
                required_env=env_list,
                recommended_for=rec_for,
                docs_url=entry.get("docs-url", ""),
                server_type=entry.get("server-type", "stdio"),
                args_template=entry.get("args-template", []),
            )
            self.servers.append(server)

        self._loaded = True

    def ensure_loaded(self) -> None:
        """Load the catalog if not already loaded."""
        if not self._loaded:
            self.load()

    def list_servers(self, category: str | None = None) -> list[McpServer]:
        """Return all servers, optionally filtered by category (FR-CAT-012).

        Results sorted by category, then name.
        """
        self.ensure_loaded()
        servers = self.servers
        if category:
            servers = [s for s in servers if s.category == category]
        return sorted(servers, key=lambda s: (s.category, s.name))

    def search(self, query: str) -> list[tuple[float, McpServer]]:
        """Search servers by relevance scoring (FR-CAT-013).

        Scoring:
          exact name match = 100
          name contains query = 50
          tag exact match = 40
          description contains query = 20
          word overlap in name = 10
          word overlap in tags = 8
          word overlap in description = 5

        Returns list of (score, server) tuples sorted descending.
        """
        self.ensure_loaded()
        if not query.strip():
            return [(0, s) for s in self.list_servers()]

        q = query.lower()
        words = set(re.split(r"[\s\-_]+", q))
        results: list[tuple[float, McpServer]] = []

        for server in self.servers:
            score = 0.0
            n = server.name.lower()
            d = server.description.lower()
            t_text = " ".join(server.tags).lower()

            # Exact name match
            if q == n:
                score += 100
            elif q in n:
                score += 50

            # Tag exact match
            for tag in server.tags:
                if q == tag.lower():
                    score += 40
                    break

            # Description contains query
            if q in d:
                score += 20

            # Word overlap
            for w in words:
                if w in n:
                    score += 10
                if w in t_text:
                    score += 8
                if w in d:
                    score += 5

            if score > 0:
                results.append((score, server))

        results.sort(key=lambda x: -x[0])
        return results

    def find_server(self, name: str) -> McpServer | None:
        """Return a single server by exact name match (FR-CAT-014)."""
        self.ensure_loaded()
        for s in self.servers:
            if s.name == name:
                return s
        return None

    def similar_names(self, query: str, limit: int = 5) -> list[str]:
        """Return server names similar to *query* (FR-CAT-015).

        Uses the same fuzzy-match algorithm as Registry.similar_names.
        """
        self.ensure_loaded()
        query_lower = query.lower()
        scored: list[tuple[float, str]] = []

        for s in self.servers:
            n_lower = s.name.lower()
            score = 0.0
            if query_lower in n_lower:
                score += 10.0
            if n_lower in query_lower:
                score += 8.0
            # common prefix
            prefix_len = len(os.path.commonprefix([query_lower, n_lower]))
            score += prefix_len * 0.5
            # word overlap
            q_words = set(re.split(r"[-_ ]", query_lower))
            n_words = set(re.split(r"[-_ ]", n_lower))
            score += len(q_words & n_words) * 3.0
            if score > 0:
                scored.append((score, s.name))

        scored.sort(key=lambda x: -x[0])
        return [n for _, n in scored[:limit]]

    def recommend(self, registry: Any) -> dict[str, list[dict]]:
        """Recommend servers based on installed skills/bundles (FR-CAT-016).

        Returns dict with keys:
          ``required`` — servers required by installed skills' mcp-dependencies
          ``recommended`` — servers whose recommended-for matches installed components
        """
        self.ensure_loaded()
        registry.ensure_loaded()

        # Collect installed component names
        installed_skills = {s.name for s in registry.skills}
        installed_agents = {a.name for a in registry.agents}
        installed_bundles = {b.name for b in registry.bundles}

        # (a) Collect mcp-dependencies from skill manifests
        required: list[dict] = []
        dep_to_skills: dict[str, list[str]] = {}

        for skill in registry.skills:
            manifest = registry.load_skill_manifest(skill)
            deps = manifest.get("mcp-dependencies", [])
            for dep in deps:
                if dep not in dep_to_skills:
                    dep_to_skills[dep] = []
                dep_to_skills[dep].append(skill.name)

        # Cross-reference against catalog
        for dep_name, skill_names in dep_to_skills.items():
            server = self.find_server(dep_name)
            required.append({
                "server": _server_to_dict(server) if server else {"name": dep_name},
                "referenced_by": skill_names,
                "in_catalog": server is not None,
            })

        # (b) Check recommended-for on catalog entries
        recommended: list[dict] = []
        required_names = set(dep_to_skills.keys())

        for server in self.servers:
            if server.name in required_names:
                continue  # Already in required list
            if server.recommended_for is None:
                continue

            refs: list[str] = []
            for sk in server.recommended_for.skills:
                if sk in installed_skills:
                    refs.append(sk)
            for ag in server.recommended_for.agents:
                if ag in installed_agents:
                    refs.append(ag)
            for bn in server.recommended_for.bundles:
                if bn in installed_bundles:
                    refs.append(bn)

            if refs:
                recommended.append({
                    "server": _server_to_dict(server),
                    "referenced_by": refs,
                    "in_catalog": True,
                })

        return {"required": required, "recommended": recommended}

    def get_valid_categories(self) -> list[str]:
        """Return the sorted list of allowed category strings (FR-CAT-021)."""
        return list(VALID_CATEGORIES)


# ── Config generation (FR-CAT-017 through FR-CAT-019) ──────────


def get_platform_config_path(platform_id: str) -> Path:
    """Return the config file path for a platform."""
    cfg = PLATFORM_CONFIGS.get(platform_id)
    if not cfg:
        raise ValueError(
            f"Unknown platform '{platform_id}'. "
            f"Supported: {', '.join(SUPPORTED_PLATFORMS)}"
        )
    raw_path = cfg["path"]
    if raw_path.startswith("~"):
        return Path(raw_path).expanduser()
    return Path.cwd() / raw_path


def generate_platform_config(server: McpServer, platform_id: str) -> dict:
    """Generate a platform config entry for a server (FR-CAT-017).

    Returns the server entry dict (not the full config file).
    """
    cfg = PLATFORM_CONFIGS.get(platform_id)
    if not cfg:
        raise ValueError(f"Unknown platform '{platform_id}'.")

    # Build command + args from args_template
    if server.args_template:
        command = server.args_template[0]
        args = server.args_template[1:]
    else:
        # Fallback: use npx with the package name
        command = "npx"
        args = ["-y", server.package]

    # Build env dict
    env: dict[str, str] = {}
    for ev in server.required_env:
        val = os.environ.get(ev.name)
        if val:
            env[ev.name] = val
        else:
            env[ev.name] = f"YOUR_{ev.name}_HERE"

    entry: dict[str, Any] = {
        "command": command,
        "args": args,
    }
    if env:
        entry["env"] = env

    return entry


def read_platform_config(platform_id: str, config_path: Path | None = None) -> dict:
    """Read and parse the platform's MCP config file.

    Returns the parsed JSON dict, or an empty default structure if the file
    does not exist.
    """
    path = config_path or get_platform_config_path(platform_id)
    cfg = PLATFORM_CONFIGS.get(platform_id, {})
    root_key = cfg.get("root_key", "mcpServers")

    if not path.exists():
        return {root_key: {}}

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError:
        raise ValueError(
            f"Existing config at {path} is not valid JSON. "
            "Fix it manually or delete it."
        )

    if root_key not in data:
        data[root_key] = {}

    return data


def merge_into_config(
    server: McpServer,
    platform_id: str,
    config_path: Path | None = None,
) -> str:
    """Merge a server entry into the platform's config file (FR-CAT-019).

    Returns:
      - ``"added"`` if the server was added
      - ``"already_configured"`` if it was already present

    Raises ValueError if the config file is malformed JSON.
    Raises PermissionError, OSError on file-system errors.
    """
    path = config_path or get_platform_config_path(platform_id)
    cfg = PLATFORM_CONFIGS.get(platform_id, {})
    root_key = cfg.get("root_key", "mcpServers")

    # Read existing config
    data = read_platform_config(platform_id, path)

    # Check if already present
    if server.name in data.get(root_key, {}):
        return "already_configured"

    # Generate and add entry
    entry = generate_platform_config(server, platform_id)
    data[root_key][server.name] = entry

    # Write atomically (NFR-CAT-2)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.parent / f".{path.name}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        # Atomic rename
        tmp_path.replace(path)
    except Exception:
        # Clean up temp file if rename fails
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise

    return "added"


# ── Dependency checking (FR-CAT-020) ───────────────────────────


def check_dependencies(
    catalog: Catalog,
    registry: Any,
) -> list[MissingDependency]:
    """Check installed skills' MCP dependencies against platform configs.

    Returns a list of MissingDependency objects for any unmet dependencies.
    """
    from archon.core.platform import get_detected_platform_ids

    catalog.ensure_loaded()
    registry.ensure_loaded()

    # Read configs for all MCP-supported detected platforms
    detected = get_detected_platform_ids()
    mcp_platforms = [p for p in detected if p in PLATFORM_CONFIGS]

    platform_servers: dict[str, set[str]] = {}
    for pid in mcp_platforms:
        try:
            cfg = PLATFORM_CONFIGS[pid]
            data = read_platform_config(pid)
            root_key = cfg["root_key"]
            platform_servers[pid] = set(data.get(root_key, {}).keys())
        except (ValueError, OSError):
            platform_servers[pid] = set()

    missing: list[MissingDependency] = []

    for skill in registry.skills:
        manifest = registry.load_skill_manifest(skill)
        deps = manifest.get("mcp-dependencies", [])
        for dep in deps:
            platforms_missing = [
                pid for pid in mcp_platforms
                if dep not in platform_servers.get(pid, set())
            ]
            if platforms_missing:
                in_cat = catalog.find_server(dep) is not None
                missing.append(MissingDependency(
                    skill_name=skill.name,
                    server_name=dep,
                    platforms_missing=platforms_missing,
                    in_catalog=in_cat,
                ))

    return missing


# ── Helpers ─────────────────────────────────────────────────────


def _server_to_dict(server: McpServer) -> dict[str, Any]:
    """Convert an McpServer to a plain dict for JSON output."""
    d: dict[str, Any] = {
        "name": server.name,
        "package": server.package,
        "category": server.category,
        "description": server.description,
        "install_command": server.install_command,
        "tags": server.tags,
        "server_type": server.server_type,
    }
    if server.required_env:
        d["required_env"] = [
            {"name": ev.name, "description": ev.description}
            for ev in server.required_env
        ]
    if server.recommended_for:
        d["recommended_for"] = {
            "skills": server.recommended_for.skills,
            "agents": server.recommended_for.agents,
            "bundles": server.recommended_for.bundles,
        }
    if server.docs_url:
        d["docs_url"] = server.docs_url
    if server.args_template:
        d["args_template"] = server.args_template
    return d


def get_valid_categories() -> list[str]:
    """Return the sorted list of allowed category strings (FR-CAT-021)."""
    return list(VALID_CATEGORIES)
