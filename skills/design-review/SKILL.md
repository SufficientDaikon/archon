---
name: design-review
description: Design critique and review methodology including heuristic evaluation, consistency checking, accessibility compliance, and visual quality assessment. Use when reviewing design artifacts, evaluating UI quality, or auditing design compliance.
---

# Design Review & Critique Methodology

## Heuristic Evaluation Framework

### Nielsen's 10 Heuristics Adapted for Design Artifacts

#### 1. Visibility of System Status
**Description**: Users should always know what's happening through appropriate feedback
**What to check**: 
- Loading states for async operations
- Progress indicators for multi-step processes
- Active states for navigation and tabs
- Form validation feedback
- Success/error message placement
**Common violations**: 
- Missing loading spinners
- No progress indication during uploads
- Unclear active navigation state
- Form errors appear after submit only
**Severity weighting**: Critical (3x) if affects core functionality

#### 2. Match Between System and Real World
**Description**: Use familiar conventions, language, and mental models
**What to check**:
- Icon meanings are universally understood
- Language matches target audience vocabulary
- Information hierarchy follows expected patterns
- Interaction patterns match platform conventions
**Common violations**:
- Abstract icons without labels
- Technical jargon for general audiences
- Unconventional navigation patterns
- Platform-inconsistent interaction models
**Severity weighting**: Standard (1x) unless affects core comprehension

#### 3. User Control and Freedom
**Description**: Provide easy ways to undo actions and navigate freely
**What to check**:
- Undo/redo functionality where appropriate
- Cancel buttons in dialogs and flows
- Back navigation always available
- Escape routes from error states
**Common violations**:
- No way to cancel multi-step processes
- Destructive actions without confirmation
- Dead-end pages without navigation
- Modal dialogs without close buttons
**Severity weighting**: Critical (3x) for destructive actions

#### 4. Consistency and Standards
**Description**: Follow established conventions and maintain internal consistency
**What to check**:
- UI component consistency across pages
- Color usage follows semantic patterns
- Typography hierarchy is consistent
- Interaction patterns are standardized
**Common violations**:
- Same component styled differently
- Primary buttons using different colors
- Inconsistent spacing between sections
- Mixed interaction patterns for similar actions
**Severity weighting**: Standard (1x) but accumulates quickly

#### 5. Error Prevention
**Description**: Design to prevent errors before they occur
**What to check**:
- Form validation prevents invalid input
- Dangerous actions require confirmation
- Clear constraints and limitations
- Smart defaults reduce user errors
**Common violations**:
- No input validation until form submit
- Destructive actions too easy to trigger
- Unclear field requirements
- Poor default values
**Severity weighting**: Critical (3x) if prevents task completion

#### 6. Recognition Rather Than Recall
**Description**: Make objects, actions, and options visible and recognizable
**What to check**:
- Important information remains visible
- Navigation shows current location
- Previous inputs are remembered
- Clear labels and descriptions
**Common violations**:
- Important info hidden behind tooltips
- No breadcrumbs in deep navigation
- Forms clear all data on error
- Unlabeled icons and buttons
**Severity weighting**: Standard (1x) unless critical workflow

#### 7. Flexibility and Efficiency of Use
**Description**: Accommodate both novice and expert users
**What to check**:
- Keyboard shortcuts for power users
- Customizable interfaces where beneficial
- Progressive disclosure of advanced features
- Multiple ways to accomplish tasks
**Common violations**:
- No keyboard navigation support
- All complexity shown at once
- Single path to accomplish goals
- No personalization options
**Severity weighting**: Standard (1x) for basic accessibility

#### 8. Aesthetic and Minimalist Design
**Description**: Remove unnecessary elements and focus on essential content
**What to check**:
- Information hierarchy is clear
- Visual noise is minimized
- Every element serves a purpose
- Whitespace is used effectively
**Common violations**:
- Cluttered interfaces with competing elements
- Poor visual hierarchy
- Decorative elements distract from content
- Insufficient whitespace creates cramped feeling
**Severity weighting**: Standard (1x) unless severely impacts usability

#### 9. Help Users Recognize, Diagnose, and Recover from Errors
**Description**: Error messages should be helpful and actionable
**What to check**:
- Error messages explain what went wrong
- Clear instructions for fixing errors
- Errors appear near the problem area
- Visual indicators help locate issues
**Common violations**:
- Generic "Something went wrong" messages
- Error messages at top of long forms
- No suggestions for fixing problems
- Errors in technical language users don't understand
**Severity weighting**: Critical (3x) if prevents error recovery

#### 10. Help and Documentation
**Description**: Provide contextual help and clear documentation
**What to check**:
- Help content is contextual and searchable
- Documentation matches current interface
- Examples and tutorials are provided
- Contact/support options are available
**Common violations**:
- Help content is outdated
- No contextual help for complex features
- Examples don't match real use cases
- No clear way to get additional support
**Severity weighting**: Standard (1x) unless critical features lack explanation

## Cognitive Walkthrough Method

A cognitive walkthrough evaluates a design by simulating a user's thought process at each step of a task. For each step, answer four questions:

### The Four Questions (Per Step)

1. **Will the user try to achieve the right effect?**
   - Does the user's goal match what this step accomplishes?
   - Is the correct action obvious given the user's current goal?

2. **Will the user notice that the correct action is available?**
   - Is the button/link/control visible and discoverable?
   - Does it look interactive? Is it in the expected location?

3. **Will the user associate the correct action with the desired effect?**
   - Does the label/icon clearly communicate what will happen?
   - Is there ambiguity between this action and similar actions?

4. **If the correct action is performed, will the user see progress?**
   - Does the system provide feedback (visual, textual, state change)?
   - Can the user tell they are closer to their goal?

### Running a Cognitive Walkthrough

1. **Define the persona**: Select a user persona from the Research Brief
2. **Define the task**: Select a key user flow from the IA Document
3. **Walk each step**: For every screen/interaction in the flow, answer the four questions
4. **Log failures**: Any "no" answer is a usability finding — record the step, the question that failed, the severity, and a suggested fix
5. **Prioritize findings**: Critical (blocks task completion) > Major (causes confusion/delay) > Minor (suboptimal but task completable)

### When to Use Cognitive Walkthrough

- **Phase 3 (Wireframes)**: Walk key flows through wireframe layouts
- **Phase 4 (UX Design)**: Walk flows including interaction states and feedback
- **Phase 5 (UI Design)**: Walk flows with full visual context
- **Phase 7 (UX Testing)**: Walk flows in the implemented product

## Consistency Checking Methodology

### Cross-Artifact Consistency

**Information Architecture ↔ Wireframes**:
- Navigation structure matches IA sitemap
- Content hierarchy reflects IA organization
- User flows align with planned paths
- Content types match IA specifications

**Wireframes ↔ UI Design**:
- Layout structure is preserved
- Content blocks maintain relative sizing
- Interactive elements are properly styled
- Navigation patterns remain consistent

**UI Design ↔ Code Implementation**:
- Visual design matches pixel-perfect where specified
- Interaction states are implemented
- Typography scales and spacing are accurate
- Color values match design tokens exactly

### Intra-Artifact Consistency

**Component-Level Consistency**:
- Same component styled identically across all instances
- State variations (hover, active, disabled) consistently applied
- Interactive patterns standardized across similar components
- Icon usage follows established meanings

**Pattern-Level Consistency**:
- Form layouts follow same structure
- Error handling uses same visual treatment
- Success states use consistent feedback patterns
- Navigation behaves predictably across sections

### Token Consistency

**Color Token Usage**:
- All colors come from established token system
- Semantic color usage follows defined rules (error=red, success=green)
- Brand colors used consistently for same purposes
- No hardcoded hex values outside token system

**Typography Token Usage**:
- Text sizes come from defined scale
- Font weights match token specifications
- Line heights follow system ratios
- Letter spacing uses token values

**Spacing Token Usage**:
- All padding/margin uses spacing scale
- Component internal spacing is standardized
- Section spacing follows consistent patterns
- No arbitrary pixel values outside token system

### Naming Consistency

**Component Naming**:
- BEM methodology followed consistently
- Component names descriptive and intuitive
- Variant names follow logical patterns
- State names match interaction patterns

**Asset Naming**:
- File names follow established conventions
- Image assets use descriptive names
- Icon names match component references
- Export names maintain consistency

## Accessibility Compliance Criteria

### WCAG 2.1 AA Checklist by Category

#### Perceivable

**1.1 Text Alternatives**:
- [ ] All images have descriptive alt text
- [ ] Decorative images have empty alt attributes
- [ ] Icons have accessible labels
- [ ] Charts/graphs have text descriptions

**1.2 Time-based Media**:
- [ ] Videos have captions
- [ ] Audio content has transcripts
- [ ] Auto-playing media can be paused

**1.3 Adaptable**:
- [ ] Content structure uses semantic HTML
- [ ] Information doesn't rely solely on visual characteristics
- [ ] Reading order is logical without CSS
- [ ] Form labels are properly associated

**1.4 Distinguishable**:
- [ ] Color contrast meets 4.5:1 for normal text, 3:1 for large text
- [ ] Information isn't conveyed by color alone
- [ ] Text can be resized to 200% without horizontal scrolling
- [ ] Focus indicators are clearly visible

#### Operable

**2.1 Keyboard Accessible**:
- [ ] All functionality available via keyboard
- [ ] No keyboard traps
- [ ] Focus order is logical
- [ ] Keyboard shortcuts don't conflict

**2.2 Enough Time**:
- [ ] Time limits can be extended/disabled
- [ ] Auto-updating content can be paused
- [ ] Session timeouts have warnings

**2.3 Seizures and Physical Reactions**:
- [ ] No content flashes more than 3 times per second
- [ ] Motion-triggered functionality can be disabled

**2.4 Navigable**:
- [ ] Skip navigation links provided
- [ ] Page titles are descriptive
- [ ] Focus order is meaningful
- [ ] Link purposes are clear from context

**2.5 Input Modalities**:
- [ ] Pointer gestures have keyboard alternatives
- [ ] Motion actuation has alternatives
- [ ] Touch targets are at least 44x44px

#### Understandable

**3.1 Readable**:
- [ ] Language of page is identified
- [ ] Language of parts is identified
- [ ] Unusual words are defined

**3.2 Predictable**:
- [ ] Navigation is consistent across pages
- [ ] Identification is consistent across pages
- [ ] Context changes only occur on user request

**3.3 Input Assistance**:
- [ ] Form errors are clearly identified
- [ ] Labels and instructions are provided
- [ ] Error suggestions are given when possible

#### Robust

**4.1 Compatible**:
- [ ] HTML is valid
- [ ] Name, role, value are programmatically determined
- [ ] Status messages are programmatically announced

## Visual Quality Assessment Rubric

### Scoring Criteria (Total: 100 points)

#### Visual Hierarchy (20 points)
**Excellent (18-20 points)**:
- Clear information hierarchy with 3+ distinct levels
- Size, color, and spacing create obvious importance ranking
- Eye flow follows intended path naturally
- Key actions and content immediately identifiable

**Good (14-17 points)**:
- Generally clear hierarchy with some minor issues
- Most important elements are emphasized appropriately
- Occasional competing elements for attention
- Overall flow is logical with minor disruptions

**Needs Improvement (10-13 points)**:
- Inconsistent hierarchy treatment
- Some important elements lack emphasis
- Multiple elements competing for primary attention
- User has to work to understand importance

**Poor (0-9 points)**:
- No clear hierarchy visible
- All elements appear equally important
- Information is difficult to scan and prioritize
- User cannot quickly identify key content/actions

#### Typography (15 points)
**Excellent (14-15 points)**:
- Consistent type scale used throughout
- Perfect font pairing (if multiple fonts)
- Appropriate line heights and spacing
- Text is highly readable at all sizes

**Good (11-13 points)**:
- Generally consistent typography
- Minor scale inconsistencies
- Mostly appropriate spacing
- Good readability with occasional issues

**Needs Improvement (8-10 points)**:
- Inconsistent type sizes and spacing
- Poor font combinations
- Some readability issues
- No clear typographic system

**Poor (0-7 points)**:
- No apparent type system
- Multiple inappropriate fonts mixed
- Poor readability throughout
- Inconsistent sizing and spacing

#### Color (15 points)
**Excellent (14-15 points)**:
- Cohesive color palette with clear system
- Proper contrast ratios throughout
- Semantic color usage is consistent
- Colors support hierarchy and branding

**Good (11-13 points)**:
- Generally good color choices
- Minor contrast issues
- Mostly consistent semantic usage
- Supports overall design goals

**Needs Improvement (8-10 points)**:
- Limited color system
- Some contrast failures
- Inconsistent color meanings
- Colors don't strongly support hierarchy

**Poor (0-7 points)**:
- No apparent color system
- Multiple contrast failures
- Confusing or inconsistent color usage
- Colors detract from usability

#### Spacing (15 points)
**Excellent (14-15 points)**:
- Consistent spacing system used throughout
- Perfect optical balance and rhythm
- Appropriate density for content type
- Effective use of whitespace

**Good (11-13 points)**:
- Generally consistent spacing
- Good overall balance
- Appropriate density with minor issues
- Effective whitespace usage

**Needs Improvement (8-10 points)**:
- Inconsistent spacing patterns
- Some areas feel cramped or too sparse
- No clear spacing system
- Poor whitespace utilization

**Poor (0-7 points)**:
- No spacing system apparent
- Inconsistent and awkward spacing
- Poor balance throughout
- Ineffective whitespace usage

#### Consistency (15 points)
**Excellent (14-15 points)**:
- Perfect consistency across all components
- Standardized patterns throughout
- No visual or functional inconsistencies
- Clear design system adherence

**Good (11-13 points)**:
- Generally consistent with minor variations
- Most components follow established patterns
- Few inconsistencies that don't impact usability
- Good system adherence

**Needs Improvement (8-10 points)**:
- Some notable inconsistencies
- Components vary more than appropriate
- Patterns not always followed
- Inconsistencies affect user experience

**Poor (0-7 points)**:
- Major inconsistencies throughout
- Components feel disconnected
- No apparent system or standards
- Inconsistencies severely impact usability

#### Accessibility (20 points)
**Excellent (18-20 points)**:
- Meets or exceeds all WCAG 2.1 AA requirements
- Perfect color contrast throughout
- Full keyboard navigation support
- Excellent semantic structure

**Good (14-17 points)**:
- Meets most WCAG 2.1 AA requirements
- Good color contrast with minor issues
- Generally good keyboard support
- Good semantic structure

**Needs Improvement (10-13 points)**:
- Meets some accessibility requirements
- Multiple contrast issues
- Limited keyboard support
- Poor semantic structure

**Poor (0-9 points)**:
- Fails most accessibility requirements
- Significant contrast failures
- No keyboard support
- No semantic structure consideration

## Phase-Specific Review Criteria

### Research Phase Review
- [ ] User personas are research-based, not assumed
- [ ] User journey maps identify pain points and opportunities
- [ ] Competitive analysis covers relevant competitors and features
- [ ] Research findings clearly inform design decisions
- [ ] Success metrics are defined and measurable
- [ ] User needs are prioritized based on evidence
- [ ] Business requirements align with user needs

### Information Architecture Review
- [ ] Site structure is logical and intuitive
- [ ] Navigation labels are clear and descriptive
- [ ] Content hierarchy supports user goals
- [ ] Taxonomy is consistent and scalable
- [ ] Search functionality is appropriate for content volume
- [ ] Information can be found within 3 clicks
- [ ] IA supports both browsing and searching behaviors

### Wireframe Review
- [ ] Layout supports content hierarchy effectively
- [ ] UI patterns are appropriate for functionality
- [ ] Interactive elements are clearly indicated
- [ ] Responsive behavior is considered at mobile/tablet/desktop
- [ ] Content blocks are appropriately sized
- [ ] Navigation patterns are consistent
- [ ] User flows are efficiently supported

### UX Review
- [ ] User flows are optimized for task completion
- [ ] Error states and edge cases are handled
- [ ] Micro-interactions enhance usability
- [ ] Form design follows best practices
- [ ] Progressive disclosure is used appropriately
- [ ] Accessibility considerations are integrated
- [ ] Performance implications are considered

### UI Design Review
- [ ] Visual design supports content hierarchy
- [ ] Brand guidelines are followed consistently
- [ ] Design system tokens are used correctly
- [ ] Interactive states are designed for all components
- [ ] Responsive design works across all breakpoints
- [ ] Color contrast meets accessibility standards
- [ ] Typography scale is applied consistently

### Frontend Implementation Review
- [ ] Design is implemented pixel-perfect where specified
- [ ] Interactive behaviors match design specifications
- [ ] Responsive breakpoints work smoothly
- [ ] Accessibility features are properly implemented
- [ ] Performance optimization is applied
- [ ] Code follows established conventions
- [ ] Browser compatibility is maintained

### Testing Review
- [ ] Usability testing identifies no critical issues
- [ ] Accessibility testing passes WCAG 2.1 AA
- [ ] Cross-browser testing shows consistent behavior
- [ ] Performance testing meets established benchmarks
- [ ] User feedback is incorporated appropriately
- [ ] Error scenarios are tested and handled properly
- [ ] Success metrics are being achieved

## Scoring Methodology

### Calculation Formula

**Total Criteria Count**: Sum of all applicable criteria per phase
**Weighted Score Calculation**: 
```
Score = (Critical Issues × 3 + Standard Issues × 1) / Total Possible Points × 100
```

**Verdict Thresholds**:
- **≥95% APPROVED**: Ready to proceed to next phase
- **85-94% APPROVED WITH CONDITIONS**: Proceed with minor fixes required
- **70-84% REVISION REQUIRED**: Significant changes needed before proceeding  
- **<70% REJECTED**: Major rework required, cannot proceed

### Critical vs Standard Issue Weighting

**Critical Issues (3x weight)**:
- Blocks core user tasks
- Creates accessibility barriers
- Violates fundamental usability principles
- Causes system errors or failures
- Significantly impacts business goals

**Standard Issues (1x weight)**:
- Reduces user experience quality
- Minor consistency issues
- Visual polish improvements
- Performance optimizations
- Enhancement opportunities

## Feedback Format Template

### Actionable Feedback Structure

**Finding ID**: DR-001
**Severity**: Critical | Standard
**Category**: Visual Hierarchy | Typography | Color | Spacing | Consistency | Accessibility | Usability
**Location**: Specific page/component/element
**What's Wrong**: Clear description of the issue
**Why It Matters**: Impact on user experience or business goals
**Expected Behavior**: What should happen instead
**Suggestion**: Specific, actionable recommendation for fixing the issue

### Example Feedback Entry

**Finding ID**: DR-023
**Severity**: Critical  
**Category**: Accessibility
**Location**: Contact form on /contact page
**What's Wrong**: Form error messages appear only at the top of the form when individual fields have validation errors
**Why It Matters**: Users with screen readers or cognitive disabilities cannot easily associate errors with specific fields, blocking form completion
**Expected Behavior**: Error messages should appear inline next to each problematic field AND be programmatically associated with the field
**Suggestion**: Add `aria-describedby` attributes linking fields to their error messages, and position error text immediately after each field label

### Feedback Summary Template

**Review Summary**: [Phase] Review for [Project Name]
**Overall Score**: [X/100] - [VERDICT]
**Total Issues Found**: [X Critical, X Standard]
**Must Fix Before Proceeding**: [List critical issues]
**Recommended Improvements**: [List standard issues]
**Estimated Fix Time**: [Hours/days based on issue complexity]
**Next Steps**: [Specific actions required before re-review or phase progression]