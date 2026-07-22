#!/usr/bin/env python3
"""SubagentStart/SubagentStop hook — role-scoped context + run telemetry.

SubagentStart: based on agent type, slices context so each agent gets only
what's relevant to its role — not the full state. (SubagentStart is not part
of the vanilla Claude Code CLI hook set; where it never fires this script is
simply inert.)

SubagentStop: records the completed run in session state for the session
summary — no injection.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.hooklog import write_record
from shared.state import load_state, save_state

# Agent type -> context builder mapping
AGENT_CONTEXT = {
    # Code-focused agents get project info + anti-rationalization
    "general-purpose": "code",
    "Plan": "code",
    # Exploration agents get project context only
    "Explore": "explore",
}


def main() -> None:
    t0 = time.perf_counter()
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    # Payload field name varies by harness: subagent_type is the Task-tool
    # spelling, agent_type the legacy one.
    agent_type = input_data.get("subagent_type") or input_data.get("agent_type", "")
    cwd = input_data.get("cwd")
    event = input_data.get("hook_event_name", "SubagentStart")

    if event == "SubagentStop":
        record_subagent_run(agent_type, cwd)
        write_record("agent_context", "SubagentStop", cwd, t0, agent_type=agent_type)
        print(json.dumps({}))
        return

    if not agent_type:
        print(json.dumps({}))
        return

    state = load_state(cwd)
    context_mode = AGENT_CONTEXT.get(agent_type, "code")
    context = build_agent_context(context_mode, state)
    write_record(
        "agent_context", "SubagentStart", cwd, t0, agent_type=agent_type, role=context_mode
    )

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


def record_subagent_run(agent_type: str, cwd: str | None = None) -> None:
    """Append a completed subagent run to session state (cheap telemetry)."""
    state = load_state(cwd)
    runs = state["session"].setdefault("subagent_runs", [])
    runs.append(
        {
            "type": agent_type or "unknown",
            "finished": datetime.now(timezone.utc).isoformat(),
        }
    )
    # Bound the list so state stays small
    state["session"]["subagent_runs"] = runs[-20:]
    save_state(state, cwd)


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
            f"</archon-agent-context>"
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
            f"  <directive>No shortcuts. Verify before claiming done. Deviation protocol: STOP → DOCUMENT → ASK → LOG.</directive>\n"
            f"</archon-agent-context>"
        )

    return ""


if __name__ == "__main__":
    main()
