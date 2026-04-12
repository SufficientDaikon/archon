"""Complexity classification and skill routing — no LLM, pure pattern matching.

Used by prompt_router.py (UserPromptSubmit hook) to classify prompts
into complexity tiers, match relevant skills, and determine active synapses.
"""

import re

# Tier thresholds (word count). Lowered TRIVIAL from 38 to 12 — real prompts
# describing actual tasks are typically 10-30 words.
TIER_THRESHOLDS = [
    (12, "TRIVIAL"),     # one-liners, greetings, single commands
    (60, "SIMPLE"),      # single-function tasks, clear requirements
    (300, "MODERATE"),   # multi-file, some ambiguity
    (1000, "COMPLEX"),   # architecture, cross-cutting
]
DEFAULT_TIER = "EXPERT"
TIERS = [t for _, t in TIER_THRESHOLDS] + [DEFAULT_TIER]

# Patterns that escalate complexity. Pre-compiled for speed.
# Cap: max total escalation is +2 tiers (prevents 4-word prompts reaching COMPLEX).
# Removed common verbs (create/implement/develop/server) that over-escalated 35% of prompts.
MAX_ESCALATION = 2
ESCALATION_PATTERNS: list[tuple[re.Pattern, int]] = [
    (re.compile(r"\b(architect|design.system|refactor|migrate|rewrite|overhaul)\b", re.I), 1),
    (re.compile(r"\b(security|authentication|authorization|penetration|vulnerability)\b", re.I), 1),
    (re.compile(r"\b(pipeline|orchestrat|multi.?agent|distributed)\b", re.I), 1),
    (re.compile(r"\b(from.scratch|end.to.end|full.stack|complete.system)\b", re.I), 2),
    (re.compile(r"\b(production.ready|deploy|ci.?cd|infrastructure)\b", re.I), 1),
    (re.compile(r"\b(microservice|database.schema|backend.architecture)\b", re.I), 1),
    (re.compile(r"\bbuild.me\b", re.I), 1),
]

# Keyword -> skill mappings using word-boundary regex to prevent substring false positives.
# Each entry: (compiled_regex, [skill_names])
SKILL_MATCHERS: list[tuple[re.Pattern, list[str]]] = [
    (re.compile(r"\bsecurity\b", re.I), ["security-awareness"]),
    (re.compile(r"\btests?\b", re.I), ["e2e-testing-patterns", "webapp-testing"]),
    (re.compile(r"\bdebug\b", re.I), ["systematic-debugging"]),
    (re.compile(r"\bapi\b", re.I), ["backend-development"]),
    (re.compile(r"\bdocker\b", re.I), ["docker-build"]),
    (re.compile(r"\bgodot\b", re.I), ["godot-best-practices", "godot-gdscript-mastery"]),
    (re.compile(r"\breact\b", re.I), ["react-best-practices"]),
    (re.compile(r"\bastro\b", re.I), ["astro-islands-expert"]),
    (re.compile(r"\bdjango\b", re.I), ["django-expert", "django-framework"]),
    (re.compile(r"\bpr\b", re.I), ["pr-quality-agent", "github-markdown-mastery"]),
    (re.compile(r"\bpull.request\b", re.I), ["pr-quality-agent", "github-markdown-mastery"]),
    (re.compile(r"\bprompt\b", re.I), ["prompt-architect"]),
    (re.compile(r"\bmcp\b", re.I), ["mcp-builder", "fastmcp"]),
    (re.compile(r"\bskills?\b", re.I), ["writing-skills", "find-skills"]),
    (re.compile(r"\bwindows\b", re.I), ["windows-error-debugger", "windows-network-optimizer"]),
    (re.compile(r"\bresearch\b", re.I), ["archon-scout"]),
]

# Execution modes by tier
EXECUTION_MODES = {
    "TRIVIAL": "direct",
    "SIMPLE": "direct",
    "MODERATE": "skill",
    "COMPLEX": "orchestrator",
    "EXPERT": "orchestrator",
}

# Synapse activation rules.
# anti-rationalization: MODERATE+ only (was SIMPLE+, contradicted virtuoso.xml "SIMPLE = REFLECT only")
# sequential-thinking: COMPLEX+ only (differentiate from metacognition which fires at MODERATE+)
# Keyword matching uses word-boundary patterns.
SYNAPSE_TRIGGERS: dict[str, dict] = {
    "metacognition": {
        "tiers": {"MODERATE", "COMPLEX", "EXPERT"},
        "patterns": [],
    },
    "sequential-thinking": {
        "tiers": {"COMPLEX", "EXPERT"},
        "patterns": [],
    },
    "anti-rationalization": {
        "tiers": {"MODERATE", "COMPLEX", "EXPERT"},
        "patterns": [],
    },
    "security-awareness": {
        "tiers": set(),
        "patterns": [
            re.compile(r"\b(security|authentication|authorization|auth)\b", re.I),
            re.compile(r"\b(api|database|user.input|password|token|encrypt)\b", re.I),
        ],
    },
    "pattern-recognition": {
        "tiers": set(),
        "patterns": [
            re.compile(r"\b(implement|refactor)\b", re.I),
        ],
    },
}

# Compressed synapse phase instructions (injected for MODERATE+ tasks)
SYNAPSE_INSTRUCTIONS = {
    "metacognition": "PLAN: Rate complexity 1-5, build knowledge inventory (Know/Don't Know/Assuming), select strategy, define exit criteria before executing.",
    "sequential-thinking": "DECOMPOSE: Break into numbered steps with dependency ordering. REASON through each step. VALIDATE before proceeding.",
    "anti-rationalization": "ENFORCE: No shortcuts. No skipping tests. No claims without verification. Deviation protocol: STOP -> DOCUMENT -> ASK -> LOG.",
    "security-awareness": "SCAN: Check input boundaries, auth chain, output safety, data handling. Flag SSRF, SQLi, XSS, path traversal risks.",
    "pattern-recognition": "DETECT: Scan code for structural patterns. Suggest matching Archon skills when patterns are found.",
}


def classify_complexity(prompt: str) -> str:
    """Classify prompt into TRIVIAL->EXPERT tier. Pure heuristic."""
    word_count = len(prompt.split())

    # Base tier from word count
    tier_idx = len(TIER_THRESHOLDS)  # default to EXPERT
    for i, (threshold, _) in enumerate(TIER_THRESHOLDS):
        if word_count <= threshold:
            tier_idx = i
            break

    # Escalate from keyword patterns (capped at MAX_ESCALATION)
    prompt_lower = prompt.lower()
    escalation = 0
    for pattern, bump in ESCALATION_PATTERNS:
        if pattern.search(prompt_lower):
            escalation += bump

    escalation = min(escalation, MAX_ESCALATION)
    tier_idx = min(tier_idx + escalation, len(TIERS) - 1)
    return TIERS[tier_idx]


def match_skills(prompt: str) -> list[str]:
    """Return skill names relevant to the prompt via word-boundary matching."""
    matched: set[str] = set()
    for pattern, skills in SKILL_MATCHERS:
        if pattern.search(prompt):
            matched.update(skills)
    return sorted(matched)


def get_execution_mode(tier: str) -> str:
    """Determine execution mode for the tier."""
    return EXECUTION_MODES.get(tier, "orchestrator")


def active_synapses(tier: str, prompt: str) -> list[str]:
    """Determine which synapses should fire for this prompt+tier."""
    active: list[str] = []

    for synapse, triggers in SYNAPSE_TRIGGERS.items():
        if tier in triggers["tiers"]:
            active.append(synapse)
            continue
        if any(p.search(prompt) for p in triggers["patterns"]):
            active.append(synapse)

    return sorted(set(active))


def build_synapse_context(synapses: list[str], tier: str) -> str:
    """Build compressed synapse instructions for additionalContext."""
    if tier in ("TRIVIAL", "SIMPLE") and "security-awareness" not in synapses:
        return ""

    lines: list[str] = []
    for synapse in synapses:
        instruction = SYNAPSE_INSTRUCTIONS.get(synapse, "")
        if instruction:
            lines.append(f"  <{synapse}>{instruction}</{synapse}>")

    return "\n".join(lines)
