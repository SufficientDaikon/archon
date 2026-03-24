"""Rich output helpers for the Archon CLI.

Provides a shared :class:`rich.console.Console`, JSON-envelope formatting,
and common UI components (tables, panels, progress bars) used across commands.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich import box

from archon import __version__

# ── Shared console ──────────────────────────────────────────────

_THEME = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "bold red",
    "title": "bold magenta",
    "muted": "dim",
})

# Respect NO_COLOR (https://no-color.org/)
_no_color = "NO_COLOR" in os.environ

console = Console(theme=_THEME, no_color=_no_color)
err_console = Console(stderr=True, theme=_THEME, no_color=_no_color)

# ── Global state set by CLI callbacks ───────────────────────────

_json_mode: bool = False
_quiet_mode: bool = False
_verbose_mode: bool = False


def set_output_flags(*, json_flag: bool = False, quiet: bool = False, verbose: bool = False) -> None:
    """Set global output-mode flags (called from the CLI callback)."""
    global _json_mode, _quiet_mode, _verbose_mode
    _json_mode = json_flag
    _quiet_mode = quiet
    _verbose_mode = verbose


def is_json() -> bool:
    return _json_mode


def is_quiet() -> bool:
    return _quiet_mode


def is_verbose() -> bool:
    return _verbose_mode


# ── JSON envelope ───────────────────────────────────────────────

def json_envelope(
    *,
    command: str,
    status: str = "success",
    data: Any = None,
    errors: list[dict] | None = None,
    diagnostics: dict | None = None,
) -> dict:
    """Build the standard JSON output envelope (Appendix D of the spec)."""
    envelope: dict[str, Any] = {
        "status": status,
        "command": command,
        "version": __version__,
        "data": data if data is not None else {},
        "errors": errors or [],
    }
    if diagnostics and _verbose_mode:
        envelope["diagnostics"] = diagnostics
    return envelope


def print_json(envelope: dict) -> None:
    """Print a JSON envelope to stdout (raw, no ANSI — suitable for piping)."""
    import sys
    sys.stdout.write(json.dumps(envelope, indent=2, default=str) + "\n")
    sys.stdout.flush()


# ── Pretty helpers ──────────────────────────────────────────────

def print_success(msg: str) -> None:
    if not _quiet_mode and not _json_mode:
        console.print(f"[success]✓[/success] {msg}")


def print_error(msg: str) -> None:
    if not _json_mode:
        err_console.print(f"[error]✗ {msg}[/error]")


def print_warning(msg: str) -> None:
    if not _quiet_mode and not _json_mode:
        console.print(f"[warning]⚠[/warning] {msg}")


def print_info(msg: str) -> None:
    if not _quiet_mode and not _json_mode:
        console.print(f"[info]ℹ[/info] {msg}")


def print_verbose(msg: str) -> None:
    if _verbose_mode and not _quiet_mode and not _json_mode:
        console.print(f"[muted]  {msg}[/muted]")


def make_table(title: str, columns: list[tuple[str, str]], rows: list[list[str]]) -> Table:
    """Build a Rich table.

    *columns* is a list of ``(header, style)`` tuples.
    """
    table = Table(title=title, box=box.ROUNDED, show_lines=False, header_style="bold cyan")
    for header, style in columns:
        table.add_column(header, style=style)
    for row in rows:
        table.add_row(*row)
    return table


def make_panel(content: str, title: str = "", border_style: str = "cyan") -> Panel:
    return Panel(content, title=title, border_style=border_style, expand=False)


def get_progress() -> Progress:
    """Return a pre-configured Rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )
