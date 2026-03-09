"""``omniskill migrate`` — convert legacy skill formats (US-8, FR-045 through FR-048)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
import yaml

from omniskill.utils.output import (
    console, print_error, print_success, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json, get_progress,
)
from omniskill.utils.paths import get_omniskill_root


# ── Format detection ────────────────────────────────────────────

def _detect_format(source: Path) -> Optional[str]:
    """Detect the format of a skill directory."""
    if (source / "SKILL.md").exists() and (source / "manifest.yaml").exists():
        return "omniskill"
    if (source / "SKILL.md").exists():
        return "copilot-cli"
    if list(source.glob("*.mdc")):
        return "cursor"
    if list(source.glob("*.md")):
        return "generic-md"
    return None


def _extract_metadata(content: str, name: str) -> dict:
    """Extract metadata from markdown content via heuristics."""
    metadata: dict = {
        "name": name,
        "version": "1.0.0",
        "description": "",
        "author": "unknown",
        "platforms": ["copilot-cli", "claude-code"],
        "tags": ["migrated"],
        "triggers": {"keywords": []},
        "priority": "P2",
    }

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        metadata["description"] = title_match.group(1).strip()

    desc_match = re.search(r"^#\s+.+\n\n(.+?)(?:\n\n|\n#)", content, re.MULTILINE | re.DOTALL)
    if desc_match:
        d = desc_match.group(1).strip()
        metadata["description"] = d[:200] if len(d) > 200 else d

    # Extract keywords
    triggers_section = re.search(
        r"(?i)##\s+(?:triggers?|when to use|activation)\s*\n(.+?)(?:\n##|\Z)",
        content, re.MULTILINE | re.DOTALL,
    )
    if triggers_section:
        keywords = re.findall(r"[-*]\s*(.+?)(?:\n|$)", triggers_section.group(1))
        metadata["triggers"]["keywords"] = [k.strip() for k in keywords[:5]]

    if not metadata["triggers"]["keywords"]:
        metadata["triggers"]["keywords"] = [name.replace("-", " ")]

    return metadata


def _migrate_single(source_dir: Path, output_dir: Path) -> dict:
    """Migrate a single skill directory. Returns a result dict."""
    result = {"source": str(source_dir), "status": "skipped", "name": source_dir.name, "message": ""}

    fmt = _detect_format(source_dir)
    if fmt is None:
        result["status"] = "failed"
        result["message"] = "Unrecognizable format"
        return result

    # FR-047: Skip if already OMNISKILL format
    if fmt == "omniskill":
        result["status"] = "skipped"
        result["message"] = "Already in OMNISKILL format"
        return result

    # Read content
    try:
        if fmt == "copilot-cli":
            content = (source_dir / "SKILL.md").read_text(encoding="utf-8")
        elif fmt == "cursor":
            mdc_files = list(source_dir.glob("*.mdc"))
            content = mdc_files[0].read_text(encoding="utf-8") if mdc_files else ""
        else:  # generic-md
            md_files = list(source_dir.glob("*.md"))
            content = md_files[0].read_text(encoding="utf-8") if md_files else ""
    except Exception as exc:
        result["status"] = "failed"
        result["message"] = f"Read error: {exc}"
        return result

    if not content.strip():
        result["status"] = "failed"
        result["message"] = "Empty content"
        return result

    # Extract metadata and write
    metadata = _extract_metadata(content, source_dir.name)
    out_skill_dir = output_dir / metadata["name"]

    try:
        out_skill_dir.mkdir(parents=True, exist_ok=True)
        (out_skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        with open(out_skill_dir / "manifest.yaml", "w", encoding="utf-8") as fh:
            yaml.dump(metadata, fh, default_flow_style=False, sort_keys=False)
        result["status"] = "converted"
        result["message"] = f"Converted from {fmt} → {out_skill_dir}"
    except Exception as exc:
        result["status"] = "failed"
        result["message"] = f"Write error: {exc}"

    return result


# ── Command ─────────────────────────────────────────────────────

def migrate_cmd(
    path: str = typer.Argument(..., help="Path to legacy skill directory or parent directory."),
    in_place: bool = typer.Option(False, "--in-place", help="Modify files in-place instead of writing to a new directory."),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory (default: ./migrated)."),
) -> None:
    """Convert legacy skill formats to OMNISKILL format."""

    source = Path(path).resolve()
    if not source.exists():
        print_error(f"Path not found: {source}")
        raise typer.Exit(1)

    out = Path(output_dir) if output_dir else (source if in_place else Path("migrated"))
    out.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    # Check if source IS a single skill or a parent directory
    if _detect_format(source):
        results.append(_migrate_single(source, out))
    else:
        subdirs = [d for d in source.iterdir() if d.is_dir()]
        if not subdirs:
            print_error(f"No skill directories found in {source}")
            raise typer.Exit(1)

        if not is_json():
            console.print(f"\n[bold]Migrating {len(subdirs)} directories...[/bold]\n")

        for d in sorted(subdirs):
            results.append(_migrate_single(d, out))

    # FR-048: Report per-file results
    converted = [r for r in results if r["status"] == "converted"]
    skipped = [r for r in results if r["status"] == "skipped"]
    failed = [r for r in results if r["status"] == "failed"]

    if is_json():
        print_json(json_envelope(
            command="migrate",
            status="success" if not failed else "error",
            data={
                "converted": len(converted),
                "skipped": len(skipped),
                "failed": len(failed),
                "output_dir": str(out),
                "results": results,
            },
        ))
        if failed:
            raise typer.Exit(1)
        return

    for r in results:
        if r["status"] == "converted":
            print_success(f"{r['name']}: {r['message']}")
        elif r["status"] == "skipped":
            print_info(f"{r['name']}: {r['message']}")
        else:
            print_error(f"{r['name']}: {r['message']}")

    console.print()
    console.rule("[bold]Migration Summary[/bold]")
    console.print(f"  ✅ Converted: {len(converted)}")
    console.print(f"  ⏭  Skipped:   {len(skipped)}")
    console.print(f"  ❌ Failed:    {len(failed)}")
    console.print(f"  📁 Output:    {out.resolve()}")
    console.print()

    if converted:
        console.print("[muted]Next: validate with[/muted] omniskill validate")
    if failed:
        raise typer.Exit(1)
