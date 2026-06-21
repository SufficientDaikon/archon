import os
from pathlib import Path

_root_env = os.environ.get("ARCHON_ROOT", "")
ARCHON_ROOT: Path = Path(_root_env) if _root_env else Path(__file__).parents[3]

VIRTUOSO_XML = ARCHON_ROOT / "virtuoso" / "virtuoso.xml"
SKILLS_DIR = ARCHON_ROOT / "skills"
PROVIDERS_YAML = Path(__file__).parents[2] / "providers.yaml"
