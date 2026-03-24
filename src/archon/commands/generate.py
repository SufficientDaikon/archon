"""``archon generate`` — generate framework artifacts."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import typer

from archon.core.registry import Registry
from archon.core.llms_txt import write_files
from archon.utils.output import (
    console,
    print_success,
    print_error,
    print_info,
    print_verbose,
    is_json,
    json_envelope,
    print_json,
)
from archon.utils.paths import get_archon_root

generate_app = typer.Typer(help="Generate framework artifacts.", no_args_is_help=True)


@generate_app.command("llms-txt")
def llms_txt_cmd(
    concise: bool = typer.Option(False, "--concise", help="Generate only llms.txt (concise index)."),
    full: bool = typer.Option(False, "--full", help="Generate only llms-full.txt (complete dump)."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory (default: repo root)."),
) -> None:
    """Generate llms.txt and/or llms-full.txt for LLM consumption."""

    # Resolve root
    try:
        root = get_archon_root()
        reg = Registry(root=root)
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    # Determine what to generate
    gen_concise = True
    gen_full = True
    if concise and full:
        print_info("Both --concise and --full specified; generating both files.")
    elif concise:
        gen_full = False
    elif full:
        gen_concise = False

    # Resolve output dir
    output_dir: Path | None = None
    if output:
        output_dir = Path(output)
        if output_dir.exists() and output_dir.is_file():
            print_error(f"Output path is a file, not a directory: {output_dir}")
            raise typer.Exit(1)

    # Verbose: announce processing
    if not is_json():
        print_verbose("Loading registry...")
        for skill in sorted(reg.skills, key=lambda s: s.name):
            print_verbose(f"Processing skill: {skill.name}")
        for agent in sorted(reg.agents, key=lambda a: a.name):
            print_verbose(f"Processing agent: {agent.name}")
        for syn in sorted(reg.synapses, key=lambda s: s.name):
            print_verbose(f"Processing synapse: {syn.name}")
        for pl in sorted(reg.pipelines, key=lambda p: p.name):
            print_verbose(f"Processing pipeline: {pl.name}")
        for bnd in sorted(reg.bundles, key=lambda b: b.name):
            print_verbose(f"Processing bundle: {bnd.name}")

    start = time.time()

    try:
        result = write_files(
            root=root,
            output_dir=output_dir,
            concise=gen_concise,
            full=gen_full,
            registry=reg,
        )
    except PermissionError as exc:
        print_error(f"Permission denied: {exc}")
        raise typer.Exit(1)
    except OSError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    elapsed = time.time() - start

    # JSON output mode
    if is_json():
        files_generated = []
        if result.get("concise"):
            info = result["concise"]
            files_generated.append({"path": str(info["path"]), "size_bytes": info["size"]})
        if result.get("full"):
            info = result["full"]
            files_generated.append({"path": str(info["path"]), "size_bytes": info["size"]})

        print_json(json_envelope(
            command="generate llms-txt",
            data={
                "files_generated": files_generated,
                "stats": result["stats"],
            },
        ))
        return

    # Rich output
    console.print()
    console.rule("[bold cyan]llms.txt Generation[/bold cyan]")
    console.print()

    if result.get("concise"):
        info = result["concise"]
        size_kb = info["size"] / 1024
        print_success(f"llms.txt  ({size_kb:.1f} KB) → {info['path']}")

    if result.get("full"):
        info = result["full"]
        size_kb = info["size"] / 1024
        print_success(f"llms-full.txt  ({size_kb:.1f} KB) → {info['path']}")

    # Stats
    stats = result.get("stats", {})
    console.print()
    console.print(f"  📦 Skills:    [bold cyan]{stats.get('skills', 0)}[/bold cyan]")
    console.print(f"  🤖 Agents:    [bold cyan]{stats.get('agents', 0)}[/bold cyan]")
    console.print(f"  🧠 Synapses:  [bold cyan]{stats.get('synapses', 0)}[/bold cyan]")
    console.print(f"  🔗 Pipelines: [bold cyan]{stats.get('pipelines', 0)}[/bold cyan]")
    console.print(f"  📚 Bundles:   [bold cyan]{stats.get('bundles', 0)}[/bold cyan]")
    console.print(f"  📄 Docs:      [bold cyan]{stats.get('docs_pages', 0)}[/bold cyan]")

    print_verbose(f"Generation time: {elapsed:.2f}s")
    console.print()


@generate_app.command("agent-cards")
def agent_cards_cmd(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory (default: repo root)."),
) -> None:
    """Generate agent-cards.json — machine-readable agent card index."""

    from archon.core.agent_cards import write_agent_cards

    # Resolve root
    try:
        root = get_archon_root()
        reg = Registry(root=root)
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    # Resolve output dir
    output_dir: Path | None = None
    if output:
        output_dir = Path(output)
        if output_dir.exists() and output_dir.is_file():
            print_error(f"Output path is a file, not a directory: {output_dir}")
            raise typer.Exit(1)

    # Verbose: announce
    if not is_json():
        print_verbose("Loading registry...")
        for agent in sorted(reg.agents, key=lambda a: a.name):
            print_verbose(f"Processing agent: {agent.name}")

    start = time.time()

    try:
        result = write_agent_cards(root=root, output_dir=output_dir, registry=reg)
    except PermissionError as exc:
        print_error(f"Permission denied: {exc}")
        raise typer.Exit(1)
    except OSError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    elapsed = time.time() - start

    # JSON output mode
    if is_json():
        print_json(json_envelope(
            command="generate agent-cards",
            data={
                "files_generated": [{"path": str(result["path"]), "size_bytes": result["size"]}],
                "stats": {"agents": result["agent_count"]},
            },
        ))
        return

    # Rich output
    console.print()
    console.rule("[bold cyan]agent-cards.json Generation[/bold cyan]")
    console.print()

    size_kb = result["size"] / 1024
    print_success(f"agent-cards.json  ({size_kb:.1f} KB) → {result['path']}")

    console.print()
    console.print(f"  🤖 Agents: [bold cyan]{result['agent_count']}[/bold cyan]")

    print_verbose(f"Generation time: {elapsed:.2f}s")
    console.print()
