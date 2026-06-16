#!/usr/bin/env python3
"""export_protocols.py — Generate all Archon protocol surface files.

Writes:
  agent-cards.json      — Machine-readable agent card index
  .well-known/agent.json — A2A AgentCard (schema version 0.2.1)
  .well-known/agents/   — Per-agent A2A cards
  mcp-tools.json        — MCP tool schemas for all skills

Usage:
    python scripts/export_protocols.py [--root <path>]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Archon protocol surface files (agent-cards, A2A, MCP)",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Path to Archon project root (default: parent of this script)",
    )
    args = parser.parse_args()

    root = Path(args.root) if args.root else Path(__file__).parent.parent
    root = root.resolve()

    if not root.exists():
        print(f"ERROR: root path does not exist: {root}", file=sys.stderr)
        return 1

    # Ensure src is importable
    src = root / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))

    try:
        from archon.core.agent_cards import write_agent_cards, write_a2a_cards
        from archon.core.skill_mcp_schema import write_mcp_tools_manifest
    except ImportError as e:
        print(f"ERROR: Cannot import Archon core modules: {e}", file=sys.stderr)
        print("Make sure you are running from the omniskill project root.", file=sys.stderr)
        return 1

    errors = []

    # 1. agent-cards.json
    try:
        result = write_agent_cards(root)
        print(f"  agent-cards.json     {result['agent_count']} agents  ({result['size']:,} bytes)")
    except Exception as e:
        errors.append(f"agent-cards.json: {e}")
        print(f"  agent-cards.json     FAILED: {e}")

    # 2. .well-known/agent.json (A2A)
    try:
        a2a_path = write_a2a_cards(root)
        count = len(__import__('json').loads(a2a_path.read_text()))
        print(f"  .well-known/agent.json  {count} agents")
    except Exception as e:
        errors.append(f".well-known/agent.json: {e}")
        print(f"  .well-known/agent.json  FAILED: {e}")

    # 3. mcp-tools.json
    try:
        mcp_path = write_mcp_tools_manifest(root)
        data = __import__('json').loads(mcp_path.read_text())
        count = len(data.get("tools", []))
        print(f"  mcp-tools.json       {count} tools  ({mcp_path.stat().st_size:,} bytes)")
    except Exception as e:
        errors.append(f"mcp-tools.json: {e}")
        print(f"  mcp-tools.json       FAILED: {e}")

    if errors:
        print(f"\n{len(errors)} error(s) occurred.")
        return 1

    print("\nAll protocol files exported successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
