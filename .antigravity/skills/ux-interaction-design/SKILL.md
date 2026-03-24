---
name: ux-interaction-design
description: UX interaction design patterns including micro-interactions, UI state machines, transition specifications, form UX, animation principles, and feedback patterns. Use when designing interactions, defining component states, or specifying animations.
---

# UX Interaction Design Skill

## Micro-Interaction Patterns

### Trigger → Rules → Feedback → Loop/Mode Model

**Trigger** (Initiates the interaction):
- **User-Initiated**: Click, tap, hover, scroll, gesture, keyboard input
- **System-Initiated**: Data loading, error state, time-based, location-based
- **Data-Initiated**: New notification, content update, sync completion

**Rules** (Logic that governs the interaction):
- **Conditions**: When does this happen? (on hover, after 3 seconds, when form valid)
- **Constraints**: What are the limits? (only once per session, mobile only)
- **Variables**: What changes? (color, position, size, opacity)

**Feedback** (Response to the trigger):
- **Visual**: Color change, animation, icon appearance, size change
- **Haptic**: Vibration patterns, tactile response (mobile/watch)
- **Audio**: Sound effects, voice feedback, notification sounds
- **Textual**: Status messages, error text, confirmation copy

**Loop/Mode** (Duration and repetition):
- **One-time**: Button click confirmation, form submission success
- **Looping**: Loading spinner, progress animations, breathing effects
- **Mode Change**: Toggle states, view switching, permanent state changes

### Common Micro-Interaction Examples

**Button Interactions**:
```
Trigger: User hovers over button
Rules: If button is enabled and not in loading state
Feedback: Background color shifts from #0066CC to #0052A3, 200ms ease-out
Loop: Reverses on mouse leave
```

**Toggle Switch**:
```
Trigger: User clicks toggle
Rules: Switch between ON/OFF states
Feedback: 
  - Circle slides left/right (300ms ease-in-out)
  - Background color changes (#CCC → #00AA00)
  - Haptic feedback on mobile (light impact)
Loop: None (maintains new state)
```

**Input Field Focus**:
```
Trigger: User clicks in text field
Rules: Field must be enabled and visible
Feedback:
  - Border color changes from #CCC to #0066CC
  - Label animates up and scales down (200ms ease-out)
  - Cursor appears with blinking animation
Loop: Maintains focus state until blur
```

**Card Hover (Desktop)**:
```
Trigger: Mouse enters card area
Rules: Only on desktop/hover-capable devices
Feedback:
  - Card elevates with shadow (transform: translateY(-4px))
  - Shadow increases (box-shadow: 0 8px 24px rgba(0,0,0,0.15))
  - Transition duration: 250ms ease-out
Loop: Reverses on mouse leave
```

**Notification Toast**:
```
Trigger: System event (success, error, info)
Rules: Maximum 3 visible at once, auto-dismiss after 5 seconds
Feedback:
  - Slide in from top-right (transform: translateX(100%) → translateX(0))
  - Success: green background, checkmark icon
  - Error: red background, X icon
Loop: Auto-dismiss with fade-out after timeout
```

## UI State Machines

### State Enumeration

**Standard Component States**:
- **Default**: Initial appearance, ready for interaction
- **Hover**: Mouse over (desktop only), indicates interactivity
- **Focus**: Keyboard navigation target, accessibility highlight
- **Active**: Currently being pressed/clicked
- **Disabled**: Non-interactive, reduced opacity/contrast
- **Loading**: Processing state, often with spinner/skeleton
- **Error**: Invalid input or system error, red indicators
- **Empty**: No content available, placeholder messaging
- **Success**: Positive outcome confirmation, green indicators

### Transition Table Format

| Current State | Trigger | Next State | Action |
|---------------|---------|------------|--------|
| Default | Mouse Enter | Hover | Apply hover styles |
| Hover | Mouse Leave | Default | Remove hover styles |
| Default | Click/Tap | Active | Apply active styles |
| Active | Release | Default | Execute action, remove active styles |
| Default | Focus (keyboard) | Focus | Apply focus ring/outline |
| Focus | Blur | Default | Remove focus styles |
| Default | Disabled prop | Disabled | Apply disabled styles, prevent interactions |
| Disabled | Enabled prop | Default | Remove disabled styles, restore interactions |
| Any | Loading trigger | Loading | Show loading indicator, disable interactions |
| Loading | Success response | Success | Show success feedback, return to default after delay |
| Loading | Error response | Error | Show error message, return to default or error state |
| Error | Retry/Fix | Default | Clear error, restore normal state |

### Component State Matrix Template

**Button Component States**:

| State | Visual Appearance | Cursor | Interactions Enabled | Accessibility |
|-------|------------------|--------|---------------------|---------------|
| Default | Normal colors, no effects | pointer | ✓ Click, Focus | Focusable, screen reader accessible |
| Hover | Darker background, subtle lift | pointer | ✓ Click, Focus | Focusable, screen reader accessible |
| Focus | Focus ring/outline visible | pointer | ✓ Click, Space/Enter | Focused element, announced by screen reader |
| Active | Pressed appearance, darker | pointer | ✓ (during press) | Active state announced |
| Disabled | Reduced opacity, muted colors | not-allowed | ✗ No interactions | Not focusable, aria-disabled="true" |
| Loading | Spinner replaces text | default | ✗ No interactions | aria-live="polite" for status updates |

**Input Field Component States**:

| State | Visual Appearance | Border/Outline | Label Position | Helper Text |
|-------|------------------|----------------|----------------|-------------|
| Default | Normal border, placeholder visible | #CCC border | Placeholder in field | Helper text below |
| Focus | Highlight border, label animated up | #0066CC border, focus ring | Above field, smaller size | Helper text visible |
| Filled | Content visible, label remains up | #CCC border | Above field, smaller size | Helper text below |
| Error | Red border, error icon | #CC0000 border | Above field | Error message in red |
| Disabled | Grayed out, no interactions | #DDD border | Grayed placeholder | Helper text grayed |
| Success | Green border, success icon | #00AA00 border | Above field | Success message in green |

## Transition Specifications

### Page Transitions

**Fade Transition**:
```css
.page-enter { opacity: 0; }
.page-enter-active { 
  opacity: 1; 
  transition: opacity 300ms ease-out;
}
.page-exit { opacity: 1; }
.page-exit-active { 
  opacity: 0; 
  transition: opacity 200ms ease-in;
}
```
- **When to Use**: Modal overlays, tab content, subtle page changes
- **Duration**: 200-400ms
- **Easing**: Ease-out for entry, ease-in for exit

**Slide Transition**:
```css
.page-enter { transform: translateX(100%); }
.page-enter-active { 
  transform: translateX(0%); 
  transition: transform 400ms ease-out;
}
.page-exit { transform: translateX(0%); }
.page-exit-active { 
  transform: translateX(-100%); 
  transition: transform 350ms ease-in;
}
```
- **When to Use**: Navigation between pages, mobile app screens
- **Direction**: Left for forward, right for back
- **Duration**: 300-500ms

**Zoom/Scale Transition**:
```css
.modal-enter { 
  opacity: 0; 
  transform: scale(0.8); 
}
.modal-enter-active { 
  opacity: 1; 
  transform: scale(1); 
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}
```
- **When to Use**: Modal dialogs, image lightboxes, popup content
- **Scale Range**: 0.8 to 1.0 typically
- **Combined**: Often paired with opacity

**Morphing Transition**:
```css
.card-to-detail { 
  transition: all 400ms cubic-bezier(0.4, 0.0, 0.2, 1);
}
```
- **When to Use**: Card expanding to detail view, shared element transitions
- **Complex**: Requires careful coordinate mapping
- **Duration**: 400-600ms for complex morphs

### Trigger Types

**Navigation Triggers**:
- Link clicks, browser back/forward
- Menu item selection, tab switching
- Breadcrumb navigation, pagination

**Action Triggers**:
- Form submission, button press
- File upload, data save operation
- User-initiated state changes

**System Triggers**:
- Page load completion, data refresh
- Error states, timeout events
- Automatic content updates

### Direction Conventions

**Forward Navigation** (Slide Left):
```
Current Page →[      New Page]
[Exits Left] ←      [Enters from Right]
```

**Back Navigation** (Slide Right):
```
[Previous Page]←     Current Page
[Enters from Left]   [Exits Right]→
```

**Modal/Overlay** (Fade/Zoom Up):
```
Background Page (dims)
    ↗️ Modal (scales up from center)
```

**Hierarchical Down** (Slide Up):
```
Parent Level
    ↑
Child Level (slides up from bottom)
```

### Duration Ranges

**Micro (100-200ms)**:
- Button hover states
- Input field focus
- Simple color changes
- Icon state changes

**Standard (200-400ms)**:
- Page transitions
- Modal appearance/disappearance
- Menu open/close
- Tab switching

**Complex (400-700ms)**:
- Morphing animations
- Multi-step transitions
- Complex page layouts
- Shared element transitions

**Extended (700ms+)**:
- Loading sequences
- Onboarding animations
- Celebration/success moments
- Tutorial or guided flows

## Form UX Best Practices

### Inline Validation

**Validate on Blur (not on keypress)**:
```javascript
// Good
inputField.addEventListener('blur', validateField);

// Bad - too aggressive
inputField.addEventListener('keyup', validateField);
```

**Validation Timing**:
- **Required Fields**: Validate when user leaves field (blur)
- **Format Validation**: Email, phone - validate on blur
- **Availability**: Username, email - debounced check after typing stops
- **Password Strength**: Real-time feedback as user types
- **Confirmation Fields**: Real-time comparison (password confirm, email confirm)

### Error Message Placement and Styling

**Placement Rules**:
```html
<div class="field-group">
  <label for="email">Email Address</label>
  <input id="email" type="email" class="error">
  <div class="error-message">Please enter a valid email address</div>
</div>
```

**Visual Treatment**:
- **Color**: Red (#CC0000 or similar) for errors
- **Border**: Red border on invalid fields
- **Icon**: Error icon (X, warning triangle) 
- **Position**: Directly below the field
- **Animation**: Slide down or fade in (200ms)

**Error Message Content**:
- **Specific**: "Email address is required" not "This field is required"
- **Actionable**: "Password must be at least 8 characters" 
- **Positive**: "Enter your email address" rather than "Invalid email"
- **Immediate**: Show as soon as error is detected

### Success Indication

**Visual Feedback**:
```css
.field-success {
  border-color: #00AA00;
}
.field-success::after {
  content: "✓";
  color: #00AA00;
  position: absolute;
  right: 12px;
}
```

**Success States**:
- **Field Level**: Green checkmark, green border
- **Form Level**: Success message at top after submission
- **Progressive**: Show success as each section completes

### Multi-Step Form Progress

**Step Indicator Types**:

**Linear Progress Bar**:
```
Step 1 → Step 2 → Step 3 → Step 4
█████████░░░░░░░░░░░░░░░░░░░░░ 30%
```

**Dot Navigation**:
```
● ○ ○ ○   Step 1 of 4
```

**Numbered Steps**:
```
① ────── ② ────── ③ ────── ④
Account  Payment  Confirm  Complete
```

**Progress Implementation**:
- **Always show**: Current step and total steps
- **Clickable**: Allow jumping to previous completed steps
- **Visual State**: Completed, current, upcoming
- **Mobile**: Use horizontal scrolling for many steps

### Keyboard Navigation

**Tab Order Logic**:
1. Form fields in logical order (top to bottom, left to right)
2. Primary action button (Submit)
3. Secondary actions (Cancel, Back)
4. Help links or additional options

**Enter Key Behavior**:
```javascript
// Form submission
form.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target.type !== 'textarea') {
    form.submit();
  }
});
```

**Escape Key Behavior**:
- **Modals**: Close modal and return focus
- **Dropdowns**: Close dropdown, maintain field focus
- **Forms**: Cancel current operation (with confirmation)

### Auto-focus Rules

**When to Auto-focus**:
- First field in a form (especially single-purpose forms)
- Search fields when search is primary action
- Modal forms when modal opens
- Error fields after validation failure

**When NOT to Auto-focus**:
- Long forms where user might be scrolling
- Mobile devices (can cause keyboard issues)
- When there are multiple equally important actions
- Accessibility concerns (screen reader disruption)

### Input Masking

**Phone Number Masking**:
```
User Types: 1234567890
Displayed: (123) 456-7890
```

**Credit Card Masking**:
```
User Types: 4111111111111111
Displayed: 4111 1111 1111 1111
```

**Date Input Masking**:
```
User Types: 01152024
Displayed: 01/15/2024
```

**Implementation Principles**:
- **Progressive**: Apply formatting as user types
- **Flexible**: Accept different input formats
- **Clear**: Show formatting hints in placeholder
- **Deletable**: Allow easy correction/deletion

## Animation Principles

### Easing Functions

**Ease-out (Deceleration Curve)**:
```css
transition-timing-function: cubic-bezier(0.0, 0.0, 0.2, 1);
```
- **Use for**: Elements entering the screen, appearing
- **Feel**: Energetic start, gentle finish
- **Examples**: Modal opening, dropdown appearing, page loads

**Ease-in (Acceleration Curve)**:
```css
transition-timing-function: cubic-bezier(0.4, 0.0, 1, 1);
```
- **Use for**: Elements leaving the screen, disappearing
- **Feel**: Gentle start, rapid finish
- **Examples**: Modal closing, pages exiting, elements hiding

**Ease-in-out (Symmetrical)**:
```css
transition-timing-function: cubic-bezier(0.4, 0.0, 0.2, 1);
```
- **Use for**: State changes, position changes, size changes
- **Feel**: Smooth acceleration and deceleration
- **Examples**: Hover states, focus changes, content transitions

**Linear (No easing)**:
```css
transition-timing-function: linear;
```
- **Use for**: Continuous animations, progress indicators
- **Feel**: Mechanical, consistent speed
- **Examples**: Loading bars, scrolling text, rotating spinners

### Purpose-Driven Animation

**Orient** (Help users understand spatial relationships):
```css
/* Slide-in from source direction */
.notification-enter {
  transform: translateY(-100%);
  animation: slideInFromTop 300ms ease-out;
}
```
- **Examples**: Notifications from top, drawers from side
- **Purpose**: Show where content comes from/goes to

**Focus** (Draw attention to important elements):
```css
/* Subtle bounce to draw attention */
.error-shake {
  animation: shake 400ms ease-in-out;
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
```
- **Examples**: Error states, new notifications, CTAs
- **Purpose**: Guide user attention without being distracting

**Express** (Convey emotion or personality):
```css
/* Playful bounce for success */
.success-bounce {
  animation: bounce 600ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```
- **Examples**: Success celebrations, playful interactions
- **Purpose**: Reinforce brand personality, emotional feedback

**Connect** (Show relationships between elements):
```css
/* Morphing transition shows connection */
.card-to-modal {
  transition: all 400ms cubic-bezier(0.4, 0.0, 0.2, 1);
  transform-origin: center;
}
```
- **Examples**: Expanding cards, shared element transitions
- **Purpose**: Maintain user context during transitions

### Motion Design Tokens

**Duration Tokens**:
```css
:root {
  --duration-instant: 100ms;    /* Immediate feedback */
  --duration-fast: 200ms;       /* Quick transitions */
  --duration-normal: 300ms;     /* Standard transitions */
  --duration-slow: 500ms;       /* Complex animations */
  --duration-extended: 700ms;   /* Special moments */
}
```

**Easing Tokens**:
```css
:root {
  --easing-standard: cubic-bezier(0.4, 0.0, 0.2, 1);      /* General purpose */
  --easing-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);    /* Elements entering */
  --easing-accelerate: cubic-bezier(0.4, 0.0, 1, 1);      /* Elements exiting */
  --easing-sharp: cubic-bezier(0.4, 0.0, 0.6, 1);         /* Quick, decisive */
  --easing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Playful */
}
```

**Usage Examples**:
```css
.button {
  transition: 
    background-color var(--duration-fast) var(--easing-standard),
    transform var(--duration-fast) var(--easing-standard);
}

.modal-enter {
  animation: modalEnter var(--duration-normal) var(--easing-decelerate);
}

.notification-exit {
  animation: slideOut var(--duration-fast) var(--easing-accelerate);
}
```

## Feedback Patterns

### Loading States

**Skeleton Screens (Preferred)**:
```html
<div class="skeleton-card">
  <div class="skeleton-image"></div>
  <div class="skeleton-text skeleton-text-title"></div>
  <div class="skeleton-text"></div>
  <div class="skeleton-text skeleton-text-short"></div>
</div>
```
- **When to Use**: Content with predictable layout structure
- **Benefits**: Maintains layout, feels faster, reduces perceived wait time
- **Implementation**: Gray blocks that shimmer or pulse

**Spinners (Fallback)**:
```css
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #0066CC;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```
- **When to Use**: Unknown content structure, simple operations
- **Placement**: Center of loading area or inline with trigger

**Progress Bars (For Known Duration)**:
```html
<div class="progress-container">
  <div class="progress-bar" style="width: 65%"></div>
  <span class="progress-text">Uploading... 65%</span>
</div>
```
- **When to Use**: File uploads, multi-step processes, known durations
- **Include**: Percentage or time remaining when possible

### Empty States

**Empty State Structure**:
```html
<div class="empty-state">
  <div class="empty-illustration">
    <!-- Friendly illustration or icon -->
  </div>
  <h3 class="empty-title">No items found</h3>
  <p class="empty-description">
    You haven't created any projects yet. Get started by creating your first project.
  </p>
  <button class="empty-cta">Create Project</button>
</div>
```

**Empty State Types**:

**First-use Empty State**:
- **Message**: Welcome and guide users to take action
- **CTA**: Primary action to populate the area
- **Tone**: Encouraging, helpful

**User-cleared Empty State**:
- **Message**: Acknowledge user action, offer way back
- **CTA**: Undo action or start fresh
- **Tone**: Neutral, matter-of-fact

**Error Empty State**:
- **Message**: Explain what went wrong, how to fix
- **CTA**: Retry action or alternative
- **Tone**: Helpful, not blaming

### Error States

**Inline Errors**:
```html
<div class="field-error">
  <input class="input-error" type="email" value="invalid-email">
  <div class="error-message">
    <icon class="error-icon">⚠️</icon>
    Please enter a valid email address
  </div>
</div>
```
- **When to Use**: Form validation, field-specific issues
- **Placement**: Directly below the problematic field

**Toast Notifications**:
```html
<div class="toast toast-error">
  <icon class="toast-icon">❌</icon>
  <div class="toast-content">
    <div class="toast-title">Upload failed</div>
    <div class="toast-message">The file is too large. Please try a smaller file.</div>
  </div>
  <button class="toast-dismiss">×</button>
</div>
```
- **When to Use**: System errors, operation failures, network issues
- **Auto-dismiss**: After 5-7 seconds, but allow manual dismiss

**Full-page Errors**:
```html
<div class="error-page">
  <div class="error-illustration">🚫</div>
  <h1 class="error-title">Something went wrong</h1>
  <p class="error-description">
    We're having trouble loading this page. Please try refreshing or come back later.
  </p>
  <button class="error-cta">Try Again</button>
  <a href="/" class="error-link">Go Home</a>
</div>
```
- **When to Use**: Critical failures, network outages, 404/500 errors
- **Include**: Recovery options, contact information

### Success States

**Subtle Confirmation**:
```css
.input-success {
  border-color: #00AA00;
  background-image: url('checkmark-icon.svg');
  background-position: right 12px center;
  background-repeat: no-repeat;
}
```
- **When to Use**: Form field validation, auto-save confirmations
- **Visual**: Green accent, checkmark icon

**Celebration Moments**:
```css
.success-celebration {
  animation: celebrationBounce 800ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes celebrationBounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}
```
- **When to Use**: Major accomplishments, first-time user achievements
- **Elements**: Animation, confetti, congratulatory messaging

## Accessibility Interaction Requirements

### Keyboard Navigation

**Tab Order Standards**:
```html
<!-- Good tab order -->
<form>
  <input tabindex="1" type="text" name="firstName">
  <input tabindex="2" type="text" name="lastName">
  <input tabindex="3" type="email" name="email">
  <button tabindex="4" type="submit">Submit</button>
  <button tabindex="5" type="button">Cancel</button>
</form>
```

**Skip Links**:
```html
<a href="#main-content" class="skip-link">Skip to main content</a>
<a href="#navigation" class="skip-link">Skip to navigation</a>
```

**Keyboard Shortcuts**:
- **Tab**: Move to next focusable element
- **Shift + Tab**: Move to previous focusable element
- **Enter/Space**: Activate buttons and links
- **Arrow keys**: Navigate within components (menus, tabs)
- **Escape**: Close modals, dropdowns, cancel operations

### Focus Management

**Focus Ring Styles**:
```css
:focus {
  outline: 2px solid #005FCC;
  outline-offset: 2px;
}

/* Custom focus styles */
.button:focus {
  box-shadow: 0 0 0 3px rgba(0, 95, 204, 0.3);
  outline: none;
}
```

**Focus Trapping (Modals)**:
```javascript
// Trap focus within modal
const modal = document.querySelector('.modal');
const focusableElements = modal.querySelectorAll('button, input, select, textarea, a[href]');
const firstElement = focusableElements[0];
const lastElement = focusableElements[focusableElements.length - 1];

modal.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault();
      lastElement.focus();
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault();
      firstElement.focus();
    }
  }
});
```

### ARIA Patterns for Custom Components

**Toggle Button**:
```html
<button 
  aria-pressed="false" 
  onclick="toggleState(this)"
>
  Dark Mode
</button>
```

**Expandable Content**:
```html
<button 
  aria-expanded="false" 
  aria-controls="content-panel"
  onclick="togglePanel()"
>
  Show Details
</button>
<div id="content-panel" aria-hidden="true">
  <!-- Content -->
</div>
```

**Live Regions**:
```html
<div aria-live="polite" id="status-message"></div>
<div aria-live="assertive" id="error-message"></div>
```

### Prefers-Reduced-Motion Handling

**Respect User Preferences**:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Alternative: Provide simpler animations */
@media (prefers-reduced-motion: reduce) {
  .fancy-animation {
    animation: none;
  }
  
  .simple-fade {
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  
  .simple-fade.active {
    opacity: 1;
  }
}
```

### Screen Reader Announcements

**Dynamic Content Updates**:
```javascript
function announceToScreenReader(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.style.position = 'absolute';
  announcement.style.left = '-10000px';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// Usage
announceToScreenReader('Form saved successfully');
announceToScreenReader('3 new notifications');
```

---

## Component State Matrix Template

### [Component Name] State Matrix

| State | Visual Treatment | Cursor | Keyboard | Screen Reader | Interactions |
|-------|-----------------|--------|----------|---------------|--------------|
| Default | [Normal appearance] | pointer | Focusable | [SR description] | [Available actions] |
| Hover | [Hover styling] | pointer | Focusable | [SR description] | [Available actions] |
| Focus | [Focus ring/outline] | pointer | Focused | [SR announcement] | [Keyboard actions] |
| Active | [Active/pressed look] | pointer | [Key behavior] | [SR feedback] | [During interaction] |
| Disabled | [Disabled styling] | not-allowed | Not focusable | [Disabled state] | None |
| Loading | [Loading indicator] | default | [Focus behavior] | [Loading announcement] | Limited/None |
| Error | [Error styling] | pointer | Focusable | [Error description] | [Recovery actions] |
| Success | [Success styling] | pointer | Focusable | [Success announcement] | [Next actions] |

---

## UX Specification Output Template

### Component Interaction Specification

**Component**: [Component Name]
**Version**: [Version Number]
**Last Updated**: [Date]

#### Overview
Brief description of component purpose and primary user interactions.

#### States and Transitions

**State Machine Diagram**:
```
[Default] ──hover──> [Hover] ──click──> [Active] ──release──> [Default]
    │                                        │
    └────focus───> [Focus] <─────────────────┘
```

**Detailed State Specifications**:

##### Default State
- **Appearance**: [Visual description]
- **Behavior**: [Available interactions]
- **Triggers to other states**: [List triggers]

##### [Additional states...]

#### Micro-interactions

**[Interaction Name]**:
- **Trigger**: [What initiates this interaction]
- **Rules**: [Logic and conditions]
- **Feedback**: [Visual, auditory, haptic response]
- **Loop/Mode**: [Duration and repetition behavior]
- **Code Example**:
```css
[CSS implementation]
```

#### Animation Specifications

**[Animation Name]**:
- **Duration**: [Time in milliseconds]
- **Easing**: [Easing function]
- **Properties**: [What animates]
- **Trigger**: [When it occurs]
- **Implementation**:
```css
[CSS animation/transition code]
```

#### Accessibility Requirements

**Keyboard Navigation**:
- **Focus Management**: [How focus moves]
- **Keyboard Shortcuts**: [Supported keys and behaviors]
- **Tab Order**: [Position in tab sequence]

**Screen Reader Support**:
- **ARIA Labels**: [Required aria attributes]
- **State Announcements**: [What gets announced when]
- **Dynamic Updates**: [How changes are communicated]

**Reduced Motion**: [Alternative behavior for users who prefer reduced motion]

#### Responsive Behavior

**Mobile (≤480px)**:
- [Mobile-specific interactions]

**Tablet (481-1024px)**:
- [Tablet adaptations]

**Desktop (≥1025px)**:
- [Desktop interactions]

#### Error Handling

**Error States**:
- [How errors are displayed]
- [Recovery mechanisms]
- [User feedback]

**Edge Cases**:
- [Unusual scenarios and handling]

#### Performance Considerations

**Animation Performance**:
- [GPU acceleration notes]
- [Performance optimizations]

**Accessibility Performance**:
- [Reduced motion handling]
- [Focus management efficiency]

#### Testing Checklist

- [ ] All states visually correct
- [ ] Transitions smooth and appropriate duration
- [ ] Keyboard navigation works
- [ ] Screen reader announces correctly
- [ ] Reduced motion preference respected
- [ ] Touch targets appropriate size (44px minimum)
- [ ] Hover states don't activate on touch devices
- [ ] Focus management works in all scenarios
- [ ] Error states provide clear feedback
- [ ] Loading states prevent double-submission