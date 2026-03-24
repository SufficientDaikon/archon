# omega-gdscript-expert

**Meta-Skill Coordinator for Godot 4.x Game Development**

## Purpose

Routes Godot development requests to the appropriate specialized skill based on the task type, ensuring optimal expertise is applied to each aspect of game development.

## Routing Logic

### 1. Code Quality & Standards → **godot-gdscript-mastery**

**Trigger keywords:** static_typing, signal_architecture, unique_nodes, @onready, class_name, signal_up_call_down, gdscript_style_guide, code review, refactoring, project standards, type hints

**Use when:**
- Reviewing GDScript code for best practices
- Establishing project coding standards
- Refactoring existing code to modern patterns
- Teaching proper signal architecture (signal up, call down)
- Implementing static typing with proper type hints
- Setting up unique node access with %NodeName
- Questions about class_name, @onready, or script organization

**Example requests:**
- "Review this GDScript file for best practices"
- "How should I structure my signals?"
- "Refactor this code to use static typing"
- "What's the proper way to access child nodes?"

---

### 2. Debugging & Troubleshooting → **godot-debugging**

**Trigger keywords:** error, crash, bug, not working, unexpected behavior, troubleshooting, debug, fix, parse error, null reference, type mismatch

**Use when:**
- Encountering Godot errors or crashes
- Unexpected game behavior
- Performance issues or lag
- Scene loading problems
- Signal connection failures
- Physics or collision bugs
- Script errors or null references

**Example requests:**
- "I'm getting 'Invalid call. Nonexistent function' error"
- "My character falls through the floor"
- "Signals aren't connecting properly"
- "Game crashes when changing scenes"
- "Why isn't my _ready() function being called?"

---

### 3. Visual Effects & Particles → **godot-particles**

**Trigger keywords:** GPUParticles2D, GPUParticles3D, ParticleProcessMaterial, particles, VFX, explosion, magic effect, weather, trails, emission, color_ramp, sub_emitter

**Use when:**
- Creating explosions, magic effects, or spell visuals
- Implementing weather systems (rain, snow, fog)
- Adding trail effects to projectiles or movement
- Designing environmental particle effects
- Using GPUParticles2D or GPUParticles3D
- Configuring ParticleProcessMaterial
- Setting up sub-emitters or custom particle shaders

**Example requests:**
- "How do I create an explosion effect?"
- "I need a rain particle system"
- "Create a magic spell with glowing particles"
- "Add a trail effect to this projectile"
- "How do I use gradient colors in particles?"

---

### 4. Game Mechanics & Patterns → **godot-gdscript-patterns**

**Trigger keywords:** state machine, signals, scenes, inventory system, save/load, game loop, object pooling, autoload, game architecture, resource management

**Use when:**
- Implementing game systems (inventory, dialogue, combat)
- Creating state machines for characters or AI
- Designing scene architecture
- Building save/load systems
- Setting up object pooling for performance
- Implementing resource management
- Structuring game loops and managers
- Questions about Autoload/singletons
- Designing game architecture

**Example requests:**
- "How do I create a player state machine?"
- "Implement an inventory system"
- "Create a save/load system"
- "How should I structure my game scenes?"
- "Build an object pool for bullets"

---

### 5. Project Setup & General Guidance → **godot-best-practices**

**Trigger keywords:** project structure, scene organization, performance optimization, export, deployment, project settings, input mapping, folder structure

**Use when:**
- Starting a new Godot project
- Organizing project folder structure
- Configuring project settings
- Setting up input actions
- Performance optimization strategies
- Preparing for export/deployment
- Questions about scene organization
- General Godot workflow guidance

**Example requests:**
- "How should I structure my Godot project?"
- "Set up a new 2D platformer project"
- "Optimize my game's performance"
- "How do I organize my scenes and scripts?"
- "Configure input mapping for gamepad support"

---

## Multi-Skill Scenarios

Some complex tasks require **multiple skills in sequence**:

### Character Controller Bug
1. **godot-debugging** → Identify root cause of movement bug
2. **godot-gdscript-patterns** → Implement proper state machine
3. **godot-gdscript-mastery** → Refactor with static typing and signals

### New Game Project
1. **godot-best-practices** → Set up project structure
2. **godot-gdscript-patterns** → Implement core game systems
3. **godot-particles** → Add visual effects
4. **godot-gdscript-mastery** → Code review and optimization

### VFX System with Performance Issues
1. **godot-debugging** → Diagnose performance bottleneck
2. **godot-particles** → Optimize particle systems
3. **godot-gdscript-patterns** → Implement object pooling

---

## Decision Tree

```
Is the request about...

├─ ERROR, BUG, CRASH?
│  └─ godot-debugging
│
├─ PARTICLES, VFX, VISUAL EFFECTS?
│  └─ godot-particles
│
├─ CODE QUALITY, REVIEW, STANDARDS?
│  └─ godot-gdscript-mastery
│
├─ GAME SYSTEM, STATE MACHINE, ARCHITECTURE?
│  └─ godot-gdscript-patterns
│
└─ PROJECT SETUP, ORGANIZATION, GENERAL?
   └─ godot-best-practices
```

---

## Skill Priority Matrix

| Task Category | Primary Skill | Secondary Skill | Tertiary Skill |
|--------------|---------------|-----------------|----------------|
| **Bug Fixing** | godot-debugging | godot-gdscript-mastery | godot-gdscript-patterns |
| **New Feature** | godot-gdscript-patterns | godot-best-practices | godot-gdscript-mastery |
| **Code Review** | godot-gdscript-mastery | godot-gdscript-patterns | godot-best-practices |
| **VFX Creation** | godot-particles | godot-gdscript-patterns | godot-debugging |
| **Project Setup** | godot-best-practices | godot-gdscript-patterns | godot-gdscript-mastery |
| **Performance** | godot-debugging | godot-gdscript-patterns | godot-particles |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this a problem or a feature?**
   - Problem → godot-debugging
   - Feature → godot-gdscript-patterns

2. **Is visual quality the focus?**
   - Yes → godot-particles
   - No → Continue

3. **Is code quality the primary concern?**
   - Yes → godot-gdscript-mastery
   - No → Continue

4. **Is this about project organization?**
   - Yes → godot-best-practices
   - No → godot-gdscript-patterns (default for implementation)

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "My player isn't moving" | godot-debugging | Bug/error scenario |
| "Create a dash ability" | godot-gdscript-patterns | New game mechanic |
| "Review this script" | godot-gdscript-mastery | Code quality focus |
| "Add explosion effect" | godot-particles | VFX creation |
| "Organize my project" | godot-best-practices | Structure/setup |
| "Implement save system" | godot-gdscript-patterns | Game system architecture |
| "Optimize particle spawn" | godot-particles + godot-debugging | Multi-skill (performance + VFX) |

---

## Integration with MCP Servers

When MCP servers are configured for Godot development:

1. **Check MCP server availability** before routing
2. **Prefer MCP-based operations** for:
   - Scene manipulation
   - Node inspection
   - Resource management
   - Project configuration
3. **Fallback to skills** when MCP unavailable

Consult `mcp-server-index` skill for active MCP routing rules.

---

## Notes for AI Assistants

- **Always choose ONE primary skill** for simple requests
- **Chain multiple skills** for complex, multi-phase tasks
- **Start with debugging** if the user reports unexpected behavior
- **Use godot-gdscript-mastery** as final review step for production code
- **Consult the specific SKILL.md** before applying skill knowledge
- **Don't mix concerns** — keep VFX separate from game logic, debugging separate from new features
