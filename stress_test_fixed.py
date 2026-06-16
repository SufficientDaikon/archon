#!/usr/bin/env python3
"""
CORRECTED STRESS TEST: File-Ops MCP Server
"""

import sys
import tempfile
from pathlib import Path
from hashlib import sha256
import time

# ============================================================================
# UTILITIES
# ============================================================================

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
    """Atomic write: temp file + replace (FIXED for Windows)."""
    import tempfile
    import os

    p = Path(path)

    # Always use '\n' in Python strings
    content_str = '\n'.join(lines) + ('\n' if lines else '')
    content_bytes = content_str.encode(encoding)

    # If file uses CRLF, convert all \n to \r\n
    if line_ending == '\r\n':
        content_bytes = content_bytes.replace(b'\n', b'\r\n')

    # Write in binary mode
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

def _content_hash(lines):
    """SHA256 hash of file content."""
    content = '\n'.join(lines)
    return sha256(content.encode()).hexdigest()[:16]

# ============================================================================
# STRESS TEST
# ============================================================================

class FixedStressTest:
    def __init__(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = Path(self.test_dir) / 'test.py'
        self.ops_passed = 0
        self.ops_failed = 0
        self.start_time = time.time()

    def log(self, label, status, info=''):
        """Log operation."""
        status_str = '[PASS]' if status else '[FAIL]'
        print(f"{status_str} {label:50} {info}")
        if status:
            self.ops_passed += 1
        else:
            self.ops_failed += 1

    def test_1_create_large_file(self):
        """Create 1000+ line file."""
        print("\n" + "="*80)
        print("TEST 1: CREATE 1000+ LINE FILE")
        print("="*80)

        lines = []

        # Header
        lines.extend(['"""Module docstring."""', '', 'import sys', ''])

        # Generate 250 classes with 4 methods each
        for i in range(1, 251):
            lines.append(f'class MyClass{i}:')
            lines.append(f'    """Class {i}."""')
            for j in range(1, 5):
                lines.append(f'    def method_{j}(self):')
                lines.append(f'        """Method {j}."""')
                lines.append(f'        return {i * j}')
                lines.append('')

        # Write and verify
        try:
            _atomic_write(str(self.file_path), lines, 'utf-8', '\n')
            read_lines, enc, le = _read_file_lines(str(self.file_path))

            success = len(read_lines) == len(lines)
            self.log('Create 1000+ lines', success, f'{len(read_lines)} lines')
            return success
        except Exception as e:
            self.log('Create 1000+ lines', False, str(e)[:50])
            return False

    def test_2_simple_edit(self):
        """Edit a single line."""
        print("\n" + "="*80)
        print("TEST 2: SIMPLE EDIT (Single line)")
        print("="*80)

        lines, enc, le = _read_file_lines(str(self.file_path))
        orig_hash = _content_hash(lines)

        # Change line 50
        if len(lines) > 50:
            lines[49] = '# EDITED LINE 50'

        try:
            _atomic_write(str(self.file_path), lines, enc, le)
            verify_lines, _, _ = _read_file_lines(str(self.file_path))

            success = len(verify_lines) == len(lines) and verify_lines[49] == '# EDITED LINE 50'
            self.log('Simple edit', success, f'{len(lines)} lines')
            return success
        except Exception as e:
            self.log('Simple edit', False, str(e)[:50])
            return False

    def test_3_block_replacement(self):
        """Replace 10 lines with 20 lines."""
        print("\n" + "="*80)
        print("TEST 3: BLOCK REPLACEMENT (10 -> 20 lines)")
        print("="*80)

        lines, enc, le = _read_file_lines(str(self.file_path))
        size_before = len(lines)

        # Find a good location
        target_start = 100
        target_end = 110

        if len(lines) > target_end:
            # Extract lines before and after
            before = lines[:target_start]
            after = lines[target_end:]

            # Create replacement
            replacement = [f'# REPLACEMENT LINE {i}' for i in range(1, 21)]

            # Build new lines array
            new_lines = before + replacement + after

            try:
                _atomic_write(str(self.file_path), new_lines, enc, le)
                verify_lines, _, _ = _read_file_lines(str(self.file_path))

                success = len(verify_lines) == len(new_lines)
                self.log('Block replacement', success, f'{size_before} -> {len(verify_lines)} lines')
                return success
            except Exception as e:
                self.log('Block replacement', False, str(e)[:50])
                return False
        else:
            self.log('Block replacement', False, 'File too small')
            return False

    def test_4_mass_insert(self):
        """Insert 500 lines at once."""
        print("\n" + "="*80)
        print("TEST 4: MASS INSERT (500 lines at once)")
        print("="*80)

        lines, enc, le = _read_file_lines(str(self.file_path))
        size_before = len(lines)

        # Insert at line 200
        insert_pos = 200
        if len(lines) > insert_pos:
            before = lines[:insert_pos]
            after = lines[insert_pos:]

            new_block = [f'# INSERTED {i}' for i in range(1, 501)]
            new_lines = before + new_block + after

            try:
                _atomic_write(str(self.file_path), new_lines, enc, le)
                verify_lines, _, _ = _read_file_lines(str(self.file_path))

                success = len(verify_lines) == len(new_lines)
                self.log('Mass insert', success, f'{size_before} -> {len(verify_lines)} lines (+{len(new_lines)-size_before})')
                return success
            except Exception as e:
                self.log('Mass insert', False, str(e)[:50])
                return False
        else:
            self.log('Mass insert', False, 'File too small')
            return False

    def test_5_mass_delete(self):
        """Delete 300 lines."""
        print("\n" + "="*80)
        print("TEST 5: MASS DELETE (300 lines)")
        print("="*80)

        lines, enc, le = _read_file_lines(str(self.file_path))
        size_before = len(lines)

        # Delete lines 150-450
        delete_start = 150
        delete_end = 450

        if len(lines) > delete_end:
            before = lines[:delete_start]
            after = lines[delete_end:]
            new_lines = before + after

            try:
                _atomic_write(str(self.file_path), new_lines, enc, le)
                verify_lines, _, _ = _read_file_lines(str(self.file_path))

                success = len(verify_lines) == len(new_lines)
                self.log('Mass delete', success, f'{size_before} -> {len(verify_lines)} lines (-{size_before-len(verify_lines)})')
                return success
            except Exception as e:
                self.log('Mass delete', False, str(e)[:50])
                return False
        else:
            self.log('Mass delete', False, 'File too small')
            return False

    def test_6_rapid_sequential(self):
        """10 rapid edits in sequence."""
        print("\n" + "="*80)
        print("TEST 6: RAPID SEQUENTIAL (10 edits)")
        print("="*80)

        for i in range(1, 11):
            lines, enc, le = _read_file_lines(str(self.file_path))

            # Random edit
            edit_line = (i * 13) % max(1, len(lines) - 10)
            if edit_line < len(lines):
                lines[edit_line] = f'# RAPID EDIT {i}'

            try:
                _atomic_write(str(self.file_path), lines, enc, le)
                self.log(f'  Sequential edit {i}/10', True, '')
            except Exception as e:
                self.log(f'  Sequential edit {i}/10', False, str(e)[:30])
                return False

        return True

    def test_7_alternating(self):
        """Mix of adds, deletes, and edits."""
        print("\n" + "="*80)
        print("TEST 7: ALTERNATING OPERATIONS")
        print("="*80)

        lines, enc, le = _read_file_lines(str(self.file_path))

        try:
            # Add 100 lines
            lines.extend([f'# ADDED {i}' for i in range(1, 101)])
            _atomic_write(str(self.file_path), lines, enc, le)
            self.log('  +Add 100 lines', True, '')

            # Read back
            lines, enc, le = _read_file_lines(str(self.file_path))

            # Delete 50 lines from middle
            del lines[len(lines)//2:len(lines)//2+50]
            _atomic_write(str(self.file_path), lines, enc, le)
            self.log('  -Delete 50 lines', True, '')

            # Edit 20 scattered lines
            for i in range(1, 21):
                idx = (i * 17) % len(lines)
                lines[idx] = f'# ALT EDIT {i}'
            _atomic_write(str(self.file_path), lines, enc, le)
            self.log('  *Edit 20 lines', True, '')

            # Verify final
            verify_lines, _, _ = _read_file_lines(str(self.file_path))
            final_ok = len(verify_lines) == len(lines)
            self.log('  Final verify', final_ok, f'{len(verify_lines)} lines')

            return final_ok
        except Exception as e:
            self.log('Alternating ops', False, str(e)[:50])
            return False

    def test_8_hash_verification(self):
        """Verify hash stability across operations."""
        print("\n" + "="*80)
        print("TEST 8: HASH STABILITY")
        print("="*80)

        lines, enc, le = _read_file_lines(str(self.file_path))
        hash1 = _content_hash(lines)

        # Write same content back
        _atomic_write(str(self.file_path), lines, enc, le)

        # Read back
        verify_lines, _, _ = _read_file_lines(str(self.file_path))
        hash2 = _content_hash(verify_lines)

        success = hash1 == hash2 and len(lines) == len(verify_lines)
        self.log('Hash stability', success, f'hash={hash1}')
        return success

    def run_all(self):
        """Run complete test suite."""
        print("\n" + "="*80)
        print(" FILE-OPS STRESS TEST - MAXIMUM LOAD")
        print("="*80)

        self.test_1_create_large_file()
        self.test_2_simple_edit()
        self.test_3_block_replacement()
        self.test_4_mass_insert()
        self.test_5_mass_delete()
        self.test_6_rapid_sequential()
        self.test_7_alternating()
        self.test_8_hash_verification()

        elapsed = time.time() - self.start_time

        print("\n" + "="*80)
        print(" FINAL SUMMARY")
        print("="*80)
        print(f"Passed:       {self.ops_passed}")
        print(f"Failed:       {self.ops_failed}")
        print(f"Success Rate: {100 * self.ops_passed / max(1, self.ops_passed + self.ops_failed):.1f}%")
        print(f"Elapsed:      {elapsed:.2f}s")
        print(f"Test File:    {self.file_path}")
        try:
            file_size = self.file_path.stat().st_size
            print(f"File Size:    {file_size:,} bytes")
        except:
            pass
        print("="*80)

        if self.ops_failed == 0:
            print("\n[SUCCESS] ALL STRESS TESTS PASSED")
            return True
        else:
            print(f"\n[FAILED] {self.ops_failed} operation(s) failed")
            return False

if __name__ == '__main__':
    runner = FixedStressTest()
    success = runner.run_all()
    sys.exit(0 if success else 1)
