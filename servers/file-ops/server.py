"""File Operations MCP Server — line-number-based file editing for Claude Code.

Solves the two critical pain points in Claude Code's built-in file tools:
1. Edit tool: exact string matching is fragile (whitespace, CRLF, context window drift)
2. Read tool: line numbers pollute content, making edits fail

APPROACH: All operations use line numbers instead of strings. Atomic multiline edits.
No string matching. No baked-in line numbers. Structured content responses.

Prefer these tools over built-in Read/Edit/Write for all file operations:
- file_read: Raw content + line metadata (no line number pollution)
- file_edit: Edit by line ranges, batch atomic edits
- file_structure: Language-aware outline (Python, JS, etc.)
- file_search: Find + context (no string encoding issues)
- file_insert: Insert at line N
- file_create: New files with parent dir creation

Typical workflow: file_read → (optional: file_structure) → file_edit → file_read (verify)

Fall back to built-in tools for: images, PDFs, notebooks (.ipynb), binary files.

Usage:
    python server.py                    # stdio transport (default)
    python server.py --trace            # enable debug tracing
"""

from __future__ import annotations

import json
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Optional, Any
from hashlib import sha256

from fastmcp import FastMCP, Context


# ── Configuration ────────────────────────────────────────────────

DEFAULT_LARGE_FILE_THRESHOLD = 800  # lines


# ── Utilities ────────────────────────────────────────────────────

def _read_file_lines(path: str) -> tuple[list[str], str, str]:
    """Read file as lines, detect encoding and line ending.

    Returns: (lines, encoding, line_ending)
    lines: list of lines WITHOUT terminator (ready for editing)
    encoding: detected encoding (utf-8 or latin-1)
    line_ending: '\n' or '\r\n' (detected from file)
    """
    p = Path(path)

    # Read raw bytes to detect encoding and line endings
    raw = p.read_bytes()

    # Detect encoding
    encoding = 'utf-8'
    try:
        content = raw.decode('utf-8')
    except UnicodeDecodeError:
        encoding = 'latin-1'
        content = raw.decode('latin-1')

    # Detect line ending
    line_ending = '\r\n' if b'\r\n' in raw else '\n'

    # Split into lines (remove terminators)
    lines = content.splitlines()

    return lines, encoding, line_ending


def _detect_language(path: str) -> Optional[str]:
    """Detect language from file extension."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'cpp',
        '.sh': 'bash',
        '.rb': 'ruby',
    }
    return ext_map.get(Path(path).suffix)


def _get_file_structure(path: str, content_lines: list[str]) -> dict:
    """Extract language-aware file structure (Python, JS, etc.)."""
    language = _detect_language(path)

    if language == 'python':
        return _structure_python(content_lines)
    elif language in ('javascript', 'typescript'):
        return _structure_javascript(content_lines)
    else:
        # Fallback for unknown languages
        return {'outline': [], 'language': language, 'note': 'language-agnostic outline only'}


def _structure_python(lines: list[str]) -> dict:
    """Extract Python structure: classes, functions, methods."""
    outline = []

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()

        # Class definition
        if stripped.startswith('class '):
            match = re.match(r'class\s+(\w+)', stripped)
            if match:
                outline.append({
                    'type': 'class',
                    'name': match.group(1),
                    'line': i,
                    'indent': len(line) - len(stripped),
                })

        # Function/method definition
        elif stripped.startswith('def '):
            match = re.match(r'def\s+(\w+)', stripped)
            if match:
                indent = len(line) - len(stripped)
                outline.append({
                    'type': 'function' if indent == 0 else 'method',
                    'name': match.group(1),
                    'line': i,
                    'indent': indent,
                })

    return {
        'outline': outline,
        'language': 'python',
        'total_lines': len(lines),
    }


def _structure_javascript(lines: list[str]) -> dict:
    """Extract JavaScript/TypeScript structure: classes, functions, methods."""
    outline = []

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()

        # Class definition
        if re.match(r'(export\s+)?(async\s+)?class\s+\w+', stripped):
            match = re.search(r'class\s+(\w+)', stripped)
            if match:
                outline.append({
                    'type': 'class',
                    'name': match.group(1),
                    'line': i,
                })

        # Function definition (exported, async, arrow, etc.)
        elif re.match(r'(export\s+)?(async\s+)?(function|\w+\s*=)', stripped):
            # function foo() or const foo = () or export async function
            match = re.search(r'(?:function\s+)?(\w+)\s*(?:[:=]|\()', stripped)
            if match:
                outline.append({
                    'type': 'function',
                    'name': match.group(1),
                    'line': i,
                })

    return {
        'outline': outline,
        'language': 'javascript',
        'total_lines': len(lines),
    }


def _atomic_write(path: str, lines: list[str], encoding: str, line_ending: str) -> None:
    """Atomic write: temp file + replace. Prevents partial writes.

    CRITICAL: Uses binary mode to avoid automatic newline conversion by Python's
    text mode, which was causing line duplication on Windows.
    """
    import tempfile
    import os

    p = Path(path)

    # Always use '\n' in Python strings for consistency
    content_str = '\n'.join(lines) + ('\n' if lines else '')

    # Encode to bytes
    content_bytes = content_str.encode(encoding)

    # If file uses CRLF, convert all \n to \r\n in the bytes
    if line_ending == '\r\n':
        content_bytes = content_bytes.replace(b'\n', b'\r\n')

    # Write in binary mode to avoid Python's automatic newline conversion
    with tempfile.NamedTemporaryFile(
        mode='wb',
        dir=p.parent,
        delete=False,
    ) as tmp:
        tmp.write(content_bytes)
        tmp_path = tmp.name

    try:
        # Atomic replace on same filesystem
        os.replace(tmp_path, path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def _content_hash(lines: list[str]) -> str:
    """SHA256 hash of file content (for external change detection)."""
    content = '\n'.join(lines)
    return sha256(content.encode()).hexdigest()[:16]


def _unified_diff(original: list[str], modified: list[str]) -> str:
    """Generate unified diff between original and modified lines."""
    import difflib

    diff = difflib.unified_diff(
        original,
        modified,
        lineterm='',
        fromfile='original',
        tofile='modified',
    )
    return '\n'.join(diff)


# ── Lifespan (session state) ─────────────────────────────────────

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Initialize server state on startup."""
    # We don't need external resources, but we track open files for verification
    yield {
        'open_files': {},  # path -> (lines, encoding, line_ending, hash)
    }


# ── Server ───────────────────────────────────────────────────────

mcp = FastMCP(
    "file-ops",
    lifespan=app_lifespan,
)


# ── Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def file_read(
    path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    ctx: Context = None,
) -> str:
    """Read file content — raw, no baked-in line numbers.

    Returns clean content + metadata. Line range parameters enable targeted reads
    for large files without token waste.

    Args:
        path: File to read
        start_line: First line to read (1-indexed, inclusive). Omit for start of file.
        end_line: Last line to read (1-indexed, inclusive). Omit for end of file.

    Returns: JSON with content (raw), lines metadata, encoding, truncation status.
    """
    p = Path(path)

    if not p.exists():
        return json.dumps({
            "error": f"File not found: {path}",
            "exists": False,
        })

    if p.is_dir():
        return json.dumps({
            "error": f"Is a directory: {path}",
            "is_directory": True,
        })

    try:
        lines, encoding, line_ending = _read_file_lines(str(p))
    except Exception as e:
        return json.dumps({
            "error": f"Cannot read file: {e}",
        })

    total_lines = len(lines)

    # Default: read all lines
    start_idx = 0
    end_idx = total_lines

    if start_line is not None:
        start_idx = max(0, start_line - 1)  # Convert 1-indexed to 0-indexed

    if end_line is not None:
        end_idx = min(total_lines, end_line)  # end_line is inclusive

    selected_lines = lines[start_idx:end_idx]
    truncated = (start_line is not None or end_line is not None) and not (start_line == 1 and end_line == total_lines)

    # Large file guidance
    large_file_note = ""
    if total_lines > DEFAULT_LARGE_FILE_THRESHOLD and start_line is None:
        large_file_note = f"⚠ Large file ({total_lines} lines). Consider using start_line/end_line for targeted reads, or file_structure for an outline."

    content = '\n'.join(selected_lines)

    return json.dumps({
        "content": content,
        "lines": {
            "start": start_idx + 1,  # Convert back to 1-indexed for display
            "end": end_idx,
            "total": total_lines,
        },
        "encoding": encoding,
        "line_ending": "CRLF" if line_ending == '\r\n' else "LF",
        "content_hash": _content_hash(lines),
        "truncated": truncated,
        "note": large_file_note or None,
    })


@mcp.tool()
async def file_structure(
    path: str,
    ctx: Context = None,
) -> str:
    """Get file structure — language-aware outline of classes, functions, etc.

    Useful for navigating large files without reading full content.
    Much cheaper than file_read in tokens. Falls back to simple outline
    for unknown languages.

    Args:
        path: File to analyze

    Returns: JSON with language, outline (array of {type, name, line, ...}), total_lines.
    """
    p = Path(path)

    if not p.exists():
        return json.dumps({"error": f"File not found: {path}"})

    try:
        lines, _, _ = _read_file_lines(str(p))
    except Exception as e:
        return json.dumps({"error": f"Cannot read file: {e}"})

    structure = _get_file_structure(str(p), lines)
    return json.dumps(structure, indent=2)


@mcp.tool()
async def file_search(
    path: str,
    pattern: str,
    literal: bool = False,
    context_lines: int = 2,
    ctx: Context = None,
) -> str:
    """Search file for pattern, return matches with context.

    Args:
        path: File to search
        pattern: Regex pattern or literal string (if literal=True)
        literal: If True, treat pattern as literal string (not regex)
        context_lines: Lines before/after each match to include

    Returns: JSON with array of matches [{line_number, text, context_before, context_after}]
    """
    p = Path(path)

    if not p.exists():
        return json.dumps({"error": f"File not found: {path}"})

    try:
        lines, _, _ = _read_file_lines(str(p))
    except Exception as e:
        return json.dumps({"error": f"Cannot read file: {e}"})

    matches = []

    try:
        if literal:
            regex = re.compile(re.escape(pattern))
        else:
            regex = re.compile(pattern)
    except re.error as e:
        return json.dumps({"error": f"Invalid regex: {e}"})

    for i, line in enumerate(lines, start=1):
        if regex.search(line):
            context_before = [
                {'line': max(1, i - j), 'text': lines[i - j - 2]}
                for j in range(1, context_lines + 1)
                if i - j > 0
            ]
            context_before.reverse()

            context_after = [
                {'line': i + j, 'text': lines[i + j - 1]}
                for j in range(1, context_lines + 1)
                if i + j <= len(lines)
            ]

            matches.append({
                'line_number': i,
                'text': line,
                'context_before': context_before,
                'context_after': context_after,
            })

    return json.dumps({
        "pattern": pattern,
        "literal": literal,
        "matches": matches,
        "total_matches": len(matches),
    }, indent=2)


@mcp.tool()
async def file_edit(
    path: str,
    edits: list[dict],
    dry_run: bool = False,
    expected_hash: Optional[str] = None,
    ctx: Context = None,
) -> str:
    """Apply one or more edits to a file atomically by line ranges.

    All edits succeed or none apply (atomic). Edits are auto-sorted bottom-up
    to prevent line-shift cascades. Returns unified diff of changes.

    Args:
        path: File to edit
        edits: List of {start_line, end_line, content} — replaces lines [start, end] inclusive
        dry_run: If True, show diff without writing
        expected_hash: If provided, verify file hasn't changed externally

    Returns: JSON with diff, new_total_lines, new_content_hash, applied (bool).
    """
    p = Path(path)

    if not p.exists():
        return json.dumps({"error": f"File not found: {path}"})

    try:
        lines, encoding, line_ending = _read_file_lines(str(p))
    except Exception as e:
        return json.dumps({"error": f"Cannot read file: {e}"})

    # Verify external change if requested
    current_hash = _content_hash(lines)
    if expected_hash and expected_hash != current_hash:
        return json.dumps({
            "error": "File changed externally",
            "current_hash": current_hash,
            "expected_hash": expected_hash,
            "applied": False,
        })

    original_lines = lines.copy()

    # Parse and validate edits
    validated_edits = []
    for edit in edits:
        start = edit['start_line']
        end = edit['end_line']
        content = edit['content']

        # Validate bounds
        if not (1 <= start <= len(lines) + 1):
            return json.dumps({"error": f"start_line {start} out of range (1-{len(lines) + 1})"})
        if not (start <= end <= len(lines)):
            return json.dumps({"error": f"end_line {end} out of range ({start}-{len(lines)})"})

        validated_edits.append((start - 1, end - 1, content))  # Convert to 0-indexed, inclusive

    # Sort bottom-up (highest line first) to prevent cascading shifts
    validated_edits.sort(reverse=True)

    # Apply edits
    for start_idx, end_idx, content in validated_edits:
        # Replace lines[start_idx:end_idx+1] with new content
        new_lines = content.splitlines() if content else []
        lines = lines[:start_idx] + new_lines + lines[end_idx + 1:]

    # Generate diff
    diff = _unified_diff(original_lines, lines)

    # Write if not dry run
    if not dry_run:
        try:
            _atomic_write(str(p), lines, encoding, line_ending)
        except Exception as e:
            return json.dumps({"error": f"Write failed: {e}", "applied": False})

    return json.dumps({
        "diff": diff,
        "new_total_lines": len(lines),
        "new_content_hash": _content_hash(lines),
        "applied": not dry_run,
    })


@mcp.tool()
async def file_insert(
    path: str,
    line: int,
    content: str,
    ctx: Context = None,
) -> str:
    """Insert content at a specific line without replacing anything.

    Content appears BEFORE the specified line. Use line > total_lines to append.

    Args:
        path: File to insert into
        line: Line number (1-indexed). Content goes BEFORE this line.
        content: Content to insert (may be multi-line)

    Returns: JSON with diff, new_total_lines, new_content_hash.
    """
    p = Path(path)

    if not p.exists():
        return json.dumps({"error": f"File not found: {path}"})

    try:
        lines, encoding, line_ending = _read_file_lines(str(p))
    except Exception as e:
        return json.dumps({"error": f"Cannot read file: {e}"})

    original_lines = lines.copy()

    # Insert position: line 1 → before first line (idx 0)
    # line > len(lines) → append at end
    insert_idx = max(0, min(len(lines), line - 1))

    new_lines = content.splitlines() if content else []
    lines = lines[:insert_idx] + new_lines + lines[insert_idx:]

    # Generate diff
    diff = _unified_diff(original_lines, lines)

    # Write
    try:
        _atomic_write(str(p), lines, encoding, line_ending)
    except Exception as e:
        return json.dumps({"error": f"Write failed: {e}"})

    return json.dumps({
        "diff": diff,
        "new_total_lines": len(lines),
        "new_content_hash": _content_hash(lines),
    })


@mcp.tool()
async def file_create(
    path: str,
    content: str = "",
    create_dirs: bool = True,
    ctx: Context = None,
) -> str:
    """Create a new file. Creates parent directories if needed.

    Fails if file already exists — use file_edit for existing files.

    Args:
        path: Path to new file
        content: Initial content (optional, defaults to empty)
        create_dirs: If True, create parent directories if they don't exist

    Returns: JSON with total_lines, size_bytes, content_hash.
    """
    p = Path(path)

    if p.exists():
        return json.dumps({"error": f"File already exists: {path}"})

    if not p.parent.exists():
        if create_dirs:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return json.dumps({"error": f"Cannot create parent directories: {e}"})
        else:
            return json.dumps({"error": f"Parent directory does not exist: {p.parent}"})

    # Write file
    try:
        lines = content.splitlines() if content else []
        _atomic_write(str(p), lines, 'utf-8', '\n')
    except Exception as e:
        return json.dumps({"error": f"Cannot create file: {e}"})

    return json.dumps({
        "total_lines": len(lines),
        "size_bytes": len(content.encode()),
        "content_hash": _content_hash(lines),
    })


# ── ServerHandler setup ────────────────────────────────────────

# FastMCP handles ServerHandler automatically via decorators


# ── Entry point ────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
