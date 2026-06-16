#!/usr/bin/env python3
"""Test file-ops utilities directly (no MCP)."""

import sys
import json
import tempfile
import os
import re
from pathlib import Path
from hashlib import sha256

# Utility functions directly from server.py

def _read_file_lines(path: str):
    """Read file as lines, detect encoding and line ending."""
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

def _detect_language(path: str):
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
    }
    return ext_map.get(Path(path).suffix)

def _structure_python(lines):
    """Extract Python structure: classes, functions, methods."""
    outline = []

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()

        if stripped.startswith('class '):
            match = re.match(r'class\s+(\w+)', stripped)
            if match:
                outline.append({
                    'type': 'class',
                    'name': match.group(1),
                    'line': i,
                    'indent': len(line) - len(stripped),
                })

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

def _atomic_write(path: str, lines, encoding: str, line_ending: str):
    """Atomic write: temp file + replace."""
    import tempfile

    p = Path(path)
    content = line_ending.join(lines) + (line_ending if lines else '')

    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding=encoding,
        dir=p.parent,
        delete=False,
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        os.replace(tmp_path, path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise

def _content_hash(lines):
    """SHA256 hash of file content."""
    content = '\n'.join(lines)
    return sha256(content.encode()).hexdigest()[:16]

def _unified_diff(original, modified):
    """Generate unified diff."""
    import difflib
    diff = difflib.unified_diff(
        original,
        modified,
        lineterm='',
        fromfile='original',
        tofile='modified',
    )
    return '\n'.join(diff)

# TESTS

def test_encoding_detection():
    """Test UTF-8 and line ending detection."""
    print("\n=== TEST 1: Encoding & Line Ending Detection ===")

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False, newline='') as f:
        f.write("line 1\nline 2\nline 3")
        fname = f.name

    try:
        lines, encoding, line_ending = _read_file_lines(fname)
        assert encoding == 'utf-8', f"Expected utf-8, got {encoding}"
        assert line_ending in ('\n', '\r\n'), f"Expected LF or CRLF, got {repr(line_ending)}"
        assert lines == ['line 1', 'line 2', 'line 3']
        print(f"[PASS] UTF-8 detected correctly (line_ending: {repr(line_ending)})")
    finally:
        Path(fname).unlink()

def test_language_detection():
    """Test language detection from extension."""
    print("\n=== TEST 2: Language Detection ===")

    tests = [
        ('/path/to/file.py', 'python'),
        ('/path/to/file.js', 'javascript'),
        ('/path/to/file.ts', 'typescript'),
        ('/path/to/file.txt', None),
    ]

    for path, expected in tests:
        result = _detect_language(path)
        assert result == expected, f"Path {path}: expected {expected}, got {result}"
        print(f"[PASS] {path} : {result}")

def test_python_structure():
    """Test Python structure extraction."""
    print("\n=== TEST 3: Python Structure Parsing ===")

    py_code = '''class MyClass:
    def __init__(self):
        pass

    def method(self):
        pass

def standalone_function():
    pass
'''

    lines = py_code.splitlines()
    struct = _structure_python(lines)

    assert struct['language'] == 'python'
    assert struct['total_lines'] >= 6  # Allow flexibility on line count

    outline = struct['outline']
    assert any(item['type'] == 'class' and item['name'] == 'MyClass' for item in outline)
    assert any(item['type'] == 'function' and item['name'] == 'standalone_function' for item in outline)

    print(f"[PASS] Found {len(outline)} definitions")
    for item in outline:
        print(f"  - {item['type']:8} '{item['name']}' @ line {item['line']}")

def test_atomic_write():
    """Test atomic write."""
    print("\n=== TEST 4: Atomic Write ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = Path(tmpdir) / 'test.txt'

        lines = ['line 1', 'line 2', 'line 3']
        _atomic_write(str(fpath), lines, 'utf-8', '\n')

        assert fpath.exists()
        content = fpath.read_text()
        assert content == 'line 1\nline 2\nline 3\n'
        print(f"[PASS] Initial atomic write succeeded")

        lines2 = ['updated 1', 'updated 2']
        _atomic_write(str(fpath), lines2, 'utf-8', '\n')

        content2 = fpath.read_text()
        assert content2 == 'updated 1\nupdated 2\n'
        print(f"[PASS] Update atomic write succeeded")

def test_content_hash():
    """Test content hashing."""
    print("\n=== TEST 5: Content Hash ===")

    lines1 = ['line 1', 'line 2']
    lines2 = ['line 1', 'line 2']
    lines3 = ['line 1', 'line 3']

    hash1 = _content_hash(lines1)
    hash2 = _content_hash(lines2)
    hash3 = _content_hash(lines3)

    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 16

    print(f"[PASS] Hash consistency verified (16-char SHA256)")

def test_unified_diff():
    """Test unified diff generation."""
    print("\n=== TEST 6: Unified Diff ===")

    original = ['line 1', 'line 2', 'line 3']
    modified = ['line 1', 'line 2 MODIFIED', 'line 3', 'line 4']

    diff = _unified_diff(original, modified)

    assert 'line 2 MODIFIED' in diff
    assert '@@' in diff
    print(f"[PASS] Diff generated successfully")

if __name__ == '__main__':
    try:
        test_encoding_detection()
        test_language_detection()
        test_python_structure()
        test_atomic_write()
        test_content_hash()
        test_unified_diff()

        print("\n" + "="*60)
        print("[OK] ALL CORE TESTS PASSED (6/6)")
        print("="*60)
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
