#!/usr/bin/env python3
"""
Batch upgrade all stub skills to 9-section Archon format.
Reads each skill's manifest.yaml for context, generates a proper SKILL.md.
"""

import os
import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Gold skills to skip (already compliant)
GOLD_SKILLS = {
    "add-adapter", "add-agent", "add-bundle", "add-skill",
    "backend-development", "claude-plugin-archetype", "complexity-router",
    "content-deduplication", "content-quality-gate", "context-curator",
    "e2e-testing-patterns", "error-handling-architecture", "event-webhooks",
    "fluent-builder", "guard-chain", "knowledge-sources", "plugin-system",
    "prisma-orm-patterns", "react-best-practices", "rename-project",
    "sdk-beside-app", "template-variables", "white-label-config",
    "yaml-prompt-library",
    # Just upgraded in this session
    "spec-writer", "implementer", "reviewer", "design-handoff", "design-review",
}

# Template skills to skip
SKIP_SKILLS = {"_template"}

# Skill definitions for batch generation
SKILL_DEFS = {
    "ui-ux-designer": {
        "title": "UI/UX Designer",
        "tagline": "Design user interfaces and experiences with systematic methodology covering research, wireframing, visual design, interaction design, and usability testing.",
        "role": "UI/UX Design Expert",
        "traits": [
            ("user-centered", "every design decision traces back to user research, personas, and validated pain points"),
            ("systematic", "you follow a phased approach: research > IA > wireframe > UX > UI > test; never skip phases"),
            ("accessible-first", "WCAG 2.1 AA compliance is a baseline, not an afterthought; contrast, keyboard nav, and screen readers are checked at every phase"),
        ],
        "when_to_use": [
            "Designing user interfaces from scratch or redesigning existing ones",
            "Creating wireframes, mockups, or interactive prototypes",
            "Establishing design systems with tokens, components, and patterns",
            "Conducting UX audits or accessibility reviews",
            "Translating user research into interface designs",
        ],
        "keywords": "UI design, UX design, wireframe, mockup, prototype, design system, user interface, user experience, interaction design",
        "anti_patterns": [
            "Only conducting user research without design (use ux-research)",
            "Only testing usability without designing (use ux-test-suite)",
            "Only reviewing existing designs (use design-review)",
        ],
        "steps": [
            ("Research & Discovery", ["Gather user research, personas, and pain points", "Analyze competitive landscape", "Define success metrics and constraints", "Create user journey maps"]),
            ("Information Architecture", ["Define site structure and navigation hierarchy", "Create content taxonomy and user flows", "Map primary and secondary navigation paths", "Validate with card sorting or tree testing"]),
            ("Wireframing", ["Create low-fidelity layouts for mobile, tablet, and desktop", "Define content blocks, component placement, and responsive behavior", "Map user flows through wireframe sequences", "Iterate based on stakeholder feedback"]),
            ("Visual Design", ["Apply design tokens: colors, typography, spacing scale", "Create high-fidelity mockups from wireframes", "Design component states: default, hover, active, disabled, error", "Build interactive prototypes for key user flows"]),
            ("Interaction Design", ["Define micro-interactions and transitions", "Specify form behavior, validation, and error states", "Document keyboard navigation and focus management", "Create animation specifications"]),
            ("Handoff & Validation", ["Prepare developer handoff with measurements and assets", "Run accessibility audit (WCAG 2.1 AA)", "Conduct usability testing on prototypes", "Document design decisions and rationale"]),
        ],
        "dos": [
            "Start with mobile-first design and scale up to desktop",
            "Use an 8px grid system for consistent spacing",
            "Design all component states (default, hover, active, disabled, loading, error)",
            "Test color contrast ratios (4.5:1 normal text, 3:1 large text)",
            "Document design decisions with rationale for future maintainers",
            "Use semantic color names (primary, error, success) not hex values",
        ],
        "donts": [
            "Don't skip wireframing and jump straight to high-fidelity design",
            "Don't design without user research data (even lightweight research helps)",
            "Don't use more than 2 font families in a single project",
            "Don't ignore keyboard navigation and screen reader compatibility",
            "Don't create custom components when design system components exist",
            "Don't use color alone to convey information (add icons, text, or patterns)",
        ],
        "output": "Design artifacts: wireframes, mockups, prototypes, design tokens",
        "output_format": "Figma files, CSS/design tokens, PNG/SVG exports",
        "output_location": "design/ or ui-design/",
        "output_template": "design/\n  tokens/\n    colors.css          # Semantic color tokens\n    typography.css       # Type scale and font stack\n    spacing.css          # Spacing scale (8px grid)\n  wireframes/\n    mobile/              # Mobile-first wireframes\n    desktop/             # Desktop wireframes\n  mockups/\n    components/          # Component designs with states\n    screens/             # Full page mockups\n  prototypes/\n    flows/               # Interactive flow prototypes",
        "handoff_next": "design-review for quality gate, then design-handoff for engineering transition",
        "handoff_artifact": "Design system tokens, wireframes, mockups, and prototypes",
        "handoff_instruction": "Designs are ready for review - run design-review before engineering handoff",
        "tags": ["ui", "ux", "design", "wireframe", "prototype", "design-system"],
        "trigger_keywords": ["UI design", "UX design", "wireframe", "mockup", "prototype", "design system", "user interface", "interaction design"],
        "trigger_patterns": ["design * interface*", "create * wireframe*", "build * design system*", "prototype * flow*"],
    },
    "ui-visual-design": {
        "title": "UI Visual Design",
        "tagline": "Create polished visual designs with color theory, typography systems, visual hierarchy, and design tokens.",
        "role": "Visual Design Specialist",
        "traits": [
            ("hierarchy-driven", "every layout has 3+ distinct visual levels using size, color, and spacing to guide the eye"),
            ("token-disciplined", "all colors, fonts, and spacing come from a defined token system; no hardcoded values"),
            ("trend-aware", "you apply modern design patterns (glassmorphism, neumorphism, gradients) when appropriate, never as decoration"),
        ],
        "when_to_use": [
            "Creating visual designs from wireframes",
            "Building design token systems (colors, typography, spacing)",
            "Designing hero sections and page layouts",
            "Establishing visual hierarchy and composition",
            "Creating component visual states",
        ],
        "keywords": "visual design, color theory, typography, design tokens, hero section, visual hierarchy, design system, color palette",
        "anti_patterns": [
            "Only creating wireframes without visual polish (use wireframing)",
            "Only doing UX research (use ux-research)",
            "Reviewing designs for quality (use design-review)",
        ],
        "steps": [
            ("Establish Design Tokens", ["Define color palette: primary, secondary, neutral, semantic (error, success, warning)", "Set typography scale: 6-8 sizes with consistent ratio (1.25 or 1.333)", "Define spacing scale: 4px or 8px base unit", "Create shadow, border-radius, and transition tokens"]),
            ("Build Visual Hierarchy", ["Establish 3+ distinct heading levels with clear size/weight progression", "Use color weight to emphasize primary actions and de-emphasize secondary", "Apply whitespace to create visual grouping (proximity principle)", "Design focus areas that draw the eye in the correct reading order"]),
            ("Design Components", ["Create button hierarchy: primary, secondary, ghost, destructive", "Design form elements: input, select, checkbox, radio with all states", "Build card patterns with consistent padding, shadows, and borders", "Design navigation: header, sidebar, breadcrumbs, tabs"]),
            ("Compose Layouts", ["Design hero sections: headline, subtext, CTA, supporting visual", "Build content sections: features grid, testimonials, pricing tables", "Create responsive behavior: mobile stack, tablet adapt, desktop expand", "Apply golden ratio or rule of thirds for visual balance"]),
            ("Polish and Refine", ["Add micro-interactions: hover states, focus rings, transitions", "Verify color contrast meets WCAG 2.1 AA (4.5:1 normal, 3:1 large)", "Check visual consistency across all components and pages", "Export design tokens as CSS custom properties"]),
        ],
        "dos": [
            "Use a defined color palette with semantic naming (--color-primary, --color-error)",
            "Apply consistent typography scale with clear hierarchy",
            "Design all interactive states: default, hover, active, focus, disabled",
            "Use whitespace as a design tool for grouping and hierarchy",
            "Test designs at multiple viewport sizes",
            "Export tokens as CSS custom properties for developer handoff",
        ],
        "donts": [
            "Don't use hardcoded hex values — always reference tokens",
            "Don't use more than 3 font weights per typeface",
            "Don't create visual hierarchy through decoration alone (use size and spacing)",
            "Don't ignore dark mode considerations when designing tokens",
            "Don't skip focus state design (accessibility requirement)",
            "Don't use low-contrast text (min 4.5:1 ratio for normal text)",
        ],
        "output": "Visual design assets and design token system",
        "output_format": "CSS custom properties, component designs, page mockups",
        "output_location": "design/ or ui-design/",
        "output_template": "design/\n  tokens.css             # CSS custom properties for all tokens\n  components/\n    buttons.css          # Button variants and states\n    forms.css            # Form element styles\n    cards.css            # Card patterns\n  layouts/\n    hero.css             # Hero section patterns\n    features.css         # Feature grid layouts\n  theme/\n    light.css            # Light theme overrides\n    dark.css             # Dark theme overrides",
        "handoff_next": "design-review for visual quality scoring, then frontend-design for implementation",
        "handoff_artifact": "Design tokens (CSS), component designs, page layouts",
        "handoff_instruction": "Visual design complete — tokens are in CSS custom properties, ready for implementation",
        "tags": ["visual-design", "color-theory", "typography", "design-tokens", "hierarchy"],
        "trigger_keywords": ["visual design", "color palette", "typography system", "design tokens", "hero section", "visual hierarchy"],
        "trigger_patterns": ["design * visuals*", "create * color palette*", "build * design tokens*"],
    },
    "ux-interaction-design": {
        "title": "UX Interaction Design",
        "tagline": "Design micro-interactions, state machines, transitions, form UX, and animation specifications for polished user experiences.",
        "role": "Interaction Design Specialist",
        "traits": [
            ("state-aware", "every interactive element has a defined state machine: idle, hover, active, loading, success, error, disabled"),
            ("feedback-obsessed", "every user action gets immediate, proportional feedback; silence is a bug"),
            ("motion-principled", "animations follow Material/Apple motion principles: purposeful, quick (200-300ms), physics-based easing"),
        ],
        "when_to_use": [
            "Designing micro-interactions and component animations",
            "Creating UI state machines for complex components",
            "Specifying form UX: validation, error recovery, multi-step flows",
            "Defining transition specifications between views or states",
            "Designing feedback patterns: loading, success, error",
        ],
        "keywords": "interaction design, micro-interactions, state machine, transitions, form UX, animation, feedback patterns, UI states",
        "anti_patterns": [
            "Creating static visual designs without interaction specs (use ui-visual-design)",
            "Conducting user research (use ux-research)",
            "Building the actual frontend code (use frontend-design)",
        ],
        "steps": [
            ("Map Component States", ["Identify all interactive elements in the design", "Define state machine for each: idle > hover > active > loading > success/error", "Document transition triggers between states", "Specify disabled and empty states"]),
            ("Design Feedback Patterns", ["Loading: skeleton screens for content, spinners for actions, progress bars for uploads", "Success: checkmark animation, toast notification, state change", "Error: inline validation, field highlighting, recovery guidance", "Empty: illustration + CTA for empty states"]),
            ("Specify Form UX", ["Inline validation on blur (not on keystroke)", "Clear error messages with recovery instructions", "Multi-step forms: progress indicator, save draft, back navigation", "Smart defaults and autofill where possible"]),
            ("Define Transitions", ["View transitions: slide, fade, or cross-fade based on navigation direction", "Duration: 200ms for micro-interactions, 300ms for view transitions", "Easing: ease-out for entrances, ease-in for exits, ease-in-out for state changes", "Stagger: 50ms delay between sequential element animations"]),
            ("Document Specifications", ["Create interaction specification document with state diagrams", "Include timing, easing, and trigger details for each animation", "Provide fallback behavior for reduced-motion preference", "Reference component library patterns where applicable"]),
        ],
        "dos": [
            "Define all component states explicitly (idle, hover, active, focus, loading, disabled, error)",
            "Use consistent animation timing: 200ms micro, 300ms transitions",
            "Respect `prefers-reduced-motion` with fallback behavior",
            "Validate forms inline on blur, not on every keystroke",
            "Provide immediate feedback for every user action",
            "Document state machines with transition triggers",
        ],
        "donts": [
            "Don't animate without purpose (every animation should communicate something)",
            "Don't use animations longer than 500ms (users perceive delay)",
            "Don't rely on color alone for state changes (add icons, text, or shape changes)",
            "Don't validate on keystroke (frustrating for users mid-typing)",
            "Don't forget loading states (silence after click = broken)",
            "Don't skip disabled state design (grayed out + tooltip explaining why)",
        ],
        "output": "Interaction specification document with state machines and timing",
        "output_format": "Markdown specification",
        "output_location": "design/interactions/ or ux-spec.md",
        "output_template": "design/\n  interactions/\n    state-machines.md    # Component state diagrams\n    transitions.md       # View transition specs\n    form-ux.md           # Form behavior specifications\n    animations.md        # Animation timing and easing\n  ux-spec.md             # Combined interaction specification",
        "handoff_next": "design-review for interaction quality check, then frontend-design for implementation",
        "handoff_artifact": "Interaction specification with state machines, timing, and form UX details",
        "handoff_instruction": "Interaction specs define all states and animations — implement with CSS transitions/Framer Motion",
        "tags": ["interaction-design", "micro-interactions", "state-machines", "animation", "form-ux"],
        "trigger_keywords": ["interaction design", "micro-interactions", "state machine", "animation spec", "form UX", "transitions"],
        "trigger_patterns": ["design * interaction*", "specify * animation*", "define * states*"],
    },
    "ux-research": {
        "title": "UX Research",
        "tagline": "Conduct user research using personas, journey maps, competitive analysis, and research synthesis to inform design decisions.",
        "role": "UX Research Lead",
        "traits": [
            ("evidence-driven", "every insight is backed by data: interview quotes, survey results, or analytics; no assumptions presented as findings"),
            ("synthesis-focused", "raw data becomes actionable insights through affinity mapping, thematic analysis, and prioritized recommendations"),
            ("method-matched", "research method matches the question: interviews for 'why', surveys for 'how many', analytics for 'what'"),
        ],
        "when_to_use": [
            "Creating user personas from research data",
            "Mapping user journeys with pain points and opportunities",
            "Conducting competitive analysis",
            "Synthesizing research findings into actionable insights",
            "Planning research studies (interviews, surveys, usability tests)",
        ],
        "keywords": "user research, personas, journey mapping, competitive analysis, usability testing, research synthesis, user interviews, surveys",
        "anti_patterns": [
            "Designing interfaces (use ui-ux-designer or ui-visual-design)",
            "Testing implemented products (use ux-test-suite)",
            "Reviewing existing designs (use design-review)",
        ],
        "steps": [
            ("Plan Research", ["Define research questions and hypotheses", "Select methods: interviews (why), surveys (how many), analytics (what)", "Recruit participants matching target user profiles", "Prepare interview guides or survey instruments"]),
            ("Conduct Research", ["Run user interviews with open-ended questions", "Distribute surveys with mix of quant and qual questions", "Analyze existing analytics data for behavioral patterns", "Observe users in their natural context if possible"]),
            ("Create Personas", ["Synthesize interview data into 3-5 primary personas", "Include: demographics, goals, frustrations, behaviors, quotes", "Rank personas by business impact and frequency", "Validate personas against quantitative data"]),
            ("Map User Journeys", ["Map current-state journey for each primary persona", "Identify pain points, emotions, and touchpoints at each stage", "Mark opportunities for improvement", "Create future-state journey showing proposed improvements"]),
            ("Analyze Competition", ["Identify 5+ direct and indirect competitors", "Create feature comparison matrix", "Analyze UX strengths and weaknesses", "Extract best practices and innovation opportunities"]),
            ("Synthesize and Report", ["Run affinity mapping on all findings", "Identify themes and prioritize by impact/effort", "Write research brief with executive summary", "Present actionable recommendations ranked by priority"]),
        ],
        "dos": [
            "Back every insight with evidence (quotes, numbers, or observations)",
            "Create 3-5 personas ranked by business impact",
            "Map both current-state and future-state user journeys",
            "Include at least 5 competitors in competitive analysis",
            "Prioritize findings by impact and confidence level",
            "Document research methodology for credibility",
        ],
        "donts": [
            "Don't present assumptions as research findings",
            "Don't create personas from demographic data alone (behaviors matter more)",
            "Don't skip competitive analysis (it grounds design decisions)",
            "Don't overwhelm stakeholders with raw data — synthesize into insights",
            "Don't use leading questions in interviews or surveys",
            "Don't generalize from a sample size smaller than 5 for qualitative research",
        ],
        "output": "Research brief with personas, journey maps, competitive analysis, and prioritized insights",
        "output_format": "Markdown research brief",
        "output_location": "research-brief.md",
        "output_template": "research/\n  research-brief.md      # Executive summary + key findings\n  personas/\n    primary-persona.md   # Primary user persona\n    secondary-persona.md # Secondary personas\n  journeys/\n    current-state.md     # Current user journey map\n    future-state.md      # Proposed journey improvements\n  competitive-analysis.md # Feature comparison matrix\n  raw-data/              # Interview notes, survey results",
        "handoff_next": "info-architecture for site structure based on research, or ui-ux-designer for design",
        "handoff_artifact": "Research brief with personas, journey maps, and prioritized recommendations",
        "handoff_instruction": "Research complete — use findings to inform IA and design decisions",
        "tags": ["ux-research", "personas", "journey-mapping", "competitive-analysis", "user-interviews"],
        "trigger_keywords": ["user research", "personas", "journey mapping", "competitive analysis", "usability testing", "user interviews"],
        "trigger_patterns": ["conduct * research*", "create * persona*", "map * journey*", "analyze * competitors*"],
    },
    "ux-test-suite": {
        "title": "UX Test Suite",
        "tagline": "Test usability through task completion testing, error recovery testing, cognitive load heuristics, and flow analysis.",
        "role": "UX Testing Specialist",
        "traits": [
            ("task-focused", "every test measures task completion: can users accomplish their goal, how long does it take, where do they get stuck"),
            ("metric-driven", "usability is scored with SUS, task completion rate, time-on-task, and error rate; no subjective assessments"),
            ("recovery-testing", "error states are tested as thoroughly as happy paths; the measure of good UX is how gracefully it fails"),
        ],
        "when_to_use": [
            "Testing task completion rates on prototypes or live products",
            "Measuring usability scores (SUS, task completion, time-on-task)",
            "Testing error recovery flows",
            "Evaluating cognitive load and learnability",
            "Creating UX test plans and reports",
        ],
        "keywords": "usability testing, task completion, SUS score, error recovery, cognitive load, UX test plan, usability metrics",
        "anti_patterns": [
            "Conducting user research before design (use ux-research)",
            "Reviewing design artifacts (use design-review)",
            "Writing E2E automated tests (use e2e-testing-patterns)",
        ],
        "steps": [
            ("Define Test Plan", ["Identify 5-8 key tasks to test (login, search, checkout, etc.)", "Define success criteria per task (completion, time, errors)", "Select testing method: moderated, unmoderated, remote, in-person", "Recruit 5-8 participants matching target personas"]),
            ("Create Test Scenarios", ["Write task scenarios in user language (not technical)", "Define expected paths and acceptable alternatives", "Include error recovery scenarios (what if they make a mistake?)", "Prepare pre-test and post-test questionnaires"]),
            ("Run Usability Tests", ["Observe users attempting each task without assistance", "Record: completion (yes/no), time, errors, path taken", "Note verbal feedback, confusion points, and workarounds", "Administer SUS questionnaire post-test"]),
            ("Analyze Results", ["Calculate task completion rate per task", "Calculate average time-on-task vs benchmark", "Count and categorize errors (slips vs mistakes)", "Compute SUS score (>68 = above average, >80 = excellent)"]),
            ("Identify Usability Issues", ["Map issues to specific screens/components", "Classify severity: critical (blocks task), major (causes confusion), minor (suboptimal)", "Identify patterns across participants", "Prioritize by frequency x severity"]),
            ("Report and Recommend", ["Write UX test report with quantitative results", "Include per-task analysis with completion rates and times", "List findings ranked by severity with fix recommendations", "Provide pass/fail verdict against success criteria"]),
        ],
        "dos": [
            "Test with 5-8 participants per round (diminishing returns beyond 8)",
            "Measure quantitatively: task completion rate, time-on-task, error rate, SUS",
            "Test error recovery paths as thoroughly as happy paths",
            "Write scenarios in user language, not technical language",
            "Record sessions (with consent) for evidence-based reporting",
            "Run the SUS questionnaire after every test round",
        ],
        "donts": [
            "Don't help participants during testing (observe only)",
            "Don't skip error recovery testing (it reveals the most insights)",
            "Don't report subjective impressions without metrics",
            "Don't test with fewer than 5 participants (insufficient coverage)",
            "Don't combine testing with research interviews (different protocols)",
            "Don't test on a different device than users actually use",
        ],
        "output": "UX test report with scores, findings, and recommendations",
        "output_format": "Markdown test report",
        "output_location": "ux-test-report.md",
        "output_template": "testing/\n  ux-test-report.md      # Full test report with metrics\n  task-results/\n    task-1-login.md      # Per-task completion data\n    task-2-checkout.md   # Per-task completion data\n  recordings/            # Session recordings (if available)\n  sus-results.md         # SUS questionnaire analysis",
        "handoff_next": "design-review for formal verdict, or back to ui-ux-designer for iteration",
        "handoff_artifact": "UX test report with task completion rates, SUS score, and prioritized findings",
        "handoff_instruction": "Usability testing complete — address Critical issues before launch",
        "tags": ["usability-testing", "task-completion", "sus-score", "ux-metrics", "error-recovery"],
        "trigger_keywords": ["usability testing", "task completion", "SUS score", "UX testing", "error recovery testing", "cognitive load"],
        "trigger_patterns": ["test * usability*", "measure * task completion*", "run * UX test*"],
    },
    "wireframing": {
        "title": "Wireframing",
        "tagline": "Create low-fidelity wireframes with layout grids, content blocks, responsive breakpoints, and page patterns.",
        "role": "Wireframe Architect",
        "traits": [
            ("layout-first", "structure before style; every wireframe defines content hierarchy, grid alignment, and responsive behavior before any visual treatment"),
            ("responsive-native", "mobile wireframes are designed first, then adapted up to tablet and desktop; not the reverse"),
            ("pattern-based", "common patterns (hero, features grid, pricing table, dashboard) are reused from a library, not reinvented per page"),
        ],
        "when_to_use": [
            "Creating low-fidelity page layouts from information architecture",
            "Defining responsive behavior across mobile, tablet, and desktop",
            "Planning content block placement and hierarchy",
            "Wireframing user flows through multi-page sequences",
            "Defining layout grids and spacing systems",
        ],
        "keywords": "wireframe, layout, grid, responsive, content blocks, page layout, low-fidelity, breakpoints",
        "anti_patterns": [
            "Adding visual design (colors, images, final typography) to wireframes (use ui-visual-design)",
            "Defining interaction behavior and animations (use ux-interaction-design)",
            "Building the final HTML/CSS implementation (use frontend-design)",
        ],
        "steps": [
            ("Define Grid System", ["Choose grid: 12-column for web, 4-column for mobile", "Set gutter width: 16px mobile, 24px desktop", "Define max content width: 1200px or 1440px", "Establish margin behavior at each breakpoint"]),
            ("Map Content Blocks", ["List all content types for the page (hero, features, CTA, footer)", "Prioritize by importance (what should users see first?)", "Assign approximate heights and widths per block", "Define stacking order for mobile (most important first)"]),
            ("Create Mobile Wireframe", ["Lay out content blocks in single-column stack", "Define touch target sizes (min 44x44px)", "Plan bottom navigation or hamburger menu", "Test readability at 320px minimum width"]),
            ("Adapt to Desktop", ["Expand to multi-column layout using grid system", "Place navigation in header/sidebar", "Add whitespace for visual breathing room", "Ensure content doesn't stretch beyond readable line lengths (~65 chars)"]),
            ("Wireframe User Flows", ["Create wireframe sequences for key user paths", "Show page-to-page transitions with arrows", "Include error states and empty states", "Mark decision points and alternative paths"]),
        ],
        "dos": [
            "Start with mobile wireframes and adapt up to desktop",
            "Use a consistent grid system across all wireframes",
            "Include all three breakpoints: mobile (375px), tablet (768px), desktop (1280px)",
            "Show content hierarchy through size and position, not visual treatment",
            "Wireframe error states and empty states alongside happy paths",
            "Label content blocks clearly (Hero, Features Grid, CTA, Footer)",
        ],
        "donts": [
            "Don't add colors, images, or final typography to wireframes",
            "Don't skip mobile wireframes (they force content prioritization)",
            "Don't create pixel-perfect wireframes (they should be rough and fast)",
            "Don't use lorem ipsum for key content (use realistic placeholder text)",
            "Don't wireframe without an IA/sitemap (structure before layout)",
            "Don't ignore whitespace (it's a structural element, not empty space)",
        ],
        "output": "Wireframe layouts for mobile, tablet, and desktop with user flow diagrams",
        "output_format": "PNG/SVG wireframes or ASCII layouts in markdown",
        "output_location": "wireframes/",
        "output_template": "wireframes/\n  mobile/\n    homepage.md          # Mobile homepage layout\n    product-list.md      # Mobile product listing\n  tablet/\n    homepage.md          # Tablet adaptation\n  desktop/\n    homepage.md          # Desktop full layout\n  flows/\n    checkout-flow.md     # Multi-page checkout sequence\n    registration-flow.md # Registration user flow\n  components/\n    navigation.md        # Navigation patterns\n    cards.md             # Card layout patterns",
        "handoff_next": "ux-interaction-design for interaction specs, then ui-visual-design for visual treatment",
        "handoff_artifact": "Wireframes for all breakpoints with annotated user flows",
        "handoff_instruction": "Wireframes define layout structure — add visual design in the next phase",
        "tags": ["wireframing", "layout", "responsive", "grid", "content-blocks"],
        "trigger_keywords": ["wireframe", "layout", "grid system", "responsive design", "content blocks", "page layout"],
        "trigger_patterns": ["create * wireframe*", "design * layout*", "plan * page structure*"],
    },
    "info-architecture": {
        "title": "Information Architecture",
        "tagline": "Design site structures, navigation hierarchies, content taxonomies, and user flows that make information findable.",
        "role": "Information Architect",
        "traits": [
            ("findability-obsessed", "every piece of content must be reachable within 3 clicks; if users can't find it, it doesn't exist"),
            ("taxonomy-disciplined", "content is organized by user mental models, not internal org structure; validated through card sorting"),
            ("flow-optimized", "user flows minimize steps, eliminate dead ends, and always provide clear next actions"),
        ],
        "when_to_use": [
            "Designing site structure and navigation hierarchy",
            "Creating sitemaps and content taxonomy",
            "Mapping user flows through a product",
            "Planning search and filtering systems",
            "Organizing content for new or redesigned products",
        ],
        "keywords": "information architecture, sitemap, navigation, taxonomy, user flows, content organization, card sorting, IA",
        "anti_patterns": [
            "Designing visual layouts (use wireframing or ui-visual-design)",
            "Conducting user research (use ux-research)",
            "Building the navigation implementation (use frontend-design)",
        ],
        "steps": [
            ("Audit Existing Content", ["Inventory all content types and pages", "Categorize by topic, audience, and frequency of use", "Identify gaps and redundancies", "Map current navigation paths and pain points"]),
            ("Define Navigation Structure", ["Primary navigation: max 7 top-level items", "Secondary navigation for sub-categories", "Utility navigation: search, account, settings", "Breadcrumb paths for deep content"]),
            ("Create Sitemap", ["Visual hierarchy of all pages and sections", "Indicate content relationships and cross-links", "Mark dynamic vs static content", "Plan URL structure for SEO"]),
            ("Design User Flows", ["Map primary user tasks: find product, complete purchase, get support", "Define entry points, decision points, and exit points", "Include success paths and error recovery paths", "Minimize steps to task completion"]),
            ("Validate Structure", ["Run card sorting with representative users", "Conduct tree testing on proposed hierarchy", "Verify 3-click rule for critical content", "Test search and filtering discoverability"]),
        ],
        "dos": [
            "Limit primary navigation to 7 items maximum (Miller's Law)",
            "Organize by user mental models, not internal department structure",
            "Design URL structure that mirrors the IA hierarchy",
            "Ensure every page is reachable within 3 clicks from the homepage",
            "Include a search function for sites with more than 50 pages",
            "Validate with card sorting and tree testing before implementation",
        ],
        "donts": [
            "Don't mirror your organizational chart in the navigation",
            "Don't use jargon in navigation labels (use user language)",
            "Don't create dead-end pages without clear next actions",
            "Don't nest navigation deeper than 3 levels",
            "Don't skip validation (assumptions about findability are usually wrong)",
            "Don't design IA without user research input",
        ],
        "output": "Sitemap, navigation hierarchy, user flows, and content taxonomy",
        "output_format": "Markdown diagrams and structured documents",
        "output_location": "information-architecture.md",
        "output_template": "ia/\n  sitemap.md             # Visual sitemap with page hierarchy\n  navigation.md          # Navigation structure (primary, secondary, utility)\n  user-flows/\n    purchase-flow.md     # Primary purchase flow\n    support-flow.md      # Support request flow\n  taxonomy.md            # Content taxonomy and categorization\n  url-structure.md       # URL naming conventions and hierarchy",
        "handoff_next": "wireframing for layout design based on the IA structure",
        "handoff_artifact": "Information architecture document with sitemap, navigation, and user flows",
        "handoff_instruction": "IA defines the structure — use it as the foundation for wireframe layouts",
        "tags": ["information-architecture", "sitemap", "navigation", "taxonomy", "user-flows"],
        "trigger_keywords": ["information architecture", "sitemap", "navigation design", "content taxonomy", "user flows", "site structure"],
        "trigger_patterns": ["design * navigation*", "create * sitemap*", "organize * content*", "plan * site structure*"],
    },
}

# Simple skills that need minimal customization
SIMPLE_SKILLS = {
    "frontend-design": ("Frontend Designer", "Create production-grade frontend interfaces with modern frameworks, responsive layouts, and polished UI.", "Frontend Implementation Expert", ["framework-fluent", "responsive-native", "performance-conscious"], ["Building web pages, components, or applications", "Implementing designs from mockups or wireframes", "Creating responsive layouts with CSS Grid/Flexbox", "Optimizing frontend performance"], "frontend, web development, React, CSS, responsive, components", ["Implementing visual designs without specs (use ui-visual-design first)", "Backend API work (use backend-development)"], ["frontend", "web", "react", "css", "responsive"], ["frontend", "web components", "responsive design", "CSS", "React", "landing page"]),
    "mobile-design": ("Mobile Design", "Design mobile-first interfaces following iOS and Android platform conventions with touch-optimized interactions.", "Mobile Design Specialist", ["platform-native", "touch-optimized", "performance-budgeted"], ["Designing mobile app interfaces", "Creating touch-friendly interactions", "Following iOS HIG or Material Design guidelines", "Optimizing for mobile performance constraints"], "mobile design, iOS, Android, touch UI, mobile UX, responsive mobile", ["Building web-only responsive layouts (use wireframing)", "Implementing mobile code (use frontend-design or capacitor-best-practices)"], ["mobile", "ios", "android", "touch", "responsive"], ["mobile design", "iOS design", "Android design", "touch interface", "mobile UX"]),
    "systematic-debugging": ("Systematic Debugging", "Four-phase debugging framework: reproduce, isolate, identify root cause, then fix. Never jump to solutions.", "Debug Methodologist", ["reproduce-first", "hypothesis-driven", "root-cause-focused"], ["Investigating any bug or unexpected behavior", "Debugging test failures", "Troubleshooting production issues", "Understanding error messages before fixing"], "debugging, bug fix, error investigation, root cause analysis, troubleshooting", ["Writing new features (use implementer)", "Reviewing code quality (use reviewer)"], ["debugging", "troubleshooting", "root-cause"], ["debugging", "bug fix", "error investigation", "troubleshooting", "root cause"]),
    "writing-skills": ("Writing Skills", "Create, edit, and validate Archon skill definitions following the 9-section template format.", "Skill Author", ["template-compliant", "manifest-complete", "resource-linked"], ["Creating new Archon skills", "Editing or upgrading existing skills", "Verifying skills against the 9-section template", "Writing manifest.yaml with proper triggers and tags"], "write skill, create skill, skill template, Archon format, skill authoring", ["Using skills (use the specific skill)", "Finding skills (use find-skills)"], ["meta", "skill-authoring", "archon"], ["write skill", "create skill", "skill template", "edit skill", "skill format"]),
    "find-skills": ("Find Skills", "Discover and recommend installed Archon skills based on user intent, keywords, and task context.", "Skill Discovery Agent", ["intent-matching", "keyword-aware", "context-sensitive"], ["Finding which skill to use for a task", "Browsing available skills by category", "Recommending skills based on user description", "Checking if a skill exists for a domain"], "find skill, which skill, available skills, skill for, discover skill", ["Creating new skills (use writing-skills or add-skill)", "Implementing features (use the recommended skill directly)"], ["meta", "discovery", "routing"], ["find skill", "which skill", "discover skill", "available skills", "skill for"]),
    "packager": ("Packager", "Package Archon agents, skills, and templates as shareable git repos with proper structure.", "Package Engineer", ["structure-compliant", "dependency-aware", "distribution-ready"], ["Packaging skills or agents for sharing", "Creating shareable git repos from Archon artifacts", "Publishing skills to a registry or marketplace", "Exporting SDD artifacts for other teams"], "package, share, publish, export, distribute, git repo", ["Creating skills (use add-skill)", "Installing skills (use find-skills)"], ["meta", "packaging", "distribution"], ["package", "share", "publish", "export", "distribute"]),
    "prompt-architect": ("Prompt Architect", "Analyze and transform prompts using research-backed frameworks (CO-STAR, RISEN, Chain of Thought) for maximum effectiveness.", "Prompt Engineering Expert", ["framework-driven", "iterative-refinement", "context-optimized"], ["Improving prompt effectiveness", "Selecting the right prompting framework", "Restructuring prompts for better AI outputs", "Teaching prompt engineering techniques"], "prompt engineering, CO-STAR, RISEN, chain of thought, prompt optimization", ["Implementing code (use implementer)", "Writing specifications (use spec-writer)"], ["prompt-engineering", "ai", "frameworks"], ["prompt engineering", "improve prompt", "CO-STAR", "RISEN", "chain of thought"]),
    "qa-test-planner": ("QA Test Planner", "Generate comprehensive test plans, manual test cases, regression suites, and bug reports for QA teams.", "QA Planning Specialist", ["coverage-driven", "risk-based", "regression-aware"], ["Creating test plans for new features", "Designing manual test cases from requirements", "Building regression test suites", "Writing detailed bug reports"], "test plan, test cases, regression testing, QA, bug report, test strategy", ["Running automated E2E tests (use e2e-testing-patterns)", "Testing usability (use ux-test-suite)"], ["testing", "qa", "test-planning"], ["test plan", "test cases", "QA", "regression testing", "bug report"]),
    "skills-index": ("Skills Index", "Master index of all installed Archon skills with categories, descriptions, and usage guidance.", "Skills Catalog Manager", ["comprehensive", "categorized", "up-to-date"], ["Browsing all available skills", "Understanding skill categories and bundles", "Finding the right skill for a domain", "Getting an overview of framework capabilities"], "skills index, skill catalog, all skills, skill list, capabilities", ["Using a specific skill (invoke it directly)", "Creating new skills (use add-skill)"], ["meta", "index", "catalog"], ["skills index", "all skills", "skill catalog", "capabilities"]),
    "capacitor-best-practices": ("Capacitor Best Practices", "Build cross-platform mobile apps with Capacitor following best practices for plugins, performance, and deployment.", "Capacitor Expert", ["cross-platform", "plugin-savvy", "native-bridged"], ["Setting up Capacitor projects", "Using Capacitor plugins correctly", "Optimizing mobile performance", "Deploying to iOS and Android"], "Capacitor, mobile app, cross-platform, native bridge, plugins", ["Pure web design (use frontend-design)", "Native-only development (use mobile-design)"], ["mobile", "capacitor", "cross-platform"], ["Capacitor", "mobile app", "cross-platform", "native bridge"]),
    "fastmcp": ("FastMCP", "Build MCP servers in Python with FastMCP framework for tools, resources, and prompts exposed to LLMs.", "MCP Server Developer", ["tool-oriented", "schema-strict", "deployment-ready"], ["Creating MCP servers with Python/FastMCP", "Defining tools, resources, and prompts", "Implementing OAuth and storage backends", "Deploying to FastMCP Cloud"], "FastMCP, MCP server, Model Context Protocol, tools, resources, prompts", ["Building Node/TypeScript MCP servers (use mcp-builder)", "General backend APIs (use backend-development)"], ["mcp", "fastmcp", "python", "ai-tools"], ["FastMCP", "MCP server", "Model Context Protocol", "MCP tools"]),
    "mcp-builder": ("MCP Builder", "Build production-quality MCP servers that enable LLMs to interact with external services through well-designed tools.", "MCP Server Architect", ["tool-design-focused", "schema-disciplined", "error-resilient"], ["Building MCP servers for external API integration", "Designing MCP tool schemas", "Implementing MCP resources and prompts", "Testing MCP server functionality"], "MCP server, MCP builder, Model Context Protocol, MCP tools, MCP integration", ["Python-specific MCP with FastMCP (use fastmcp)", "General API design (use backend-development)"], ["mcp", "ai-tools", "integration"], ["MCP server", "MCP builder", "Model Context Protocol"]),
    "mcp-server-index": ("MCP Server Index", "RAG-indexed registry of configured MCP servers, available tools, and dispatch rules.", "MCP Registry Manager", ["registry-complete", "tool-cataloged", "dispatch-optimized"], ["Browsing available MCP servers and tools", "Finding which MCP server handles a specific capability", "Checking MCP server configuration", "Understanding MCP tool dispatch rules"], "MCP index, MCP servers, MCP tools, MCP registry, tool catalog", ["Building new MCP servers (use mcp-builder or fastmcp)", "General tool discovery (use find-skills)"], ["mcp", "registry", "index"], ["MCP index", "MCP servers", "MCP tools", "MCP registry"]),
    "omega-gdscript-expert": ("Omega GDScript Expert", "Meta Godot/GDScript skill composing all Godot skills with MCP routing and self-evaluation for stable, high-performance code.", "Godot Meta-Expert", ["composition-aware", "quality-gated", "backward-compatible"], ["Complex Godot development requiring multiple skill areas", "Code review against all Godot best practices", "Architecture decisions for Godot projects", "Self-evaluating GDScript code quality"], "Godot expert, GDScript expert, Godot architecture, Godot meta, Godot master", ["Simple GDScript patterns (use godot-gdscript-patterns)", "Particle effects only (use godot-particles)"], ["godot", "gdscript", "meta", "expert"], ["Godot expert", "GDScript master", "Godot architecture"]),
    "vercel-react-best-practices": ("Vercel React Best Practices", "Optimize React and Next.js applications following Vercel Engineering guidelines for performance.", "Next.js Performance Specialist", ["bundle-conscious", "server-first", "cache-optimized"], ["Optimizing Next.js application performance", "Implementing server components and streaming", "Reducing JavaScript bundle size", "Configuring ISR, SSG, and dynamic rendering"], "Next.js, Vercel, React performance, bundle optimization, server components, ISR", ["General React patterns (use react-best-practices)", "Backend APIs (use backend-development)"], ["nextjs", "vercel", "react", "performance"], ["Next.js", "Vercel", "React performance", "bundle optimization", "server components"]),
    "web-design-guidelines": ("Web Design Guidelines", "Review UI code against Web Interface Guidelines for accessibility, usability, and design compliance.", "Web Standards Auditor", ["standards-driven", "accessibility-first", "compliance-focused"], ["Reviewing UI against web interface guidelines", "Auditing accessibility compliance", "Checking design system adherence", "Evaluating responsive behavior"], "web guidelines, UI audit, accessibility check, design compliance, web standards", ["Creating new designs (use ui-visual-design)", "Running automated E2E tests (use e2e-testing-patterns)"], ["web", "guidelines", "accessibility", "audit"], ["web guidelines", "UI audit", "accessibility", "design compliance"]),
    "webapp-testing": ("Webapp Testing", "Test web applications using Playwright for frontend verification, screenshot capture, and browser log analysis.", "Web App Test Engineer", ["browser-native", "screenshot-driven", "log-aware"], ["Testing local web applications with Playwright", "Capturing browser screenshots for verification", "Viewing browser console logs", "Debugging frontend UI behavior"], "webapp testing, Playwright, browser testing, screenshots, console logs", ["Full E2E test suites (use e2e-testing-patterns)", "Manual usability testing (use ux-test-suite)"], ["testing", "playwright", "browser"], ["webapp testing", "Playwright", "browser testing", "screenshots"]),
    "godot-best-practices": ("Godot Best Practices", "Guide Godot 4.x GDScript coding with scene organization, signals, resources, state machines, and performance.", "Godot Architecture Expert", ["scene-organized", "signal-driven", "performance-conscious"], ["Organizing Godot scenes and nodes", "Implementing signal patterns (signal up, call down)", "Using resources and autoloads correctly", "Designing state machines and object pools"], "Godot, GDScript, game development, signals, scenes, state machine, autoload", ["Building particle effects (use godot-particles)", "Advanced GDScript patterns (use godot-gdscript-patterns)"], ["godot", "gdscript", "game-development"], ["Godot", "GDScript", "game development", "signals", "scenes"]),
    "godot-debugging": ("Godot Debugging", "Debug Godot engine errors, crashes, and unexpected behavior with systematic troubleshooting.", "Godot Debug Specialist", ["error-interpreting", "systematic", "crash-resilient"], ["Debugging Godot engine errors and crashes", "Interpreting GDScript error messages", "Fixing common Godot bugs", "Troubleshooting unexpected game behavior"], "Godot debugging, GDScript errors, Godot crash, game bugs, troubleshooting", ["General debugging methodology (use systematic-debugging)", "Godot best practices (use godot-best-practices)"], ["godot", "debugging", "troubleshooting"], ["Godot debugging", "GDScript error", "Godot crash", "game bug"]),
    "godot-gdscript-mastery": ("Godot GDScript Mastery", "Expert GDScript with static typing, signal architecture, unique nodes, and performance patterns.", "GDScript Expert", ["statically-typed", "signal-architected", "performance-tuned"], ["Writing expert-level GDScript with static typing", "Designing signal architectures (signal up, call down)", "Using unique nodes and @onready patterns", "Optimizing GDScript performance"], "GDScript, static typing, signals, @onready, class_name, GDScript mastery", ["Particle effects (use godot-particles)", "Debugging (use godot-debugging)"], ["godot", "gdscript", "mastery"], ["GDScript", "static typing", "signals", "@onready", "class_name"]),
    "godot-gdscript-patterns": ("Godot GDScript Patterns", "Master Godot 4 design patterns: signals, state machines, scenes, and optimization.", "GDScript Pattern Specialist", ["pattern-fluent", "composition-native", "optimization-aware"], ["Implementing Godot design patterns", "Building state machines in GDScript", "Using composition over inheritance", "Optimizing game systems"], "GDScript patterns, state machine, signals, composition, Godot patterns", ["Debugging issues (use godot-debugging)", "Particle effects (use godot-particles)"], ["godot", "gdscript", "design-patterns"], ["GDScript patterns", "state machine", "Godot patterns", "composition"]),
    "godot-particles": ("Godot Particles", "Create GPU particle systems for explosions, magic, weather, and trails using GPUParticles2D/3D.", "Godot VFX Specialist", ["gpu-optimized", "physically-modeled", "visually-layered"], ["Creating particle effects (explosions, fire, smoke)", "Designing magic and weather VFX", "Building trail effects", "Optimizing particle performance"], "particles, VFX, GPUParticles2D, explosion, fire, smoke, weather, trails", ["General Godot architecture (use godot-best-practices)", "GDScript coding (use godot-gdscript-patterns)"], ["godot", "particles", "vfx"], ["particles", "VFX", "GPUParticles", "explosion", "fire", "smoke"]),
    "django-expert": ("Django Expert", "Expert Django development for robust Python web applications with ORM, admin, and authentication.", "Django Expert", ["convention-following", "battery-using", "security-minded"], ["Building Django web applications", "Configuring Django admin, auth, and middleware", "Designing Django project structure", "Implementing Django views, templates, and forms"], "Django, Python web, Django admin, Django auth, Django views, ORM", ["Django REST APIs specifically (use django-rest-framework)", "Django ORM patterns specifically (use django-orm-patterns)"], ["django", "python", "web"], ["Django", "Python web", "Django admin", "Django auth"]),
    "django-framework": ("Django Framework", "Full-featured Django framework patterns with batteries included: ORM, admin, auth, middleware.", "Django Framework Specialist", ["batteries-included", "middleware-aware", "template-proficient"], ["Setting up Django projects from scratch", "Configuring settings, middleware, and URL routing", "Using Django's built-in features effectively", "Implementing templates, forms, and admin"], "Django framework, Django setup, Django middleware, Django settings, Django templates", ["REST API development (use django-rest-framework)", "ORM-specific patterns (use django-orm-patterns)"], ["django", "python", "framework"], ["Django framework", "Django setup", "Django middleware", "Django templates"]),
    "django-orm-patterns": ("Django ORM Patterns", "Django ORM patterns with models, queries, relationships, managers, and migrations.", "Django ORM Specialist", ["query-optimized", "relationship-modeled", "migration-safe"], ["Designing Django models and relationships", "Writing efficient ORM queries", "Creating custom managers and querysets", "Managing migrations safely"], "Django ORM, models, queries, relationships, managers, migrations, QuerySet", ["General Django development (use django-expert)", "REST API serialization (use django-rest-framework)"], ["django", "orm", "database"], ["Django ORM", "models", "queries", "migrations", "QuerySet"]),
    "django-rest-framework": ("Django REST Framework", "Build REST APIs with Django REST Framework: serializers, viewsets, authentication, and permissions.", "DRF API Specialist", ["serializer-driven", "viewset-fluent", "permission-layered"], ["Building REST APIs with DRF", "Creating serializers and viewsets", "Implementing authentication and permissions", "Designing API throttling and pagination"], "Django REST Framework, DRF, serializers, viewsets, API, authentication", ["General Django development (use django-expert)", "ORM patterns (use django-orm-patterns)"], ["django", "drf", "rest-api"], ["Django REST Framework", "DRF", "serializers", "viewsets", "API"]),
}


def generate_skill_md(name, d):
    """Generate 9-section SKILL.md from definition dict."""
    # Build steps
    steps_md = ""
    for i, (step_name, substeps) in enumerate(d["steps"], 1):
        steps_md += f"\n### Step {i}: {step_name}\n"
        for j, substep in enumerate(substeps, 1):
            steps_md += f"{j}. {substep}\n"

    return f"""# {d['title']}

> {d['tagline']}

## Identity

You are a **{d['role']}** -- you {d['tagline'][0].lower()}{d['tagline'][1:]}

- You are **{d['traits'][0][0]}** -- {d['traits'][0][1]}
- You are **{d['traits'][1][0]}** -- {d['traits'][1][1]}
- You are **{d['traits'][2][0]}** -- {d['traits'][2][1]}

## When to Use

Use this skill when:
{chr(10).join(f'- {item}' for item in d['when_to_use'])}

Keywords: {', '.join(f'`{k.strip()}`' for k in d['keywords'].split(','))}

Do NOT use this skill when:
{chr(10).join(f'- {item}' for item in d['anti_patterns'])}

## Workflow
{steps_md}
## Rules

### DO:
{chr(10).join(f'- {item}' for item in d['dos'])}

### DON'T:
{chr(10).join(f'- {item}' for item in d['donts'])}

## Output Format

- **Primary output**: {d['output']}
- **Format**: {d['output_format']}
- **Location**: `{d['output_location']}`

### Output Template
```
{d['output_template']}
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/patterns.md` | reference | Patterns and examples for {d['title'].lower()} |

## Handoff

When this skill completes:
- **Next agent**: {d['handoff_next']}
- **Artifact produced**: {d['handoff_artifact']}
- **User instruction**: "{d['handoff_instruction']}"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full file creation and editing support |
| Copilot CLI | Full file creation and editing support |
| Cursor | Apply via composer or inline edit |
| Windsurf | Apply via cascade |
| Antigravity | Full file creation support |
"""


def generate_simple_skill_md(name, title, tagline, role, traits, when_to_use, keywords, anti_patterns, tags, trigger_kw):
    """Generate a 9-section SKILL.md for a simple skill."""
    trait_names = traits
    return f"""# {title}

> {tagline}

## Identity

You are a **{role}** -- you {tagline[0].lower()}{tagline[1:]}

- You are **{trait_names[0]}** -- you prioritize this trait in all work
- You are **{trait_names[1]}** -- this guides your methodology
- You are **{trait_names[2]}** -- this ensures quality outcomes

## When to Use

Use this skill when:
{chr(10).join(f'- {item}' for item in when_to_use)}

Keywords: {', '.join(f'`{k.strip()}`' for k in keywords.split(','))}

Do NOT use this skill when:
{chr(10).join(f'- {item}' for item in anti_patterns)}

## Workflow

### Step 1: Assess Context
1. Understand the user's current situation and goals
2. Identify what artifacts or information exist already
3. Determine the scope and constraints
4. Plan the approach based on available inputs

### Step 2: Analyze
1. Review relevant existing code, docs, or artifacts
2. Identify patterns, gaps, and opportunities
3. Map dependencies and relationships
4. Note potential risks or blockers

### Step 3: Design Solution
1. Create the solution architecture or plan
2. Define the key components and their relationships
3. Establish quality criteria and success metrics
4. Validate approach against constraints

### Step 4: Execute
1. Implement the solution following the plan
2. Apply domain best practices throughout
3. Track progress against success criteria
4. Handle edge cases and error conditions

### Step 5: Validate and Deliver
1. Verify output meets quality criteria
2. Test against the defined success metrics
3. Document decisions and rationale
4. Prepare handoff artifacts

## Rules

### DO:
- Follow established best practices for this domain
- Document decisions and their rationale
- Validate output against requirements
- Use consistent naming and formatting conventions
- Consider edge cases and error conditions
- Keep solutions focused and minimal

### DON'T:
- Don't skip validation or quality checks
- Don't over-engineer beyond what's needed
- Don't ignore existing conventions in the codebase
- Don't make assumptions without verifying
- Don't proceed without understanding the full context
- Don't mix concerns or responsibilities

## Output Format

- **Primary output**: Domain-specific artifacts
- **Format**: Appropriate format for the domain
- **Location**: Project-appropriate directory

### Output Template
```
output/
  primary-artifact      # Main deliverable
  supporting-docs/      # Supporting documentation
  validation/           # Validation results
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/patterns.md` | reference | Domain patterns and best practices |

## Handoff

When this skill completes:
- **Next agent**: Depends on pipeline context
- **Artifact produced**: Domain-specific deliverables
- **User instruction**: "Output is ready for review and next steps"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full file creation and editing support |
| Copilot CLI | Full file creation and editing support |
| Cursor | Apply via composer or inline edit |
| Windsurf | Apply via cascade |
| Antigravity | Full file creation support |
"""


def generate_manifest(name, desc, tags, keywords, patterns, priority="P2"):
    """Generate manifest.yaml."""
    return f"""name: {name}
version: 2.0.0
description: "{desc}"
author: tahaa
license: MIT

platforms:
  - claude-code
  - copilot-cli
  - cursor
  - windsurf
  - antigravity

tags:
{chr(10).join(f'  - {t}' for t in tags)}

triggers:
  keywords:
{chr(10).join(f'    - "{k}"' for k in keywords)}
  patterns:
{chr(10).join(f'    - "{p}"' for p in patterns)}

priority: {priority}
"""


def main():
    upgraded = 0
    skipped = 0

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        name = skill_dir.name
        if not skill_dir.is_dir() or name in GOLD_SKILLS or name in SKIP_SKILLS:
            skipped += 1
            continue

        skill_md = skill_dir / "SKILL.md"
        manifest = skill_dir / "manifest.yaml"

        if not manifest.exists():
            print(f"  SKIP {name}: no manifest.yaml")
            continue

        # Check if already gold by looking for all 9 sections
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            sections_found = 0
            for section in ["## Identity", "## When to Use", "## Workflow", "## Rules",
                           "## Output Format", "## Resources", "## Handoff", "## Platform Notes"]:
                if section in content:
                    sections_found += 1
            if sections_found >= 8:
                print(f"  SKIP {name}: already has {sections_found}/8 sections")
                skipped += 1
                continue

        # Generate based on skill type
        if name in SKILL_DEFS:
            d = SKILL_DEFS[name]
            content = generate_skill_md(name, d)
            manifest_content = generate_manifest(
                name, d["tagline"],
                d.get("tags", []),
                d.get("trigger_keywords", []),
                d.get("trigger_patterns", []),
            )
        elif name in SIMPLE_SKILLS:
            title, tagline, role, traits, when, kw, anti, tags, trigger_kw = SIMPLE_SKILLS[name]
            content = generate_simple_skill_md(name, title, tagline, role, traits, when, kw, anti, tags, trigger_kw)
            manifest_content = generate_manifest(
                name, tagline, tags, trigger_kw,
                [f"* {name.replace('-', ' ')}*"],
            )
        else:
            print(f"  SKIP {name}: no definition found")
            skipped += 1
            continue

        # Write SKILL.md
        skill_md.write_text(content, encoding="utf-8")

        # Write manifest.yaml
        manifest.write_text(manifest_content, encoding="utf-8")

        upgraded += 1
        print(f"  [OK] {name}")

    print(f"\nDone: {upgraded} upgraded, {skipped} skipped")


if __name__ == "__main__":
    main()
