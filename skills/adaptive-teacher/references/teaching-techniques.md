# Teaching Techniques & Interactive Elements Reference

Patterns for generating interactive learning artifacts — self-contained HTML files that teach concepts through visuals, quizzes, and interactive elements. Adapted from the codebase-to-course system with additions for adaptive difficulty.

## Table of Contents

1. [Artifact Structure](#artifact-structure)
2. [Adaptive Difficulty System](#adaptive-difficulty-system)
3. [Code ↔ Plain English Translation Blocks](#code--plain-english-translation-blocks)
4. [Reverse Prompt Pause Points](#reverse-prompt-pause-points)
5. [Scenario-Based Quizzes](#scenario-based-quizzes)
6. [Concept Animation Patterns](#concept-animation-patterns)
7. [Group Chat Animation](#group-chat-animation)
8. [Data Flow Animation](#data-flow-animation)
9. [Glossary Tooltip System](#glossary-tooltip-system)
10. [Metaphor Callout Boxes](#metaphor-callout-boxes)
11. [Progressive Disclosure Toggles](#progressive-disclosure-toggles)
12. [Confidence Check Cards](#confidence-check-cards)
13. [Teach-Back Challenge Blocks](#teach-back-challenge-blocks)
14. [Design System Tokens](#design-system-tokens)

---

## Artifact Structure

Every teaching artifact is a **single self-contained HTML file** with embedded CSS and JS. Only external dependency: Google Fonts.

### HTML Shell

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>[Topic] — Interactive Lesson</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=JetBrains+Mono:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <style>
      /* === DESIGN TOKENS === */
      :root {
        /* ... see Design System Tokens section ... */
      }
      /* === ALL CSS === */
    </style>
  </head>
  <body>
    <nav class="nav"><!-- Navigation + progress bar --></nav>

    <div class="level-indicator" id="level-indicator">
      <span class="level-badge"
        >Level: <span id="current-level">Explorer</span></span
      >
      <div class="level-controls">
        <button class="level-btn" onclick="adjustLevel(-1)" title="Make easier">
          🔽 Easier
        </button>
        <button class="level-btn" onclick="adjustLevel(1)" title="Make harder">
          🔼 Harder
        </button>
      </div>
    </div>

    <section class="module" id="module-1"><!-- Module content --></section>
    <section class="module" id="module-2"><!-- Module content --></section>
    <!-- ... more modules ... -->

    <script>
      // === ALL JAVASCRIPT ===
      (function () {
        "use strict";
        // ... initialization, navigation, interactivity ...
      })();
    </script>
  </body>
</html>
```

### Build Order

1. HTML shell with empty module sections + complete CSS + navigation
2. One module at a time (fill content, translations, interactive elements)
3. Polish pass (transitions, mobile responsive, visual consistency)

---

## Adaptive Difficulty System

Each module has content at multiple difficulty levels. The artifact tracks the learner's level and shows appropriate content.

### Level Indicator UI

```html
<div class="level-indicator" id="level-indicator">
  <span class="level-badge" id="level-badge">🔭 Explorer</span>
  <div class="level-controls">
    <button class="level-btn level-down" onclick="adjustLevel(-1)">
      <span>I'm lost</span>
    </button>
    <button class="level-btn level-up" onclick="adjustLevel(1)">
      <span>Too easy</span>
    </button>
  </div>
</div>
```

```css
.level-indicator {
  position: fixed;
  bottom: var(--space-4);
  right: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--color-surface);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-md);
  z-index: 100;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

.level-badge {
  padding: var(--space-1) var(--space-3);
  background: var(--color-accent-light);
  border-radius: var(--radius-full);
  color: var(--color-accent);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.level-btn {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  cursor: pointer;
  font-size: var(--text-xs);
  transition: all var(--duration-fast);
}

.level-btn:hover {
  background: var(--color-accent-light);
  border-color: var(--color-accent);
}
```

### Multi-Level Content Blocks

```html
<!-- Content shown at different levels -->
<div class="level-content" data-min-level="1" data-max-level="2">
  <p>Think of an API like a waiter at a restaurant...</p>
</div>

<div class="level-content" data-min-level="3" data-max-level="5">
  <p>The API exposes a RESTful interface with CRUD endpoints...</p>
</div>

<!-- "Go Deeper" toggle for optional advanced content -->
<div class="depth-toggle">
  <button class="depth-btn" onclick="toggleDepth(this)">🔍 Go Deeper</button>
  <div class="depth-content" style="display: none;">
    <p>Under the hood, this uses HTTP/2 multiplexing to...</p>
  </div>
</div>
```

### JS for Level Management

```javascript
const LEVELS = [
  { id: 1, name: "Explorer", emoji: "🔭" },
  { id: 2, name: "Navigator", emoji: "🧭" },
  { id: 3, name: "Builder", emoji: "🔨" },
  { id: 4, name: "Architect", emoji: "📐" },
  { id: 5, name: "Sage", emoji: "🧙" },
];

let currentLevel = 2; // Default: Navigator

function adjustLevel(delta) {
  currentLevel = Math.max(1, Math.min(5, currentLevel + delta));
  updateLevelDisplay();
  filterContent();
}

function updateLevelDisplay() {
  const level = LEVELS[currentLevel - 1];
  document.getElementById("level-badge").textContent =
    `${level.emoji} ${level.name}`;
}

function filterContent() {
  document.querySelectorAll(".level-content").forEach((el) => {
    const min = parseInt(el.dataset.minLevel) || 1;
    const max = parseInt(el.dataset.maxLevel) || 5;
    el.style.display =
      currentLevel >= min && currentLevel <= max ? "block" : "none";
  });
}
```

---

## Code ↔ Plain English Translation Blocks

The most important teaching element. Shows real code on the left and plain English on the right.

### HTML

```html
<div class="translation-block animate-in">
  <div class="translation-code">
    <span class="translation-label">CODE</span>
    <pre><code>
<span class="code-line"><span class="code-keyword">const</span> response = <span class="code-keyword">await</span> <span class="code-function">fetch</span>(url, {</span>
<span class="code-line">  <span class="code-property">method</span>: <span class="code-string">'POST'</span>,</span>
<span class="code-line">  <span class="code-property">headers</span>: { <span class="code-string">'Authorization'</span>: apiKey }</span>
<span class="code-line">});</span>
    </code></pre>
  </div>
  <div class="translation-english">
    <span class="translation-label">PLAIN ENGLISH</span>
    <div class="translation-lines">
      <p class="tl">Send a request to the URL and wait for a response...</p>
      <p class="tl">
        We're sending data (POST), not just asking for it (GET)...
      </p>
      <p class="tl">Include our API key so the server knows who we are...</p>
      <p class="tl">End of the request setup.</p>
    </div>
  </div>
</div>
```

### CSS

```css
.translation-block {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  margin: var(--space-8) 0;
}

.translation-code {
  background: var(--color-bg-code);
  color: #cdd6f4;
  padding: var(--space-6);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.7;
  position: relative;
  overflow-x: hidden;
}

.translation-code pre,
.translation-code code {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: hidden;
}

.translation-english {
  background: var(--color-surface-warm);
  padding: var(--space-6);
  font-size: var(--text-sm);
  line-height: 1.7;
  border-left: 3px solid var(--color-accent);
}

.translation-label {
  position: absolute;
  top: var(--space-2);
  right: var(--space-3);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.5;
}

@media (max-width: 768px) {
  .translation-block {
    grid-template-columns: 1fr;
  }
  .translation-english {
    border-left: none;
    border-top: 3px solid var(--color-accent);
  }
}
```

### Rules

- Each English line corresponds to 1-2 code lines
- Use conversational language, not jargon
- Explain WHY, not just WHAT: "Include our API key so the server knows who we are" not "Set the Authorization header"
- Use ORIGINAL code exactly — never modify or simplify
- Choose naturally short (5-10 line) code snippets

---

## Reverse Prompt Pause Points

Unique to the adaptive-teacher skill. The artifact pauses and asks the learner to think before revealing the answer.

### HTML

```html
<div class="pause-point animate-in">
  <div class="pause-question">
    <div class="pause-icon">🤔</div>
    <h3>Before I show you the answer...</h3>
    <p>
      What do you THINK this function returns? Look at the variable names and
      take a guess.
    </p>
  </div>
  <div class="pause-reveal" style="display: none;">
    <div class="pause-answer">
      <h4>Here's what actually happens:</h4>
      <p>[Explanation revealed after clicking]</p>
    </div>
  </div>
  <button class="pause-btn" onclick="revealAnswer(this)">
    I've thought about it — show me
  </button>
</div>
```

### CSS

```css
.pause-point {
  background: linear-gradient(
    135deg,
    var(--color-accent-light),
    var(--color-surface-warm)
  );
  border: 2px dashed var(--color-accent-muted);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin: var(--space-8) 0;
  text-align: center;
}

.pause-icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-4);
}

.pause-btn {
  margin-top: var(--space-6);
  padding: var(--space-3) var(--space-8);
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.pause-btn:hover {
  background: var(--color-accent-hover);
  transform: scale(1.03);
}
```

### JS

```javascript
window.revealAnswer = function (btn) {
  const pausePoint = btn.closest(".pause-point");
  const reveal = pausePoint.querySelector(".pause-reveal");
  reveal.style.display = "block";
  reveal.style.animation = "fadeSlideUp 0.5s var(--ease-out)";
  btn.textContent = "✅ Answer revealed";
  btn.disabled = true;
  btn.style.background = "var(--color-success)";
};
```

---

## Scenario-Based Quizzes

Quizzes that test APPLICATION, not memorization. Present a scenario the learner hasn't seen and ask them to apply what they learned.

### HTML

```html
<div class="quiz-container">
  <div class="quiz-header">
    <span class="quiz-label">🧠 Check Your Understanding</span>
  </div>

  <div class="quiz-question-block" data-question="q1" data-correct="option-b">
    <div class="scenario-context">
      <span class="scenario-label">📋 Scenario</span>
      <p>
        A user reports that they can save their profile (they see a success
        message) but when they reload the page, their changes are gone.
      </p>
    </div>
    <h3 class="quiz-question">
      Based on what you learned about state management — what's probably
      happening?
    </h3>
    <div class="quiz-options">
      <button
        class="quiz-option"
        data-value="option-a"
        data-explanation="The database is working fine — the user sees a success message, so the save action completed. The issue is about what happens AFTER the save."
        onclick="selectOption(this)"
      >
        <div class="quiz-option-radio"></div>
        <span>The database isn't saving the data</span>
      </button>
      <button
        class="quiz-option"
        data-value="option-b"
        data-explanation="Exactly! The state was updated in memory (showing the success message) but was never persisted to the server/database. When the page reloads, it fetches the OLD data from the server."
        onclick="selectOption(this)"
      >
        <div class="quiz-option-radio"></div>
        <span
          >The frontend state was updated but the backend was never called</span
        >
      </button>
      <button
        class="quiz-option"
        data-value="option-c"
        data-explanation="Not likely — the user can load the page fine, so the server is up. The issue is specifically about data persistence, not connectivity."
        onclick="selectOption(this)"
      >
        <div class="quiz-option-radio"></div>
        <span>The server is down</span>
      </button>
    </div>
    <div class="quiz-feedback" id="q1-feedback"></div>
  </div>

  <button class="quiz-check-btn" onclick="checkQuiz('q1')">Check Answer</button>
</div>
```

### Quiz JS Pattern

```javascript
window.selectOption = function (btn) {
  const block = btn.closest(".quiz-question-block");
  block
    .querySelectorAll(".quiz-option")
    .forEach((o) => o.classList.remove("selected"));
  btn.classList.add("selected");
};

window.checkQuiz = function (questionId) {
  const block = document.querySelector(`[data-question="${questionId}"]`);
  const selected = block.querySelector(".quiz-option.selected");
  const feedback = block.querySelector(".quiz-feedback");
  const correctValue = block.dataset.correct;

  if (!selected) {
    feedback.textContent = "Pick an answer first!";
    feedback.className = "quiz-feedback show warning";
    return;
  }

  const explanation = selected.dataset.explanation;

  if (selected.dataset.value === correctValue) {
    selected.classList.add("correct");
    feedback.innerHTML = `<strong>🎯 Exactly!</strong> ${explanation}`;
    feedback.className = "quiz-feedback show success";
  } else {
    selected.classList.add("incorrect");
    block
      .querySelector(`[data-value="${correctValue}"]`)
      .classList.add("correct");
    feedback.innerHTML = `<strong>Not quite.</strong> ${explanation}`;
    feedback.className = "quiz-feedback show error";
  }

  block.querySelectorAll(".quiz-option").forEach((o) => (o.disabled = true));
};
```

### Quiz CSS

```css
.quiz-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  margin: var(--space-8) 0;
}

.quiz-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  font-weight: 600;
}

.scenario-context {
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-5);
  margin: var(--space-4) 0;
  border-left: 3px solid var(--color-info);
}

.scenario-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-info);
  font-weight: 600;
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  cursor: pointer;
  width: 100%;
  transition:
    border-color var(--duration-fast),
    background var(--duration-fast);
  margin-bottom: var(--space-2);
  font-family: var(--font-body);
  font-size: var(--text-base);
  text-align: left;
}

.quiz-option:hover {
  border-color: var(--color-accent-muted);
}
.quiz-option.selected {
  border-color: var(--color-accent);
  background: var(--color-accent-light);
}
.quiz-option.correct {
  border-color: var(--color-success);
  background: var(--color-success-light);
}
.quiz-option.incorrect {
  border-color: var(--color-error);
  background: var(--color-error-light);
}

.quiz-option-radio {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  flex-shrink: 0;
  transition: all var(--duration-fast);
}

.quiz-option.selected .quiz-option-radio {
  border-color: var(--color-accent);
  background: var(--color-accent);
  box-shadow: inset 0 0 0 3px white;
}

.quiz-feedback {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition:
    max-height var(--duration-normal),
    opacity var(--duration-normal);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

.quiz-feedback.show {
  max-height: 200px;
  opacity: 1;
  padding: var(--space-3) var(--space-4);
  margin-top: var(--space-3);
}

.quiz-feedback.success {
  background: var(--color-success-light);
  color: var(--color-success);
}
.quiz-feedback.error {
  background: var(--color-error-light);
  color: var(--color-error);
}
.quiz-feedback.warning {
  background: var(--color-info-light);
  color: var(--color-info);
}

.quiz-check-btn {
  margin-top: var(--space-4);
  padding: var(--space-3) var(--space-8);
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.quiz-check-btn:hover {
  background: var(--color-accent-hover);
}
```

---

## Concept Animation Patterns

### Group Chat Animation

iMessage/WhatsApp-style chat showing components "talking" to each other. Messages appear one by one with typing indicators.

Use the exact same pattern as defined in the codebase-to-course interactive-elements reference. Group chats MUST appear at least once per artifact — they're the most engaging element.

### Data Flow Animation

Step-by-step visualization of data moving between components. Use when teaching request/response, event propagation, or any multi-step process.

Same pattern as codebase-to-course with one addition: **level-aware descriptions.**

```javascript
const flowSteps = [
  {
    from: "client",
    to: "api",
    label: {
      1: "Your browser asks for data, like calling a friend for information",
      3: "The client sends an HTTP GET request to the /api/users endpoint",
      5: "GET /api/users with Accept: application/json header, including the JWT bearer token",
    },
  },
  // ... more steps
];

// Show label based on current level
function getStepLabel(step) {
  const levels = Object.keys(step.label)
    .map(Number)
    .sort((a, b) => a - b);
  let best = levels[0];
  for (const l of levels) {
    if (l <= currentLevel) best = l;
  }
  return step.label[best];
}
```

---

## Glossary Tooltip System

Every technical term gets a tooltip on first use per module.

### Implementation

Use `position: fixed` tooltips appended to `document.body` — never `position: absolute` inside containers (they get clipped by `overflow: hidden`).

```html
<span
  class="term"
  data-definition="A service that runs in the background, even when the web page is closed. Think of it like a security guard who stays at the building 24/7."
  >service worker</span
>
```

```css
.term {
  border-bottom: 1.5px dashed var(--color-accent-muted);
  cursor: pointer;
  position: relative;
}

.term:hover,
.term.active {
  border-bottom-color: var(--color-accent);
  color: var(--color-accent);
}

.term-tooltip {
  position: fixed;
  background: var(--color-bg-code);
  color: #cdd6f4;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-family: var(--font-body);
  line-height: var(--leading-normal);
  width: max(200px, min(320px, 80vw));
  box-shadow: var(--shadow-lg);
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--duration-fast);
  z-index: 10000;
}

.term-tooltip.visible {
  opacity: 1;
}
```

### JS Positioning

```javascript
let activeTooltip = null;

document.querySelectorAll(".term").forEach((term) => {
  const tip = document.createElement("span");
  tip.className = "term-tooltip";
  tip.textContent = term.dataset.definition;

  function show() {
    if (activeTooltip && activeTooltip !== tip) {
      activeTooltip.classList.remove("visible");
      activeTooltip.remove();
    }
    const rect = term.getBoundingClientRect();
    const tipWidth = 300;
    let left = rect.left + rect.width / 2 - tipWidth / 2;
    left = Math.max(8, Math.min(left, window.innerWidth - tipWidth - 8));

    document.body.appendChild(tip);
    const tipHeight = tip.offsetHeight;

    if (rect.top - tipHeight - 8 < 0) {
      tip.style.top = rect.bottom + 8 + "px";
    } else {
      tip.style.top = rect.top - tipHeight - 8 + "px";
    }
    tip.style.left = left + "px";
    requestAnimationFrame(() => tip.classList.add("visible"));
    activeTooltip = tip;
  }

  function hide() {
    tip.classList.remove("visible");
    setTimeout(() => {
      if (!tip.classList.contains("visible")) tip.remove();
    }, 150);
    activeTooltip = null;
  }

  term.addEventListener("mouseenter", show);
  term.addEventListener("mouseleave", hide);
  term.addEventListener("click", (e) => {
    e.stopPropagation();
    tip.classList.contains("visible") ? hide() : show();
  });
});

document.addEventListener("click", () => {
  if (activeTooltip) {
    activeTooltip.classList.remove("visible");
    activeTooltip.remove();
    activeTooltip = null;
  }
});
```

---

## Metaphor Callout Boxes

"Aha!" moments with fresh, unique metaphors.

```html
<div class="callout callout-metaphor">
  <div class="callout-icon">💡</div>
  <div class="callout-content">
    <strong class="callout-title">Think of it like...</strong>
    <p>
      A database index is like the index at the back of a textbook. Without it,
      you'd have to read every single page to find what you're looking for. With
      it, you jump straight to the right page. The trade-off? The index takes up
      space and needs updating when pages change.
    </p>
  </div>
</div>
```

### Variants

```css
.callout {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-5) var(--space-6);
  border-radius: var(--radius-md);
  margin: var(--space-6) 0;
}

/* Metaphor/Insight */
.callout-metaphor {
  background: var(--color-accent-light);
  border-left: 4px solid var(--color-accent);
}

/* Pro tip */
.callout-tip {
  background: var(--color-info-light);
  border-left: 4px solid var(--color-info);
}

/* Warning / common mistake */
.callout-warning {
  background: var(--color-error-light);
  border-left: 4px solid var(--color-error);
}

/* "Why should I care?" motivation box */
.callout-motivation {
  background: var(--color-success-light);
  border-left: 4px solid var(--color-success);
}

.callout-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.callout-title {
  font-family: var(--font-display);
  font-weight: 600;
  display: block;
  margin-bottom: var(--space-1);
}
```

---

## Progressive Disclosure Toggles

"Go Deeper" buttons that reveal advanced content without overwhelming beginners.

```html
<div class="depth-toggle">
  <button class="depth-btn" data-label="How does this work under the hood?" onclick="toggleDepth(this)">
    🔍 Go Deeper — How does this work under the hood?
  </button>
  <div class="depth-content">
    <p>Under the hood, the JavaScript runtime uses an event loop that...</p>
  </div>
</div>
```

```css
.depth-toggle {
  margin: var(--space-4) 0;
}

.depth-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: none;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  transition: all var(--duration-fast);
}

.depth-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.depth-content {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition:
    max-height var(--duration-slow),
    opacity var(--duration-slow);
  padding: 0 var(--space-4);
  background: var(--color-bg-warm);
  border-radius: var(--radius-sm);
  margin-top: var(--space-2);
}

.depth-content.expanded {
  max-height: 1000px;
  opacity: 1;
  padding: var(--space-4);
}
```

```javascript
window.toggleDepth = function (btn) {
  const content = btn.nextElementSibling;
  const expanded = content.classList.toggle("expanded");
  btn.textContent = expanded
    ? "🔼 Collapse"
    : "🔍 Go Deeper — " + btn.dataset.label;
};
```

---

## Confidence Check Cards

Periodic confidence calibration embedded in the artifact.

```html
<div class="confidence-check animate-in">
  <h3>Quick Confidence Check</h3>
  <p>Could you explain <strong>[concept]</strong> to a teammate right now?</p>
  <div class="confidence-scale">
    <button class="conf-btn" data-level="1" onclick="setConfidence(this, 1)">
      😰 No way
    </button>
    <button class="conf-btn" data-level="2" onclick="setConfidence(this, 2)">
      🤔 Maybe
    </button>
    <button class="conf-btn" data-level="3" onclick="setConfidence(this, 3)">
      😊 Mostly
    </button>
    <button class="conf-btn" data-level="4" onclick="setConfidence(this, 4)">
      💪 Definitely
    </button>
  </div>
  <div class="conf-response" style="display:none;"></div>
</div>
```

### CSS

```css
.confidence-check {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  margin: var(--space-8) 0;
  text-align: center;
}

.confidence-scale {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
  margin: var(--space-6) 0;
}

.conf-btn {
  padding: var(--space-3) var(--space-5);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  cursor: pointer;
  font-size: var(--text-base);
  transition: all var(--duration-fast);
}

.conf-btn:hover {
  border-color: var(--color-accent-muted);
  background: var(--color-accent-light);
}

.conf-btn.active {
  border-color: var(--color-accent);
  background: var(--color-accent-light);
  font-weight: 600;
}

.conf-response {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}
```

### JS

```javascript
window.setConfidence= function (btn, level) {
  const check = btn.closest(".confidence-check");
  const response = check.querySelector(".conf-response");

  check
    .querySelectorAll(".conf-btn")
    .forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");

  const messages = {
    1: "That's okay — let's revisit this with a different angle. Scroll back up and try the 'I'm lost' button to see a simpler explanation.",
    2: "You're getting there! The parts you're unsure about are usually the most valuable to nail down. Try the teach-back challenge below.",
    3: "Solid! Try explaining it in the teach-back box below — that'll lock it in.",
    4: "Excellent! You've got this. Let's move on to the next concept.",
  };

  response.textContent = messages[level];
  response.style.display = "block";
  response.style.animation = "fadeSlideUp 0.3s var(--ease-out)";
};
```

---

## Teach-Back Challenge Blocks

The learner writes their own explanation. This is the highest-retention learning technique.

```html
<div class="teachback animate-in">
  <div class="teachback-header">
    <span class="teachback-icon">🎓</span>
    <h3>Your Turn to Teach</h3>
  </div>
  <p>
    Explain <strong>[concept]</strong> in your own words, as if you're telling a
    teammate who missed the meeting:
  </p>
  <textarea
    class="teachback-input"
    placeholder="Type your explanation here... There's no wrong answer. Use your own words."
    rows="4"
  ></textarea>
  <button class="teachback-submit" onclick="submitTeachback(this)">
    Done — show me the model answer
  </button>
  <div class="teachback-model" style="display:none;">
    <strong>Here's a solid explanation:</strong>
    <p>[Model answer that the learner can compare against]</p>
  </div>
</div>
```

### JS

```javascript
window.submitTeachback = function (btn) {
  const block = btn.closest(".teachback");
  const textarea = block.querySelector(".teachback-input");
  const model = block.querySelector(".teachback-model");

  if (!textarea.value.trim()) {
    textarea.style.borderColor = "var(--color-error)";
    textarea.setAttribute("placeholder", "Give it a try first — even a rough answer helps you learn.");
    return;
  }

  model.style.display = "block";
  model.style.animation = "fadeSlideUp 0.5s var(--ease-out)";
  btn.textContent = "✅ Model answer revealed — compare with yours";
  btn.disabled = true;
  btn.style.opacity = "0.6";
  textarea.readOnly = true;
  textarea.style.borderColor = "var(--color-success)";
};
```

### CSS

```css
.teachback {
  background: linear-gradient(
    135deg,
    var(--color-surface-warm),
    var(--color-surface)
  );
  border: 2px solid var(--color-accent-muted);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin: var(--space-8) 0;
}

.teachback-input {
  width: 100%;
  padding: var(--space-4);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  resize: vertical;
  transition: border-color var(--duration-fast);
}

.teachback-input:focus {
  outline: none;
  border-color: var(--color-accent);
}
```

---

## Design System Tokens

Complete CSS custom properties for teaching artifacts.

```css
:root {
  /* Backgrounds */
  --color-bg: #faf7f2;
  --color-bg-warm: #f5f0e8;
  --color-bg-code: #1e1e2e;
  --color-text: #2c2a28;
  --color-text-secondary: #6b6560;
  --color-text-muted: #9e9790;
  --color-border: #e5dfd6;
  --color-border-light: #eeebe5;
  --color-surface: #ffffff;
  --color-surface-warm: #fdf9f3;

  /* Accent (adapt per topic) */
  --color-accent: #d94f30;
  --color-accent-hover: #c4432a;
  --color-accent-light: #fdeee9;
  --color-accent-muted: #e8836c;

  /* Semantic */
  --color-success: #2d8b55;
  --color-success-light: #e8f5ee;
  --color-error: #c93b3b;
  --color-error-light: #fde8e8;
  --color-info: #2a7b9b;
  --color-info-light: #e4f2f7;

  /* Typography */
  --font-display: "Bricolage Grotesque", Georgia, serif;
  --font-body: "DM Sans", -apple-system, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", monospace;

  /* Type Scale */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  /* Leading */
  --leading-tight: 1.15;
  --leading-snug: 1.3;
  --leading-normal: 1.6;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Layout */
  --content-width: 800px;
  --content-width-wide: 1000px;
  --nav-height: 50px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(44, 42, 40, 0.05);
  --shadow-md: 0 4px 12px rgba(44, 42, 40, 0.08);
  --shadow-lg: 0 8px 24px rgba(44, 42, 40, 0.1);

  /* Animation */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --stagger-delay: 120ms;
}

/* Syntax Highlighting (Catppuccin) */
.code-keyword {
  color: #cba6f7;
}
.code-string {
  color: #a6e3a1;
}
.code-function {
  color: #89b4fa;
}
.code-comment {
  color: #6c7086;
}
.code-number {
  color: #fab387;
}
.code-property {
  color: #f9e2af;
}
.code-operator {
  color: #94e2d5;
}
.code-tag {
  color: #f38ba8;
}

/* Global Animations */
@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity var(--duration-slow) var(--ease-out),
    transform var(--duration-slow) var(--ease-out);
}

.animate-in.visible {
  opacity: 1;
  transform: translateY(0);
}
```

---

## Arabic-Specific Design Additions

When generating artifacts with Arabic content, add these tokens:

```css
/* Arabic font support */
@import url("https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&display=swap");

[dir="rtl"] {
  font-family: "IBM Plex Sans Arabic", "Cairo", var(--font-body);
  text-align: right;
  direction: rtl;
}

[dir="rtl"] pre,
[dir="rtl"] code,
[dir="rtl"] .translation-code {
  direction: ltr;
  text-align: left;
  font-family: var(--font-mono);
}

[dir="rtl"] .translation-block {
  grid-template-columns: 1fr 1fr;
}

[dir="rtl"] .translation-english {
  border-left: none;
  border-right: 3px solid var(--color-accent);
}

/* Mixed content: English terms flow naturally in RTL */
[dir="rtl"] .english-inline {
  direction: ltr;
  unicode-bidi: embed;
}
```
