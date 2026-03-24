# ux-design-expert

**Meta-Skill Coordinator for UX/UI Design Lifecycle**

## Purpose

Orchestrates the complete UX/UI design lifecycle from research to testing, routing requests to specialized skills based on the design phase and deliverable type.

## UX Lifecycle Phases

The UX design process follows a structured lifecycle. Route based on the current phase:

```
1. RESEARCH → ux-research
2. INFORMATION ARCHITECTURE → info-architecture  
3. WIREFRAMING → wireframing
4. VISUAL DESIGN → ui-visual-design
5. INTERACTION DESIGN → ux-interaction-design
6. TESTING → ux-test-suite
7. GENERAL/OVERVIEW → ui-ux-designer
```

---

## Routing Logic

### 1. Phase 1: User Research → **ux-research**

**Trigger keywords:** research, persona, user journey, competitive analysis, user needs, target audience, pain points, user interviews, research synthesis

**Use when:**
- Starting a new UX project
- Creating user personas
- Mapping user journeys
- Conducting competitive analysis
- Synthesizing user research data
- Understanding user needs and pain points
- Defining target audience

**Deliverable:** Research Brief with personas, journey maps, competitive insights

**Example requests:**
- "Create personas for an e-commerce app"
- "Map the user journey for onboarding"
- "Analyze competitors in the fitness app space"
- "Who are our target users?"

---

### 2. Phase 2: Information Architecture → **info-architecture**

**Trigger keywords:** sitemap, navigation, content strategy, screen inventory, user flow, site structure, IA, page hierarchy, navigation design

**Use when:**
- Organizing site structure
- Creating sitemaps
- Designing navigation systems
- Building screen inventories
- Mapping user flows between screens
- Planning content hierarchy
- Defining page relationships

**Deliverable:** IA Document with sitemap, navigation design, user flows

**Example requests:**
- "Create a sitemap for a SaaS dashboard"
- "Design the navigation for a multi-level site"
- "Map the flow from homepage to checkout"
- "Organize content structure"

---

### 3. Phase 3: Wireframing → **wireframing**

**Trigger keywords:** wireframe, layout, low-fidelity, grayscale, page structure, responsive layout, grid, content blocks, mockup, lo-fi

**Use when:**
- Creating low-fidelity layouts
- Defining page structure
- Establishing content block placement
- Planning responsive breakpoints
- Building grayscale mockups
- Defining layout grids
- Creating rapid prototypes

**Deliverable:** HTML/CSS Wireframes (grayscale, layout-focused)

**Example requests:**
- "Wireframe a landing page"
- "Create a layout for a dashboard"
- "Design the structure of a checkout flow"
- "Build a responsive wireframe for mobile and desktop"

---

### 4. Phase 4: Visual Design → **ui-visual-design**

**Trigger keywords:** color, typography, visual hierarchy, design tokens, hero section, style guide, branding, aesthetics, high-fidelity, visual polish

**Use when:**
- Creating high-fidelity designs
- Defining color palettes and typography
- Establishing visual hierarchy
- Building design systems
- Creating design tokens
- Designing hero sections
- Adding visual polish
- Implementing brand aesthetics

**Deliverable:** High-Fidelity Visual Designs with design tokens, component library

**Example requests:**
- "Create a color scheme for a fintech app"
- "Design a hero section for a landing page"
- "Build a design system with tokens"
- "Define typography hierarchy"
- "Make this wireframe beautiful"

---

### 5. Phase 5: Interaction Design → **ux-interaction-design**

**Trigger keywords:** interaction, animation, transitions, hover states, component states, micro-interactions, feedback, form UX, state machine, loading states

**Use when:**
- Defining component interaction states
- Specifying animations and transitions
- Designing micro-interactions
- Planning hover/focus/active states
- Creating form UX patterns
- Building interaction state machines
- Defining feedback mechanisms (success, error, loading)

**Deliverable:** UX Specification with interaction patterns, state machines, transition specs

**Example requests:**
- "Define the states for this button component"
- "Design the interaction for a dropdown menu"
- "Specify animations for page transitions"
- "Create micro-interactions for form validation"
- "Design loading and error states"

---

### 6. Phase 6: Usability Testing → **ux-test-suite**

**Trigger keywords:** test, usability, cognitive load, task completion, accessibility, user testing, heuristic evaluation, UX audit, flow testing

**Use when:**
- Testing user flows
- Evaluating usability
- Running task completion tests
- Assessing cognitive load
- Conducting heuristic evaluations
- Creating UX test plans
- Measuring usability scores
- Testing error recovery

**Deliverable:** UX Test Report with usability scores, issues, and recommendations

**Example requests:**
- "Test the checkout flow for usability"
- "Evaluate cognitive load of this dashboard"
- "Run a heuristic evaluation"
- "Create a usability test plan"
- "Check if users can complete this task"

---

### 7. General/Advisory Role → **ui-ux-designer**

**Trigger keywords:** UX advice, design consultation, general design, design principles, best practices, design critique

**Use when:**
- General UX/UI questions
- Design principle guidance
- Broad design consultation
- Not fitting into specific lifecycle phase
- Need holistic design perspective
- Design strategy discussions

**Use sparingly** — prefer routing to specific lifecycle skills.

**Example requests:**
- "What are UX best practices for forms?"
- "Review this design holistically"
- "General design advice for mobile apps"

---

## Multi-Phase Workflows

### Complete UX Project (Sequential)
1. **ux-research** → Personas, journey maps
2. **info-architecture** → Sitemap, navigation
3. **wireframing** → Lo-fi layouts
4. **ui-visual-design** → Hi-fi visuals, design tokens
5. **ux-interaction-design** → Interaction specs
6. **ux-test-suite** → Usability testing

### Redesign Project (Skip research if available)
1. **info-architecture** → Restructure IA
2. **wireframing** → New layouts
3. **ui-visual-design** → Visual refresh
4. **ux-interaction-design** → Enhanced interactions
5. **ux-test-suite** → Validate improvements

### Component Design (Focused)
1. **wireframing** → Component structure
2. **ui-visual-design** → Visual styling
3. **ux-interaction-design** → Component states
4. **ux-test-suite** → Usability validation

---

## Decision Tree

```
What phase are you in?

├─ RESEARCH / DISCOVERY
│  └─ ux-research
│
├─ STRUCTURE / ORGANIZATION
│  └─ info-architecture
│
├─ LAYOUT / STRUCTURE
│  └─ wireframing
│
├─ VISUAL / AESTHETICS
│  └─ ui-visual-design
│
├─ INTERACTIONS / STATES
│  └─ ux-interaction-design
│
├─ TESTING / VALIDATION
│  └─ ux-test-suite
│
└─ GENERAL / ADVICE
   └─ ui-ux-designer
```

---

## Deliverable-Based Routing

| Deliverable Needed | Routed To |
|-------------------|-----------|
| **Persona** | ux-research |
| **Journey Map** | ux-research |
| **Competitive Analysis** | ux-research |
| **Sitemap** | info-architecture |
| **Navigation Design** | info-architecture |
| **User Flow** | info-architecture |
| **Wireframe** | wireframing |
| **Lo-fi Mockup** | wireframing |
| **Color Palette** | ui-visual-design |
| **Design Tokens** | ui-visual-design |
| **Hero Section** | ui-visual-design |
| **Component States** | ux-interaction-design |
| **Animation Spec** | ux-interaction-design |
| **Micro-interactions** | ux-interaction-design |
| **Usability Test Plan** | ux-test-suite |
| **UX Audit Report** | ux-test-suite |

---

## Lifecycle Handoff Chain

Each phase produces input for the next:

```
ux-research (personas, journeys)
    ↓
info-architecture (sitemap, flows)
    ↓
wireframing (layouts, structure)
    ↓
ui-visual-design (colors, typography)
    ↓
ux-interaction-design (states, animations)
    ↓
ux-test-suite (validation, metrics)
```

**AI assistants should:**
- Recognize current phase artifacts
- Route to next logical phase
- Pass forward relevant context

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **New Project** | ux-research | info-architecture | wireframing |
| **Site Structure** | info-architecture | wireframing | ui-ux-designer |
| **Visual Refresh** | ui-visual-design | ux-interaction-design | ux-test-suite |
| **Interaction Spec** | ux-interaction-design | ui-visual-design | ux-test-suite |
| **Usability Audit** | ux-test-suite | ui-ux-designer | ux-interaction-design |
| **Component Design** | wireframing | ui-visual-design | ux-interaction-design |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this the START of a project?**
   - Yes → ux-research
   - No → Continue

2. **What deliverable is needed?**
   - Sitemap/Navigation → info-architecture
   - Layout/Structure → wireframing
   - Colors/Typography → ui-visual-design
   - States/Interactions → ux-interaction-design
   - Testing/Validation → ux-test-suite

3. **What phase are you in?**
   - Research → ux-research
   - IA → info-architecture
   - Wireframing → wireframing
   - Visual → ui-visual-design
   - Interaction → ux-interaction-design
   - Testing → ux-test-suite

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "Create personas for a fitness app" | ux-research | Phase 1: Research |
| "Design the sitemap" | info-architecture | Phase 2: IA |
| "Wireframe the dashboard" | wireframing | Phase 3: Wireframing |
| "Choose colors for the brand" | ui-visual-design | Phase 4: Visual design |
| "Define button hover states" | ux-interaction-design | Phase 5: Interactions |
| "Test the checkout flow" | ux-test-suite | Phase 6: Testing |
| "General UX advice" | ui-ux-designer | Advisory/general |

---

## Quality Gates Between Phases

Before moving to next phase, validate:

1. **Research → IA**: Personas and journeys defined?
2. **IA → Wireframing**: Sitemap and flows complete?
3. **Wireframing → Visual**: Layouts approved?
4. **Visual → Interaction**: Design tokens defined?
5. **Interaction → Testing**: All states specified?

**Use design-review skill** for formal quality gates (if available in environment).

---

## Integration with Design-Review Skill

When `design-review` skill is available:
- **After each phase**, optionally call design-review for quality gate
- **Before handoff**, always validate artifacts
- **On issues**, route back to appropriate phase skill

---

## Notes for AI Assistants

- **Always start with ux-research** for new projects
- **Follow the lifecycle sequentially** unless user requests specific phase
- **Pass artifacts forward** — personas inform IA, IA informs wireframes, etc.
- **Don't skip phases** unless user explicitly requests
- **Use ui-ux-designer** only for general advice, not deliverable creation
- **Each skill produces REAL artifacts**, not just advice
- **Consult each skill's SKILL.md** before applying knowledge
