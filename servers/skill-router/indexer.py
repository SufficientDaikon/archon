"""Skill indexer — parses skill .md files and builds a TF-IDF inverted index.

Enhanced version of agent-router's indexer with manifest-aware parsing.
Reads SKILL.md content from skill-library/ and cross-references manifest.yaml
from the original skill directories for rich metadata (tags, triggers, priority).

Zero LLM calls. Pure text matching with weighted term scoring.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ── Stop words ──────────────────────────────────────────────────
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
    # Domain noise — words that appear in nearly every skill
    "skill", "guidelines", "best", "practices", "patterns", "component",
    "components", "design", "development", "implementation", "approach",
    "strategy", "framework", "use", "using", "used", "based", "ensure",
    "provide", "create", "build", "make", "work", "working", "follow",
    "following", "include", "including", "new", "expert", "focused",
})

MIN_TERM_LEN = 2

# ── Category derivation rules ──────────────────────────────────
CATEGORY_RULES: list[tuple[set[str], str]] = [
    ({"orchestration", "routing", "meta", "forge"}, "forge"),
    ({"design", "ui-ux", "wireframing", "ux"}, "design"),
    ({"frontend", "web-development", "astro", "react", "svelte", "vue"}, "web"),
    ({"backend", "django", "api", "rest"}, "backend"),
    ({"testing", "e2e", "qa", "test"}, "testing"),
    ({"godot", "gdscript", "game", "gamedev"}, "gamedev"),
    ({"mobile", "capacitor", "ios", "android"}, "mobile"),
    ({"mcp", "fastmcp", "model-context-protocol"}, "mcp"),
    ({"docker", "windows", "devops", "system"}, "ops"),
    ({"workflow", "templates", "skill-creation", "packaging"}, "workflow"),
]


@dataclass
class SkillEntry:
    """Parsed metadata for a single skill file."""
    filename: str           # e.g. "frontend-design.md"
    name: str               # from YAML frontmatter: "frontend-design"
    description: str        # from YAML frontmatter
    category: str           # derived from tags or filename
    priority: str           # P0/P1/P2/P3 from manifest.yaml
    tags: list[str]         # from manifest.yaml
    triggers: dict[str, list[str]]  # keywords + patterns from manifest
    size_bytes: int
    size_category: str      # S (<5KB), M (5-15KB), L (>15KB)
    terms: dict[str, float] = field(default_factory=dict)


@dataclass
class SkillIndex:
    """TF-IDF inverted index over skill files."""

    skills_dir: Path               # ~/.claude/skill-library/
    manifests_dir: Path | None     # ~/.claude/skills/ (for manifest.yaml lookup)
    skills: list[SkillEntry] = field(default_factory=list)
    _idf: dict[str, float] = field(default_factory=dict)
    _index: dict[str, list[tuple[str, float]]] = field(default_factory=dict)

    def build(self) -> None:
        """Scan skills_dir, parse all .md files, build the index."""
        self.skills.clear()
        self._idf.clear()
        self._index.clear()

        if not self.skills_dir.exists():
            return

        for md_file in sorted(self.skills_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            entry = self._parse_skill(md_file)
            if entry:
                self.skills.append(entry)

        if not self.skills:
            return

        # Build IDF
        n = len(self.skills)
        doc_freq: dict[str, int] = {}
        for skill in self.skills:
            for term in skill.terms:
                doc_freq[term] = doc_freq.get(term, 0) + 1

        for term, df in doc_freq.items():
            self._idf[term] = math.log(n / df) + 1.0

        # Build inverted index with TF-IDF scores
        for skill in self.skills:
            for term, tf in skill.terms.items():
                idf = self._idf.get(term, 1.0)
                score = tf * idf
                if term not in self._index:
                    self._index[term] = []
                self._index[term].append((skill.filename, score))

    def search(self, query: str, top_k: int = 3) -> list[tuple[SkillEntry, float]]:
        """Search for skills matching a query string."""
        query_terms = _tokenize(query)
        if not query_terms:
            return []

        scores: dict[str, float] = {}
        for term in query_terms:
            if term in self._index:
                for filename, tfidf in self._index[term]:
                    scores[filename] = scores.get(filename, 0.0) + tfidf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        skill_map = {s.filename: s for s in self.skills}
        return [(skill_map[fn], score) for fn, score in ranked if fn in skill_map]

    def by_category(self, category: str | None = None) -> list[SkillEntry]:
        """List skills, optionally filtered by category."""
        if category is None:
            return list(self.skills)
        cat = category.lower()
        return [s for s in self.skills if s.category == cat]

    def get_skill(self, name: str) -> SkillEntry | None:
        """Get a skill by filename or display name (case-insensitive)."""
        name_lower = name.lower()
        for skill in self.skills:
            if skill.filename.lower() == name_lower:
                return skill
            if skill.filename.lower() == name_lower + ".md":
                return skill
            if skill.name.lower() == name_lower:
                return skill
        return None

    def get_skill_content(self, skill: SkillEntry) -> str:
        """Read the full content of a skill file."""
        path = self.skills_dir / skill.filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    # ── Internal parsing ────────────────────────────────────────

    def _parse_skill(self, path: Path) -> SkillEntry | None:
        """Parse a single skill .md file."""
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return None

        # Extract YAML frontmatter from the .md file
        fm = _extract_frontmatter(content)
        name = fm.get("name", path.stem)
        description = fm.get("description", "")

        # Load manifest.yaml for rich metadata
        manifest = self._load_manifest(path.stem)
        tags = manifest.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        priority = manifest.get("priority", "P3")
        triggers = manifest.get("triggers", {})
        if not isinstance(triggers, dict):
            triggers = {}

        # Derive category from tags first, then filename
        category = _derive_category_from_tags(tags, path.stem)

        # Size classification
        size = path.stat().st_size
        if size < 5000:
            size_cat = "S"
        elif size < 15000:
            size_cat = "M"
        else:
            size_cat = "L"

        # Extract weighted terms
        terms = self._extract_terms(content, name, description, tags, triggers)

        return SkillEntry(
            filename=path.name,
            name=name,
            description=description,
            category=category,
            priority=priority,
            tags=tags,
            triggers=triggers,
            size_bytes=size,
            size_category=size_cat,
            terms=terms,
        )

    def _load_manifest(self, skill_name: str) -> dict[str, Any]:
        """Load manifest.yaml from the original skill directory."""
        if not self.manifests_dir:
            return {}

        manifest_path = self.manifests_dir / skill_name / "manifest.yaml"
        if not manifest_path.exists():
            # Try following symlinks
            skill_dir = self.manifests_dir / skill_name
            if skill_dir.is_symlink():
                target = skill_dir.resolve()
                manifest_path = target / "manifest.yaml"

        if not manifest_path.exists():
            return {}

        try:
            return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}

    def _extract_terms(
        self,
        content: str,
        name: str,
        description: str,
        tags: list[str],
        triggers: dict[str, list[str]],
    ) -> dict[str, float]:
        """Extract weighted terms from skill content.

        Weights:
          - Name + description: 3x (highest routing signal)
          - Tags + trigger keywords: 2.5x
          - Category/priority sections: 2x
          - Body text: 1x
        """
        terms: dict[str, float] = {}
        body = _strip_frontmatter(content)

        # Weight 3x: name + description
        for token in _tokenize(name + " " + description):
            terms[token] = terms.get(token, 0.0) + 3.0

        # Weight 2.5x: tags + trigger keywords
        tag_text = " ".join(tags)
        trigger_keywords = triggers.get("keywords", [])
        if isinstance(trigger_keywords, list):
            tag_text += " " + " ".join(str(k) for k in trigger_keywords)
        for token in _tokenize(tag_text):
            terms[token] = terms.get(token, 0.0) + 2.5

        # Weight 2x: identity/role sections
        role_text = _extract_section(body, r"(?:identity|role|core|purpose)")
        for token in _tokenize(role_text):
            terms[token] = terms.get(token, 0.0) + 2.0

        # Weight 1x: everything else
        for token in _tokenize(body):
            terms[token] = terms.get(token, 0.0) + 1.0

        # Normalize by max TF
        if terms:
            max_tf = max(terms.values())
            if max_tf > 0:
                terms = {t: v / max_tf for t, v in terms.items()}

        return terms


# ── Utility functions ────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase terms, removing stop words."""
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
    next_heading = re.search(r"^##\s+", body[start:], re.MULTILINE)
    if next_heading:
        return body[start:start + next_heading.start()]
    return body[start:]


def _derive_category_from_tags(tags: list[str], filename: str) -> str:
    """Derive category from manifest tags, falling back to filename heuristics."""
    if tags:
        tag_set = {t.lower() for t in tags}
        for match_tags, category in CATEGORY_RULES:
            if tag_set & match_tags:
                return category

    # Filename-based fallback
    name = filename.lower()
    if name.startswith(("godot-", "game-", "omega-")):
        return "gamedev"
    if name.startswith("django-"):
        return "backend"
    if name.startswith(("design-", "ui-", "ux-", "wireframing")):
        return "design"
    if name.startswith(("docker-", "windows-")):
        return "ops"
    if name.startswith("testing-") or "test" in name:
        return "testing"
    if any(k in name for k in ("frontend", "react", "astro", "web", "vercel")):
        return "web"
    if "mcp" in name:
        return "mcp"

    return "general"
