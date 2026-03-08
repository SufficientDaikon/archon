# Bundles

Domain kits that install related skills as a single unit.

| Bundle                          | Skills | Description                    |
| ------------------------------- | ------ | ------------------------------ |
| [godot-kit](godot-kit/)         | 5      | Godot 4 / GDScript development |
| [web-dev-kit](web-dev-kit/)     | 5      | Frontend, React, backend       |
| [ux-design-kit](ux-design-kit/) | 7      | Full UX lifecycle              |
| [django-kit](django-kit/)       | 4      | Django framework & APIs        |
| [sdd-kit](sdd-kit/)             | 5      | Spec-Driven Development        |
| [testing-kit](testing-kit/)     | 4      | Testing & debugging            |
| [mobile-kit](mobile-kit/)       | 2      | Mobile development             |
| [meta-kit](meta-kit/)           | 5      | Skill creation & tooling       |

## How Bundles Work

Each bundle contains:

- `bundle.yaml` — manifest listing skills, meta-skill, and conflict resolution
- `meta-skill/` — a composition skill that routes between constituent skills
- `shared-resources/` — resources available to all skills in the bundle
