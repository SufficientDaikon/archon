#!/usr/bin/env python3
"""UserPromptSubmit hook — classifies complexity, routes to skills, activates synapses.

Fires on every prompt. Injects structured routing metadata and synapse
instructions as additionalContext. This is where passive synapses become
enforced behavior.
"""

import json
import sys
import time
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.classifier import (
    active_synapses,
    build_synapse_context,
    classify_complexity,
    get_execution_mode,
    match_skills,
    strip_noise,
)
from shared.config import get_property
from shared.hooklog import write_record
from shared.state import load_state, save_state


def _classifier_thresholds(cwd: str | None) -> list[tuple[int, str]]:
    """Tier thresholds from properties (defaults match the classifier constants)."""
    return [
        (get_property("classifier/trivial_max_words", cwd), "TRIVIAL"),
        (get_property("classifier/simple_max_words", cwd), "SIMPLE"),
        (get_property("classifier/moderate_max_words", cwd), "MODERATE"),
        (get_property("classifier/complex_max_words", cwd), "COMPLEX"),
    ]


def _enabled_synapses(synapses: list[str], cwd: str | None) -> list[str]:
    """Filter active synapses through the injection/* toggles."""
    if not get_property("injection/enabled", cwd):
        return []
    return [s for s in synapses if get_property(f"injection/{s.replace('-', '_')}", cwd)]


def main() -> None:
    t0 = time.perf_counter()
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    prompt = input_data.get("prompt", "")
    if not prompt.strip():
        print(json.dumps({}))
        return

    cwd = input_data.get("cwd")

    # Classify
    tier = classify_complexity(
        prompt,
        thresholds=_classifier_thresholds(cwd),
        max_escalation=get_property("classifier/max_escalation", cwd),
    )
    skills = match_skills(prompt)
    mode = get_execution_mode(tier)
    synapses = active_synapses(tier, prompt)

    # Session state feeds {state.*?} placeholders in the instructions
    # (e.g. a live tests-failing notice), so load before building context.
    state = load_state(cwd)
    synapse_context = build_synapse_context(
        _enabled_synapses(synapses, cwd), tier, state["session"]
    )

    # Update state
    state["session"]["complexity_tier"] = tier
    state["session"]["active_skills"] = skills
    save_state(state, cwd)

    # Build XML context
    context = build_route_context(tier, mode, skills, synapses, synapse_context)

    # Log the classification (stripped prompt stored only when opted in)
    stripped = strip_noise(prompt)
    log_extra: dict = {
        "tier": tier,
        "mode": mode,
        "skills": skills,
        "synapses": synapses,
        "word_count": len(stripped.split()),
        "preview": " ".join(stripped.split())[:80],
    }
    if get_property("logging/log_prompts", cwd):
        cap = get_property("logging/prompt_max_chars", cwd)
        log_extra["stripped_prompt"] = stripped[:cap]
        log_extra["prompt_truncated"] = len(stripped) > cap
    write_record("prompt_router", "UserPromptSubmit", cwd, t0, **log_extra)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


def build_route_context(
    tier: str,
    mode: str,
    skills: list[str],
    synapses: list[str],
    synapse_context: str,
) -> str:
    """Build the XML routing context."""
    skills_str = ",".join(skills) if skills else "none"
    synapses_str = ",".join(synapses) if synapses else "none"

    lines = [
        f'<archon-route tier="{tier}" mode="{mode}" skills="{skills_str}" synapses="{synapses_str}">'
    ]

    if synapse_context:
        lines.append(synapse_context)

    lines.append("</archon-route>")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
