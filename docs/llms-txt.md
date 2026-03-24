# llms.txt

## What is llms.txt?

[llms.txt](https://llmstxt.org/) is an emerging convention that provides a machine-readable index of a project's documentation. It lets Large Language Models (and any tool that works with them) instantly understand a project's purpose, structure, and capabilities — without crawling dozens of files.

Archon generates **two** files:

| File | Purpose | Size |
|------|---------|------|
| `llms.txt` | Concise index — skill names, agent roles, pipeline chains, bundle contents | ~10–15 KB |
| `llms-full.txt` | Complete dump — every SKILL.md, AGENT.md, SYNAPSE.md, pipeline YAML, bundle YAML, and docs page | ~500 KB – 3 MB |

## What Archon's llms.txt Contains

### Concise Index (`llms.txt`)

- **Header** — framework name, version, repository URL, docs URL, license
- **Skills** — all 83 skills with one-line descriptions (from `manifest.yaml` or `SKILL.md`)
- **Agents** — all 10 agents with roles and descriptions
- **Synapses** — cognitive enhancement modules with type and description
- **Pipelines** — multi-agent workflows with trigger phrases and step chains
- **Bundles** — domain kits with descriptions and skill lists
- **Documentation** — links to all docs pages
- **Installation** — quick-start instructions
- **Links** — repository, docs site, link to `llms-full.txt`

### Full Dump (`llms-full.txt`)

Contains the **complete text content** of every component file in the framework:

- `README.md` (verbatim)
- `archon.yaml` (the registry)
- Every `SKILL.md` for all registered skills
- Every `AGENT.md` for all registered agents
- Every `SYNAPSE.md` for all registered synapses
- Every pipeline YAML file
- Every `bundle.yaml` file
- Every documentation `.md` page

Each section is preceded by a separator (`---`), an H2 heading, and a `> Source:` line showing the file path.

## How to Generate

### CLI Command (recommended)

```bash
# Generate both files (default)
archon generate llms-txt

# Generate only the concise index
archon generate llms-txt --concise

# Generate only the full dump
archon generate llms-txt --full

# Write to a custom directory
archon generate llms-txt --output ./dist/

# JSON output (for scripting)
archon --json generate llms-txt

# Verbose output (shows each component being processed)
archon --verbose generate llms-txt
```

### Standalone Script

Works without the `archon` package installed — only requires Python 3.10+ and PyYAML:

```bash
# Generate both files
python scripts/generate-llms-txt.py

# Concise only
python scripts/generate-llms-txt.py --concise

# Full only
python scripts/generate-llms-txt.py --full

# Custom output directory
python scripts/generate-llms-txt.py --output ./dist/
```

## Where It's Deployed

When you push to the `master` branch, GitHub Actions automatically:

1. Sets up Python 3.12
2. Installs PyYAML
3. Runs `python scripts/generate-llms-txt.py`
4. Deploys both files to the docs site

After deployment, the files are available at:

- `https://sufficientdaikon.github.io/archon/llms.txt`
- `https://sufficientdaikon.github.io/archon/llms-full.txt`

## Validation

You can check whether your local `llms.txt` files are up to date:

```bash
# Via CLI
archon validate --check-llms-txt

# Via standalone script
python scripts/validate.py --check-llms-txt
```

The validator regenerates the files in memory and compares them to the on-disk versions. It reports:

- ✓ **Up to date** — files match
- ⚠ **Stale** — files differ from what would be generated now
- ⚠ **Not found** — files don't exist yet

The staleness check is **warning-only** — it never causes validation failures (exit code 2).
