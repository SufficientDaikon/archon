"""Build-time script: index skills/ → wakeel/edge/src/index.json + kv-skills.json.

Run from repo root:
    python wakeel/scripts/build_index.py

Outputs:
  wakeel/edge/src/index.json   — TF-IDF inverted index (bundled into Worker)
  wakeel/edge/kv-skills.json   — skill body content for wrangler kv bulk upload

Reads from: skills/ (read-only)
Writes to:  wakeel/edge/ (only)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
OUT_INDEX = REPO_ROOT / "wakeel" / "edge" / "src" / "index.json"
OUT_KV = REPO_ROOT / "wakeel" / "edge" / "kv-skills.json"

sys.path.insert(0, str(REPO_ROOT / "wakeel" / "src"))

from wakeel.kernel.router.indexer import SkillIndex


def main() -> None:
    idx = SkillIndex(skills_dir=SKILLS_DIR, manifests_dir=SKILLS_DIR)
    idx.build()

    if not idx.skills:
        print("ERROR: no skills found — check SKILLS_DIR", file=sys.stderr)
        sys.exit(1)

    # Emit only what router.ts needs: inverted index + minimal skill metadata.
    # DO NOT prune or round scores — full fidelity with Python is required for
    # routing parity. The full index is 359KB compressed, under the 1MB free limit.
    index_data = {
        "index": idx._index,
        "skills": [{"filename": s.filename, "name": s.name} for s in idx.skills],
    }
    OUT_INDEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_INDEX.write_text(json.dumps(index_data, ensure_ascii=False), encoding="utf-8")
    index_size = OUT_INDEX.stat().st_size
    print(f"index.json: {len(idx.skills)} skills, {len(idx._index)} terms, {index_size:,} bytes")

    # KV bulk upload format: [{"key": "...", "value": "..."}]
    kv_entries = []
    for skill in idx.skills:
        md_path = SKILLS_DIR / skill.filename / "SKILL.md"
        if md_path.exists():
            kv_entries.append({
                "key": skill.filename,
                "value": md_path.read_text(encoding="utf-8"),
            })

    OUT_KV.parent.mkdir(parents=True, exist_ok=True)
    OUT_KV.write_text(json.dumps(kv_entries, ensure_ascii=False), encoding="utf-8")
    kv_size = OUT_KV.stat().st_size
    print(f"kv-skills.json: {len(kv_entries)} entries, {kv_size:,} bytes")


if __name__ == "__main__":
    main()
