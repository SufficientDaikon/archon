# Prompt Library

Categorized prompt templates for common workflows.

## Categories

| Category                 | Description              |
| ------------------------ | ------------------------ |
| [web-dev/](web-dev/)     | Web development prompts  |
| [game-dev/](game-dev/)   | Game development prompts |
| [ux-design/](ux-design/) | UX/UI design prompts     |
| [general/](general/)     | General-purpose prompts  |

## Using Prompts

Prompt templates use `{{variable}}` placeholders:

```
Build a {{component_type}} for {{project_name}} that {{description}}
```

Variables are filled from your input or you're prompted for missing values.

## Adding Custom Prompts

Create a markdown file in the appropriate category directory:

```markdown
# Prompt Name

> Brief description

## Template

{{your prompt template with variables}}

## Variables

- `variable_name`: Description of what this variable is

## Triggers Pipeline

sdd-pipeline (optional — if this prompt should trigger a pipeline)
```
