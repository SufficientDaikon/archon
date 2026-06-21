"""Skill indexer — parses skill SKILL.md files and builds a TF-IDF inverted index.

Adapted from servers/skill-router/indexer.py for use inside Wakeel.
TF-IDF math is identical. Discovery layer changed:
  - Skills discovered via skills_dir.glob("*/SKILL.md"), not flat *.md files.
  - Skill identifier (filename field) = directory name, e.g. "backend-development".
  - Manifests resolve at skills_dir/<dir_name>/manifest.yaml.

Original: servers/skill-router/indexer.py
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
    """Parsed metadata for a single skill directory."""
    filename: str           # directory name, e.g. "backend-development"
    name: str               # from YAML frontmatter, fallback = dir name
    description: str
    category: str
    priority: str
    tags: list[str]
    triggers: dict[str, list[str]]
    size_bytes: int
    size_category: str      # S (<5KB), M (5-15KB), L (>15KB)
    terms: dict[str, float] = field(default_factory=dict)


@dataclass
class SkillIndex:
    """TF-IDF inverted index over skill directories."""

    skills_dir: Path               # e.g. /repo/skills/
    manifests_dir: Path | None     # same as skills_dir for repo-layout
    skills: list[SkillEntry] = field(default_factory=list)
    _idf: dict[str, float] = field(default_factory=dict)
    _index: dict[str, list[tuple[str, float]]] = field(default_factory=dict)

    def build(self) -> None:
        """Scan skills_dir for */SKILL.md, parse all, build the index."""
        self.skills.clear()
        self._idf.clear()
        self._index.clear()

        if not self.skills_dir.exists():
            return

        for skill_md in sorted(self.skills_dir.glob("*/SKILL.md")):
            if skill_md.parent.name.startswith("_"):
                continue
            entry = self._parse_skill(skill_md)
            if entry:
                self.skills.append(entry)

        if not self.skills:
            return

        n = len(self.skills)
        doc_freq: dict[str, int] = {}
        for skill in self.skills:
            for term in skill.terms:
                doc_freq[term] = doc_freq.get(term, 0) + 1

        for term, df in doc_freq.items():
            self._idf[term] = math.log(n / df) + 1.0

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
        if category is None:
            return list(self.skills)
        cat = category.lower()
        return [s for s in self.skills if s.category == cat]

    def get_skill(self, name: str) -> SkillEntry | None:
        name_lower = name.lower()
        for skill in self.skills:
            if skill.filename.lower() == name_lower:
                return skill
            if skill.name.lower() == name_lower:
                return skill
        return None

    def get_skill_content(self, skill: SkillEntry) -> str:
        """Read the full content of a skill's SKILL.md file."""
        path = self.skills_dir / skill.filename / "SKILL.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    # ── Internal parsing ────────────────────────────────────────

    def _parse_skill(self, path: Path) -> SkillEntry | None:
        """Parse a single SKILL.md file. path is the SKILL.md file path."""
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return None

        dir_name = path.parent.name  # "backend-development"

        fm = _extract_frontmatter(content)
        name = fm.get("name", dir_name)
        description = fm.get("description", "")

        manifest = self._load_manifest(dir_name)
        tags = manifest.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        priority = manifest.get("priority", "P3")
        triggers = manifest.get("triggers", {})
        if not isinstance(triggers, dict):
            triggers = {}

        category = _derive_category_from_tags(tags, dir_name)

        size = path.stat().st_size
        if size < 5000:
            size_cat = "S"
        elif size < 15000:
            size_cat = "M"
        else:
            size_cat = "L"

        terms = self._extract_terms(content, name, description, tags, triggers)

        return SkillEntry(
            filename=dir_name,
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
        if not self.manifests_dir:
            return {}

        manifest_path = self.manifests_dir / skill_name / "manifest.yaml"
        if not manifest_path.exists():
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
        terms: dict[str, float] = {}
        body = _strip_frontmatter(content)

        for token in _tokenize(name + " " + description):
            terms[token] = terms.get(token, 0.0) + 3.0

        tag_text = " ".join(tags)
        trigger_keywords = triggers.get("keywords", [])
        if isinstance(trigger_keywords, list):
            tag_text += " " + " ".join(str(k) for k in trigger_keywords)
        for token in _tokenize(tag_text):
            terms[token] = terms.get(token, 0.0) + 2.5

        role_text = _extract_section(body, r"(?:identity|role|core|purpose)")
        for token in _tokenize(role_text):
            terms[token] = terms.get(token, 0.0) + 2.0

        for token in _tokenize(body):
            terms[token] = terms.get(token, 0.0) + 1.0

        if terms:
            max_tf = max(terms.values())
            if max_tf > 0:
                terms = {t: v / max_tf for t, v in terms.items()}

        return terms


# ── Utility functions ────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z][a-z0-9]+", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) >= MIN_TERM_LEN]


def _extract_frontmatter(content: str) -> dict[str, str]:
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
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def _extract_section(body: str, heading_pattern: str) -> str:
    pattern = rf"^##\s+.*{heading_pattern}.*$"
    match = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", body[start:], re.MULTILINE)
    if next_heading:
        return body[start:start + next_heading.start()]
    return body[start:]


def _derive_category_from_tags(tags: list[str], dirname: str) -> str:
    if tags:
        tag_set = {t.lower() for t in tags}
        for match_tags, category in CATEGORY_RULES:
            if tag_set & match_tags:
                return category

    name = dirname.lower()
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
