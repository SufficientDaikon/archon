from __future__ import annotations

from pathlib import Path

from .indexer import SkillEntry, SkillIndex


class SkillRouter:
    def __init__(self, index: SkillIndex) -> None:
        self._index = index

    @classmethod
    def build(cls, skills_dir: Path) -> "SkillRouter":
        idx = SkillIndex(skills_dir=skills_dir, manifests_dir=skills_dir)
        idx.build()
        return cls(idx)

    def select_skill(self, text: str, threshold: float = 0.3) -> SkillEntry | None:
        """Return the top-matching skill if its score meets the threshold, else None."""
        results = self._index.search(text, top_k=1)
        if not results:
            return None
        entry, score = results[0]
        return entry if score >= threshold else None

    def get_skill_content(self, entry: SkillEntry) -> str:
        return self._index.get_skill_content(entry)
