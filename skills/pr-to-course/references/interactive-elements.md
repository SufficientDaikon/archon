# Interactive Elements Reference

Implementation patterns for every interactive element used in PR courses. Pick the elements that best serve each module's teaching goal.

---

## Code ↔ English Translation Blocks

The most important teaching element for PR courses. Shows real code from the changed files on the left and plain English explanation on the right.

**HTML:**

```html
<div class="translation-block animate-in">
  <div class="translation-code">
    <span class="translation-label">CODE</span>
    <pre><code>
<span class="code-line"><span class="code-keyword">if</span> (<span class="code-function">EarlyCheckForHiddenWindowStyle</span>(args))</span>
<span class="code-line">{</span>
<span class="code-line">    <span class="code-function">TryAllocConsoleWithMode</span>(<span class="code-property">NoWindow</span>);</span>
<span class="code-line">}</span>
    </code></pre>
  </div>
  <div class="translation-english">
    <span class="translation-label">PLAIN ENGLISH</span>
    <div class="translation-lines">
      <p class="tl">
        Before anything else runs, quickly scan the command line for
        -WindowStyle Hidden...
      </p>
      <p class="tl">If we found it...</p>
      <p class="tl">
        Create a console for I/O but tell the OS: "don't show a window for it"
      </p>
      <p class="tl">End of the early check.</p>
    </div>
  </div>
</div>
```

**CSS:**

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

**Rules:**

- Each English line should correspond to 1-2 code lines
- Explain the WHY, not just the WHAT
- Code must be exact — copied from the actual source file, never modified

---

## Multiple-Choice Quizzes

For testing understanding with instant feedback. Each question tests application, not memory.

**HTML:**

```html
<div class="quiz-container">
  <div class="quiz-question-block" data-question="q1" data-correct="option-b">
    <h3 class="quiz-question">
      A scheduled task runs pwsh.exe -WindowStyle Hidden on Windows 10. What
      happens?
    </h3>
    <div class="quiz-options">
      <button class="quiz-option" data-value="option-a" data-answer="wrong">
        <div class="quiz-option-radio"></div>
        <span>No console window appears</span>
      </button>
      <button class="quiz-option" data-value="option-b" data-answer="correct">
        <div class="quiz-option-radio"></div>
        <span>Console briefly flashes, then hides</span>
      </button>
      <button class="quiz-option" data-value="option-c" data-answer="wrong">
        <div class="quiz-option-radio"></div>
        <span>PowerShell fails to start</span>
      </button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
</div>
```

**CRITICAL: Never put "(CORRECT)" or "(WRONG)" in option text.** The data-answer attribute drives the JS logic. CSS classes show correct/incorrect after clicking.

**JS:**

```javascript
document.querySelectorAll(".quiz-option").forEach((btn) => {
  btn.addEventListener("click", function () {
    const block = this.closest(".quiz-question-block");
    if (block.classList.contains("answered")) return;
    block.classList.add("answered");

    const feedback = block.querySelector(".quiz-feedback");
    const isCorrect = this.dataset.answer === "correct";

    if (isCorrect) {
      this.classList.add("correct");
      feedback.innerHTML =
        "<strong>Exactly!</strong> On Windows 10 the manifest attribute is ignored, so the OS creates a visible console before Main() runs.";
      feedback.className = "quiz-feedback show success";
    } else {
      this.classList.add("incorrect");
      block.querySelector('[data-answer="correct"]').classList.add("correct");
      feedback.innerHTML =
        "<strong>Not quite.</strong> Windows 10 doesn't support consoleAllocationPolicy, so it falls back to normal CUI behavior — the console window appears briefly.";
      feedback.className = "quiz-feedback show error";
    }

    block
      .querySelectorAll(".quiz-option")
      .forEach((o) => (o.style.pointerEvents = "none"));
  });
});
```

**CSS:**

```css
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
}
.quiz-option:hover {
  border-color: var(--color-accent-muted);
}
.quiz-option.correct {
  border-color: var(--color-success);
  background: var(--color-success-light);
}
.quiz-option.incorrect {
  border-color: var(--color-error);
  background: var(--color-error-light);
}
.quiz-feedback {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition:
    max-height var(--duration-normal),
    opacity var(--duration-normal);
}
.quiz-feedback.show {
  max-height: 200px;
  opacity: 1;
  padding: var(--space-3);
  margin-top: var(--space-2);
  border-radius: var(--radius-sm);
}
.quiz-feedback.success {
  background: var(--color-success-light);
  color: var(--color-success);
}
.quiz-feedback.error {
  background: var(--color-error-light);
  color: var(--color-error);
}
```

---

## Before/After Visual

PR-specific element showing old behavior vs new behavior side by side.

**HTML:**

```html
<div class="before-after animate-in">
  <div class="before-side">
    <span class="ba-label">BEFORE</span>
    <div class="ba-content">
      <!-- For behavioral changes, use a CSS animation -->
      <div class="console-flash-demo">
        <div class="mini-console" style="animation: flashAnim 3s infinite">
          <div class="mini-titlebar">■ pwsh.exe</div>
        </div>
      </div>
      <p class="ba-desc">Console window flashes visibly</p>
    </div>
  </div>
  <div class="after-side">
    <span class="ba-label">AFTER</span>
    <div class="ba-content">
      <div class="no-flash-demo">
        <span style="font-size: 2rem">✨</span>
      </div>
      <p class="ba-desc">No window. Zero flash.</p>
    </div>
  </div>
</div>
```

**CSS for flash animation:**

```css
@keyframes flashAnim {
  0%,
  100% {
    opacity: 0;
    transform: scale(0.95);
  }
  10% {
    opacity: 1;
    transform: scale(1);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0;
    transform: scale(0.95);
  }
}
.mini-console {
  width: 120px;
  height: 80px;
  background: #1a1a2e;
  border-radius: 6px;
  margin: 0 auto;
  overflow: hidden;
}
.mini-titlebar {
  background: #333;
  color: #aaa;
  font-size: 0.65rem;
  padding: 3px 6px;
  font-family: var(--font-mono);
}
```

---

## Data Flow / Decision Flow Animation

Step-by-step visualization of data or control flow through PR components.

**HTML:**

```html
<div class="flow-animation">
  <div class="flow-steps" id="flow-steps">
    <div class="flow-step" data-step="0">
      <div class="flow-step-icon" style="background: var(--color-actor-3)">
        OS
      </div>
      <div class="flow-step-content">
        <strong>Process Created</strong>
        <p>Windows sees pwsh.exe is a CUI binary</p>
      </div>
    </div>
    <div class="flow-arrow">→</div>
    <div class="flow-step" data-step="1">
      <div class="flow-step-icon" style="background: var(--color-actor-4)">
        📋
      </div>
      <div class="flow-step-content">
        <strong>Manifest Read</strong>
        <p>OS finds consoleAllocationPolicy=detached</p>
      </div>
    </div>
    <!-- more steps -->
  </div>

  <p class="flow-hint" id="flow-hint">↓ Watch the execution flow unfold ↓</p>

  <div class="flow-controls">
    <button onclick="playFlow()">▶ Play</button>
    <button onclick="replayFlow()">↺ Replay</button>
  </div>
</div>
```

**JS:**

```javascript
function playFlow() {
  document.getElementById("flow-hint").style.display = "none";
  const steps = document.querySelectorAll(".flow-step");
  const arrows = document.querySelectorAll(".flow-arrow");

  // Reset
  steps.forEach((s) => s.classList.remove("visible"));
  arrows.forEach((a) => a.classList.remove("visible"));

  // Stagger reveal
  let delay = 0;
  steps.forEach((step, i) => {
    setTimeout(() => step.classList.add("visible"), delay);
    delay += 600;
    if (arrows[i]) {
      setTimeout(() => arrows[i].classList.add("visible"), delay);
      delay += 300;
    }
  });
}

// Auto-trigger on scroll
const flowObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        playFlow();
        flowObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 },
);
```

**CSS:**

```css
.flow-step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  opacity: 0;
  transform: translateX(-30px);
  transition:
    opacity var(--duration-slow) var(--ease-out),
    transform var(--duration-slow) var(--ease-out);
}
.flow-step.visible {
  opacity: 1;
  transform: translateX(0);
}
.flow-arrow {
  font-size: 1.5rem;
  color: var(--color-accent);
  opacity: 0;
  transition: opacity var(--duration-normal);
}
.flow-arrow.visible {
  opacity: 1;
}
.flow-step-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  flex-shrink: 0;
}
.flow-hint {
  text-align: center;
  color: var(--color-text-muted);
  font-style: italic;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}
```

---

## Behavior Matrix

Interactive table showing how the fix behaves across different scenarios.

**HTML:**

```html
<div class="behavior-matrix animate-in">
  <table class="matrix-table">
    <thead>
      <tr>
        <th>Launch Context</th>
        <th>Windows 11 24H2+</th>
        <th>Older Windows</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="matrix-context">Task Scheduler</td>
        <td
          class="matrix-cell matrix-new"
          data-detail="AllocConsoleWithOptions(NoWindow) — zero flash"
        >
          ✅ No flash
        </td>
        <td
          class="matrix-cell matrix-existing"
          data-detail="Falls back to AllocConsole() — brief flash, then hidden"
        >
          ⚡ Brief flash
        </td>
      </tr>
      <!-- more rows -->
    </tbody>
  </table>
</div>
```

**CSS:**

```css
.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}
.matrix-table th {
  background: var(--color-bg-code);
  color: #cdd6f4;
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.matrix-cell {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background var(--duration-fast);
}
.matrix-cell:hover {
  background: var(--color-accent-light);
}
.matrix-new {
  color: var(--color-success);
  font-weight: 600;
}
.matrix-existing {
  color: var(--color-text-secondary);
}
.matrix-context {
  font-weight: 600;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
}
```

---

## Test Coverage Cards

Grid of cards showing each test, what it validates, and why it matters.

**HTML:**

```html
<div class="test-grid animate-in">
  <div class="test-card">
    <div class="test-card-header">
      <span class="test-badge pass">PASS</span>
      <span class="test-category">Argument Parsing</span>
    </div>
    <h4 class="test-card-name">
      Detects -WindowStyle Hidden with double-dash prefix
    </h4>
    <p class="test-card-desc">
      Ensures the early parser handles --WindowStyle (with double dash) the same
      as -WindowStyle, matching PowerShell's standard behavior.
    </p>
  </div>
  <!-- more cards -->
</div>
```

**CSS:**

```css
.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}
.test-card {
  background: var(--color-surface);
  border-left: 4px solid var(--color-success);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
  transition:
    transform var(--duration-fast),
    box-shadow var(--duration-fast);
}
.test-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.test-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}
.test-badge {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.test-badge.pass {
  background: var(--color-success-light);
  color: var(--color-success);
}
.test-badge.fail {
  background: var(--color-error-light);
  color: var(--color-error);
}
.test-category {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.test-card-name {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: var(--space-2);
  line-height: var(--leading-snug);
}
.test-card-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-normal);
}
```

---

## Source File Cards

One card per changed file in the PR, with expandable code view.

**HTML:**

```html
<div class="file-card animate-in">
  <div class="file-card-header">
    <div>
      <span class="file-badge new">NEW</span>
      <span class="file-path"
        >src/engine/Interop/Windows/AllocConsoleWithOptions.cs</span
      >
    </div>
    <button class="file-expand-btn" onclick="toggleFileCode(this)">
      View Code ▾
    </button>
  </div>
  <p class="file-desc">
    P/Invoke declarations for the Windows 11 26100+ AllocConsoleWithOptions API,
    plus a TryAllocConsoleWithMode() helper that wraps the call with
    EntryPointNotFoundException fallback.
  </p>
  <div class="file-code-expand" style="display: none">
    <div class="translation-block">
      <!-- code↔English translation -->
    </div>
  </div>
</div>
```

**JS:**

```javascript
function toggleFileCode(btn) {
  const card = btn.closest(".file-card");
  const code = card.querySelector(".file-code-expand");
  if (code.style.display === "none") {
    code.style.display = "block";
    btn.textContent = "Hide Code ▴";
  } else {
    code.style.display = "none";
    btn.textContent = "View Code ▾";
  }
}
```

---

## Group Chat Animation

iMessage-style chat where PR components "talk" to each other to explain the flow.

**HTML:**

```html
<div class="chat-window">
  <div class="chat-messages" id="chat-msgs">
    <div
      class="chat-message"
      data-msg="0"
      data-sender="os"
      style="display:none"
    >
      <div class="chat-avatar" style="background: var(--color-actor-3)">OS</div>
      <div class="chat-bubble">
        <span class="chat-sender" style="color: var(--color-actor-3)"
          >Windows</span
        >
        <p>
          New process starting: pwsh.exe. It's a CUI app, so I'll create a
          console for it...
        </p>
      </div>
    </div>
    <div
      class="chat-message"
      data-msg="1"
      data-sender="manifest"
      style="display:none"
    >
      <div class="chat-avatar" style="background: var(--color-actor-4)">📋</div>
      <div class="chat-bubble">
        <span class="chat-sender" style="color: var(--color-actor-4)"
          >Manifest</span
        >
        <p>
          Wait! I have consoleAllocationPolicy=detached. Skip the automatic
          console.
        </p>
      </div>
    </div>
    <!-- more messages -->
  </div>

  <div class="chat-typing" id="chat-typing" style="display:none">
    <div class="chat-avatar" id="typing-avatar">?</div>
    <div class="chat-typing-dots">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  </div>

  <div class="chat-controls">
    <button onclick="chatNext()">Next Message</button>
    <button onclick="chatPlayAll()">Play All</button>
    <button onclick="chatReset()">Replay</button>
    <span class="chat-progress">0 / N</span>
  </div>
</div>
```

**CSS:**

```css
.chat-window {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  max-width: 600px;
  margin: var(--space-8) auto;
}
.chat-messages {
  padding: var(--space-4);
  min-height: 300px;
}
.chat-message {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
  animation: fadeSlideUp 0.3s var(--ease-out);
}
.chat-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: var(--text-xs);
  flex-shrink: 0;
}
.chat-bubble {
  background: var(--color-bg);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  max-width: 80%;
}
.chat-sender {
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.chat-controls {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-surface-warm);
}
.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: typingBounce 1.4s infinite;
}
.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes typingBounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}
@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## Callout Boxes

For "aha!" moments, warnings, and key insights.

**HTML:**

```html
<div class="callout callout-insight animate-in">
  <span class="callout-icon">💡</span>
  <div class="callout-content">
    <strong>Key Insight</strong>
    <p>
      The console window appears BEFORE Main() runs because Windows creates it
      at process startup for CUI binaries. No amount of C# code can prevent it —
      the fix must happen at the OS level via the manifest.
    </p>
  </div>
</div>

<div class="callout callout-warning animate-in">
  <span class="callout-icon">⚠️</span>
  <div class="callout-content">
    <strong>Backward Compatibility</strong>
    <p>
      On Windows versions before 26100, the manifest attribute is silently
      ignored and AllocConsoleWithOptions throws EntryPointNotFoundException.
      The code catches this and falls back to AllocConsole().
    </p>
  </div>
</div>
```

**CSS:**

```css
.callout {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  margin: var(--space-6) 0;
}
.callout-insight {
  background: var(--color-accent-light);
  border-left: 4px solid var(--color-accent);
}
.callout-warning {
  background: #fef3e2;
  border-left: 4px solid #d4a843;
}
.callout-info {
  background: var(--color-info-light);
  border-left: 4px solid var(--color-info);
}
.callout-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}
.callout-content strong {
  display: block;
  margin-bottom: var(--space-1);
  font-family: var(--font-display);
}
```

---

## Numbered Step Cards

For explaining a sequential process (like the 5 steps of the fix).

**HTML:**

```html
<div class="step-cards animate-in stagger-children">
  <div class="step-card animate-in">
    <div class="step-number">1</div>
    <div class="step-content">
      <h4>Manifest declares detached policy</h4>
      <p>
        pwsh.manifest tells Windows 11 26100+ to skip automatic console
        allocation.
      </p>
    </div>
  </div>
  <div class="step-card animate-in">
    <div class="step-number">2</div>
    <div class="step-content">
      <h4>EarlyConsoleInit runs first</h4>
      <p>Before any other startup code, Main() calls EarlyConsoleInit(args).</p>
    </div>
  </div>
  <!-- more steps -->
</div>
```

**CSS:**

```css
.step-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.step-card {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
.step-number {
  width: 40px;
  height: 40px;
  background: var(--color-accent);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 800;
  font-size: var(--text-lg);
  flex-shrink: 0;
}
.step-content h4 {
  font-family: var(--font-display);
  font-weight: 600;
  margin-bottom: var(--space-1);
}
.step-content p {
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}
```

---

## Stats Grid

Hero section element showing key PR metrics.

**HTML:**

```html
<div class="stats-grid animate-in">
  <div class="stat-card">
    <span class="stat-value">6</span>
    <span class="stat-label">Files Changed</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">13</span>
    <span class="stat-label">Pester Tests</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">~250</span>
    <span class="stat-label">Lines Added</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">0</span>
    <span class="stat-label">Regressions</span>
  </div>
</div>
```

**CSS:**

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin: var(--space-8) 0;
}
.stat-card {
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  text-align: center;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}
.stat-value {
  display: block;
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: 800;
  color: var(--color-accent);
  line-height: 1;
}
.stat-label {
  display: block;
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin-top: var(--space-2);
}
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

---

## PR/Issue Link Buttons

Hero section buttons linking to the original PR and issue.

**HTML:**

```html
<div class="link-buttons animate-in">
  <a
    href="https://github.com/org/repo/pull/123"
    class="link-btn link-btn-primary"
    target="_blank"
    rel="noopener"
  >
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path
        d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354z"
      />
      <path
        d="M3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5z"
      />
    </svg>
    PR #123
  </a>
  <a
    href="https://github.com/org/repo/issues/456"
    class="link-btn link-btn-secondary"
    target="_blank"
    rel="noopener"
  >
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
      <path
        d="M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z"
      />
    </svg>
    Issue #456
  </a>
</div>
```

**CSS:**

```css
.link-buttons {
  display: flex;
  gap: var(--space-3);
  margin: var(--space-6) 0;
  flex-wrap: wrap;
}
.link-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-full);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  text-decoration: none;
  transition:
    transform var(--duration-fast),
    box-shadow var(--duration-fast);
}
.link-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.link-btn-primary {
  background: var(--color-accent);
  color: white;
}
.link-btn-secondary {
  background: transparent;
  color: var(--color-accent);
  border: 2px solid var(--color-accent);
}
```
