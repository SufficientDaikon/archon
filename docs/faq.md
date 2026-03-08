# FAQ

## General

**Q: What platforms does OMNISKILL support?**
A: Claude Code, GitHub Copilot CLI, Cursor, Windsurf, and Antigravity.

**Q: Can I use just one bundle instead of everything?**
A: Yes. `python scripts/install.py --bundle web-dev-kit` installs only that bundle.

**Q: Do I need all 5 platforms installed?**
A: No. You need at least one. The installer auto-detects what you have.

## Skills

**Q: How do I create a new skill?**
A: Use the skill factory: tell your AI assistant "create a new skill for [domain]". Or copy `skills/_template/` manually.

**Q: My skill's triggers conflict with another skill. What do I do?**
A: Either make your triggers more specific, or put both skills in a bundle with conflict-resolution rules in the bundle.yaml.

**Q: Can a skill inherit from another skill?**
A: Yes. Set `extends: parent-skill-name` in your manifest.yaml.

## Bundles

**Q: What's the difference between a bundle and just installing multiple skills?**
A: Bundles include a meta-skill that resolves conflicts and routes between constituent skills. They also support atomic install/update/uninstall.

## Pipelines

**Q: Can I create custom pipelines?**
A: Yes. Create a YAML file in `pipelines/` following the pipeline schema.

**Q: What happens if a pipeline step fails?**
A: Depends on the step's `on-failure` setting: halt (stop), loop (retry from earlier step), skip, or retry.

## Contributing

**Q: How do I contribute a new skill?**
A: See [CONTRIBUTING.md](../CONTRIBUTING.md). Fork, create your skill, validate, and submit a PR.
