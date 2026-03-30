# Academic Elements Reference

> **Prerequisite:** These elements use CSS custom properties from the shared `codebase-to-course` design system (`references/design-system.md`). All `--color-*`, `--radius-*`, `--space-*`, `--shadow-*`, `--font-*`, `--text-*`, `--duration-*`, and `--ease-*` variables must be defined by the design system's `:root` block. This skill declares `composes: [codebase-to-course]` in its manifest for this reason.

Implementation patterns for interactive elements unique to research paper courses. These complement the standard interactive elements (quizzes, code translations, chat animations, tooltips) from the shared design system.

---

## Equation Walkthrough

Step-by-step equation breakdown where each symbol highlights with a plain English tooltip. The most important element for making math-heavy papers accessible.

### HTML

```html
<div class="equation-walkthrough animate-in">
  <div class="eq-header">
    <span class="eq-label">EQUATION WALKTHROUGH</span>
    <h3>Self-Attention Score</h3>
  </div>

  <div class="eq-display" id="eq-1">
    <div class="eq-formula">
      <span
        class="eq-term"
        data-term="attention"
        data-explain="The attention score — how much should word A pay attention to word B?"
        >Attention</span
      >(<span
        class="eq-term"
        data-term="Q"
        data-explain="Query: 'What am I looking for?' — each word asks this question"
        >Q</span
      >,
      <span
        class="eq-term"
        data-term="K"
        data-explain="Key: 'What do I contain?' — each word advertises its content"
        >K</span
      >,
      <span
        class="eq-term"
        data-term="V"
        data-explain="Value: 'Here's my actual information' — the content that gets passed forward"
        >V</span
      >) = softmax(<span
        class="eq-term"
        data-term="QK"
        data-explain="Multiply queries by keys — high score means 'these two words are relevant to each other'"
        >QK<sup>T</sup></span
      >
      /
      <span
        class="eq-term"
        data-term="sqrt"
        data-explain="Divide by √d to prevent the dot products from getting too large (which would make softmax too 'sharp')"
        >√d<sub>k</sub></span
      >)<span
        class="eq-term"
        data-term="V2"
        data-explain="Multiply by values — weight each word's information by how relevant it is"
        >V</span
      >
    </div>
  </div>

  <div class="eq-plain-english">
    <span class="eq-label">PLAIN ENGLISH</span>
    <p>
      "For every word, ask 'which other words are relevant to me?' Score all
      pairs, normalize the scores to sum to 1, then use those scores to create a
      weighted mix of everyone's information."
    </p>
  </div>

  <div class="eq-step-through">
    <button class="eq-step-btn active" data-highlight="attention">
      Full equation
    </button>
    <button class="eq-step-btn" data-highlight="Q">
      Q — what am I looking for?
    </button>
    <button class="eq-step-btn" data-highlight="K">
      K — what do I contain?
    </button>
    <button class="eq-step-btn" data-highlight="V">
      V — my actual information
    </button>
    <button class="eq-step-btn" data-highlight="QK">
      QK<sup>T</sup> — relevance scores
    </button>
    <button class="eq-step-btn" data-highlight="sqrt">
      ÷ √d — scaling factor
    </button>
  </div>

  <div class="eq-tooltip" id="eq-tooltip" style="display: none;"></div>
</div>
```

### CSS

```css
.equation-walkthrough {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  margin: var(--space-8) 0;
}

.eq-header {
  margin-bottom: var(--space-6);
}

.eq-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  font-weight: 600;
}

.eq-display {
  background: var(--color-bg-code);
  border-radius: var(--radius-md);
  padding: var(--space-8) var(--space-6);
  text-align: center;
  margin: var(--space-4) 0;
}

.eq-formula {
  font-size: clamp(1rem, 3vw, 1.5rem);
  color: #cdd6f4;
  font-family: var(--font-mono);
  line-height: 2;
  word-spacing: 0.2em;
}

.eq-term {
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all var(--duration-fast);
  position: relative;
}

.eq-term:hover,
.eq-term.highlighted {
  background: rgba(137, 180, 250, 0.2);
  color: #89b4fa;
}

.eq-plain-english {
  background: var(--color-surface-warm);
  border-left: 3px solid var(--color-accent);
  padding: var(--space-4) var(--space-6);
  margin: var(--space-4) 0;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.eq-step-through {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.eq-step-btn {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.eq-step-btn:hover,
.eq-step-btn.active {
  border-color: var(--color-accent);
  background: var(--color-accent-light);
  color: var(--color-accent);
}

@media (max-width: 768px) {
  .eq-formula {
    font-size: 0.9rem;
    word-spacing: 0.1em;
  }
  .eq-step-through {
    flex-direction: column;
  }
}
```

### JS

```javascript
document.querySelectorAll(".eq-step-btn").forEach((btn) => {
  btn.addEventListener("click", function () {
    const walkthrough = this.closest(".equation-walkthrough");
    walkthrough
      .querySelectorAll(".eq-step-btn")
      .forEach((b) => b.classList.remove("active"));
    this.classList.add("active");

    const target = this.dataset.highlight;
    walkthrough.querySelectorAll(".eq-term").forEach((term) => {
      term.classList.toggle(
        "highlighted",
        target === "attention" || term.dataset.term === target,
      );
    });
  });
});

document.querySelectorAll(".eq-term").forEach((term) => {
  term.addEventListener("mouseenter", function () {
    const tooltip = this.closest(".equation-walkthrough").querySelector(
      ".eq-tooltip",
    );
    if (!tooltip) return;
    tooltip.textContent = this.dataset.explain;
    const rect = this.getBoundingClientRect();
    const parent = this.closest(
      ".equation-walkthrough",
    ).getBoundingClientRect();
    tooltip.style.top = rect.bottom - parent.top + 8 + "px";
    tooltip.style.left = rect.left - parent.left + "px";
    tooltip.style.display = "block";
  });

  term.addEventListener("mouseleave", function () {
    const tooltip = this.closest(".equation-walkthrough").querySelector(
      ".eq-tooltip",
    );
    if (tooltip) tooltip.style.display = "none";
  });
});
```

---

## Results Comparator

Interactive sortable table of experimental results. The reader can sort by any metric, highlight the paper's model, and visually compare against baselines.

### HTML

```html
<div class="results-comparator animate-in">
  <div class="rc-header">
    <span class="eq-label">RESULTS COMPARATOR</span>
    <h3>Performance Comparison</h3>
    <p class="rc-hint">
      Click any column header to sort. The paper's model is highlighted.
    </p>
  </div>

  <div class="rc-table-wrapper">
    <table class="rc-table" id="results-table">
      <thead>
        <tr>
          <th data-sort="name" class="sortable">Model ↕</th>
          <th data-sort="accuracy" class="sortable">Accuracy ↕</th>
          <th data-sort="f1" class="sortable">F1 Score ↕</th>
          <th data-sort="params" class="sortable">Parameters ↕</th>
          <th data-sort="latency" class="sortable">Latency (ms) ↕</th>
        </tr>
      </thead>
      <tbody>
        <tr class="rc-baseline">
          <td>Baseline A</td>
          <td data-value="91.2">91.2%</td>
          <td data-value="89.5">89.5</td>
          <td data-value="110">110M</td>
          <td data-value="45">45ms</td>
        </tr>
        <tr class="rc-ours">
          <td><strong>This Paper</strong></td>
          <td data-value="94.3"><strong>94.3%</strong></td>
          <td data-value="92.8"><strong>92.8</strong></td>
          <td data-value="85">85M</td>
          <td data-value="32"><strong>32ms</strong></td>
        </tr>
        <!-- more rows -->
      </tbody>
    </table>
  </div>

  <div class="rc-context">
    <div class="callout callout-insight">
      <span class="callout-icon">📊</span>
      <div class="callout-content">
        <strong>What the numbers mean</strong>
        <p>
          [Contextual interpretation — e.g., "A 3.1% accuracy improvement on
          this benchmark means approximately X in real-world terms..."]
        </p>
      </div>
    </div>
  </div>
</div>
```

### CSS

```css
.results-comparator {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  margin: var(--space-8) 0;
}

.rc-hint {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  font-style: italic;
}

.rc-table-wrapper {
  overflow-x: auto;
  margin: var(--space-4) 0;
}

.rc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.rc-table th {
  background: var(--color-bg-code);
  color: #cdd6f4;
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.rc-table th:hover {
  background: #2a2a3e;
}

.rc-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
}

.rc-ours {
  background: var(--color-accent-light);
  border-left: 3px solid var(--color-accent);
}

.rc-ours td {
  color: var(--color-accent);
  font-weight: 600;
}

.rc-baseline td {
  color: var(--color-text-secondary);
}

.rc-table th.sort-asc::after {
  content: " ▲";
}
.rc-table th.sort-desc::after {
  content: " ▼";
}
```

### JS

```javascript
document.querySelectorAll(".rc-table .sortable").forEach((th) => {
  th.addEventListener("click", function () {
    const table = this.closest("table");
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const colIndex = Array.from(this.parentNode.children).indexOf(this);
    const isAsc = this.classList.contains("sort-asc");

    table.querySelectorAll("th").forEach((h) => {
      h.classList.remove("sort-asc", "sort-desc");
    });

    this.classList.add(isAsc ? "sort-desc" : "sort-asc");

    rows.sort((a, b) => {
      const aParsed = parseFloat(a.children[colIndex].dataset.value);
      const bParsed = parseFloat(b.children[colIndex].dataset.value);
      const aVal = isNaN(aParsed) ? a.children[colIndex].textContent : aParsed;
      const bVal = isNaN(bParsed) ? b.children[colIndex].textContent : bParsed;
      if (typeof aVal === "number" && typeof bVal === "number") {
        return isAsc ? bVal - aVal : aVal - bVal;
      }
      return isAsc
        ? bVal.toString().localeCompare(aVal.toString())
        : aVal.toString().localeCompare(bVal.toString());
    });

    rows.forEach((row) => tbody.appendChild(row));
  });
});
```

---

## Assumption Audit Cards

Flippable cards that reveal assumptions the paper makes, why they're made, and what breaks if they're wrong.

### HTML

```html
<div class="assumption-audit animate-in">
  <div class="aa-header">
    <span class="eq-label">ASSUMPTION AUDIT</span>
    <h3>What This Paper Takes for Granted</h3>
    <p>Click each card to flip it and see the full analysis.</p>
  </div>

  <div class="aa-grid">
    <div class="aa-card" onclick="flipCard(this)">
      <div class="aa-card-inner">
        <div class="aa-card-front">
          <span class="aa-number">A1</span>
          <h4>Data is i.i.d.</h4>
          <p class="aa-hint">Tap to analyze →</p>
        </div>
        <div class="aa-card-back">
          <div class="aa-section">
            <strong>The assumption:</strong>
            <p>
              Training and test data come from the same distribution, and
              samples are independent.
            </p>
          </div>
          <div class="aa-section">
            <strong>Why they make it:</strong>
            <p>
              Standard ML assumption. Required for their theoretical guarantees
              on generalization bounds.
            </p>
          </div>
          <div class="aa-section aa-danger">
            <strong>What breaks if it's wrong:</strong>
            <p>
              Distribution shift in production would degrade the reported 94.3%
              accuracy significantly. The paper does not test for this.
            </p>
          </div>
        </div>
      </div>
    </div>
    <!-- more cards -->
  </div>
</div>
```

### CSS

```css
.aa-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
  margin: var(--space-6) 0;
}

.aa-card {
  perspective: 1000px;
  cursor: pointer;
  height: 280px;
}

.aa-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s var(--ease-out);
  transform-style: preserve-3d;
}

.aa-card.flipped .aa-card-inner {
  transform: rotateY(180deg);
}

.aa-card-front,
.aa-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: var(--radius-md);
  padding: var(--space-6);
  overflow-y: auto;
}

.aa-card-front {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  box-shadow: var(--shadow-md);
}

.aa-card-back {
  background: var(--color-bg-code);
  color: #cdd6f4;
  transform: rotateY(180deg);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

.aa-number {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-accent);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: var(--space-2);
}

.aa-hint {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-4);
}

.aa-section {
  margin-bottom: var(--space-3);
}

.aa-section strong {
  color: #89b4fa;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.aa-danger strong {
  color: #f38ba8;
}
```

### JS

```javascript
window.flipCard = function (card) {
  card.classList.toggle("flipped");
};
```

---

## Method Pipeline Diagram

Interactive step-by-step visualization of the paper's methodology. Click each step to see details and the data transformation.

### HTML

```html
<div class="method-pipeline animate-in">
  <div class="mp-header">
    <span class="eq-label">METHOD PIPELINE</span>
    <h3>How the Model Works</h3>
  </div>

  <div class="mp-steps">
    <div class="mp-step active" data-step="0" onclick="selectStep(this)">
      <div class="mp-step-icon" style="background: var(--color-actor-1)">1</div>
      <div class="mp-step-label">Input</div>
    </div>
    <div class="mp-connector"></div>
    <div class="mp-step" data-step="1" onclick="selectStep(this)">
      <div class="mp-step-icon" style="background: var(--color-actor-2)">2</div>
      <div class="mp-step-label">Encoder</div>
    </div>
    <div class="mp-connector"></div>
    <div class="mp-step" data-step="2" onclick="selectStep(this)">
      <div class="mp-step-icon" style="background: var(--color-actor-3)">3</div>
      <div class="mp-step-label">Attention</div>
    </div>
    <div class="mp-connector"></div>
    <div class="mp-step" data-step="3" onclick="selectStep(this)">
      <div class="mp-step-icon" style="background: var(--color-actor-4)">4</div>
      <div class="mp-step-label">Output</div>
    </div>
  </div>

  <div class="mp-detail" id="mp-detail">
    <div class="mp-detail-content" data-for="0">
      <h4>Step 1: Input Processing</h4>
      <p>Raw text is tokenized and converted to embeddings...</p>
      <div class="mp-data-shape">
        <span class="eq-label">DATA SHAPE</span>
        <code
          >Input: (batch_size, seq_length) → Embeddings: (batch_size,
          seq_length, d_model)</code
        >
      </div>
    </div>
    <!-- more detail panels -->
  </div>
</div>
```

### CSS

```css
.mp-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin: var(--space-8) 0;
  flex-wrap: wrap;
}

.mp-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast);
}

.mp-step:hover,
.mp-step.active {
  background: var(--color-accent-light);
}

.mp-step-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
  font-size: var(--text-lg);
  font-family: var(--font-display);
  transition: transform var(--duration-fast);
}

.mp-step.active .mp-step-icon {
  transform: scale(1.15);
  box-shadow: 0 0 0 4px var(--color-accent-light);
}

.mp-step-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
}

.mp-connector {
  width: 40px;
  height: 2px;
  background: var(--color-border);
  position: relative;
}

.mp-connector::after {
  content: "→";
  position: absolute;
  right: -4px;
  top: -9px;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.mp-detail {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  min-height: 120px;
}

.mp-data-shape {
  background: var(--color-bg-code);
  border-radius: var(--radius-sm);
  padding: var(--space-3) var(--space-4);
  margin-top: var(--space-3);
}

.mp-data-shape code {
  color: #a6e3a1;
  font-size: var(--text-sm);
}

@media (max-width: 768px) {
  .mp-steps {
    flex-direction: column;
  }
  .mp-connector {
    width: 2px;
    height: 24px;
  }
  .mp-connector::after {
    content: "↓";
    right: -6px;
    top: 4px;
  }
}
```

### JS

```javascript
window.selectStep = function (stepEl) {
  const pipeline = stepEl.closest(".method-pipeline");
  pipeline
    .querySelectorAll(".mp-step")
    .forEach((s) => s.classList.remove("active"));
  stepEl.classList.add("active");

  const stepIndex = stepEl.dataset.step;
  const detail = pipeline.querySelector(".mp-detail");
  const panels = detail.querySelectorAll(".mp-detail-content");
  panels.forEach((p) => {
    p.style.display = p.dataset.for === stepIndex ? "block" : "none";
  });
};
```

---

## Citation Context Cards

When the paper cites an important related work, show a compact card with context — but ONLY information stated in the current paper. Never fabricate descriptions of cited works.

### HTML

```html
<div class="citation-card animate-in">
  <div class="cc-header">
    <span class="cc-ref">[Vaswani et al., 2017]</span>
    <span class="cc-venue">NeurIPS 2017</span>
  </div>
  <div class="cc-body">
    <div class="cc-section">
      <strong>Cited for:</strong>
      <p>
        Introducing the self-attention mechanism and Transformer architecture
        used as the backbone in this paper.
      </p>
    </div>
    <div class="cc-section">
      <strong>How this paper builds on it:</strong>
      <p>
        Extends the original attention mechanism with [modification described in
        current paper].
      </p>
    </div>
  </div>
</div>
```

### CSS

```css
.citation-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-5);
  margin: var(--space-4) 0;
  box-shadow: var(--shadow-sm);
}

.cc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.cc-ref {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-accent);
}

.cc-venue {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.cc-section {
  margin-bottom: var(--space-2);
}

.cc-section strong {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
}

.cc-section p {
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}
```

---

## Ablation Explorer

Interactive toggle where readers can "remove" model components and see the performance impact. Makes abstract ablation tables tangible.

### HTML

```html
<div class="ablation-explorer animate-in">
  <div class="abl-header">
    <span class="eq-label">ABLATION EXPLORER</span>
    <h3>What Happens Without Each Component?</h3>
    <p>Toggle components off to see how performance changes.</p>
  </div>

  <div class="abl-controls">
    <label class="abl-toggle">
      <input
        type="checkbox"
        checked
        data-component="attention"
        data-impact="-4.2"
        onchange="updateAblation()"
      />
      <span class="abl-toggle-label">Self-Attention</span>
      <span class="abl-impact" data-for="attention">−4.2%</span>
    </label>
    <label class="abl-toggle">
      <input
        type="checkbox"
        checked
        data-component="residual"
        data-impact="-2.8"
        onchange="updateAblation()"
      />
      <span class="abl-toggle-label">Residual Connections</span>
      <span class="abl-impact" data-for="residual">−2.8%</span>
    </label>
    <label class="abl-toggle">
      <input
        type="checkbox"
        checked
        data-component="layernorm"
        data-impact="-1.5"
        onchange="updateAblation()"
      />
      <span class="abl-toggle-label">Layer Normalization</span>
      <span class="abl-impact" data-for="layernorm">−1.5%</span>
    </label>
  </div>

  <div class="abl-result">
    <div class="abl-bar-container">
      <div class="abl-bar-bg">
        <div class="abl-bar-fill" id="abl-bar" style="width: 100%">
          <span class="abl-bar-label" id="abl-label">94.3%</span>
        </div>
      </div>
      <div class="abl-baseline-marker">
        <span>Full model: 94.3%</span>
      </div>
    </div>
  </div>
</div>
```

### CSS

```css
.ablation-explorer {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  margin: var(--space-8) 0;
}

.abl-controls {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin: var(--space-6) 0;
}

.abl-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.abl-toggle:hover {
  border-color: var(--color-accent-muted);
}

.abl-toggle input[type="checkbox"] {
  width: 20px;
  height: 20px;
  accent-color: var(--color-accent);
}

.abl-toggle-label {
  flex: 1;
  font-weight: 500;
}

.abl-impact {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-error);
  opacity: 0;
  transition: opacity var(--duration-fast);
}

.abl-toggle input:not(:checked) ~ .abl-impact {
  opacity: 1;
}

.abl-bar-container {
  margin-top: var(--space-4);
  position: relative;
}

.abl-bar-bg {
  width: 100%;
  height: 40px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.abl-bar-fill {
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--color-accent),
    var(--color-accent-hover)
  );
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: var(--space-4);
  transition: width var(--duration-slow) var(--ease-out);
}

.abl-bar-label {
  font-family: var(--font-mono);
  font-weight: 700;
  color: white;
  font-size: var(--text-sm);
}

.abl-baseline-marker {
  text-align: right;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
  font-family: var(--font-mono);
}
```

### JS

```javascript
window.updateAblation = function () {
  const explorer = document.querySelector(".ablation-explorer");
  const checkboxes = explorer.querySelectorAll('input[type="checkbox"]');
  const baseAccuracy = 94.3;
  let totalImpact = 0;

  checkboxes.forEach((cb) => {
    if (!cb.checked) {
      totalImpact += parseFloat(cb.dataset.impact);
    }
  });

  const currentAccuracy = Math.max(0, baseAccuracy + totalImpact);
  const percentage = (currentAccuracy / baseAccuracy) * 100;

  const bar = explorer.querySelector(".abl-bar-fill");
  const label = explorer.querySelector(".abl-label");

  bar.style.width = percentage + "%";
  label.textContent = currentAccuracy.toFixed(1) + "%";

  if (currentAccuracy < baseAccuracy * 0.85) {
    bar.style.background =
      "linear-gradient(90deg, var(--color-error), #e06060)";
  } else if (currentAccuracy < baseAccuracy * 0.95) {
    bar.style.background = "linear-gradient(90deg, #d4a843, #c49530)";
  } else {
    bar.style.background =
      "linear-gradient(90deg, var(--color-accent), var(--color-accent-hover))";
  }
};
```

---

## Scale & Impact Gauge

Visual that contextualizes raw numbers from the paper into meaningful real-world terms.

### HTML

```html
<div class="scale-gauge animate-in">
  <div class="sg-header">
    <span class="eq-label">SCALE & IMPACT</span>
    <h3>Putting the Numbers in Context</h3>
  </div>

  <div class="sg-grid">
    <div class="sg-card">
      <div class="sg-icon">📊</div>
      <div class="sg-metric">3.1%</div>
      <div class="sg-label">Accuracy Improvement</div>
      <div class="sg-context">
        On a system processing 10M predictions/day, that's
        <strong>310,000 additional correct outcomes</strong> daily
      </div>
    </div>
    <div class="sg-card">
      <div class="sg-icon">⚡</div>
      <div class="sg-metric">1.4×</div>
      <div class="sg-label">Speed Improvement</div>
      <div class="sg-context">
        A query that took 45ms now takes 32ms —
        <strong>300ms saved per 10-request batch</strong>
      </div>
    </div>
    <div class="sg-card">
      <div class="sg-icon">💾</div>
      <div class="sg-metric">23%</div>
      <div class="sg-label">Fewer Parameters</div>
      <div class="sg-context">
        85M vs 110M parameters —
        <strong>fits on a single consumer GPU</strong> instead of requiring
        cloud inference
      </div>
    </div>
  </div>
</div>
```

### CSS

```css
.sg-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
  margin: var(--space-6) 0;
}

.sg-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  text-align: center;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.sg-icon {
  font-size: 2rem;
  margin-bottom: var(--space-2);
}

.sg-metric {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: 800;
  color: var(--color-accent);
  line-height: 1;
}

.sg-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  margin: var(--space-2) 0;
}

.sg-context {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-normal);
}

.sg-context strong {
  color: var(--color-text);
}
```

---

## "What the Paper Actually Says" Callout

Used for exact quotes from the paper. Distinguishes author claims from course interpretation.

### HTML

```html
<div class="paper-quote animate-in">
  <div class="pq-header">
    <span class="pq-icon">📄</span>
    <span class="pq-label">WHAT THE PAPER ACTUALLY SAYS</span>
  </div>
  <blockquote class="pq-text">
    "Our model achieves state-of-the-art results on three out of five
    benchmarks, while using 23% fewer parameters than the previous best model."
  </blockquote>
  <div class="pq-source">— Section 5.2, Results, page 7</div>
</div>
```

### CSS

```css
.paper-quote {
  background: var(--color-surface-warm);
  border-left: 4px solid var(--color-info);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: var(--space-5) var(--space-6);
  margin: var(--space-6) 0;
}

.pq-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.pq-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-info);
  font-weight: 600;
}

.pq-text {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  font-style: italic;
  color: var(--color-text);
  margin: 0;
  padding: 0;
  border: none;
}

.pq-source {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-3);
}
```

---

## "What This Course Doesn't Cover" Section

Mandatory honesty section. Every course must have one.

### HTML

```html
<div class="not-covered animate-in">
  <div class="nc-header">
    <span class="nc-icon">🚧</span>
    <h3>What This Course Doesn't Cover</h3>
    <p>In the interest of honesty, here's what we skipped or simplified:</p>
  </div>

  <div class="nc-items">
    <div class="nc-item">
      <span class="nc-category">SIMPLIFIED</span>
      <p>
        The full mathematical proof of Theorem 2 (convergence guarantee). We
        showed the intuition but omitted the formal derivation.
      </p>
    </div>
    <div class="nc-item">
      <span class="nc-category">NOT VERIFIED</span>
      <p>
        The paper's claim about performance on non-English datasets. We couldn't
        verify the exact numbers from the supplementary materials.
      </p>
    </div>
    <div class="nc-item">
      <span class="nc-category">OUT OF SCOPE</span>
      <p>
        Comparison with concurrent work published after this paper. The
        landscape has evolved since publication.
      </p>
    </div>
  </div>
</div>
```

### CSS

```css
.not-covered {
  background: var(--color-bg-warm);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin: var(--space-8) 0;
}

.nc-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.nc-item {
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  padding: var(--space-4) var(--space-5);
  box-shadow: var(--shadow-sm);
}

.nc-category {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  margin-bottom: var(--space-2);
  display: inline-block;
}

.nc-category:nth-child(1) {
  background: var(--color-info-light);
  color: var(--color-info);
}
.nc-category.simplified {
  background: var(--color-info-light);
  color: var(--color-info);
}
.nc-category.not-verified {
  background: #fff3cd;
  color: #856404;
}
.nc-category.out-of-scope {
  background: #f0f0f0;
  color: #666;
}
```
