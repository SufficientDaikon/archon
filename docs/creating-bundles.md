# Creating Bundles

## What's a Bundle?

A bundle is a **domain kit** — a collection of related skills packaged together with a **meta-skill** that orchestrates them. Bundles solve the problem of overlapping skills by defining clear routing and priority.

## Bundle Structure

```
bundles/my-kit/
├── bundle.yaml            # Bundle manifest
├── meta-skill/            # Composition skill
│   ├── SKILL.md           # How to route between constituent skills
│   └── manifest.yaml      # Meta-skill metadata
└── shared-resources/      # Resources available to all skills in the bundle
```

## Creating a Bundle

### Step 1: Define bundle.yaml

```yaml
name: my-domain-kit
version: 1.0.0
description: "Complete toolkit for [domain]"
author: your-name

skills:
  - skill-a
  - skill-b
  - skill-c

meta-skill: my-domain-expert

dependencies: []

conflict-resolution:
  - when: "skill-a AND skill-b both match"
    prefer: skill-a
    reason: "skill-a is more specific for this case"
```

### Step 2: Create the Meta-Skill

The meta-skill is the orchestrator. Its SKILL.md defines how to route between constituent skills:

```markdown
# My Domain Expert

You are a **meta-skill** that composes and routes between these skills:

- **skill-a**: Use for [situation]
- **skill-b**: Use for [situation]
- **skill-c**: Use for [situation]

## Routing Rules

1. If the request is about X → invoke skill-a
2. If the request is about Y → invoke skill-b
3. For everything else → invoke skill-c
```

### Step 3: Add Shared Resources

Resources in `shared-resources/` are available to all skills in the bundle:

```
shared-resources/
├── domain-reference.md
├── common-patterns.md
└── style-guide.md
```

### Step 4: Validate

```bash
python scripts/validate.py bundles/my-domain-kit
```

## Self-Customization

Instead of manually creating bundles, use the AI-guided approach:

> "Follow the add-bundle skill to create a bundle for [domain]"

The `add-bundle` skill guides you through:
1. Identifying constituent skills
2. Creating the bundle structure
3. Writing the meta-skill
4. Defining conflict resolution rules
5. Validation and installation

## Existing Bundles

See the [bundles directory](../bundles/) for all available bundles.

The **meta-kit** bundle includes the self-customization skills (`add-skill`, `add-bundle`, `add-agent`, `add-adapter`, `rename-project`) for extending OMNISKILL.
