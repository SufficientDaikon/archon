#!/usr/bin/env python3
"""DEBUG: Find the bug in read/write cycle."""

import tempfile
from pathlib import Path

def _read_file_lines(path: str):
    """Read file as lines."""
    p = Path(path)
    raw = p.read_bytes()
    encoding = 'utf-8'
    try:
        content = raw.decode('utf-8')
    except UnicodeDecodeError:
        encoding = 'latin-1'
        content = raw.decode('latin-1')
    line_ending = '\r\n' if b'\r\n' in raw else '\n'
    lines = content.splitlines()
    return lines, encoding, line_ending

def _atomic_write(path: str, lines, encoding: str, line_ending: str):
    """Atomic write: temp file + replace.

    FIX: Use binary mode to avoid automatic newline conversion.
    """
    import tempfile
    import os
    p = Path(path)

    # Always use '\n' in Python strings; encode as bytes with explicit line ending
    content_str = '\n'.join(lines) + ('\n' if lines else '')
    content_bytes = content_str.encode(encoding)

    # If we detected CRLF, convert all \n to \r\n in the bytes
    if line_ending == '\r\n':
        content_bytes = content_bytes.replace(b'\n', b'\r\n')

    # Write in binary mode to avoid Python's automatic conversion
    with tempfile.NamedTemporaryFile(
        mode='wb',
        dir=p.parent,
        delete=False,
    ) as tmp:
        tmp.write(content_bytes)
        tmp_path = tmp.name

    try:
        os.replace(tmp_path, path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise

# ============================================================================
# MINIMAL DEBUG TEST
# ============================================================================

print("DEBUG TEST: Read/Write Cycle")
print("="*80)

# Create temp file
test_dir = tempfile.mkdtemp()
file_path = Path(test_dir) / 'debug.txt'

# STEP 1: Create file with 10 lines
print("\nSTEP 1: Create file with 10 lines")
lines = [f'Line {i}' for i in range(1, 11)]
print(f"  Original lines: {len(lines)}")
_atomic_write(str(file_path), lines, 'utf-8', '\n')

# STEP 2: Read back
print("\nSTEP 2: Read back")
read_lines, enc, le = _read_file_lines(str(file_path))
print(f"  Read lines: {len(read_lines)}")
print(f"  Content matches: {read_lines == lines}")
print(f"  Encoding: {enc}, Line ending: {repr(le)}")

# STEP 3: Modify one line
print("\nSTEP 3: Modify line 5")
print(f"  Before: '{read_lines[4]}'")
read_lines[4] = 'Line 5 MODIFIED'
print(f"  After: '{read_lines[4]}'")
print(f"  Total lines still: {len(read_lines)}")

# STEP 4: Write back
print("\nSTEP 4: Write back")
_atomic_write(str(file_path), read_lines, enc, le)

# STEP 5: Read again
print("\nSTEP 5: Read again")
read_lines2, _, _ = _read_file_lines(str(file_path))
print(f"  Read lines: {len(read_lines2)}")
print(f"  Line 5: '{read_lines2[4]}'")
print(f"  Content matches: {read_lines2 == read_lines}")

if len(read_lines2) != len(lines):
    print(f"\n!!! BUG DETECTED !!!")
    print(f"Expected {len(lines)} lines, got {len(read_lines2)} lines")
    print(f"File size: {file_path.stat().st_size} bytes")
    print(f"First 5 lines of file:")
    with open(file_path) as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(f"  {i+1}: {repr(line)}")
else:
    print("\nOK: Read/write cycle is stable")
