"""Agent role registry — maps Archon agent roles to Claude Code tool access directives.

Used by agent_context.py (SubagentStart hook) to inject role-appropriate
tool-use guidance and subagent_type recommendations into every subagent.

No I/O at module level. No imports from non-stdlib. Pure data + functions.
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical role definitions
# ---------------------------------------------------------------------------
ROLES: dict[str, dict] = {
    "implementer": {
        "subagent_type": "general-purpose",
        "tools_use": ["Write", "Edit", "Bash", "Read", "Glob", "Grep", "TodoWrite", "Skill"],
        "tools_avoid": ["WebFetch", "Agent"],
        "directives": [
            "Follow spec exactly — no features beyond what was specified.",
            "Write tests before implementation (red-green-refactor).",
            "Verify each section before proceeding to the next.",
            "DONE status requires: all tests passing, zero deviations from spec.",
        ],
    },
    "reviewer": {
        "subagent_type": "Explore",
        "tools_use": ["Read", "Glob", "Grep"],
        "tools_avoid": ["Write", "Edit", "Bash", "Agent", "WebFetch"],
        "directives": [
            "READ ONLY. Never modify files.",
            "Report findings as evidence-based observations. Do not fix.",
            "Verify every requirement against spec. No skipping.",
        ],
    },
    "debugger": {
        "subagent_type": "general-purpose",
        "tools_use": ["Read", "Glob", "Grep", "Bash"],
        "tools_avoid": ["Write", "Edit", "Agent", "WebFetch"],
        "directives": [
            "Investigate before proposing. Four phases: symptom -> context -> hypothesis -> fix.",
            "Reproduce the issue with Bash before claiming root cause.",
            "No fixes until root cause is confirmed with evidence.",
        ],
    },
    "spec-writer": {
        "subagent_type": "Plan",
        "tools_use": ["Write", "Read", "Glob", "Grep"],
        "tools_avoid": ["Bash", "Agent", "WebFetch"],
        "directives": [
            "Produce a specification — not code.",
            "Every requirement must be verifiable and binary (pass/fail).",
        ],
    },
    "qa-master": {
        "subagent_type": "general-purpose",
        "tools_use": ["Bash", "Read", "Write", "Glob", "Grep"],
        "tools_avoid": ["Agent", "WebFetch"],
        "directives": [
            "Run tests with Bash. Never claim pass/fail without running.",
            "Write test plans before test code.",
            "Report exact failure output, not paraphrased.",
        ],
    },
    "dissector": {
        "subagent_type": "Explore",
        "tools_use": ["Read", "Glob", "Grep", "Bash"],
        "tools_avoid": ["Write", "Edit", "Agent", "WebFetch"],
        "directives": [
            "READ ONLY. Never modify the codebase under analysis.",
            "Cite every excerpt with file path and line range.",
            "Produce output even for partial analysis — no silent failures.",
        ],
    },
    "context-curator": {
        "subagent_type": "general-purpose",
        "tools_use": ["Read", "Glob", "Grep", "Write"],
        "tools_avoid": ["Bash", "Agent", "WebFetch"],
        "directives": [
            "Distill, do not expand. Summaries must be shorter than the source.",
            "Never include content that the target agent does not need.",
            "Persist state to disk — do not rely on context surviving compression.",
        ],
    },
    "security-reviewer": {
        "subagent_type": "Explore",
        "tools_use": ["Read", "Glob", "Grep", "Bash"],
        "tools_avoid": ["Write", "Edit", "Agent"],
        "directives": [
            "READ ONLY. Never modify files during audit.",
            "Check OWASP A1-A10. Flag with severity: CRITICAL / HIGH / MEDIUM / LOW.",
            "No approval of code with known injection vectors.",
        ],
    },
    "skill-validator": {
        "subagent_type": "Explore",
        "tools_use": ["Read", "Bash", "Glob", "Grep"],
        "tools_avoid": ["Write", "Edit", "Agent"],
        "directives": [
            "READ ONLY. Validate, do not fix.",
            "Produce binary pass/fail verdict per criterion.",
        ],
    },
    "design-agent": {
        "subagent_type": "general-purpose",
        "tools_use": [
            "Write", "Edit", "Read",
            "mcp__pencil__batch_design", "mcp__pencil__batch_get",
            "mcp__pencil__get_editor_state", "mcp__pencil__get_screenshot",
            "mcp__pencil__export_nodes", "mcp__pencil__get_guidelines",
            "mcp__pencil__find_empty_space_on_canvas", "mcp__pencil__open_document",
            "mcp__pencil__snapshot_layout", "mcp__pencil__get_variables",
            "mcp__pencil__set_variables", "mcp__pencil__replace_all_matching_properties",
            "mcp__pencil__search_all_unique_properties",
        ],
        "tools_avoid": ["Bash", "Agent", "WebFetch"],
        "directives": [
            "All design values must reference design tokens — never raw hex/px.",
            "Use mcp__pencil__* tools for all canvas operations.",
            "Validate with get_screenshot after every batch_design call.",
        ],
    },
    "prompt-architect": {
        "subagent_type": "general-purpose",
        "tools_use": ["Write", "Read"],
        "tools_avoid": ["Bash", "Agent", "WebFetch"],
        "directives": [
            "Produce prompt frameworks and trigger patterns — not implementations.",
        ],
    },
    "ux-research": {
        "subagent_type": "Explore",
        "tools_use": ["Read", "Glob", "Grep", "WebFetch"],
        "tools_avoid": ["Write", "Edit", "Bash", "Agent"],
        "directives": [
            "Research and report. Never implement.",
            "Every claim cites a source (URL or file path + line).",
        ],
    },
    "ux-lifecycle-master": {
        "subagent_type": "general-purpose",
        "tools_use": ["Agent", "Read", "TodoWrite"],
        "tools_avoid": ["Write", "Edit", "Bash"],
        "directives": [
            "Orchestrate — never do design work directly.",
            "Enforce quality gates at every phase transition.",
            "Spawn specialized subagents for each pipeline phase.",
        ],
    },
    "university-professor": {
        "subagent_type": "general-purpose",
        "tools_use": ["Write", "Read"],
        "tools_avoid": ["Bash", "Agent"],
        "directives": [
            "Teach with five anti-hallucination gates active.",
            "Adapt difficulty to learner level. Cite sources for every factual claim.",
        ],
    },
}

DEFAULT_ROLE = "implementer"

# ---------------------------------------------------------------------------
# Role classification
# ---------------------------------------------------------------------------

# Explicit [ROLE:x] marker — highest priority, overrides everything
_ROLE_MARKER_RE = re.compile(r"\[ROLE:([a-z][a-z0-9-]*)\]", re.I)

# Keyword patterns — checked in order, first match wins.
# Narrower / more specific patterns come first to avoid false matches.
_ROLE_KEYWORDS: list[tuple] = [
    (re.compile(r"\bsecurit\w*|owasp|vulnerab\w*|penetrat\w*", re.I), "security-reviewer"),
    (re.compile(r"ux[.-]research|user[.-]journey|heatmap", re.I), "ux-research"),
    (re.compile(r"ux[.-]lifecycle|pipeline[.-]master", re.I), "ux-lifecycle-master"),
    (re.compile(r"context[.-]curat\w*|phase[.-]brief|handoff[.-]summar\w*", re.I), "context-curator"),
    (re.compile(r"\bdissect\b|reverse[.-]engineer|architecture[.-]map|codebase[.-]anal\w*", re.I), "dissector"),
    (re.compile(r"skill[.-]validat\w*|validat.*skill", re.I), "skill-validator"),
    (re.compile(r"prompt[.-]architect|prompt[.-]engineer|trigger[.-]pattern", re.I), "prompt-architect"),
    (re.compile(r"\bprofessor\b|pedagog\w*", re.I), "university-professor"),
    (re.compile(r"\bdesign\b|\bwireframe\b|\bpencil\b|design[.-]token", re.I), "design-agent"),
    (re.compile(r"\breview\b|\baudit\b|verif\w*|\bcompliance\b|inspect\w*", re.I), "reviewer"),
    (re.compile(r"\bdebug\b|root[.-]cause|investigat\w*|\btrace\b|reproduc\w*", re.I), "debugger"),
    (re.compile(r"\bqa\b|quality[.-]assur\w*|\be2e\b|end[.-]to[.-]end[.-]test", re.I), "qa-master"),
    (re.compile(r"\btest\b|\btesting\b", re.I), "qa-master"),
    (re.compile(r"specif\w*|\brequirement\b|acceptance[.-]criteria", re.I), "spec-writer"),
]


def classify_role(agent_type: str, description: str = "", prompt: str = "") -> str:
    """
    Determine the Archon role for a subagent.

    Priority:
      1. [ROLE:x] marker in description or prompt
      2. agent_type == "Explore"  -> dissector
      3. agent_type == "Plan"     -> spec-writer
      4. Keyword inference on combined description + prompt text
      5. DEFAULT_ROLE ("implementer")
    """
    text = f"{description} {prompt}".strip()

    # Priority 1: explicit marker
    m = _ROLE_MARKER_RE.search(text)
    if m:
        candidate = m.group(1).lower()
        if candidate in ROLES:
            return candidate

    # Priority 2/3: agent_type signals (platform-enforced)
    if agent_type == "Explore":
        return "dissector"
    if agent_type == "Plan":
        return "spec-writer"

    # Priority 4: keyword inference
    if text:
        for pattern, role_name in _ROLE_KEYWORDS:
            if pattern.search(text):
                return role_name

    return DEFAULT_ROLE


# ---------------------------------------------------------------------------
# Tool directive builder
# ---------------------------------------------------------------------------

def build_tool_directives(role_name: str) -> str:
    """
    Build XML tool directives for injection into additionalContext.
    Falls back to DEFAULT_ROLE if role_name is unknown.
    """
    role = ROLES.get(role_name, ROLES[DEFAULT_ROLE])
    if role_name not in ROLES:
        role_name = DEFAULT_ROLE

    use = ", ".join(role["tools_use"])
    avoid = ", ".join(role["tools_avoid"])
    rules = "".join(f"\n    <rule>{d}</rule>" for d in role["directives"])

    return (
        f'  <tool-access use="{use}" avoid="{avoid}" />\n'
        f'  <role>{role_name}</role>\n'
        f'  <task-protocol>{rules}\n'
        f'  </task-protocol>'
    )


# ---------------------------------------------------------------------------
# Transcript reader — extracts agent description from parent session JSONL
# ---------------------------------------------------------------------------

def extract_description_from_transcript(
    transcript_path: str,
    agent_type: str,
    max_scan_lines: int = 200,
) -> str:
    """
    Read the parent session JSONL transcript and find the most recent
    Agent tool call matching agent_type. Returns its description field,
    or empty string on any error or miss.

    Only reads tail of file (max_scan_lines) for performance.
    Never raises — any failure returns "".
    """
    try:
        path = Path(transcript_path)
        if not path.exists():
            return ""

        lines = path.read_bytes().decode("utf-8", errors="replace").splitlines()
        tail = lines[-max_scan_lines:] if len(lines) > max_scan_lines else lines

        for line in reversed(tail):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = entry.get("message", {})
            if not isinstance(msg, dict):
                continue

            items = msg.get("content", [])
            if not isinstance(items, list):
                continue

            for item in items:
                if (
                    isinstance(item, dict)
                    and item.get("type") == "tool_use"
                    and item.get("name") == "Agent"
                ):
                    inp = item.get("input", {})
                    if inp.get("subagent_type") == agent_type:
                        return inp.get("description", "")

    except Exception:
        pass

    return ""
