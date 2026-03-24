# meta-agent

**Meta-Skill Coordinator for Meta-Development**

## Purpose

Routes meta-development requests related to creating skills, discovering capabilities, packaging work, and engineering prompts. This is the "skill about skills" coordinator.

## Routing Logic

### 1. Skill Creation & Editing → **writing-skills**

**Trigger keywords:** create skill, write skill, edit skill, new skill, SKILL.md, manifest.yaml, skill development, verify skill, test skill, deploy skill

**Use when:**
- Creating new agent skills
- Editing existing skills
- Writing SKILL.md documentation
- Creating manifest.yaml files
- Testing skills before deployment
- Verifying skills work correctly
- Skill development workflow

**Example requests:**
- "Create a new skill for X"
- "Edit this skill to add Y"
- "Write a SKILL.md for Z"
- "Verify this skill works"
- "Test my skill before deploying"
- "Create a manifest for this skill"

---

### 2. Skill Discovery & Installation → **find-skills**

**Trigger keywords:** find skill, search skill, discover skill, install skill, is there a skill, how do I do X, skill for X, available skills, skill catalog

**Use when:**
- User asks "how do I do X" and looking for skill
- Searching for available skills
- Discovering skills by capability
- Installing new skills
- Exploring skill catalog
- Finding skills for specific use cases
- User interested in extending capabilities

**Example requests:**
- "Find a skill for testing"
- "Is there a skill for X?"
- "How do I do Y?" (looking for skill)
- "Search for skills related to Z"
- "What skills are available for A?"
- "Install a skill for B"

---

### 3. Skill Lookup & Routing → **skills-index**

**Trigger keywords:** list skills, show skills, what skills, which skill should I use, skill routing, consult skills, available skills, skill documentation

**Use when:**
- Looking up installed skills
- Determining which skill to use
- Understanding skill routing decisions
- Consulting skill documentation
- Finding skill capabilities
- Skill inventory questions

**Example requests:**
- "What skills are installed?"
- "Which skill should I use for X?"
- "List all available skills"
- "Show me the skills index"
- "What can skill Y do?"
- "Consult skills for routing"

---

### 4. Packaging & Sharing → **packager**

**Trigger keywords:** package, share, publish, export, distribute, make repo, git repo, share agent, share skill, package this, publish agent, shareable

**Use when:**
- Packaging agents for sharing
- Creating shareable git repos
- Publishing skills or agents
- Exporting SDD artifacts
- Distributing custom agents
- Creating README documentation
- Making work shareable
- Publishing to GitHub

**Example requests:**
- "Package this agent"
- "Share this skill"
- "Create a repo for this"
- "Publish my agent"
- "Make this shareable"
- "Export this as a git repo"
- "Package my custom agents"

---

### 5. Prompt Engineering → **prompt-architect**

**Trigger keywords:** prompt engineering, optimize prompt, improve prompt, prompt framework, CO-STAR, RISEN, prompt structure, better prompt, prompt design

**Use when:**
- Optimizing prompts for effectiveness
- Applying prompt engineering frameworks
- Structuring prompts with CO-STAR, RISEN, etc.
- Getting prompt recommendations
- Improving prompt clarity
- Designing system prompts
- Expert prompt guidance

**Example requests:**
- "Optimize this prompt"
- "Apply CO-STAR framework"
- "Improve prompt effectiveness"
- "Structure this prompt better"
- "Prompt engineering guidance"
- "Use RISEN framework"
- "Design a system prompt"

---

## Multi-Skill Scenarios

### Creating and Sharing a Skill
1. **writing-skills** → Create the skill
2. **writing-skills** → Test and verify
3. **packager** → Package for sharing

### Discovering and Customizing Skills
1. **find-skills** → Find relevant skills
2. **skills-index** → Review skill capabilities
3. **writing-skills** → Customize if needed

### Building a Custom Agent
1. **skills-index** → Identify required skills
2. **writing-skills** → Create agent-specific skills
3. **prompt-architect** → Optimize agent prompts
4. **packager** → Package complete agent

---

## Decision Tree

```
Is the request about...

├─ CREATING or EDITING skills?
│  └─ writing-skills
│
├─ FINDING or INSTALLING skills?
│  └─ find-skills
│
├─ LOOKING UP installed skills or ROUTING?
│  └─ skills-index
│
├─ PACKAGING or SHARING work?
│  └─ packager
│
└─ PROMPT ENGINEERING?
   └─ prompt-architect
```

---

## Action-Based Routing

| Action | Routed To |
|--------|-----------|
| **Create** | writing-skills |
| **Edit** | writing-skills |
| **Find** | find-skills |
| **Discover** | find-skills |
| **List** | skills-index |
| **Consult** | skills-index |
| **Package** | packager |
| **Share** | packager |
| **Optimize** | prompt-architect |
| **Engineer** | prompt-architect |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **Skill Creation** | writing-skills | skills-index | prompt-architect |
| **Skill Discovery** | find-skills | skills-index | - |
| **Skill Lookup** | skills-index | find-skills | - |
| **Packaging** | packager | writing-skills | - |
| **Prompt Optimization** | prompt-architect | writing-skills | - |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this about CREATING or EDITING?**
   - Yes → writing-skills
   - No → Continue

2. **Is this about FINDING or DISCOVERING?**
   - Yes → find-skills
   - No → Continue

3. **Is this about LOOKING UP or ROUTING?**
   - Yes → skills-index
   - No → Continue

4. **Is this about PACKAGING or SHARING?**
   - Yes → packager
   - No → Continue

5. **Is this about PROMPT ENGINEERING?**
   - Yes → prompt-architect
   - No → skills-index (default for meta questions)

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "Create a skill for X" | writing-skills | Skill creation |
| "Find a skill for testing" | find-skills | Skill discovery |
| "What skills are available?" | skills-index | Skill lookup |
| "Package this agent" | packager | Packaging for sharing |
| "Optimize this prompt" | prompt-architect | Prompt engineering |
| "Is there a skill for Y?" | find-skills | Skill search |
| "Edit this SKILL.md" | writing-skills | Skill editing |
| "Share my custom agent" | packager | Distribution |
| "Which skill should I use?" | skills-index | Routing guidance |
| "Apply CO-STAR framework" | prompt-architect | Prompt structuring |

---

## Meta-Development Workflow

### Complete Skill Development
```
writing-skills (create skill)
    ↓
prompt-architect (optimize skill prompts)
    ↓
writing-skills (verify and test)
    ↓
packager (package for sharing)
```

### Discovering and Using Skills
```
find-skills (search for skill)
    ↓
skills-index (review capabilities)
    ↓
[use the skill]
```

### Building Custom Agent System
```
skills-index (audit available skills)
    ↓
find-skills (discover missing capabilities)
    ↓
writing-skills (create custom skills)
    ↓
prompt-architect (optimize agent prompts)
    ↓
packager (package complete system)
```

---

## Integration Points

### Writing + Packaging
- **writing-skills** creates the skill
- **packager** makes it shareable
- Coordinate: Ensure skill is tested before packaging

### Find + Index
- **find-skills** discovers new skills
- **skills-index** tracks installed skills
- Coordinate: Index updates after skill installation

### Prompt Architect + Writing
- **prompt-architect** optimizes prompts
- **writing-skills** implements in SKILL.md
- Coordinate: Prompt improvements feed back to skill docs

---

## Quality Gates

Before considering meta-work complete:

1. **Skill created?** → writing-skills ✓
2. **Skill tested?** → writing-skills ✓
3. **Prompts optimized?** → prompt-architect ✓ (optional)
4. **Documentation complete?** → writing-skills ✓
5. **Packaged for sharing?** → packager ✓ (if sharing)

---

## Common Anti-Patterns (Avoid)

- ❌ Using find-skills to create skills → Use writing-skills
- ❌ Using skills-index to package → Use packager
- ❌ Using packager for skill creation → Use writing-skills
- ❌ Using writing-skills to discover skills → Use find-skills

---

## Self-Referential Note

**This meta-agent is itself a skill**, demonstrating the Archon framework's recursive nature. Meta-development skills can be used to:
- Improve themselves
- Create new meta-skills
- Build higher-order abstractions

---

## Archon Framework Integration

This bundle supports the complete Archon lifecycle:

1. **Discover** → find-skills
2. **Create** → writing-skills
3. **Optimize** → prompt-architect
4. **Index** → skills-index
5. **Share** → packager

---

## Notes for AI Assistants

- **Creating/editing → writing-skills**
- **Finding/discovering → find-skills**
- **Looking up/routing → skills-index**
- **Packaging/sharing → packager**
- **Prompt engineering → prompt-architect**
- **Always consult skills-index** before making routing decisions
- **Test with writing-skills** before packaging
- **Optimize with prompt-architect** for production skills
- **This is recursive** — meta-skills can improve themselves
- **Consult each SKILL.md** before applying meta-skill knowledge
