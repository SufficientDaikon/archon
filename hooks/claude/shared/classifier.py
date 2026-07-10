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
# NOTE: security keywords activate the security-awareness *synapse* (below),
# not a skill — skills listed here must exist as skills/<name>/ directories.
SKILL_MATCHERS: list[tuple[re.Pattern, list[str]]] = [
    (re.compile(r"\btests?\b", re.I), ["e2e-testing-patterns", "webapp-testing"]),
    (re.compile(r"\bdebug\b", re.I), ["systematic-debugging"]),
    (re.compile(r"\bapi\b", re.I), ["backend-development"]),
    (re.compile(r"\bdocker\b", re.I), ["docker-build"]),
    (re.compile(r"\bgodot\b", re.I), ["godot-best-practices", "godot-gdscript-mastery"]),
    (re.compile(r"\breact\b", re.I), ["vercel-react-best-practices"]),
    (re.compile(r"\bastro\b", re.I), ["astro-islands-expert"]),
    (re.compile(r"\bdjango\b", re.I), ["django-expert"]),
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

# Tier-banded synapse instructions, distilled from the full SYNAPSE.md content.
# Bands layer cumulatively: MODERATE gets "base"; COMPLEX adds "complex";
# EXPERT adds "expert". Keyword-triggered synapses (security-awareness,
# pattern-recognition) carry only a base band.
# Budget: ~130 tokens at MODERATE, ~330 at COMPLEX, ~450 at EXPERT.
SYNAPSE_INSTRUCTIONS: dict[str, dict[str, str]] = {
    "metacognition": {
        "base": (
            "PLAN before executing: rate complexity 1-5; list Know / Don't Know / "
            "Assuming; define exit criteria. Tag key claims HIGH (verified), "
            "MEDIUM (inferred), LOW (assumed)."
        ),
        "complex": (
            "ESCAPE HATCH: after 3 failed attempts at the same subtask with the same "
            "approach, STOP. Report what was tried and what you know, then ask — do "
            "not attempt a 4th variation. Confidence must be proportional to evidence: "
            "'seen it before' is MEDIUM; 'I ran it and observed X' is HIGH."
        ),
        "expert": (
            "STUCK-LOOP CHECK: editing the same file a 3rd time for the same failure, "
            "or re-running the same failing command unchanged, means you are looping — "
            "simplify scope or escalate. State the simpler fallback before continuing."
        ),
    },
    "anti-rationalization": {
        "base": (
            "NO UNVERIFIED CLAIMS: never say 'should work', 'probably fine', "
            "'I think I fixed it', 'basically done'. Replace with evidence: "
            "'verified by [test/output]'. Deviation from plan: STOP -> DOCUMENT -> ASK -> LOG."
        ),
        "complex": (
            "IRON LAWS: a task is done only when its verification command has been run "
            "this session and passed. Do not narrow the spec to fit the code — 'out of "
            "scope' is decided by the spec, not by difficulty. Partial completion must "
            "be reported as partial."
        ),
    },
    "sequential-thinking": {
        "base": (
            "DECOMPOSE: numbered steps with explicit dependencies before any edit. "
            "After each step, validate its output before consuming it in the next. "
            "Never parallelize steps whose inputs depend on unverified outputs."
        ),
    },
    "security-awareness": {
        "base": (
            "SECURITY SCAN: on any code touching input, auth, or data — check injection "
            "(SQLi/XSS/SSRF/path traversal), authz on every entry point, secrets never "
            "hardcoded, output encoding at trust boundaries."
        ),
    },
    "pattern-recognition": {
        "base": (
            "Before implementing, check whether an existing Archon skill or in-repo "
            "pattern already covers this; prefer extending it over parallel reimplementation."
        ),
    },
}

# Which instruction bands each tier receives.
_TIER_BANDS = {
    "TRIVIAL": ("base",),
    "SIMPLE": ("base",),
    "MODERATE": ("base",),
    "COMPLEX": ("base", "complex"),
    "EXPERT": ("base", "complex", "expert"),
}

# --- Noise stripping ------------------------------------------------------
# Pasted code, logs, and tracebacks inflate word counts and push terse-but-hard
# prompts into the wrong tier. Strip them before classification.
_FENCED_CODE = re.compile(r"```.*?```", re.S)
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_NOISE_LINES = re.compile(
    r"^\s*(?:"
    r"at\s+\S+"                       # JS/Java stack frames
    r"|File \"[^\"]+\", line \d+"     # Python tracebacks
    r"|Traceback \(most recent"       # Python traceback header
    r"|\d{4}-\d{2}-\d{2}[T ]\d{2}:"   # timestamped log lines
    r"|>"                             # quoted lines
    r").*$",
    re.M,
)

# --- Structural signals ---------------------------------------------------
_QUESTION_START = re.compile(
    r"^\s*(?:what|why|how|where|when|who|which|does|do|is|are|can|could|should|would|will)\b",
    re.I,
)
_IMPERATIVE_VERBS = re.compile(
    r"\b(?:fix|implement|add|refactor|build|write|create|migrate|delete|update|"
    r"make|remove|rename|deploy|install|convert|replace)\b",
    re.I,
)
_FILE_PATH = re.compile(
    r"\S+\.(?:py|ts|tsx|js|jsx|rs|go|java|rb|php|c|cpp|cs|md|ya?ml|json|toml)\b"
)
_NUMBERED_STEP = re.compile(r"^\s*\d+[.)]\s+\S", re.M)


def strip_noise(prompt: str) -> str:
    """Remove pasted code blocks, logs, tracebacks, and quotes from a prompt."""
    text = _FENCED_CODE.sub(" ", prompt)
    text = _INLINE_CODE.sub(" ", text)
    text = _NOISE_LINES.sub(" ", text)
    return text


def classify_complexity(prompt: str) -> str:
    """Classify prompt into TRIVIAL->EXPERT tier. Pure heuristic, no LLM."""
    stripped = strip_noise(prompt)
    word_count = len(stripped.split())

    # Base tier from word count of the actual request (noise removed)
    tier_idx = len(TIER_THRESHOLDS)  # default to EXPERT
    for i, (threshold, _) in enumerate(TIER_THRESHOLDS):
        if word_count <= threshold:
            tier_idx = i
            break

    # Escalate from keyword patterns (capped at MAX_ESCALATION)
    escalation = 0
    for pattern, bump in ESCALATION_PATTERNS:
        if pattern.search(stripped):
            escalation += bump
    tier_idx += min(escalation, MAX_ESCALATION)

    # Structural escalation: many files named or an explicit multi-step list
    file_refs = set(_FILE_PATH.findall(stripped))
    numbered_steps = len(_NUMBERED_STEP.findall(stripped))
    if len(file_refs) >= 3 or numbered_steps >= 3:
        tier_idx += 1

    # Pure questions with no imperative verb are informational — de-escalate
    if _QUESTION_START.search(stripped) and not _IMPERATIVE_VERBS.search(stripped):
        tier_idx -= 1

    tier_idx = max(0, min(tier_idx, len(TIERS) - 1))
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
    """Build tier-banded synapse instructions for additionalContext.

    MODERATE injects the base band; COMPLEX adds the complex band; EXPERT adds
    all three. TRIVIAL/SIMPLE inject nothing except keyword-triggered synapses
    (security-awareness) — low tiers must stay near-zero overhead.
    """
    if tier in ("TRIVIAL", "SIMPLE"):
        synapses = [s for s in synapses if s == "security-awareness"]
        if not synapses:
            return ""

    bands = _TIER_BANDS.get(tier, ("base",))
    lines: list[str] = []
    for synapse in synapses:
        instructions = SYNAPSE_INSTRUCTIONS.get(synapse, {})
        text = " ".join(instructions[band] for band in bands if band in instructions)
        if text:
            lines.append(f"  <{synapse}>{text}</{synapse}>")

    return "\n".join(lines)
