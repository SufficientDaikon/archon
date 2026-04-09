"""Agent indexer — parses agent .md files and builds a TF-IDF inverted index.

Zero LLM calls. Pure text matching with weighted term scoring.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path


# ── Stop words (common words with no routing signal) ─────────────
STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "must", "need",
    "this", "that", "these", "those", "it", "its", "you", "your", "i",
    "we", "our", "they", "their", "he", "she", "his", "her", "not", "no",
    "all", "each", "every", "any", "some", "most", "more", "less", "very",
    "just", "also", "so", "if", "then", "than", "when", "while", "as",
    "about", "up", "out", "into", "over", "after", "before", "between",
    "through", "during", "without", "against", "above", "below",
    # Domain noise — words that appear in nearly every agent and carry no signal
    "agent", "specialist", "expert", "focused", "use", "using", "used",
    "based", "ensure", "provide", "create", "build", "make", "work",
    "working", "follow", "following", "include", "including", "new",
})

# ── Minimum term length ─────────────────────────────────────────
MIN_TERM_LEN = 2


@dataclass
class AgentEntry:
    """Parsed metadata for a single agent file."""
    filename: str           # e.g. "engineering-frontend-developer.md"
    name: str               # from YAML: "Frontend Developer"
    description: str        # from YAML: one-line desc
    vibe: str               # from YAML: personality hint
    category: str           # derived from filename prefix
    size_bytes: int
    size_category: str      # S (<5KB), M (5-15KB), L (>15KB)
    terms: dict[str, float] = field(default_factory=dict)  # term → weighted TF


@dataclass
class AgentIndex:
    """TF-IDF inverted index over agent files."""

    agents_dir: Path
    agents: list[AgentEntry] = field(default_factory=list)
    # inverted index: term → list of (agent_filename, tf_idf_score)
    _idf: dict[str, float] = field(default_factory=dict)
    _index: dict[str, list[tuple[str, float]]] = field(default_factory=dict)

    def build(self) -> None:
        """Scan agents_dir, parse all .md files, build the index."""
        self.agents.clear()
        self._idf.clear()
        self._index.clear()

        if not self.agents_dir.exists():
            return

        for md_file in sorted(self.agents_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            entry = self._parse_agent(md_file)
            if entry:
                self.agents.append(entry)

        if not self.agents:
            return

        # Build IDF
        n = len(self.agents)
        doc_freq: dict[str, int] = {}
        for agent in self.agents:
            for term in agent.terms:
                doc_freq[term] = doc_freq.get(term, 0) + 1

        for term, df in doc_freq.items():
            self._idf[term] = math.log(n / df) + 1.0  # smoothed IDF

        # Build inverted index with TF-IDF scores
        for agent in self.agents:
            for term, tf in agent.terms.items():
                idf = self._idf.get(term, 1.0)
                score = tf * idf
                if term not in self._index:
                    self._index[term] = []
                self._index[term].append((agent.filename, score))

    def search(self, query: str, top_k: int = 3) -> list[tuple[AgentEntry, float]]:
        """Search for agents matching a query string.

        Returns a list of (AgentEntry, score) tuples, sorted by score descending.
        """
        query_terms = _tokenize(query)
        if not query_terms:
            return []

        scores: dict[str, float] = {}
        for term in query_terms:
            if term in self._index:
                for filename, tfidf in self._index[term]:
                    scores[filename] = scores.get(filename, 0.0) + tfidf

        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Map back to AgentEntry
        agent_map = {a.filename: a for a in self.agents}
        return [(agent_map[fn], score) for fn, score in ranked if fn in agent_map]

    def by_category(self, category: str | None = None) -> list[AgentEntry]:
        """List agents, optionally filtered by category."""
        if category is None:
            return list(self.agents)
        cat = category.lower()
        return [a for a in self.agents if a.category == cat]

    def get_agent(self, name: str) -> AgentEntry | None:
        """Get an agent by filename or display name (case-insensitive)."""
        name_lower = name.lower()
        for agent in self.agents:
            if agent.filename.lower() == name_lower:
                return agent
            if agent.filename.lower() == name_lower + ".md":
                return agent
            if agent.name.lower() == name_lower:
                return agent
        return None

    def get_agent_content(self, agent: AgentEntry) -> str:
        """Read the full content of an agent file."""
        path = self.agents_dir / agent.filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    # ── Internal parsing ────────────────────────────────────────

    def _parse_agent(self, path: Path) -> AgentEntry | None:
        """Parse a single agent .md file."""
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return None

        # Extract YAML frontmatter
        fm = _extract_frontmatter(content)
        name = fm.get("name", path.stem.replace("-", " ").title())
        description = fm.get("description", "")
        vibe = fm.get("vibe", "")

        # Derive category from filename
        category = _derive_category(path.name)

        # Size classification
        size = path.stat().st_size
        if size < 5000:
            size_cat = "S"
        elif size < 15000:
            size_cat = "M"
        else:
            size_cat = "L"

        # Extract weighted terms
        terms = self._extract_terms(content, name, description, vibe)

        return AgentEntry(
            filename=path.name,
            name=name,
            description=description,
            vibe=vibe,
            category=category,
            size_bytes=size,
            size_category=size_cat,
            terms=terms,
        )

    def _extract_terms(
        self, content: str, name: str, description: str, vibe: str
    ) -> dict[str, float]:
        """Extract weighted terms from agent content.

        Weights:
          - Name + description: 3x (highest signal)
          - Vibe + Role/Mission sections: 2x
          - Body text: 1x
        """
        terms: dict[str, float] = {}
        body = _strip_frontmatter(content)

        # Weight 3x: name + description (highest routing signal)
        for token in _tokenize(name + " " + description):
            terms[token] = terms.get(token, 0.0) + 3.0

        # Weight 2x: vibe + role/mission sections
        role_text = _extract_section(body, r"(?:role|identity|core mission)")
        for token in _tokenize(vibe + " " + role_text):
            terms[token] = terms.get(token, 0.0) + 2.0

        # Weight 1x: everything else
        for token in _tokenize(body):
            terms[token] = terms.get(token, 0.0) + 1.0

        # Normalize by max TF to prevent long documents from dominating
        if terms:
            max_tf = max(terms.values())
            if max_tf > 0:
                terms = {t: v / max_tf for t, v in terms.items()}

        return terms


# ── Utility functions ────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase terms, removing stop words."""
    # Split on non-alphanumeric, lowercase
    tokens = re.findall(r"[a-z][a-z0-9]+", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) >= MIN_TERM_LEN]


def _extract_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fm: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                fm[key] = value
    return fm


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def _extract_section(body: str, heading_pattern: str) -> str:
    """Extract text under a markdown heading matching the pattern."""
    pattern = rf"^##\s+.*{heading_pattern}.*$"
    match = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
    if not match:
        return ""

    start = match.end()
    # Find next heading of same or higher level
    next_heading = re.search(r"^##\s+", body[start:], re.MULTILINE)
    if next_heading:
        return body[start:start + next_heading.start()]
    return body[start:]


def _derive_category(filename: str) -> str:
    """Derive category from agent filename prefix."""
    prefixes = {
        "engineering-": "engineering",
        "design-": "design",
        "testing-": "testing",
        "game-": "game",
        "godot-": "game",
        "agents-": "orchestration",
    }
    for prefix, cat in prefixes.items():
        if filename.startswith(prefix):
            return cat
    return "niche"
