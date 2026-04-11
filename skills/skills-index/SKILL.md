---
name: skills-index
description: Master index of all installed agent skills. Consult this to know which skills are available and when to use them. AI agents should read the corresponding SKILL.md before working in a skill's domain.
---

# Installed Skills Index

This file is the master index of all skills installed globally for Claude Code and other AI agents. When a task falls within a skill's domain, load the full SKILL.md from the listed path before proceeding.

---

## 🎮 Godot / GDScript

| Skill | Description | Path |
|-------|-------------|------|
| `godot-best-practices` | Godot 4.x GDScript best practices: scene organization, signals, resources, state machines, performance, autoload, type hints. Use when generating GDScript, creating scenes, designing game architecture, or implementing state machines/save systems. | `~/.claude/skills/godot-best-practices/SKILL.md` |
| `godot-gdscript-mastery` | Expert GDScript: static typing, signal-up-call-down architecture, `%NodeName` unique nodes, `@onready`, `class_name`, and performance patterns. Use for code review, refactoring, or establishing project standards. | `~/.claude/skills/godot-gdscript-mastery/SKILL.md` |
| `godot-gdscript-patterns` | Godot 4 GDScript patterns: signals, scenes, state machines, optimization. Use when building Godot games or implementing game systems. | `~/.claude/skills/godot-gdscript-patterns/SKILL.md` |
| `godot-particles` | GPU particle systems (explosions, magic, weather, trails) using `GPUParticles2D/3D`, `ParticleProcessMaterial`, gradients, sub-emitters, custom shaders. Use when creating VFX or visual feedback. | `~/.claude/skills/godot-particles/SKILL.md` |
| `omega-gdscript-expert` | Meta Godot skill that composes all GDScript skills, enforces MCP routing, and requires self-evaluation loops for stable, backward-compatible implementations. | `~/.claude/skills/omega-gdscript-expert/SKILL.md` |

---

## 🐍 Django

| Skill | Description | Path |
|-------|-------------|------|
| `django-expert` | Expert-level Django: ORM, admin, authentication, full project patterns. Broadest Django coverage. | `~/.claude/skills/django-expert/SKILL.md` |
| `django-framework` | Django core framework patterns with batteries-included features (ORM, admin, auth). | `~/.claude/skills/django-framework/SKILL.md` |
| `django-orm-patterns` | Django ORM: models, queries, relationships. Use when building database-driven Django applications. | `~/.claude/skills/django-orm-patterns/SKILL.md` |
| `django-rest-framework` | Django REST Framework: serializers, viewsets, authentication. Use when creating RESTful APIs. | `~/.claude/skills/django-rest-framework/SKILL.md` |

---

## 🧪 Testing

| Skill | Description | Path |
|-------|-------------|------|
| `e2e-testing-patterns` | E2E testing with Playwright and Cypress: reliable test suites, debugging flaky tests, testing standards. Use when implementing E2E tests. | `~/.claude/skills/e2e-testing-patterns/SKILL.md` |
| `qa-test-planner` | Generate comprehensive test plans, manual test cases, regression suites, and bug reports. Includes Figma MCP integration for design validation. | `~/.claude/skills/qa-test-planner/SKILL.md` |
| `webapp-testing` | Test local web apps with Playwright: frontend functionality, UI debugging, screenshots, browser logs. | `~/.claude/skills/webapp-testing/SKILL.md` |

---

## ⚛️ React / Frontend

| Skill | Description | Path |
|-------|-------------|------|
| `vercel-react-best-practices` | React and Next.js performance optimization from Vercel Engineering: waterfalls, bundle size, hooks, data fetching. | `~/.claude/skills/vercel-react-best-practices/SKILL.md` |
| `react-best-practices` | React development: hooks, component patterns, state management, performance optimization. | `~/.claude/skills/react-best-practices/SKILL.md` |
| `frontend-design` | Production-grade frontend interfaces: web components, pages, dashboards, HTML/CSS, polished UI design. | `~/.claude/skills/frontend-design/SKILL.md` |
| `web-design-guidelines` | Web interface guidelines compliance: accessibility, UX audit, design best practices review. | `~/.claude/skills/web-design-guidelines/SKILL.md` |

---

## 📱 Mobile

| Skill | Description | Path |
|-------|-------------|------|
| `mobile-design` | Mobile-first design for iOS and Android: touch interaction, performance, platform conventions, offline behavior. For React Native, Flutter, or native apps. | `~/.claude/skills/mobile-design/SKILL.md` |
| `capacitor-best-practices` | Capacitor app development: project structure, plugin usage, performance, security, deployment. | `~/.claude/skills/capacitor-best-practices/SKILL.md` |

---

## 🔧 Backend

| Skill | Description | Path |
|-------|-------------|------|
| `backend-development` | Backend API design, database architecture, microservices patterns, test-driven development. | `~/.claude/skills/backend-development/SKILL.md` |

---

## 🎨 Design & UX

| Skill | Description | Path |
|-------|-------------|------|
| `ui-ux-designer` | UI/UX design expert: interface design, interaction design, user experience, design systems. | `~/.claude/skills/ui-ux-designer/SKILL.md` |

---

## 🤖 AI / Prompting / Meta

| Skill | Description | Path |
|-------|-------------|------|
| `prompt-architect` | Analyzes and transforms prompts using CO-STAR, RISEN, RISE-IE, TIDD-EC, RTF, Chain of Thought frameworks. Use when users need expert prompt engineering. | `~/.claude/skills/prompt-architect/SKILL.md` |
| `mcp-builder` | Build and structure MCP servers with strong defaults and implementation guidance. | `~/.claude/skills/mcp-builder/SKILL.md` |
| `mcp-server-index` | RAG-indexed MCP registry mapping tasks to the correct server and dispatch policy. | `~/.claude/skills/mcp-server-index/SKILL.md` |
| `fastmcp` | FastMCP-oriented guidance for building Python MCP servers and tool interfaces. | `~/.claude/skills/fastmcp/SKILL.md` |
| `writing-skills` | Use when creating new skills, editing existing skills, or verifying skills work before deployment. Covers skill authoring, structure, and validation. | `~/.claude/skills/writing-skills/SKILL.md` |
| `find-skills` | Discover and install new agent skills from the skills.sh ecosystem using `npx skills find [query]` and `npx skills add <package>`. | `~/.claude/skills/find-skills/SKILL.md` |

---

## Quick Reference: When to Load Which Skill

- **Working in Godot/GDScript** → `godot-best-practices` + `godot-gdscript-mastery`
- **Using the full Godot expert stack** → `omega-gdscript-expert` + `mcp-server-index`
- **Building Godot VFX/particles** → `godot-particles`
- **Django API project** → `django-expert` + `django-rest-framework`
- **Django database work** → `django-orm-patterns`
- **Writing E2E tests** → `e2e-testing-patterns`
- **Testing a web app manually** → `webapp-testing`
- **React/Next.js performance** → `vercel-react-best-practices`
- **Building UI components** → `frontend-design` + `web-design-guidelines`
- **Mobile app work** → `mobile-design`
- **REST API / backend** → `backend-development`
- **Crafting AI prompts** → `prompt-architect`
- **Building MCP servers** → `mcp-builder` + `fastmcp`
- **Creating or editing a skill** → `writing-skills`
- **Looking for a skill** → `find-skills`
