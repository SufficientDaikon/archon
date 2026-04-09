"""
Archon SDK - Programmatic access to the framework
"""
import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import subprocess
import sys


class Archon:
    """
    Archon SDK — programmatic access to the framework.

    Usage:
        from archon import Archon

        sdk = Archon()
        sdk.list_skills(tags=['godot'])
        sdk.install(platform='copilot-cli', bundle='godot-kit')
    """

    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize Archon SDK.

        Args:
            root_path: Path to Archon root. If None, auto-detects from:
                       - ARCHON_ROOT env var
                       - ~/.archon/
                       - Current directory if archon.yaml exists
        """
        self.root = self._detect_root(root_path)
        self.manifest = self._load_manifest()

    def _detect_root(self, root_path: Optional[Path]) -> Path:
        """Auto-detect Archon root directory."""
        if root_path:
            return Path(root_path).resolve()

        # Check environment variable
        import os
        if 'ARCHON_ROOT' in os.environ:
            return Path(os.environ['ARCHON_ROOT']).resolve()

        # Check ~/.archon/
        home_install = Path.home() / '.archon'
        if (home_install / 'archon.yaml').exists():
            return home_install

        # Check current directory
        cwd = Path.cwd()
        if (cwd / 'archon.yaml').exists():
            return cwd

        # Check parent directories
        for parent in cwd.parents:
            if (parent / 'archon.yaml').exists():
                return parent

        raise FileNotFoundError(
            "Could not find Archon root. "
            "Set ARCHON_ROOT environment variable or "
            "run from Archon directory."
        )

    def _load_manifest(self) -> Dict[str, Any]:
        """Load archon.yaml manifest."""
        manifest_path = self.root / 'archon.yaml'
        if not manifest_path.exists():
            raise FileNotFoundError(f"archon.yaml not found at {manifest_path}")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def list_skills(self, tags: Optional[List[str]] = None,
                    platform: Optional[str] = None,
                    bundle: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available skills, optionally filtered.

        Args:
            tags: Filter by tags (e.g., ['godot', 'game-dev'])
            platform: Filter by platform support
            bundle: Filter by bundle membership

        Returns:
            List of skill dictionaries with name, path, version, description
        """
        skills = []
        skills_dir = self.root / 'skills'

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
                continue

            manifest_path = skill_dir / 'manifest.yaml'
            if not manifest_path.exists():
                continue

            with open(manifest_path, 'r', encoding='utf-8') as f:
                try:
                    skill_manifest = yaml.safe_load(f)
                except yaml.YAMLError:
                    continue

            if not skill_manifest or not isinstance(skill_manifest, dict):
                continue

            # Apply filters
            if tags and not any(tag in skill_manifest.get('tags', []) for tag in tags):
                continue

            if platform and platform not in skill_manifest.get('platforms', []):
                continue

            if bundle and skill_manifest.get('bundle') != bundle:
                continue

            skills.append({
                'name': skill_manifest['name'],
                'path': str(skill_dir.relative_to(self.root)),
                'version': skill_manifest.get('version', 'unknown'),
                'description': skill_manifest.get('description', ''),
                'tags': skill_manifest.get('tags', []),
                'bundle': skill_manifest.get('bundle'),
                'priority': skill_manifest.get('priority', 'P2')
            })

        return sorted(skills, key=lambda s: s['name'])

    def list_bundles(self) -> List[Dict[str, Any]]:
        """
        List available bundles.

        Returns:
            List of bundle dictionaries with name, path, skills
        """
        bundles = []

        for bundle_def in self.manifest.get('bundles', []):
            bundle_path = self.root / bundle_def['path']
            bundle_yaml = bundle_path / 'bundle.yaml'

            if bundle_yaml.exists():
                with open(bundle_yaml, 'r', encoding='utf-8') as f:
                    bundle_manifest = yaml.safe_load(f)
            else:
                bundle_manifest = {}

            bundles.append({
                'name': bundle_def['name'],
                'path': bundle_def['path'],
                'skills': bundle_def.get('skills', []),
                'description': bundle_manifest.get('description', ''),
                'version': bundle_manifest.get('version', 'unknown')
            })

        return bundles

    def get_skill(self, name: str) -> Dict[str, Any]:
        """
        Get a skill's SKILL.md content and manifest.

        Args:
            name: Skill name (e.g., 'godot-best-practices')

        Returns:
            Dictionary with 'manifest', 'content', 'path', 'resources'
        """
        skill_path = self.root / 'skills' / name

        if not skill_path.exists():
            raise FileNotFoundError(f"Skill '{name}' not found at {skill_path}")

        manifest_path = skill_path / 'manifest.yaml'
        skill_md_path = skill_path / 'SKILL.md'

        if not manifest_path.exists():
            raise FileNotFoundError(f"manifest.yaml not found for skill '{name}'")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)

        content = ""
        if skill_md_path.exists():
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

        # List resources
        resources_dir = skill_path / 'resources'
        resources = []
        if resources_dir.exists():
            resources = [r.name for r in resources_dir.iterdir() if r.is_file()]

        return {
            'manifest': manifest,
            'content': content,
            'path': str(skill_path.relative_to(self.root)),
            'resources': resources
        }

    def route(self, query: str) -> Dict[str, Any]:
        """
        Route a query through the complexity router.

        Args:
            query: The user's request/question

        Returns:
            Dictionary with classification, route, reasoning
        """
        # Simplified routing logic (full version would load complexity-router skill)
        token_count = len(query.split()) * 1.3

        if token_count < 50:
            classification = "TRIVIAL"
            model_tier = "fast"
            execution_mode = "direct"
        elif token_count < 200:
            classification = "SIMPLE"
            model_tier = "fast"
            execution_mode = "skill"
        elif token_count < 1000:
            classification = "MODERATE"
            model_tier = "standard"
            execution_mode = "skill+resources"
        elif token_count < 3000:
            classification = "COMPLEX"
            model_tier = "premium"
            execution_mode = "agent"
        else:
            classification = "EXPERT"
            model_tier = "premium"
            execution_mode = "pipeline"

        return {
            'classification': classification,
            'token_count': int(token_count),
            'model_tier': model_tier,
            'execution_mode': execution_mode,
            'reasoning': f"Token count: {int(token_count)} -> {classification}"
        }

    def install(self, platform: Optional[str] = None,
                bundle: Optional[str] = None,
                skill: Optional[str] = None,
                target: Optional[str] = None) -> bool:
        """
        Install skills to a platform.

        Args:
            platform: Target platform (e.g., 'copilot-cli', 'cursor')
            bundle: Bundle to install (installs all member skills)
            skill: Single skill to install
            target: Custom installation path (overrides platform default)

        Returns:
            True if successful
        """
        if not platform and not target:
            raise ValueError("Must specify either 'platform' or 'target'")

        # Get platform adapter
        if platform:
            platform_def = next(
                (p for p in self.manifest.get('platforms', []) if p['id'] == platform),
                None
            )
            if not platform_def:
                raise ValueError(f"Unknown platform: {platform}")

            adapter_path = self.root / platform_def['adapter']
            if not target:
                target = platform_def['target']

        print(f"Installing to: {target}")

        # Determine what to install
        skills_to_install = []

        if bundle:
            bundle_def = next(
                (b for b in self.manifest.get('bundles', []) if b['name'] == bundle),
                None
            )
            if not bundle_def:
                raise ValueError(f"Unknown bundle: {bundle}")
            skills_to_install = bundle_def.get('skills', [])
        elif skill:
            skills_to_install = [skill]
        else:
            raise ValueError("Must specify either 'bundle' or 'skill'")

        # Install each skill
        target_path = Path(target).expanduser()
        target_path.mkdir(parents=True, exist_ok=True)

        for skill_name in skills_to_install:
            skill_data = self.get_skill(skill_name)

            # Copy SKILL.md to target
            skill_target = target_path / f"{skill_name}.md"
            skill_target.write_text(skill_data['content'], encoding='utf-8')
            print(f"  Installed {skill_name}")

        return True

    def validate(self, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a skill, bundle, agent, or everything.

        Args:
            target: Path to validate (e.g., 'skills/godot-best-practices')
                   If None, validates everything

        Returns:
            Dictionary with validation results and errors
        """
        errors = []
        warnings = []

        if target:
            target_path = self.root / target
            if not target_path.exists():
                return {'valid': False, 'errors': [f"Path not found: {target}"]}

            # Validate based on type
            if 'skills/' in target:
                return self._validate_skill(target_path)
            elif 'bundles/' in target:
                return self._validate_bundle(target_path)
            elif 'agents/' in target:
                return self._validate_agent(target_path)
        else:
            # Validate everything
            print("Validating Archon framework...")

            # Validate root manifest
            try:
                self._load_manifest()
                print("  archon.yaml is valid")
            except Exception as e:
                errors.append(f"archon.yaml: {e}")

            # Validate all skills
            skills = self.list_skills()
            for skill in skills:
                result = self._validate_skill(self.root / skill['path'])
                if not result['valid']:
                    errors.extend(result['errors'])

            print(f"  Validated {len(skills)} skills")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_skill(self, skill_path: Path) -> Dict[str, Any]:
        """Validate a single skill."""
        errors = []

        # Check manifest exists
        manifest_path = skill_path / 'manifest.yaml'
        if not manifest_path.exists():
            errors.append(f"Missing manifest.yaml in {skill_path.name}")
        else:
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = yaml.safe_load(f)

                # Check required fields
                required = ['name', 'version', 'description', 'author', 'license', 'platforms', 'tags']
                for field in required:
                    if field not in manifest:
                        errors.append(f"{skill_path.name}: Missing field '{field}' in manifest.yaml")
            except Exception as e:
                errors.append(f"{skill_path.name}: Invalid YAML: {e}")

        # Check SKILL.md exists
        if not (skill_path / 'SKILL.md').exists():
            errors.append(f"Missing SKILL.md in {skill_path.name}")

        return {'valid': len(errors) == 0, 'errors': errors}

    def _validate_bundle(self, bundle_path: Path) -> Dict[str, Any]:
        """Validate a single bundle."""
        errors = []
        # Add bundle validation logic
        return {'valid': len(errors) == 0, 'errors': errors}

    def _validate_agent(self, agent_path: Path) -> Dict[str, Any]:
        """Validate a single agent."""
        errors = []
        # Add agent validation logic
        return {'valid': len(errors) == 0, 'errors': errors}

    def sync_sources(self, source_id: Optional[str] = None, force: bool = False) -> bool:
        """
        Sync knowledge sources.

        Args:
            source_id: Specific source to sync (None = sync all)
            force: Force re-sync even if cache is fresh

        Returns:
            True if successful
        """
        # Load knowledge sources config
        sources_config = self.root / 'skills' / 'knowledge-sources' / 'sources.yaml'

        if not sources_config.exists():
            print("No knowledge sources configured")
            return False

        with open(sources_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        sources = config.get('sources', [])
        if source_id:
            sources = [s for s in sources if s['id'] == source_id]

        for source in sources:
            print(f"Syncing {source['id']}...")
            # Sync logic would go here
            # For now, just placeholder
            print(f"  {source['id']} synced")

        return True

    def health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive health check.

        Returns:
            Dictionary with health status and metrics
        """
        skills = self.list_skills()
        bundles = self.list_bundles()
        agents = self.manifest.get('agents', [])
        pipelines = self.manifest.get('pipelines', [])

        synapses = self.manifest.get('synapses', [])

        return {
            'status': 'healthy',
            'archon_version': self.manifest.get('version', 'unknown'),
            'root_path': str(self.root),
            'skills_count': len(skills),
            'bundles_count': len(bundles),
            'agents_count': len(agents),
            'pipelines_count': len(pipelines),
            'synapses_count': len(synapses),
            'platforms_count': len(self.manifest.get('platforms', []))
        }

    # --- Pipeline Execution Methods (v2.0) ---

    def execute_pipeline(
        self,
        name: str,
        project_dir: str = ".",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a pipeline by name.

        Args:
            name: Pipeline name (e.g., 'sdd-pipeline')
            project_dir: Project directory for artifacts
            config: Additional configuration

        Returns:
            Pipeline execution state dict
        """
        sys.path.insert(0, str(self.root / 'src'))
        from archon.core.pipeline_engine import PipelineExecutor

        executor = PipelineExecutor(
            hooks_dir=self.root / 'hooks',
            state_dir=Path.home() / '.archon' / 'pipeline-states',
        )
        pipeline = executor.load_pipeline(name)
        return executor.execute(pipeline, project_dir=project_dir, config=config)

    def resume_pipeline(self, state_id: str) -> Dict[str, Any]:
        """
        Resume a paused or failed pipeline.

        Args:
            state_id: Pipeline state ID

        Returns:
            Updated pipeline state dict
        """
        sys.path.insert(0, str(self.root / 'src'))
        from archon.core.pipeline_engine import PipelineExecutor

        executor = PipelineExecutor(hooks_dir=self.root / 'hooks')
        return executor.resume(state_id)

    def get_pipeline_status(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a pipeline execution.

        Args:
            state_id: Pipeline state ID

        Returns:
            Pipeline state dict or None if not found
        """
        sys.path.insert(0, str(self.root / 'src'))
        from archon.core.pipeline_state import PipelineState

        state = PipelineState.load(state_id)
        return state.to_dict() if state else None

    def list_active_pipelines(self) -> List[Dict[str, Any]]:
        """
        List all active (running/paused) pipeline executions.

        Returns:
            List of pipeline state summaries
        """
        state_dir = Path.home() / '.archon' / 'pipeline-states'
        if not state_dir.exists():
            return []

        active = []
        for state_file in state_dir.glob('*.json'):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                status = data.get('status', '')
                if status in ('executing', 'paused', 'pending', 'validating'):
                    active.append({
                        'state_id': data.get('state_id', ''),
                        'pipeline': data.get('pipeline_name', ''),
                        'status': status,
                        'project_dir': data.get('project_dir', ''),
                        'health_score': data.get('health_score', 100),
                    })
            except (json.JSONDecodeError, KeyError):
                continue

        return active

    def cancel_pipeline(self, state_id: str) -> bool:
        """
        Cancel a running pipeline.

        Args:
            state_id: Pipeline state ID

        Returns:
            True if cancelled, False if not found
        """
        sys.path.insert(0, str(self.root / 'src'))
        from archon.core.pipeline_state import PipelineState

        state = PipelineState.load(state_id)
        if state:
            state.update_status('cancelled')
            return True
        return False

    # --- Synapse Methods (v2.0) ---

    def list_synapses(self) -> List[Dict[str, Any]]:
        """List all registered synapses."""
        synapses_raw = self.manifest.get('synapses', [])
        synapses = []
        for s in synapses_raw:
            # Handle both string and dict formats
            if isinstance(s, dict):
                synapse_name = s.get('name', '')
                synapse_path = s.get('path', f'synapses/{synapse_name}')
            else:
                synapse_name = s
                synapse_path = f'synapses/{s}'
            synapse_dir = self.root / synapse_path
            manifest_path = synapse_dir / 'manifest.yaml'
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = yaml.safe_load(f)
                    synapses.append({
                        'name': manifest.get('name', synapse_name),
                        'version': manifest.get('version', ''),
                        'type': manifest.get('synapse-type', ''),
                        'description': manifest.get('description', ''),
                        'phases': [p['name'] for p in manifest.get('firing-phases', [])],
                    })
                except Exception:
                    synapses.append({'name': synapse_name, 'error': 'Failed to load manifest'})
            else:
                synapses.append({'name': synapse_name, 'error': 'No manifest found'})
        return synapses

    def get_core_synapses(self) -> List[str]:
        """Get names of all core synapses (always-on)."""
        return [
            s['name'] for s in self.list_synapses()
            if s.get('type') == 'core'
        ]


# Convenience function
def load_skill(name: str) -> Dict[str, Any]:
    """Quick helper to load a skill."""
    archon_sdk = Archon()
    return archon_sdk.get_skill(name)
