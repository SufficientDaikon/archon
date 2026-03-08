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

## Complexity Router

**Q: What is the complexity router?**
A: An automatic pre-step that classifies every request by complexity (trivial → simple → moderate → complex → expert), selects the optimal model tier, and routes to the right skill/agent/pipeline. It has P0 priority and runs before everything else.

**Q: Can I bypass the complexity router?**
A: Yes. Set `OMNISKILL_BYPASS_ROUTER=true` in your environment or use direct skill/agent invocation.

**Q: How does the router classify complexity?**
A: It analyzes task scope, dependencies, required domain expertise, output complexity, and time constraints. See `skills/complexity-router/resources/complexity-signals.md`.

**Q: What model tiers exist?**
A: Fast/cheap (for trivial/simple tasks), Standard (for moderate tasks), and Premium (for complex/expert tasks).

## Knowledge Sources

**Q: What are knowledge sources?**
A: External knowledge repositories (GitHub repos, local directories, URLs, APIs) that skills can reference. They use file-based search — no vector databases or embeddings required.

**Q: How do I add a knowledge source?**
A: Edit `templates/source-config.yaml` and run `python scripts/admin.py --sync`.

**Q: What file types are supported?**
A: Markdown (.md), YAML (.yaml), JSON (.json), and plain text (.txt). Other file types are ignored during content normalization.

**Q: How often are sources synced?**
A: By default, sources are synced daily. Run `python scripts/admin.py --sync` to trigger a manual sync.

## Self-Customization Skills

**Q: What are self-customization skills?**
A: AI-guided skills that help you extend OMNISKILL: `add-skill`, `add-bundle`, `add-agent`, `add-adapter`, and `rename-project`. Tell your AI assistant to "Follow the [skill-name] skill to..." and it will guide you through the process.

**Q: Do I still need to follow the manual creation process?**
A: No. The self-customization skills automate validation, template generation, and installation. But you can still create things manually if you prefer.

**Q: Can I customize the self-customization skills themselves?**
A: Yes. They're regular skills in `skills/add-*` and can be edited or extended.

## Prompt Library

**Q: What's in the prompt library?**
A: Reusable prompt components: router prompts, system prompts, shared formatting rules, and persona templates. Located in `prompts/`.

**Q: Can I customize prompts?**
A: Yes. Edit files in `prompts/` to change how OMNISKILL interacts with AI models.

**Q: Are prompts platform-specific?**
A: No. Prompts are universal. Platform adapters handle any platform-specific formatting.

## SDK

**Q: What is the OMNISKILL SDK?**
A: A Python library (`sdk/omniskill.py`) providing programmatic access to OMNISKILL functionality: list skills, route requests, install bundles, validate, sync sources, health checks.

**Q: When should I use the SDK vs. CLI scripts?**
A: Use the SDK when integrating OMNISKILL into other Python tools or automation. Use CLI scripts for manual operations.

**Q: Can I use the SDK from other languages?**
A: Not directly, but you can call it via subprocess or create language bindings.

## Admin Dashboard

**Q: What is the admin dashboard?**
A: A CLI tool (`scripts/admin.py`) for operational tasks: viewing stats, checking errors, managing knowledge sources, generating health reports.

**Q: How do I see what skills are installed?**
A: Run `python scripts/admin.py --stats`.

**Q: How do I check for validation errors?**
A: Run `python scripts/admin.py --errors`.

## Contributing

**Q: How do I contribute a new skill?**
A: See [CONTRIBUTING.md](../CONTRIBUTING.md). Fork, create your skill, validate, and submit a PR.
