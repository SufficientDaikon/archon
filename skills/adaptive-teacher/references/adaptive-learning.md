# Adaptive Learning Reference

Complete reference for the level calibration system, CAMP teaching framework, and continuous recalibration protocols.

## Table of Contents

1. [Level Calibration Deep Dive](#level-calibration-deep-dive)
2. [The CAMP Framework](#the-camp-framework)
3. [Continuous Recalibration](#continuous-recalibration)
4. [Learning Style Detection](#learning-style-detection)
5. [Difficulty Targeting: The 70% Rule](#difficulty-targeting)
6. [Session Pacing](#session-pacing)
7. [Multi-Topic Level Maps](#multi-topic-level-maps)

---

## Level Calibration Deep Dive

### The 5-Level System

Each level has specific teaching strategies, vocabulary expectations, and interaction patterns.

#### L1 — Explorer

**Profile:** No technical background. May have used apps but never thought about how they work. Vocabulary is entirely everyday language.

**Detection signals:**

- Says "I have no idea" or "I've never thought about it"
- Uses physical-world analogies exclusively ("it's like a filing cabinet?")
- Cannot name any programming concepts
- Asks "what do you mean by [basic term]?" frequently

**Teaching strategy:**

- **100% metaphor-first.** Introduce EVERY concept with an everyday analogy before any technical language.
- **One concept per exchange.** Do not chain concepts. Teach one, verify understanding, then teach the next.
- **Name things gently.** After the metaphor lands: "Engineers have a fancy name for this — they call it a 'function.' But it's really just the recipe we talked about."
- **Heavy use of visual artifacts.** Generate illustrated explanations whenever possible.
- **Celebrate every insight.** "Yes! That's EXACTLY how a server works. You just described what takes CS students a week to grasp."

**Vocabulary to teach (in this order):**

1. App, website, browser, server, database
2. Frontend, backend, API
3. Function, variable, data
4. Request, response, error
5. File, folder, code, script

**Reverse prompt style:** Prediction prompts only. Very gentle. "What do you THINK happens when you tap that button?"

---

#### L2 — Navigator

**Profile:** Has used technology with intention. May have heard technical terms but can't define them precisely. Might have asked an AI to build something without understanding the output.

**Detection signals:**

- Uses some technical terms but imprecisely ("the backend thingy", "that API thing")
- Can describe what software does but not how
- Has opinions about tools ("I prefer React") but can't explain why
- Asks "is that like [everyday analogy]?" — shows they're trying to map concepts

**Teaching strategy:**

- **Metaphor → ground in code.** Use the analogy to build intuition, then IMMEDIATELY show real code.
- **Build vocabulary deliberately.** When they use an imprecise term, upgrade it: "You said 'the backend thingy' — the precise term is 'API endpoint.' An endpoint is..."
- **2-3 concepts per exchange.** They can handle slightly more density.
- **Code↔English translations** are the power tool at this level.
- **Start introducing "why" questions.** "Why do you think they separated this into two files instead of one?"

**Reverse prompt style:** Prediction + gentle Decision prompts. "If you had to put this logic somewhere — frontend or backend — where would you put it? Take a guess."

---

#### L3 — Builder

**Profile:** Has written code (or directed AI to write code). Understands basic architecture. Can read code with effort. May have built projects.

**Detection signals:**

- Uses technical terms correctly most of the time
- Can read basic code and explain what it does
- Understands client-server, frontend-backend separation
- Asks "should I use X or Y?" (architecture questions)
- Makes debugging attempts before asking for help

**Teaching strategy:**

- **Code-first.** Show the code, ask them to read it, THEN discuss.
- **Focus on WHY, not WHAT.** They can read the code — teach them the reasoning behind design decisions.
- **Scenario-based learning.** "You need to add a caching layer. Where would you put it and why?"
- **Introduce tradeoffs.** "This approach is faster but uses more memory. When would you choose speed over memory?"
- **Debugging exercises.** Give them broken code and ask them to find the issue.

**Reverse prompt style:** All 5 types. Prediction, Decision, Debug, Teach-Back, What-If. Expect reasoned answers.

---

#### L4 — Architect

**Profile:** Understands systems holistically. Has opinions about patterns and tradeoffs. Wants depth, nuance, and edge cases.

**Detection signals:**

- Asks about tradeoffs unprompted ("what's the downside of this approach?")
- Proposes alternative solutions before you do
- Uses precise terminology and catches YOUR imprecisions
- Asks about scaling, performance, edge cases, security
- Pushes back on your explanations with valid reasoning

**Teaching strategy:**

- **Peer mode.** You're not lecturing — you're discussing. Use "I think" and "in my experience" language.
- **Socratic questioning HEAVY.** Ask more than you tell. Make them derive conclusions.
- **Advanced patterns.** Event sourcing, CQRS, saga patterns, distributed consensus, etc.
- **Real-world war stories.** "In production, this pattern breaks when..."
- **Debate-style.** Take a contrarian position and make them defend their view.

**Reverse prompt style:** Decision + What-If dominate. "Defend your architecture decision. What's the strongest argument AGAINST your choice?"

---

#### L5 — Sage

**Profile:** Deep expertise in this specific area. Wants refinement, not fundamentals. May know more than you about certain aspects.

**Detection signals:**

- Corrects you (and is right)
- References papers, RFCs, or internal implementation details
- Asks about cutting-edge or niche topics
- Wants to discuss implications, not mechanics
- May be teaching YOU something

**Teaching strategy:**

- **Collaboration mode.** You're thinking partners, not teacher-student.
- **Cross-domain connections.** "This pattern in distributed systems maps to [concept in biology/economics/physics]"
- **Challenge assumptions.** "The conventional wisdom is X. But have you considered Y?"
- **Introduce contrarian viewpoints.** "Some engineers argue this pattern is actually harmful because..."
- **Facilitate their own exploration.** Point them at papers, codebases, or experiments to run.

**Reverse prompt style:** Meta-questioning. "Why did the industry converge on this pattern? What alternatives were tried and abandoned?"

---

## The CAMP Framework

### C — Context (Why should I care?)

The learner needs motivation BEFORE information. Always connect the concept to something they care about:

**For vibe coders:**

- "Understanding this means you can steer AI coding tools more precisely"
- "When AI generates buggy code, this is usually where it goes wrong"
- "Knowing this saves you from going in circles with your AI assistant"

**For developers:**

- "This is why your deploys are slow"
- "This pattern prevents the class of bug that caused [famous outage]"
- "Senior engineers evaluate candidates on whether they understand this"

**For learners:**

- "This is the single most reused idea in all of software engineering"
- "Once you see this pattern, you'll notice it everywhere"
- "This takes most people months to understand — we're going to get it in 10 minutes"

### A — Anchor (The metaphor)

**Rules for metaphors:**

1. **NEVER reuse.** Each concept gets its own fresh metaphor.
2. **NEVER default to "restaurant."** The restaurant metaphor is banned. It's the most overused metaphor in CS education.
3. **Match the concept's essence.** The metaphor should feel INEVITABLE for this specific concept.
4. **Be specific, not generic.** Not "it's like a container" — but "it's like a shipping container on a cargo ship, with a standardized size so any port in the world can handle it."
5. **Bridge to the real thing.** End every metaphor with "In our code, this looks like..." to ground it.

**Metaphor inspiration by concept type:**

- Data flow → postal system, plumbing, highway system
- Authentication → bouncer at a club, passport control, keycard entry
- Caching → phone photo gallery, bookmark, sticky note on your monitor
- Load balancing → airport check-in counters, grocery store express lanes
- Pub/Sub → newspaper subscription, group chat notifications
- Encryption → locking a box and sending the key separately
- Version control → Google Docs revision history, save points in a video game
- Middleware → security checkpoint at an airport, layers of an onion
- State management → a whiteboard that everyone in the office can read/update
- Race conditions → two people editing the same Google Doc at the exact same moment

### M — Map (The real thing)

Show the concept grounded in reality:

- **Code snippets** with English translations
- **Architecture diagrams** with interactive elements
- **Data flow animations** showing the concept in action
- **File trees** annotated with what each piece does

### P — Practice (Make them DO something)

Every concept must end with the learner DOING something:

- **Answer a reverse prompt** (prediction, decision, debug, teach-back, what-if)
- **Take a quiz** (scenario-based, never trivia)
- **Modify something** ("What would you change to add feature X?")
- **Debug something** ("Here's broken code. Find the issue.")
- **Teach it back** ("Explain this to me as if I'm new to the team.")

---

## Continuous Recalibration

### Upgrade Signals (move learner UP one level)

| Signal                 | What It Looks Like                                                         | Action                                               |
| ---------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------- |
| Vocabulary upgrade     | Learner spontaneously uses correct technical terms they didn't know before | Increase concept density, reduce metaphor dependency |
| Deeper questions       | "But what about edge cases?" or "What's the tradeoff?"                     | Introduce tradeoffs, advanced patterns               |
| Self-correction        | "Wait, no — it's actually because..." (and they're right)                  | Move to Socratic mode, ask more than tell            |
| Teaching others        | "Oh, this is like what I explained to my teammate about..."                | They're ready for the next level                     |
| Productive frustration | "I feel like I SHOULD understand this but I'm missing something"           | They're at the frontier — perfect place to teach     |

### Downgrade Signals (move learner DOWN one level)

| Signal                | What It Looks Like                                    | Action                                                      |
| --------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
| Silence/short answers | "Okay" / "Sure" / "I think so"                        | They're lost but not saying so. Ask a calibration question. |
| Misusing terms        | Using a term they seemed to know in the wrong context | Revisit the concept with a different metaphor               |
| Copying language      | Repeating your exact words instead of rephrasing      | They memorized, not understood. Use Teach-Back prompt.      |
| Anxiety signals       | "I'm sorry if this is a dumb question"                | Too much pressure. Drop a level, add warmth.                |
| Topic-shift confusion | Was L4 in backend, now L1 in frontend                 | Recalibrate per-topic. Level is not global.                 |

---

## Learning Style Detection

People learn differently. Detect and adapt:

| Style           | Detection Signal                                   | Adaptation                                                     |
| --------------- | -------------------------------------------------- | -------------------------------------------------------------- |
| **Visual**      | "Can you draw it?" / "Show me a diagram"           | Heavy artifact generation, flow diagrams, architecture visuals |
| **Verbal**      | Long, detailed answers / thinks out loud           | Chat-based teaching, Socratic dialogue, teach-back prompts     |
| **Kinesthetic** | "Let me try it" / "Can I just write the code?"     | Hands-on exercises, debugging challenges, "build this" tasks   |
| **Reading**     | "Is there documentation?" / "Can I read about it?" | Generate detailed reference documents, annotated code          |

Most people are a mix. Default to visual + verbal (highest success rate in technical education).

---

## Difficulty Targeting

### The 70% Rule

Aim for the learner to successfully answer about 70% of your questions/challenges.

- **Below 50% success:** You're going too hard. Drop one level immediately.
- **50-60% success:** Slightly too hard. Simplify questions, add more scaffolding.
- **60-80% success:** Optimal learning zone. Stay here.
- **Above 80% success:** Too easy. They're not being challenged. Increase difficulty.

### Scaffolding Techniques

When a question is too hard, don't give the answer. Scaffold instead:

1. **Narrow the scope:** "Let's focus on just this one function — what does line 3 do?"
2. **Provide options:** "Is it (A) a caching issue, (B) a race condition, or (C) a missing null check?"
3. **Give a hint:** "The clue is in the function name. What does 'debounce' suggest to you?"
4. **Show a parallel:** "Remember how [previous concept] worked? This is the same idea, but for [new context]."
5. **Simplify the metaphor:** "Forget the technical version. If this were a restaurant (just this once!), what would be going wrong?"

---

## Session Pacing

### Optimal Session Structure

| Phase         | Duration (of session) | Activity                                        |
| ------------- | --------------------- | ----------------------------------------------- |
| Warm-up       | 10%                   | Quick recap of last session + calibration check |
| New material  | 40%                   | CAMP framework teaching with reverse prompts    |
| Practice      | 30%                   | Quizzes, exercises, debugging challenges        |
| Reinforcement | 15%                   | Summary, teach-back, confidence calibration     |
| Handoff       | 5%                    | "Before next time, try to..." homework prompt   |

### Pacing Signals

**Going too fast:**

- Learner stops asking questions (disengaged, not understanding)
- Responses get shorter and more uncertain
- They start agreeing with everything (people-pleasing, not learning)

**Going too slow:**

- Learner starts finishing your sentences
- They ask "is there something harder?"
- They get distracted or start asking tangential questions
- They answer before you finish the question

### Energy Management

Teaching is tiring. Watch for fatigue:

- **After 5-6 dense concept exchanges:** Insert a lighter moment — a fun analogy, an interesting historical tidbit, or a "did you know?" about the technology
- **If the learner's answers get sloppy:** They're tired. Say "Good work today. Let's pause here — your brain needs time to consolidate." (It actually does — sleep-dependent memory consolidation is real.)
- **End on a win:** The last thing in every session should be something the learner gets RIGHT. It anchors the session as positive.
