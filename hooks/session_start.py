"""
Archon Session Start Hook

Fires at session start to inject core discipline rules into the agent context.
Ensures anti-rationalization and sequential thinking synapses are loaded.
"""

from pathlib import Path
from typing import Any

ARCHON_ROOT = Path(__file__).parent.parent


def execute(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Session start hook. Injects core synapses and discipline context.

    Returns a dict with injected context that should be merged into agent state.
    """
    context = context or {}
    result: dict[str, Any] = {
        "status": "success",
        "injected": [],
        "warnings": [],
    }

    core_synapses = _load_core_synapses()
    for synapse_name, synapse_content in core_synapses.items():
        result["injected"].append(synapse_name)

    iron_laws = _load_iron_laws()
    if iron_laws:
        result["injected"].append("iron-laws")

    result["discipline"] = {
        "anti_rationalization": True,
        "sequential_thinking": True,
        "iron_laws_count": len(iron_laws) if iron_laws else 0,
        "core_synapses": list(core_synapses.keys()),
        "deviation_protocol": "STOP → DOCUMENT → ASK → LOG",
        "stuck_loop_threshold": 3,
        "escape_hatch_threshold": 3,
    }

    return result


def _load_core_synapses() -> dict[str, str]:
    """Load all core synapses (synapse-type: core in manifest)."""
    import yaml

    synapses: dict[str, str] = {}
    synapses_dir = ARCHON_ROOT / "synapses"

    if not synapses_dir.exists():
        return synapses

    for manifest_path in synapses_dir.glob("*/manifest.yaml"):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            if manifest.get("synapse-type") == "core":
                synapse_md = manifest_path.parent / "SYNAPSE.md"
                if synapse_md.exists():
                    synapses[manifest["name"]] = synapse_md.read_text(encoding="utf-8")
        except Exception:
            continue

    return synapses


def _load_iron_laws() -> list[str]:
    """Load Iron Laws from anti-rationalization synapse."""
    iron_laws_path = (
        ARCHON_ROOT / "synapses" / "anti-rationalization" / "resources" / "iron-laws.md"
    )
    if not iron_laws_path.exists():
        return []

    content = iron_laws_path.read_text(encoding="utf-8")
    laws = []
    for line in content.splitlines():
        if line.startswith("## Law "):
            laws.append(line.strip("# ").strip())

    return laws


if __name__ == "__main__":
    result = execute()
    print(f"Session start hook executed: {result['status']}")
    print(f"Injected: {result['injected']}")
    print(f"Discipline config: {result['discipline']}")
