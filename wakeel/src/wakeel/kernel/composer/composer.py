from __future__ import annotations

import xml.etree.ElementTree as ET
from functools import lru_cache

from ...paths import VIRTUOSO_XML
from ..router.indexer import SkillEntry

PERSONA = """You are Wakeel — a disciplined, friendly assistant running on the Archon Harness.

WhatsApp reply guidelines:
- Keep responses short and conversational (3-5 sentences max).
- Never use markdown tables or heavy formatting — plain text only.
- Use simple bullet points (• or -) sparingly when needed.
- Respond in the same language the user wrote in.
- Be warm, direct, and precise."""


@lru_cache(maxsize=1)
def _load_synapses() -> str:
    """Extract the full <synapses> block from virtuoso.xml. Parsed once, cached."""
    tree = ET.parse(str(VIRTUOSO_XML))
    root = tree.getroot()
    synapses_el = root.find("synapses")
    if synapses_el is None:
        raise RuntimeError(f"<synapses> block not found in {VIRTUOSO_XML}")
    return ET.tostring(synapses_el, encoding="unicode")


def build_system_prompt(
    skill_entry: SkillEntry | None = None,
    skill_content: str = "",
) -> str:
    """Assemble the kernel system prompt.

    Structure: Wakeel persona
             + full <synapses> block (contains 5 synapses + the 10 Iron Laws
               inside <synapse name="anti-rationalization">)
             + skill content (only when a skill was matched by the router).

    Raises RuntimeError if the discipline sentinel is missing — never ships silently.
    """
    synapses = _load_synapses()

    if "VERIFY, DON'T TRUST" not in synapses:
        raise RuntimeError(
            "Discipline kernel integrity check FAILED: "
            "'VERIFY, DON'T TRUST' sentinel not found in extracted synapses. "
            "The synapses block is malformed or the wrong XML section was extracted."
        )

    parts = [
        PERSONA,
        "\n\n<!-- COGNITIVE DISCIPLINE -->\n" + synapses,
    ]

    if skill_entry and skill_content:
        parts.append(
            f"\n\n<!-- DOMAIN SKILL: {skill_entry.name} -->\n{skill_content}"
        )

    return "\n".join(parts)
