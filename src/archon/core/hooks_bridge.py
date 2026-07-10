"""Bridge from the archon package to the stdlib-only hook-shared modules.

The properties registry, state-path logic, and classifier live in
``hooks/claude/shared/`` so the hooks (subprocesses with no package installed)
can import them. The CLI must not duplicate that logic — it loads the same
modules from the repo tree via importlib.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from archon.utils.paths import get_archon_root

_cache: dict[str, ModuleType] = {}


class HooksBridgeError(RuntimeError):
    """The hooks/claude/shared/ tree is not available (e.g. bare pip install)."""


def load_shared(module_name: str) -> ModuleType:
    """Load ``hooks/claude/shared/<module_name>.py`` from the archon root.

    Cached per process. Raises HooksBridgeError with a clear message when the
    hooks tree can't be found — callers should surface it, not traceback.
    """
    if module_name in _cache:
        return _cache[module_name]

    root = get_archon_root()
    shared_dir = Path(root) / "hooks" / "claude" / "shared"
    module_path = shared_dir / f"{module_name}.py"
    if not module_path.is_file():
        raise HooksBridgeError(
            f"Hook module not found: {module_path}. "
            "This command needs the Archon repo tree (hooks/claude/shared/); "
            "run it from an Archon checkout or set ARCHON_ROOT."
        )

    spec = importlib.util.spec_from_file_location(f"archon_hooks_shared.{module_name}", module_path)
    if spec is None or spec.loader is None:
        raise HooksBridgeError(f"Cannot load hook module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    # shared modules import each other as top-level names (e.g. classifier
    # does not, but state/hooklog may); keep sys.path untouched — they are
    # self-contained by convention.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _cache[module_name] = module
    return module
