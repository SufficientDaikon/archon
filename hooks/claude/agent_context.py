#!/usr/bin/env python3
"""SubagentStart hook — injects role-specific context into subagents.

Fires when Claude spawns a subagent. Based on agent type, slices context
so each agent gets only what's relevant to its role — not the full state.
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.state import load_state

# Agent type -> context builder mapping
AGENT_CONTEXT = {
    # Code-focused agents get project info + anti-rationalization
    "general-purpose": "code",
    "Plan": "code",
    # Exploration agents get project context only
    "Explore": "explore",
}


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    agent_type = input_data.get("agent_type", "")

    if not agent_type:
        print(json.dumps({}))
        return

    state = load_state()
    context_mode = AGENT_CONTEXT.get(agent_type, "code")
    context = build_agent_context(context_mode, state)

    if context:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SubagentStart",
                "additionalContext": context,
            }
        }
        print(json.dumps(output))
    else:
        print(json.dumps({}))


def build_agent_context(mode: str, state: dict) -> str:
    """Build role-specific context for the subagent."""
    project = state.get("project", {})
    session = state.get("session", {})
    git = state.get("git", {})

    if mode == "explore":
        # Minimal: just project info for orientation
        return (
            f'<archon-agent-context role="explore">\n'
            f'  <project type="{project.get("type", "")}" name="{project.get("name", "")}" '
            f'framework="{project.get("framework", "")}" />\n'
            f'  <git branch="{git.get("branch", "")}" />\n'
            f'</archon-agent-context>'
        )

    if mode == "code":
        files = session.get("files_modified", [])
        files_str = ", ".join(files[-5:]) if files else "none yet"
        tier = session.get("complexity_tier", "")

        return (
            f'<archon-agent-context role="code">\n'
            f'  <project type="{project.get("type", "")}" name="{project.get("name", "")}" '
            f'framework="{project.get("framework", "")}" />\n'
            f'  <session tier="{tier}" files-modified="{files_str}" />\n'
            f'  <git branch="{git.get("branch", "")}" uncommitted="{git.get("uncommitted_changes", 0)}" />\n'
            f'  <directive>No shortcuts. Verify before claiming done. Deviation protocol: STOP → DOCUMENT → ASK → LOG.</directive>\n'
            f'</archon-agent-context>'
        )

    return ""


if __name__ == "__main__":
    main()
