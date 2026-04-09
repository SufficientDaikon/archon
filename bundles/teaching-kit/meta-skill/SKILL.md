# teaching-expert

**Meta-Skill Coordinator for Adaptive Teaching and Course Generation**

## Purpose

Orchestrates a comprehensive teaching toolkit that adapts to the learner and the source material. Covers live interactive tutoring with real-time level calibration, automated course generation from codebases, academic research papers, and pull requests. All delivery modes are ADHD-friendly with anti-hallucination guardrails and support for Egyptian Arabic.

## Teaching Modes

The teaching system routes based on content source and delivery mode:

```
1. LIVE TUTORING         -> adaptive-teacher
2. CODEBASE COURSES      -> codebase-to-course
3. RESEARCH PAPER COURSES -> research-paper-to-course
4. PR-BASED COURSES      -> pr-to-course
```

---

## Routing Logic

### 1. Live Interactive Tutoring -> **adaptive-teacher**

**Trigger keywords:** teach me, explain, tutor, help me understand, Socratic, level calibration, concept explanation, Egyptian Arabic, reverse prompting

**Use when:**
- Real-time concept explanation and tutoring
- Socratic questioning to test understanding
- Adaptive level calibration (beginner to expert)
- Reverse prompting to verify comprehension
- Teaching with Egyptian colloquial Arabic
- Explaining complex concepts interactively
- One-on-one adaptive instruction

**Deliverable:** Interactive teaching session with level-adapted explanations

**Example requests:**
- "Teach me about dependency injection"
- "Explain how React hooks work"
- "Help me understand this algorithm"
- "Tutor me on database normalization"
- "Explain this in Egyptian Arabic"

---

### 2. Codebase-to-Course Generation -> **codebase-to-course**

**Trigger keywords:** codebase course, repository walkthrough, code tour, architecture course, visual walkthrough, code analysis course

**Use when:**
- Generating courses from repository or codebase analysis
- Creating visual walkthroughs of code architecture
- Building structured learning paths from code structure
- Analyzing code patterns and generating teaching material
- Creating module-by-module course outlines

**Deliverable:** Structured course with visual walkthroughs derived from codebase analysis

**Example requests:**
- "Create a course from this repository"
- "Generate a walkthrough of this codebase"
- "Build a learning path for this project's architecture"
- "Turn this codebase into teaching material"
- "Create a visual tour of this codebase"

---

### 3. Research Paper-to-Course Generation -> **research-paper-to-course**

**Trigger keywords:** paper course, research paper, academic paper, equation translation, assumption audit, results comparison, paper walkthrough

**Use when:**
- Converting academic papers into accessible courses
- Translating mathematical equations into intuitive explanations
- Auditing paper assumptions for the learner
- Comparing results across related papers
- Building progressive disclosure courses from dense research

**Deliverable:** Accessible course with equation translation and assumption auditing

**Example requests:**
- "Turn this research paper into a course"
- "Explain this paper's methodology"
- "Create a learning module from this paper"
- "Break down the math in this paper"
- "Compare these two papers' approaches"

---

### 4. PR-to-Course Generation -> **pr-to-course**

**Trigger keywords:** PR course, pull request learning, before/after, behavior matrix, PR walkthrough, code review course, diff analysis

**Use when:**
- Creating learning material from pull requests
- Building before/after visualizations of changes
- Generating behavior matrices from diffs
- Teaching code review practices via real PRs
- Creating courses from significant architectural PRs

**Deliverable:** PR-based course with before/after visualization and behavior matrices

**Example requests:**
- "Create a course from this pull request"
- "Turn this PR into a learning module"
- "Build a walkthrough of this PR's changes"
- "Generate a before/after comparison from this diff"
- "Create a code review course from these PRs"

---

## Core Teaching Workflows

### Live Learning Session
```
adaptive-teacher (calibrate level)
    |
adaptive-teacher (teach concept with Socratic method)
    |
adaptive-teacher (verify with reverse prompting)
    |
DONE or CONTINUE (next concept)
```

### Codebase Learning Path
```
codebase-to-course (analyze and generate course)
    |
adaptive-teacher (live Q&A on course material)
    |
DONE
```

### Paper Study Session
```
research-paper-to-course (generate accessible course)
    |
adaptive-teacher (interactive deep-dive on confusing sections)
    |
DONE
```

### PR Review Learning
```
pr-to-course (generate PR walkthrough)
    |
adaptive-teacher (explain decisions and tradeoffs)
    |
DONE
```

---

## Decision Tree

```
What is the learning context?

+-- LIVE EXPLANATION OR CONCEPT TEACHING?
|   -> adaptive-teacher
|
+-- LEARNING FROM A CODEBASE?
|   -> codebase-to-course
|
+-- LEARNING FROM A RESEARCH PAPER?
|   -> research-paper-to-course
|
+-- LEARNING FROM A PULL REQUEST?
|   -> pr-to-course
|
+-- COURSE + INTERACTIVE FOLLOW-UP?
    -> [appropriate course skill] THEN adaptive-teacher
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **Concept Question** | Live tutoring | adaptive-teacher |
| **Repository Provided** | Generate course | codebase-to-course |
| **Paper Provided** | Generate course | research-paper-to-course |
| **PR Provided** | Generate course | pr-to-course |
| **Course Generated** | Interactive Q&A | adaptive-teacher |
| **Confusion Detected** | Re-explain adaptively | adaptive-teacher |
| **Egyptian Arabic Requested** | Switch language mode | adaptive-teacher |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **Live Teaching** | adaptive-teacher | - | - |
| **Codebase Learning** | codebase-to-course | adaptive-teacher | - |
| **Paper Learning** | research-paper-to-course | adaptive-teacher | - |
| **PR Learning** | pr-to-course | adaptive-teacher | - |
| **Mixed (Course + Q&A)** | [course skill] | adaptive-teacher | - |

---

## Quality Gates

### Gate 1: Level Calibration
- **Checked by:** adaptive-teacher
- **Criteria:** Learner level accurately assessed, explanations match level, no condescension or over-complexity
- **Pass -> Teaching is effective**

### Gate 2: Course Completeness
- **Checked by:** codebase-to-course / research-paper-to-course / pr-to-course
- **Criteria:** All major sections covered, visual aids included, progressive disclosure used, ADHD-friendly format
- **Pass -> Course ready for delivery**

### Gate 3: Anti-Hallucination
- **Checked by:** All skills
- **Criteria:** No fabricated facts, code examples verified against source, equations match original paper, PR diffs accurate
- **Pass -> Content is trustworthy**

---

## Input/Output Contracts

### adaptive-teacher
- **Input:** Concept or topic, learner level (auto-detected or specified), language preference
- **Output:** Adaptive explanation with Socratic questions and reverse prompts

### codebase-to-course
- **Input:** Repository path or URL, scope (full or specific modules)
- **Output:** Structured course with visual walkthroughs and module breakdown

### research-paper-to-course
- **Input:** Paper content or URL, focus areas
- **Output:** Accessible course with equation translation, assumption audit, and results comparison

### pr-to-course
- **Input:** PR diff or URL, context about the codebase
- **Output:** PR walkthrough with before/after visualization and behavior matrix

---

## Cross-Skill Dependencies

- **research-paper-to-course** shares the design system with **codebase-to-course** -- visual output format is consistent
- **adaptive-teacher** is the universal follow-up -- any course skill can hand off to it for interactive Q&A

---

## Notes for AI Assistants

- **adaptive-teacher is the default** for any "explain" or "teach" request
- **Course skills are source-specific** -- match the skill to the content source
- **Always offer interactive follow-up** via adaptive-teacher after course generation
- **ADHD-friendly means:** short sections, visual anchors, progressive disclosure, no walls of text
- **Anti-hallucination is non-negotiable** -- never fabricate examples or misquote papers
- **Egyptian Arabic is fully supported** in adaptive-teacher with technical code-switching
- **Consult each SKILL.md** before applying skill knowledge
