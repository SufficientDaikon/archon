# web-fullstack-expert

**Meta-Skill Coordinator for Full-Stack Web Development**

## Purpose

Routes full-stack web development requests to the appropriate specialized skill, ensuring frontend design, React optimization, backend architecture, and UX compliance are handled by the right expertise.

## Routing Logic

### 1. Creating New UI Components/Pages → **frontend-design**

**Trigger keywords:** build, create, design, new component, new page, landing page, dashboard, website, HTML, CSS, styling, beautify, artifact, poster, web UI

**Use when:**
- Building new web components from scratch
- Creating landing pages or marketing sites
- Designing dashboards or admin interfaces
- Building HTML/CSS layouts
- Styling or beautifying existing UI
- Creating web artifacts (posters, cards, widgets)
- Need distinctive, production-grade design
- Avoiding generic AI aesthetics

**Example requests:**
- "Build a landing page for a SaaS product"
- "Create a React dashboard component"
- "Design a pricing page"
- "Build a hero section with animations"
- "Create a beautiful portfolio website"

---

### 2. React/Next.js Performance Optimization → **vercel-react-best-practices**

**Trigger keywords:** Next.js, performance, optimization, bundle size, data fetching, server components, client components, hydration, streaming, Vercel, getStaticProps, getServerSideProps, app router

**Use when:**
- Optimizing React or Next.js performance
- Bundle size reduction
- Data fetching strategy decisions
- Server vs client component choices
- Implementing streaming or Suspense
- Next.js app router patterns
- SSR/SSG optimization
- Hydration issues
- Code splitting strategies

**Example requests:**
- "Optimize this Next.js page load time"
- "Should this be a server or client component?"
- "Reduce my React bundle size"
- "Implement data fetching with Next.js 14"
- "Fix hydration mismatch errors"

---

### 3. React Component Patterns → **react-best-practices**

**Trigger keywords:** React hooks, useState, useEffect, useContext, custom hooks, component lifecycle, state management, props, composition, component patterns

**Use when:**
- Using React hooks (useState, useEffect, etc.)
- Creating custom hooks
- Managing component state
- Component composition patterns
- React context and providers
- Component lifecycle questions
- Props drilling solutions
- General React patterns (not Next.js-specific)

**Example requests:**
- "Create a custom hook for data fetching"
- "How should I structure this React component?"
- "Fix this useEffect infinite loop"
- "Implement state management with Context"
- "Best way to pass props through multiple levels?"

---

### 4. UI/UX Compliance Review → **web-design-guidelines**

**Trigger keywords:** review, audit, accessibility, WCAG, compliance, best practices, UX review, design audit, check accessibility, review my site, interface guidelines

**Use when:**
- Reviewing existing UI code for compliance
- Accessibility audits (WCAG, ARIA)
- Design system consistency checks
- UX heuristic evaluation
- Interface guideline compliance
- Code review for UI quality
- Checking against web standards

**Example requests:**
- "Review my UI for accessibility"
- "Audit this design for best practices"
- "Check WCAG compliance"
- "Review my site against interface guidelines"
- "Is this component accessible?"

---

### 5. Backend/API Development → **backend-development**

**Trigger keywords:** API, backend, database, REST, GraphQL, microservices, authentication, authorization, server, endpoint, schema, SQL, NoSQL, architecture

**Use when:**
- Designing REST or GraphQL APIs
- Database schema design
- Backend architecture decisions
- Microservices patterns
- Authentication/authorization systems
- API endpoint implementation
- Database queries and optimization
- Server-side logic
- Test-driven backend development

**Example requests:**
- "Design a REST API for user management"
- "Create a database schema for e-commerce"
- "Implement JWT authentication"
- "Build a GraphQL resolver"
- "Design a microservices architecture"

---

## Multi-Skill Scenarios

### Full-Stack Feature Development
1. **backend-development** → Design API endpoints and schema
2. **react-best-practices** → Implement React components
3. **vercel-react-best-practices** → Optimize data fetching
4. **frontend-design** → Polish UI and styling
5. **web-design-guidelines** → Final compliance review

### React App Performance Audit
1. **vercel-react-best-practices** → Identify performance bottlenecks
2. **react-best-practices** → Refactor component patterns
3. **web-design-guidelines** → Review for UX impact

### New Web Application
1. **backend-development** → API and database architecture
2. **frontend-design** → UI design and component creation
3. **react-best-practices** → React implementation
4. **vercel-react-best-practices** → Next.js optimization
5. **web-design-guidelines** → Accessibility audit

---

## Decision Tree

```
Is the request about...

├─ NEW UI DESIGN/CREATION?
│  └─ frontend-design
│
├─ NEXT.JS PERFORMANCE OR APP ROUTER?
│  └─ vercel-react-best-practices
│
├─ REACT HOOKS, STATE, PATTERNS?
│  └─ react-best-practices
│
├─ UI REVIEW, AUDIT, ACCESSIBILITY?
│  └─ web-design-guidelines
│
└─ BACKEND, API, DATABASE?
   └─ backend-development
```

---

## Layer-Based Routing

### Frontend Layer
- **Visual/Design** → frontend-design
- **React Patterns** → react-best-practices  
- **Next.js Optimization** → vercel-react-best-practices
- **Compliance** → web-design-guidelines

### Backend Layer
- **Everything backend** → backend-development

---

## Technology-Specific Routing

| Technology | Primary Skill | Secondary Skill |
|-----------|---------------|-----------------|
| **Next.js 13/14** | vercel-react-best-practices | react-best-practices |
| **React Hooks** | react-best-practices | vercel-react-best-practices |
| **HTML/CSS/Tailwind** | frontend-design | web-design-guidelines |
| **REST APIs** | backend-development | - |
| **GraphQL** | backend-development | - |
| **Database Design** | backend-development | - |
| **Accessibility** | web-design-guidelines | frontend-design |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **New Feature** | frontend-design | backend-development | react-best-practices |
| **Performance** | vercel-react-best-practices | react-best-practices | backend-development |
| **Code Review** | web-design-guidelines | react-best-practices | vercel-react-best-practices |
| **API Design** | backend-development | - | - |
| **React Refactor** | react-best-practices | vercel-react-best-practices | web-design-guidelines |
| **Styling** | frontend-design | web-design-guidelines | - |

---

## Self-Evaluation Loop

Before routing, ask:

1. **Is this about CREATING or REVIEWING?**
   - Creating → frontend-design or backend-development
   - Reviewing → web-design-guidelines

2. **Is this frontend or backend?**
   - Frontend → Continue to Q3
   - Backend → backend-development

3. **Is performance the primary concern?**
   - Yes + Next.js → vercel-react-best-practices
   - Yes + React → react-best-practices
   - No → Continue to Q4

4. **Is this about design/styling or logic/patterns?**
   - Design/styling → frontend-design
   - Logic/patterns → react-best-practices

---

## Example Routing Decisions

| User Request | Routed To | Rationale |
|--------------|-----------|-----------|
| "Build a landing page" | frontend-design | New UI creation |
| "Optimize Next.js SSR" | vercel-react-best-practices | Next.js performance |
| "Create a custom useAuth hook" | react-best-practices | React hook pattern |
| "Review accessibility" | web-design-guidelines | UI compliance audit |
| "Design user API" | backend-development | Backend/API design |
| "Fix useEffect issues" | react-best-practices | React pattern issue |
| "Create hero section" | frontend-design | UI component creation |
| "Reduce bundle size" | vercel-react-best-practices | Performance optimization |
| "Database schema for blog" | backend-development | Backend architecture |

---

## Framework Detection

Auto-detect framework from context:

- **Next.js detected** (pages/, app/, next.config.js)
  → Prefer vercel-react-best-practices for optimization tasks

- **React detected** (src/components/, package.json with "react")
  → Use react-best-practices for component patterns

- **Backend files detected** (routes/, api/, models/, schema/)
  → Route backend concerns to backend-development

- **No framework, HTML/CSS**
  → Use frontend-design for creation, web-design-guidelines for review

---

## Integration Notes

### When to combine skills:

**Frontend Design + React Patterns**
- Frontend-design creates the UI/styling
- React-best-practices handles state and logic

**Vercel + React Best Practices**
- Vercel-react-best-practices for Next.js-specific optimization
- React-best-practices for general React patterns

**Backend + Frontend**
- Backend-development defines API contracts
- Frontend skills implement the consuming UI

### When NOT to combine:

- Don't mix backend-development with frontend skills in the same file
- Don't use vercel-react-best-practices for non-Next.js React apps
- Don't use frontend-design for accessibility audits (use web-design-guidelines)

---

## Quality Gates

Before marking work complete:

1. **Creation phase**: frontend-design or backend-development
2. **Optimization phase**: vercel-react-best-practices or react-best-practices
3. **Review phase**: web-design-guidelines
4. **All phases pass**: Ship it ✅

---

## Notes for AI Assistants

- **New UI** → Always start with frontend-design for visual quality
- **Existing UI** → Always audit with web-design-guidelines
- **Next.js** → Default to vercel-react-best-practices for perf questions
- **React (non-Next)** → Use react-best-practices
- **Backend** → Exclusively backend-development
- **Full-stack** → Chain backend → frontend → optimization → review
