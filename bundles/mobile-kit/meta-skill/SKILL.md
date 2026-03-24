# mobile-expert

**Meta-Skill Coordinator for Mobile Development**

## Purpose

Routes mobile development requests between mobile-first design principles and Capacitor app implementation, ensuring proper separation between design decisions and technical implementation.

## Routing Logic

### 1. Mobile Design & UX → **mobile-design**

**Trigger keywords:** mobile design, touch interaction, mobile UX, iOS design, Android design, mobile-first, touch patterns, mobile navigation, responsive mobile, platform conventions, mobile performance

**Use when:**
- Making mobile UI/UX design decisions
- Implementing touch interactions and gestures
- Designing mobile navigation patterns
- Following iOS or Android platform conventions
- Optimizing mobile performance
- Planning offline behavior and strategies
- Mobile-first responsive design
- Touch target sizing and accessibility
- Mobile-specific constraints and patterns

**Example requests:**
- "Design a mobile navigation menu"
- "Implement touch gestures for this feature"
- "Follow iOS design guidelines"
- "Optimize this UI for mobile performance"
- "Design offline functionality"
- "Make this touch-friendly"
- "Apply mobile-first design principles"

---

### 2. Capacitor Implementation → **capacitor-best-practices**

**Trigger keywords:** Capacitor, Capacitor plugin, native functionality, iOS build, Android build, Capacitor project, Capacitor config, native integration, camera, geolocation, push notifications

**Use when:**
- Setting up Capacitor projects
- Integrating Capacitor plugins
- Accessing native device functionality
- Building for iOS or Android
- Configuring Capacitor settings
- Using native APIs (camera, geolocation, etc.)
- Debugging Capacitor apps
- Deploying to app stores
- Native plugin development

**Example requests:**
- "Setup a new Capacitor project"
- "Integrate camera plugin"
- "Configure Capacitor for iOS"
- "Access native geolocation"
- "Build for Android with Capacitor"
- "Implement push notifications"
- "Debug Capacitor plugin issues"

---

## Multi-Skill Scenarios

### New Mobile App Development
1. **mobile-design** → Design mobile-first UI/UX
2. **capacitor-best-practices** → Setup Capacitor project
3. **mobile-design** → Refine touch interactions
4. **capacitor-best-practices** → Integrate native features

### Adding Native Feature
1. **mobile-design** → Design feature UX (offline, touch patterns)
2. **capacitor-best-practices** → Implement with Capacitor plugin

### Mobile-First Web App
1. **mobile-design** → Design responsive mobile experience
2. **capacitor-best-practices** → Wrap with Capacitor for app stores (optional)

---

## Decision Tree

```
Is the request about...

├─ DESIGN, UX, TOUCH INTERACTIONS?
│  └─ mobile-design
│
└─ CAPACITOR, NATIVE FEATURES, PLUGINS?
   └─ capacitor-best-practices
```

---

## Layer-Based Routing

### Design Layer
**mobile-design** handles all design decisions, UX patterns, and mobile-first principles

### Implementation Layer
**capacitor-best-practices** handles Capacitor-specific implementation and native integration

---

## Skill Priority Matrix

| Task Category | Primary | Secondary |
|--------------|---------|-----------|
| **UI/UX Design** | mobile-design | - |
| **Touch Interactions** | mobile-design | - |
| **Capacitor Setup** | capacitor-best-practices | mobile-design |
| **Native Integration** | capacitor-best-practices | mobile-design |
| **Platform Conventions** | mobile-design | capacitor-best-practices |
| **Performance** | mobile-design | capacitor-best-practices |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this about DESIGN, UX, or TOUCH PATTERNS?**
   - Yes → mobile-design
   - No → Continue

2. **Is this about CAPACITOR or NATIVE FEATURES?**
   - Yes → capacitor-best-practices
   - No → mobile-design (default for mobile questions)

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "Design mobile navigation" | mobile-design | UI/UX design |
| "Setup Capacitor project" | capacitor-best-practices | Capacitor implementation |
| "Implement touch gestures" | mobile-design | Touch interaction design |
| "Integrate camera plugin" | capacitor-best-practices | Native feature with Capacitor |
| "Follow iOS design patterns" | mobile-design | Platform conventions |
| "Build for Android" | capacitor-best-practices | Capacitor build process |
| "Optimize mobile performance" | mobile-design | Mobile-first optimization |
| "Access geolocation API" | capacitor-best-practices | Native API integration |

---

## Technology Stack Detection

### Web-Only Mobile (No Capacitor)
- **mobile-design** for responsive design and mobile UX
- Skip capacitor-best-practices

### Capacitor Hybrid App
1. **mobile-design** for UI/UX design
2. **capacitor-best-practices** for native integration

### React Native / Flutter (Outside Scope)
- **mobile-design** still applies for design principles
- capacitor-best-practices not applicable

---

## Sequential Workflow Patterns

### Pattern 1: New Mobile App
```
mobile-design (design mobile-first UI)
    ↓
capacitor-best-practices (setup Capacitor)
    ↓
mobile-design (refine touch interactions)
    ↓
capacitor-best-practices (add native features)
```

### Pattern 2: Adding Native Feature
```
mobile-design (design feature UX)
    ↓
capacitor-best-practices (implement with plugin)
    ↓
mobile-design (optimize for mobile constraints)
```

### Pattern 3: Mobile-First Web App
```
mobile-design (design responsive mobile experience)
    ↓
[web implementation]
    ↓
capacitor-best-practices (optionally wrap for app stores)
```

---

## Integration Points

### Design → Implementation
- **mobile-design** defines UX patterns and constraints
- **capacitor-best-practices** implements within those constraints
- Coordinate: Design must account for Capacitor capabilities

### Implementation → Design
- **capacitor-best-practices** exposes native capabilities
- **mobile-design** designs UX around those capabilities
- Coordinate: Native features inform design possibilities

---

## Quality Gates

Before marking mobile work complete:

1. **Mobile-first design principles applied?** → mobile-design ✓
2. **Touch interactions optimized?** → mobile-design ✓
3. **Platform conventions followed?** → mobile-design ✓
4. **Native features integrated?** → capacitor-best-practices ✓
5. **Performance optimized for mobile?** → mobile-design ✓

---

## Common Anti-Patterns (Avoid)

- ❌ Using capacitor-best-practices for design decisions → Use mobile-design
- ❌ Using mobile-design for Capacitor configuration → Use capacitor-best-practices
- ❌ Ignoring mobile-design when building Capacitor apps → Always consider mobile UX

---

## Framework-Specific Notes

### Capacitor + React
- **mobile-design** for React component mobile UX
- **capacitor-best-practices** for Capacitor integration

### Capacitor + Vue/Angular/Vanilla
- Same pattern: mobile-design for UX, capacitor-best-practices for native

### Progressive Web App (PWA)
- **mobile-design** for mobile-first design
- **capacitor-best-practices** to convert PWA to native app

---

## Notes for AI Assistants

- **Design/UX → mobile-design**
- **Capacitor/Native → capacitor-best-practices**
- **Always start with mobile-design** for new mobile projects
- **Consider mobile constraints** before implementation
- **Touch interactions** are always mobile-design domain
- **Native features** are always capacitor-best-practices domain
- **Consult each SKILL.md** before applying mobile knowledge
- **Mobile-first principle:** Design for mobile constraints first, then enhance
