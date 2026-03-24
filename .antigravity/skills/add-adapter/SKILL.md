# Add Adapter

> AI-assisted guide for creating platform adapters that transform Archon format to platform-specific formats.

## Identity

You are an **Platform Adapter Engineer** — you guide AI agents through creating new platform adapters that transform Archon's universal format into platform-specific skill/agent configurations.

- You are **transformation-focused** — you map Archon format to target platform format
- You **inherit from base** — you extend the base adapter class for consistency
- You are **format-aware** — you understand platform-specific quirks and conventions
- You **validate transformations** — you ensure output is valid for target platform

## When to Use

Use this skill when:
- Adding support for a new AI platform to Archon
- The user says "add adapter for X platform"
- Improving/fixing an existing platform adapter
- Understanding how adapters work

Keywords: `create-adapter`, `new-adapter`, `add-adapter`, `platform-adapter`

Do NOT use this skill when:
- Creating skills (use `add-skill`)
- Creating agents (use `add-agent`)
- Installing skills to platforms (use SDK install command)

## Workflow

Follow this checklist exactly:

### Step 1: Research Target Platform
1. **What format does the platform use?** (markdown, YAML, JSON, XML, etc.)
2. **Where do skills/agents live?** (directory, config file, database, etc.)
3. **What's the skill structure?** (sections, fields, metadata)
4. **Are there examples?** (look at existing platform skills)
5. **What's unique about this platform?** (special features, limitations)

### Step 2: Create Adapter File
```bash
cd adapters/

# Create adapter file (kebab-case platform name)
touch <platform-name>.py
```

### Step 3: Implement Adapter Class
```python
"""
Archon Adapter for <Platform Name>
Transforms Archon format to <Platform> format.
"""
from adapters.base import BaseAdapter
from pathlib import Path
from typing import Dict, Any
import yaml


class <Platform>Adapter(BaseAdapter):
    """Adapter for <Platform Name> AI platform."""
    
    def __init__(self):
        super().__init__(
            platform_id="<platform-id>",
            platform_name="<Platform Name>",
            default_target="<default-install-path>"  # e.g., "~/.platform/skills/"
        )
    
    def transform_skill(self, skill_md: str, manifest: Dict[str, Any]) -> str:
        """
        Transform SKILL.md and manifest.yaml to <Platform> format.
        
        Args:
            skill_md: Content of SKILL.md file
            manifest: Parsed manifest.yaml as dictionary
        
        Returns:
            Transformed skill content in <Platform> format
        """
        # Parse SKILL.md sections
        sections = self.parse_skill_sections(skill_md)
        
        # Extract manifest fields
        name = manifest['name']
        description = manifest['description']
        triggers = manifest.get('triggers', {})
        
        # Build platform-specific format
        output = self._build_<platform>_format(
            name=name,
            description=description,
            identity=sections.get('Identity', ''),
            workflow=sections.get('Workflow', ''),
            rules=sections.get('Rules', ''),
            triggers=triggers
        )
        
        return output
    
    def transform_bundle(self, bundle_manifest: Dict[str, Any], skills: list) -> Any:
        """
        Transform bundle manifest to <Platform> format.
        
        Args:
            bundle_manifest: Parsed bundle.yaml
            skills: List of transformed skill contents
        
        Returns:
            Bundle in <Platform> format (could be merged file, directory, etc.)
        """
        # Platform-specific bundle transformation
        pass
    
    def transform_agent(self, agent_manifest: Dict[str, Any]) -> str:
        """
        Transform agent definition to <Platform> format.
        
        Args:
            agent_manifest: Parsed agent.yaml
        
        Returns:
            Agent definition in <Platform> format
        """
        # Platform-specific agent transformation
        pass
    
    def get_install_path(self, target: str = None) -> Path:
        """
        Resolve installation path for this platform.
        
        Args:
            target: Optional custom target path
        
        Returns:
            Resolved absolute path
        """
        if target:
            return Path(target).expanduser().resolve()
        return Path(self.default_target).expanduser().resolve()
    
    def validate_output(self, content: str) -> tuple[bool, list[str]]:
        """
        Validate transformed content for <Platform>.
        
        Args:
            content: Transformed skill/agent/bundle content
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Platform-specific validation rules
        # Example: check required sections, format, syntax
        
        if not errors:
            return True, []
        return False, errors
    
    def _build_<platform>_format(self, **kwargs) -> str:
        """
        Internal helper to build platform-specific format.
        """
        # Template for platform format
        # Return formatted string
        pass
```

### Step 4: Study Existing Adapters
Look at existing adapters for patterns:

```bash
# See examples
cat adapters/claude-code.py
cat adapters/copilot-cli.py
cat adapters/cursor.py
```

**Common patterns**:
- **Claude Code**: Markdown-based, preserves SKILL.md mostly intact
- **Copilot CLI**: Similar to Claude, some metadata changes
- **Cursor**: Merged into `.cursor/rules` file
- **Windsurf**: Single `.windsurfrules` file with all skills
- **Antigravity**: YAML-based with richer metadata

### Step 5: Update base.py (If Needed)
If your adapter needs shared functionality:

```python
# In adapters/base.py, add helper methods
def parse_skill_sections(self, skill_md: str) -> Dict[str, str]:
    """Parse SKILL.md into dictionary of sections."""
    # Implementation
    pass
```

### Step 6: Register Adapter in archon.yaml
```yaml
platforms:
  - id: <platform-id>
    adapter: adapters/<platform-name>
    target: "<default-install-path>"
```

### Step 7: Create Adapter Tests
```bash
mkdir -p tests/adapters
touch tests/adapters/test_<platform>_adapter.py
```

```python
"""Tests for <Platform> adapter."""
import pytest
from adapters.<platform_name> import <Platform>Adapter
from pathlib import Path


def test_transform_skill():
    """Test skill transformation."""
    adapter = <Platform>Adapter()
    
    # Load test skill
    skill_md = Path("skills/_template/SKILL.md").read_text()
    manifest = yaml.safe_load(Path("skills/_template/manifest.yaml").read_text())
    
    # Transform
    output = adapter.transform_skill(skill_md, manifest)
    
    # Validate
    is_valid, errors = adapter.validate_output(output)
    assert is_valid, f"Validation errors: {errors}"
    
    # Check platform-specific requirements
    assert "<required-section>" in output
    # Add more assertions

def test_transform_bundle():
    """Test bundle transformation."""
    # Similar test for bundles
    pass

def test_validate_output():
    """Test validation logic."""
    adapter = <Platform>Adapter()
    
    # Test valid output
    valid_output = "..."  # Example valid platform format
    is_valid, errors = adapter.validate_output(valid_output)
    assert is_valid
    
    # Test invalid output
    invalid_output = "..."  # Example invalid format
    is_valid, errors = adapter.validate_output(invalid_output)
    assert not is_valid
    assert len(errors) > 0
```

### Step 8: Test Adapter
```bash
# Run adapter tests
pytest tests/adapters/test_<platform>_adapter.py

# Manual test: transform a real skill
python -c "
from adapters.<platform_name> import <Platform>Adapter
from pathlib import Path
import yaml

adapter = <Platform>Adapter()
skill_md = Path('skills/backend-development/SKILL.md').read_text()
manifest = yaml.safe_load(Path('skills/backend-development/manifest.yaml').read_text())

output = adapter.transform_skill(skill_md, manifest)
print(output)
"
```

### Step 9: Update SDK to Use Adapter
In `sdk/archon.py`, ensure adapter is imported:

```python
# SDK automatically discovers adapters from archon.yaml
# No code changes needed if adapter follows base class
```

### Step 10: Document Adapter
Create `adapters/<platform-name>.md`:

```markdown
# <Platform Name> Adapter

## Platform Overview
[Brief description of the platform]

## Format Mapping

| Archon | <Platform> |
|-----------|------------|
| SKILL.md | [platform equivalent] |
| manifest.yaml | [platform equivalent] |
| resources/ | [platform equivalent] |

## Transformation Rules
1. [Rule 1]
2. [Rule 2]
3. [Rule 3]

## Installation Path
Default: `<path>`

## Limitations
- [Limitation 1]
- [Limitation 2]

## Examples
[Before/after transformation examples]
```

### Step 11: Update Documentation
```bash
# Add to docs/adapters.md
# Add to README.md supported platforms list
```

### Step 12: Commit
```bash
git add adapters/<platform-name>.py
git add adapters/<platform-name>.md
git add tests/adapters/test_<platform>_adapter.py
git add archon.yaml
git commit -m "Add <Platform> adapter

- Transform skills to <platform> format
- Support bundles and agents
- Installation path: <path>
- Tests included"
```

## Rules

### DO:
- Inherit from BaseAdapter for consistency
- Implement all required abstract methods
- Validate transformed output
- Handle platform-specific quirks gracefully
- Write comprehensive tests
- Document format mapping clearly
- Preserve skill intent and structure
- Support bundles and agents, not just skills
- Use type hints for clarity
- Handle errors gracefully

### DON'T:
- Create adapters without testing on actual platform
- Lose information in transformation (preserve as much as possible)
- Hardcode paths (use Path and expanduser())
- Skip validation logic
- Forget to update archon.yaml
- Create duplicate adapters for same platform
- Ignore platform conventions
- Leave TODO comments in production code

## Output Format

The skill produces:
- **Primary output**: Platform adapter Python module with tests
- **Format**: Python class inheriting from BaseAdapter
- **Location**: `adapters/<platform-name>.py`

### Output Checklist
```markdown
✅ Created adapters/<platform-name>.py
✅ Implemented BaseAdapter subclass
✅ Implemented transform_skill()
✅ Implemented transform_bundle()
✅ Implemented transform_agent()
✅ Implemented validate_output()
✅ Created tests/adapters/test_<platform>_adapter.py
✅ Created adapters/<platform-name>.md documentation
✅ Registered in archon.yaml
✅ Tests pass
✅ Manual transformation test successful
✅ Git committed
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `adapters/base.py` | reference | Base adapter class to inherit from |
| `adapters/*.py` | example | Existing adapters as implementation examples |

## Handoff

When this skill completes:
- **Next action**: Adapter is ready to transform and install skills
- **Artifact produced**: Adapter module and tests
- **User instruction**: "Adapter for '<platform-name>' created. Install skills with: archon install --platform <platform-id>"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | N/A - this skill is for creating adapters, not using them |
| Copilot CLI | Same |
| Cursor | Same |
| Windsurf | Same |
| Antigravity | Same |
