"""
OMNISKILL Adapters Package
Cross-platform skill installation adapters.
"""

from pathlib import Path
import sys

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base import BaseAdapter

# Import platform-specific adapters
try:
    from antigravity.adapter import AntigravityAdapter
except ImportError:
    AntigravityAdapter = None

try:
    from claude_code.adapter import ClaudeCodeAdapter
except ImportError:
    try:
        # Try with hyphen directory name
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "claude_code_adapter",
            Path(__file__).parent / "claude-code" / "adapter.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ClaudeCodeAdapter = module.ClaudeCodeAdapter
        else:
            ClaudeCodeAdapter = None
    except Exception:
        ClaudeCodeAdapter = None

try:
    from copilot_cli.adapter import CopilotCLIAdapter
except ImportError:
    try:
        # Try with hyphen directory name
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "copilot_cli_adapter",
            Path(__file__).parent / "copilot-cli" / "adapter.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            CopilotCLIAdapter = module.CopilotCLIAdapter
        else:
            CopilotCLIAdapter = None
    except Exception:
        CopilotCLIAdapter = None

try:
    from cursor.adapter import CursorAdapter
except ImportError:
    CursorAdapter = None

try:
    from windsurf.adapter import WindsurfAdapter
except ImportError:
    WindsurfAdapter = None


# Registry of available adapters
ADAPTERS = {
    'antigravity': AntigravityAdapter,
    'claude-code': ClaudeCodeAdapter,
    'copilot-cli': CopilotCLIAdapter,
    'cursor': CursorAdapter,
    'windsurf': WindsurfAdapter,
}


def get_adapter(platform: str) -> BaseAdapter:
    """
    Get an adapter instance for a specific platform.
    
    Args:
        platform: Platform name (antigravity, claude-code, copilot-cli, cursor, windsurf)
        
    Returns:
        Adapter instance
        
    Raises:
        ValueError: If platform is not supported or adapter failed to load
    """
    adapter_class = ADAPTERS.get(platform)
    
    if adapter_class is None:
        raise ValueError(f"Platform '{platform}' is not supported or failed to load")
    
    return adapter_class()


def get_available_platforms():
    """
    Get list of platforms that have working adapters.
    
    Returns:
        List of platform names
    """
    return [name for name, cls in ADAPTERS.items() if cls is not None]


__all__ = [
    'BaseAdapter',
    'AntigravityAdapter',
    'ClaudeCodeAdapter',
    'CopilotCLIAdapter',
    'CursorAdapter',
    'WindsurfAdapter',
    'get_adapter',
    'get_available_platforms',
    'ADAPTERS',
]
