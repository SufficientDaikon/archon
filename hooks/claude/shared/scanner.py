"""Secret scanning and security pattern detection.

Used by guard_bash.py and guard_write.py (PreToolUse hooks) and
quality_bash.py (PostToolUse) for test/build command detection.

All patterns compiled at import time for maximum speed (<50ms per call).
"""

import re

# -- Secret patterns (compiled once) --
# Negative lookahead excludes safe patterns: env-var lookups, config reads
_SAFE_VALUE = r"(?!os\.getenv|os\.environ|process\.env|config\.get|get_env|ENV\[|\$\{)"
SECRET_PATTERNS = [
    (re.compile(r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?'+ _SAFE_VALUE + r'[A-Za-z0-9_\-]{20,}', re.I), "API key"),
    (re.compile(r'(?:secret|password|passwd|pwd)\s*[=:]\s*["\']?' + _SAFE_VALUE + r'[^\s"\']{8,}', re.I), "Password/secret"),
    (re.compile(r'(?:token)\s*[=:]\s*["\']?' + _SAFE_VALUE + r'[A-Za-z0-9_\-\.]{20,}', re.I), "Token"),
    (re.compile(r'(?:aws_access_key_id|aws_secret_access_key)\s*[=:]\s*["\']?' + _SAFE_VALUE + r'\w{16,}', re.I), "AWS credential"),
    (re.compile(r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----'), "Private key"),
    (re.compile(r'ghp_[A-Za-z0-9]{36,}'), "GitHub personal access token"),
    (re.compile(r'gho_[A-Za-z0-9]{36,}'), "GitHub OAuth token"),
    (re.compile(r'ghs_[A-Za-z0-9]{36,}'), "GitHub server token"),
    (re.compile(r'github_pat_[A-Za-z0-9_]{22,}'), "GitHub fine-grained PAT"),
    (re.compile(r'sk-ant-[A-Za-z0-9\-]{20,}'), "Anthropic API key"),
    (re.compile(r'sk-(?:proj-)?[A-Za-z0-9\-]{20,}'), "OpenAI API key"),
    (re.compile(r'xox[bpsar]-[A-Za-z0-9\-]{10,}'), "Slack token"),
    (re.compile(r'AKIA[A-Z0-9]{16}'), "AWS access key ID"),
    (re.compile(r'glpat-[A-Za-z0-9\-_]{20,}'), "GitLab personal access token"),
    (re.compile(r'sk_(?:live|test)_[A-Za-z0-9]{24,}'), "Stripe secret key"),
    (re.compile(r'rk_(?:live|test)_[A-Za-z0-9]{24,}'), "Stripe restricted key"),
    (re.compile(r'AIzaSy[A-Za-z0-9\-_]{33}'), "Google API key"),
    (re.compile(r'sq0atp-[A-Za-z0-9\-_]{22,}'), "Square access token"),
]

# Files that are expected to contain secret-like patterns (don't flag these)
SECRET_ALLOWLIST_PATTERNS = [
    re.compile(r'\.env\.example$', re.I),
    re.compile(r'\.env\.template$', re.I),
    re.compile(r'\.env\.sample$', re.I),
    re.compile(r'scanner\.py$'),  # this file itself
    # Test files across languages
    re.compile(r'test[^/\\]*\.(py|js|ts|jsx|tsx|rb|go|rs|java)$', re.I),
    re.compile(r'\.(test|spec)\.(js|ts|jsx|tsx)$', re.I),
    re.compile(r'\.cy\.(js|ts)$', re.I),
    re.compile(r'spec[/\\].*\.(rb|js|ts)$', re.I),
    re.compile(r'__tests__[/\\]', re.I),
]

# -- Dangerous bash command patterns --
DANGEROUS_COMMANDS = [
    (re.compile(r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/(?!tmp)'), "rm targeting root filesystem"),
    (re.compile(r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?~'), "rm targeting home directory"),
    (re.compile(r'\bchmod\s+777\b'), "chmod 777 (world-writable)"),
    (re.compile(r'\bcurl\s+.*\|\s*(bash|sh|python)\b'), "piping curl to shell"),
    (re.compile(r'\bwget\s+.*\|\s*(bash|sh|python)\b'), "piping wget to shell"),
    # Only flag DROP/TRUNCATE when piped to a DB client
    (re.compile(r'\b(DROP|TRUNCATE)\s+(TABLE|DATABASE)\b.*\|\s*(psql|mysql|sqlite3|mongosh)', re.I), "destructive SQL piped to database"),
    (re.compile(r'\bgit\s+push\s+.*--force\s+.*(main|master)\b'), "force push to main/master"),
    (re.compile(r'\bgit\s+push\s+-f\s+.*(main|master)\b'), "force push to main/master"),
    # git reset --hard: only block when targeting main/master or origin
    (re.compile(r'\bgit\s+reset\s+--hard\s+.*\b(main|master|origin)\b'), "git reset --hard targeting main/master/origin"),
    (re.compile(r':(){.*\|.*&\s*};'), "fork bomb"),
    (re.compile(r'>\s*/dev/sd[a-z]'), "writing directly to disk device"),
    (re.compile(r'\bmkfs\b'), "formatting filesystem"),
    (re.compile(r'\bdd\s+.*of=/dev/'), "dd to raw device"),
    # Windows/PowerShell dangerous commands
    (re.compile(r'powershell.*Remove-Item.*-Recurse.*-Force', re.I), "PowerShell recursive force delete"),
    (re.compile(r'powershell.*Format-Volume', re.I), "PowerShell format volume"),
    (re.compile(r'pwsh.*Remove-Item.*-Recurse.*-Force', re.I), "PowerShell Core recursive force delete"),
]

# -- Test command patterns --
TEST_PATTERNS = [
    re.compile(r'\b(pytest|py\.test)\b'),
    re.compile(r'\bpython\s+(-m\s+)?(pytest|unittest)\b'),
    re.compile(r'\b(vitest|jest|mocha|jasmine)\b'),
    re.compile(r'\bnpm\s+(run\s+)?test\b'),
    re.compile(r'\byarn\s+test\b'),
    re.compile(r'\bpnpm\s+(run\s+)?test\b'),
    re.compile(r'\bcargo\s+test\b'),
    re.compile(r'\bgo\s+test\b'),
    re.compile(r'\bdotnet\s+test\b'),
    re.compile(r'\bplaywright\s+test\b'),
]

# -- Build command patterns --
BUILD_PATTERNS = [
    re.compile(r'\bnpm\s+run\s+build\b'),
    re.compile(r'\byarn\s+build\b'),
    re.compile(r'\bpnpm\s+(run\s+)?build\b'),
    re.compile(r'\bcargo\s+build\b'),
    re.compile(r'\bgo\s+build\b'),
    re.compile(r'\bmake\b'),
    re.compile(r'\bcmake\b'),
    re.compile(r'\btsc\b'),
    re.compile(r'\bwebpack\b'),
    re.compile(r'\bvite\s+build\b'),
    re.compile(r'\bastro\s+build\b'),
    re.compile(r'\bnext\s+build\b'),
    re.compile(r'\bdotnet\s+build\b'),
    re.compile(r'\bpython\s+.*setup\.py\s+build\b'),
]


def scan_for_secrets(content: str, file_path: str = "") -> list[dict[str, str]]:
    """Scan content for secret patterns. Returns list of findings."""
    # Skip allowlisted files
    if file_path:
        for pattern in SECRET_ALLOWLIST_PATTERNS:
            if pattern.search(file_path):
                return []

    findings = []
    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern, secret_type in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "type": secret_type,
                    "line": str(line_num),
                })
                break  # one finding per line is enough
    return findings


def scan_bash_command(command: str) -> list[dict[str, str]]:
    """Scan a bash command for dangerous patterns. Returns findings."""
    findings = []
    for pattern, description in DANGEROUS_COMMANDS:
        if pattern.search(command):
            findings.append({
                "description": description,
                "pattern": pattern.pattern[:60],
            })
    return findings


def is_test_command(command: str) -> bool:
    """Detect if a command is running tests."""
    return any(p.search(command) for p in TEST_PATTERNS)


def is_build_command(command: str) -> bool:
    """Detect if a command is building the project."""
    return any(p.search(command) for p in BUILD_PATTERNS)
