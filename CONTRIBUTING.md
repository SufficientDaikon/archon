# Contributing to Archon

Thank you for your interest in contributing to Archon! This document provides guidelines and workflows for contributing.

## How to Contribute

### Adding a New Skill

1. **Use the skill factory** (recommended):

   ```
   "Create a new skill for [domain]" → triggers the skill-factory pipeline
   ```

2. **Manual creation**:
   - Copy `skills/_template/` to `skills/your-skill-name/`
   - Fill in `manifest.yaml` with your skill's metadata
   - Write your `SKILL.md` following the template structure
   - Add resources, examples, and tests
   - Run validation: `python scripts/validate.py skills/your-skill-name`

### Skill Quality Standards

Every skill MUST:

- [ ] Have a complete `manifest.yaml` passing schema validation
- [ ] Have a `SKILL.md` with all required sections (Identity, When to Use, Workflow, Rules, Output, Handoff)
- [ ] Declare at least one trigger keyword
- [ ] Have no conflicting triggers with existing skills
- [ ] Include at least one example interaction in `examples/`
- [ ] Include at least one test case in `tests/cases/`

Every skill SHOULD:

- [ ] Include resources (cheat sheets, references) in `resources/`
- [ ] Include output templates in `templates/`
- [ ] Support all 5 platforms (or document which are unsupported in overrides)

### Adding a Skill to a Bundle

1. Edit the bundle's `bundle.yaml`
2. Add your skill name to the `skills:` list
3. Update the meta-skill if the new skill changes routing logic
4. Run bundle validation: `python scripts/validate.py bundles/bundle-name`

### Creating a New Bundle

1. Create directory `bundles/your-bundle-kit/`
2. Create `bundle.yaml` following `schemas/bundle-manifest.schema.yaml`
3. Create `meta-skill/SKILL.md` and `meta-skill/manifest.yaml`
4. Optionally add `shared-resources/`
5. Register in `archon.yaml`

### Modifying an Agent

1. Edit the agent's `AGENT.md` and/or `agent-manifest.yaml`
2. Ensure all referenced skills still exist
3. Ensure all handoff targets are valid agents
4. Run validation: `python scripts/validate.py agents/agent-name`

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run full validation: `python scripts/validate.py --all`
5. Update `CHANGELOG.md` under `[Unreleased]`
6. Submit a PR with a clear description

## Naming Conventions

| Entity    | Convention         | Example                |
| --------- | ------------------ | ---------------------- |
| Skills    | `kebab-case`       | `react-best-practices` |
| Bundles   | `kebab-case-kit`   | `web-dev-kit`          |
| Agents    | `kebab-case-agent` | `spec-writer-agent`    |
| Pipelines | `kebab-case`       | `sdd-pipeline`         |
| Synapses  | `kebab-case`       | `sequential-thinking`  |
| Hooks     | `snake_case.py`    | `pre_step.py`          |

### Adding a Synapse

1. Copy `synapses/_template/` to `synapses/your-synapse/`
2. Write `SYNAPSE.md` defining firing phases, rules, and resources
3. Create `manifest.yaml` with `type: core` or `type: optional`
4. Add resource files as needed
5. Register in `archon.yaml` under `synapses:`
6. Validate: `python scripts/validate.py --synapses`

### Adding a Hook

1. Create `hooks/your_hook.py` with an `execute(context)` function
2. Register in `hooks/hooks.yaml` with the lifecycle event it handles
3. Validate: `python scripts/validate.py --hooks`

### Validation Commands

```bash
python scripts/validate.py --all          # Validate everything
python scripts/validate.py --skills       # Skills only
python scripts/validate.py --agents       # Agents + guardrails
python scripts/validate.py --synapses     # Synapses
python scripts/validate.py --hooks        # Hook system
python scripts/validate.py --pipelines    # Pipeline schemas
```

## Code of Conduct

Be respectful, constructive, and collaborative. We're building something amazing together.
