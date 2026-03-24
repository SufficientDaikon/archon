# FAQ

## General

**Q: What platforms does Archon support?**
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
A: Yes. Set `Archon_BYPASS_ROUTER=true` in your environment or use direct skill/agent invocation.

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
A: AI-guided skills that help you extend Archon: `add-skill`, `add-bundle`, `add-agent`, `add-adapter`, and `rename-project`. Tell your AI assistant to "Follow the [skill-name] skill to..." and it will guide you through the process.

**Q: Do I still need to follow the manual creation process?**
A: No. The self-customization skills automate validation, template generation, and installation. But you can still create things manually if you prefer.

**Q: Can I customize the self-customization skills themselves?**
A: Yes. They're regular skills in `skills/add-*` and can be edited or extended.

## Prompt Library

**Q: What's in the prompt library?**
A: Reusable prompt components: router prompts, system prompts, shared formatting rules, and persona templates. Located in `prompts/`.

**Q: Can I customize prompts?**
A: Yes. Edit files in `prompts/` to change how Archon interacts with AI models.

**Q: Are prompts platform-specific?**
A: No. Prompts are universal. Platform adapters handle any platform-specific formatting.

## SDK

**Q: What is the Archon SDK?**
A: A Python library (`sdk/archon.py`) providing programmatic access to Archon functionality: list skills, route requests, install bundles, validate, sync sources, health checks.

**Q: When should I use the SDK vs. CLI scripts?**
A: Use the SDK when integrating Archon into other Python tools or automation. Use CLI scripts for manual operations.

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

## Guardrails Engine (v2.0)

**Q: What are guardrails?**
A: Guardrails are structured rules attached to every agent that define what an agent must and must-not do. In v2.0, guardrails are enforced at runtime via the hook system, not just documented.

**Q: What's the guardrail format?**
A: Each guardrail has three fields: `rule` (the constraint), `severity` (critical/major/minor), and `on-violation` (halt/warn/log). See [Guardrails Guide](guardrails.md).

**Q: What is the anti-rationalization synapse?**
A: A core synapse that prevents agents from making excuses to skip steps. It includes 10 Iron Laws, forbidden phrases, and rationalization detection tables. It fires automatically for every agent.

**Q: Can I disable guardrails for testing?**
A: Set `Archon_GUARDRAILS=disabled` in your environment. Not recommended for production use.

## Synapses (v2.0)

**Q: What are synapses?**
A: Synapses are cognitive capabilities that shape HOW agents think, not WHAT they do. Unlike skills (which are domain methodologies), synapses affect the reasoning process itself. They are cross-cutting cognitive enhancements that layer structured thinking (planning, monitoring, reflection) on top of any agent task.

**Q: What's the difference between core and optional synapses?**
A: Core synapses fire automatically for every agent. Cross-cutting synapses fire for specific task types (e.g., security-awareness fires for code-related tasks). Optional synapses require explicit binding in the agent manifest.

**Q: What types of synapses exist?**
A: There are three types: **core** (always fire for every agent — metacognition, anti-rationalization, sequential-thinking), **cross-cutting** (fire for specific task types — security-awareness, pattern-recognition), and **optional** (fire only when bound to an agent — risk-assessment, custom synapses).

**Q: What core synapses exist?**
A: Three: **metacognition** (plan → monitor → reflect), **anti-rationalization** (detect → challenge → enforce), and **sequential-thinking** (decompose → reason → validate → synthesize).

**Q: How do I create a custom synapse?**
A: See [Creating Synapses](creating-synapses.md). Copy `synapses/_template/` and define your SYNAPSE.md and manifest.yaml. Choose a synapse-type (core, cross-cutting, or optional) based on how broadly the synapse should fire.

## Hook System (v2.0)

**Q: What are hooks?**
A: Python lifecycle hooks that execute at specific points during pipeline execution: session start, before/after each step, on failure, and on deviation.

**Q: Where are hooks defined?**
A: In `hooks/hooks.yaml` (configuration) and individual `.py` files in `hooks/` (handlers). Each hook has an `execute(context)` function.

**Q: Can I add custom hooks?**
A: Yes. Create a new `.py` file in `hooks/`, register it in `hooks.yaml`, and specify which lifecycle event triggers it.

## Pipeline Engine (v2.0)

**Q: How is the v2.0 pipeline engine different from v0.x?**
A: In v0.x, pipelines were just YAML specs — documentation of what should happen. In v2.0, `PipelineExecutor` actually runs the pipeline with state management, artifact validation, failure recovery, and context curation between steps.

**Q: How do I run a pipeline?**
A: Via CLI: `archon pipeline run sdd-pipeline --project ./myapp`. Or via SDK: `os.execute_pipeline("sdd-pipeline", project_name="myapp")`.

**Q: What happens to pipeline state if execution stops?**
A: State is persisted as JSON to `~/.copilot/.archon/pipeline-states/`. Use `archon pipeline resume <state-id>` to continue from where it stopped.

**Q: What is context curation?**
A: Between pipeline steps, the context-curator agent creates focused summaries of the previous step's output, filtering to only what the next agent needs. This prevents context pollution across steps.

## HTML Documentation (v2.0)

**Q: How do I build the HTML docs?**
A: Run `python scripts/build_docs.py`. This converts all Markdown files in `docs/` to styled HTML in `docs/html/` with automatic Mermaid diagram rendering.

**Q: Can I preview the docs locally?**
A: Yes. Run `python -m http.server 8000` from the `docs/html/` directory and visit `http://localhost:8000`.
