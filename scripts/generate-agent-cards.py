#!/usr/bin/env python3
"""Generate agent-cards.json for the Archon framework.

Standalone script — works with only Python 3.10+ and PyYAML installed.
If the archon package is installed, uses its core module for generation.
Otherwise, uses a self-contained fallback implementation.

Usage:
    python scripts/generate-agent-cards.py                     # Generate agent-cards.json
    python scripts/generate-agent-cards.py --output ./dist/    # Custom output directory
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ARCHON_ROOT = Path(__file__).resolve().parent.parent


# ── Fallback implementation (stdlib + pyyaml only) ──────────────


def _fallback_generate(root: Path, registry: dict) -> str:
    """Generate agent-cards.json content using raw YAML data."""
    version = registry.get("version", "0.0.0")
    agents_data: list[dict] = []

    for entry in sorted(registry.get("agents", []), key=lambda e: e["name"]):
        agent_name = entry["name"]
        agent_path = entry.get("path", f"agents/{agent_name}")
        manifest_file = root / agent_path / "agent-manifest.yaml"

        manifest: dict = {}
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as fh:
                    manifest = yaml.safe_load(fh) or {}
            except Exception:
                pass

        card_data = manifest.get("card")
        card_out = None
        if card_data and isinstance(card_data, dict):
            card_out = {
                "capabilities": card_data.get("capabilities", {}),
                "skills-provided": card_data.get("skills-provided", []),
                "input-modes": card_data.get("input-modes", []),
                "output-modes": card_data.get("output-modes", []),
                "cost-tier": card_data.get("cost-tier", "standard"),
                "avg-tokens": card_data.get("avg-tokens", {}),
                "quality-metrics": card_data.get("quality-metrics"),
            }

        agents_data.append({
            "name": agent_name,
            "version": manifest.get("version", "0.0.0"),
            "role": manifest.get("role", ""),
            "description": manifest.get("description", ""),
            "path": agent_path,
            "card": card_out,
        })

    index = {
        "$schema": "archon-agent-cards-v1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "framework_version": version,
        "agents": agents_data,
    }

    return json.dumps(index, indent=2, ensure_ascii=False)


# ── Main ────────────────────────────────────────────────────────

def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Generate agent-cards.json for Archon")
    parser.add_argument("--output", type=str, default=None, help="Output directory (default: repo root)")
    args = parser.parse_args()

    root = ARCHON_ROOT
    if not (root / "archon.yaml").exists():
        print(f"Error: archon.yaml not found at {root}. Run this script from the Archon repository root.", file=sys.stderr)
        return 1

    output_dir = Path(args.output) if args.output else root
    if output_dir.exists() and output_dir.is_file():
        print(f"Error: Output path is a file, not a directory: {output_dir}", file=sys.stderr)
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()

    # Try the archon package first
    try:
        from archon.core.agent_cards import write_agent_cards as _write
        result = _write(root, output_dir=output_dir)
    except ImportError:
        # Fallback: self-contained implementation
        with open(root / "archon.yaml", "r", encoding="utf-8") as fh:
            registry = yaml.safe_load(fh) or {}

        content = _fallback_generate(root, registry)
        file_path = output_dir / "agent-cards.json"
        file_path.write_text(content, encoding="utf-8", newline="\n")

        data = json.loads(content)
        result = {
            "path": file_path,
            "size": file_path.stat().st_size,
            "agent_count": len(data.get("agents", [])),
        }

    elapsed = time.time() - start

    # Print summary
    size_kb = result["size"] / 1024
    print(f"\n✅ agent-cards.json generation complete\n")
    print(f"  📄 {result['path']}  ({size_kb:.1f} KB)")
    print(f"  🤖 Agents: {result['agent_count']}")
    print(f"  ⏱️  Time: {elapsed:.2f}s\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
