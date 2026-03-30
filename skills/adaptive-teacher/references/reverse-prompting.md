# Reverse Prompting Reference

Complete taxonomy, implementation patterns, and escalation protocols for reverse prompting — the technique where the AI asks the learner questions instead of giving answers.

## Table of Contents

1. [Why Reverse Prompting Works](#why-reverse-prompting-works)
2. [The 5 Prompt Types (Full Taxonomy)](#the-5-prompt-types)
3. [Escalation Protocol](#escalation-protocol)
4. [Response Handling Patterns](#response-handling-patterns)
5. [Anti-Patterns](#anti-patterns)
6. [Advanced Techniques](#advanced-techniques)
7. [Examples by Topic](#examples-by-topic)

---

## Why Reverse Prompting Works

### The Science

Three cognitive science principles underpin reverse prompting:

1. **Testing Effect (Roediger & Karpicke, 2006):** Retrieving information from memory strengthens that memory more than re-studying it. When the AI asks a question, the learner must RETRIEVE — even if they retrieve incorrectly, the act of trying primes the neural pathways for the correct answer.

2. **Generation Effect (Slamecka & Graf, 1978):** Information that a person generates themselves (even partially) is remembered better than information they receive passively. A learner who says "I think it's because the server checks the token..." remembers better than one who reads "the server checks the token."

3. **Desirable Difficulty (Bjork, 1994):** Learning conditions that make initial performance slower actually produce BETTER long-term retention. Reverse prompting feels harder than reading an explanation — that difficulty IS the learning.

### The Practical Benefit

For AI-assisted learning specifically, reverse prompting solves the **passive consumption problem.** When an AI explains something, the learner nods along. When an AI asks something, the learner ENGAGES. The difference in retention is enormous.

---

## The 5 Prompt Types

### Type 1: Prediction Prompt

**Purpose:** Prime the learner's brain before introducing new information. Their attempt to predict — even if wrong — creates a "hook" for the correct answer to attach to.

**When to use:**

- Before explaining a new concept
- Before showing what a piece of code does
- Before revealing how a system works

**Template:**

> "Before I explain — what do you THINK [X] does? Just from [clue 1] and [clue 2], take a guess."

**Examples:**

For code:

> "Look at this function called `debounceSearch`. Based on the name alone — what do you think it does? What might 'debounce' mean?"

For systems:

> "When you type a URL and hit enter, what do you think happens in the next 500 milliseconds? Walk me through your best guess."

For concepts:

> "The word 'middleware' has 'middle' in it. Before I explain — what do you think is in the 'middle' of what?"

**Difficulty level:** Low pressure. Great for L1-L2 learners. The question has no "wrong" answer because you're asking for a guess.

**After their response:**

- If close: "You're closer than you think! You said [X]. The real answer is [Y]. Notice how [X and Y are connected]."
- If off: "Interesting guess! Here's what actually happens — [explain]. The reason your guess was off is [specific gap]."
- If correct: "Exactly right. Now the harder question — WHY does it work that way?"

---

### Type 2: Decision Prompt

**Purpose:** Force the learner to weigh tradeoffs, consider constraints, and make engineering decisions. This builds architectural thinking.

**When to use:**

- Teaching design patterns or architecture
- When there are genuine tradeoffs to consider
- When you want the learner to think like a tech lead

**Template:**

> "You're the tech lead. The team asks you: should we [option A] or [option B]? You have [constraint 1] and [constraint 2]. What's your call, and why?"

**Examples:**

Architecture:

> "Your app needs to send email notifications. Option A: send the email immediately when the event happens. Option B: add it to a queue and process it later. You have 1,000 users. Which do you choose and why?"

Caching:

> "You're building a news feed. Option A: cache the entire feed for each user (fast reads, complex invalidation). Option B: build the feed fresh on every request (always fresh, slower). Your users check the feed 50 times a day but new posts only appear 5 times a day. Which approach?"

Security:

> "You need to store user passwords. Option A: encrypt them (reversible). Option B: hash them (irreversible). Think about what you need to DO with passwords — do you ever need to get the original back?"

**Difficulty level:** Medium-high. Best for L3-L4 learners.

**After their response:**

- If they pick correctly with good reasoning: "Solid thinking. You mentioned [their reasoning]. Let me add one more consideration: [extension]."
- If they pick correctly with weak reasoning: "Right answer, but I want to push you on the WHY. You said [their reason]. What about [stronger reason they missed]?"
- If they pick incorrectly: "I see your logic — [validate their reasoning]. But here's the factor you're missing: [key insight]. With that in mind, would you change your answer?"

---

### Type 3: Debug Prompt

**Purpose:** Build systematic debugging intuition. The learner must reason from symptoms to causes without seeing the code.

**When to use:**

- Teaching troubleshooting methodology
- After explaining how a system works (now test if they can reason about failures)
- Building "when X breaks, check Y" intuition

**Template:**

> "A user reports: [symptom]. You can't look at the code yet. Based on what you know about [the system], where would you look FIRST and why?"

**Examples:**

API debugging:

> "A user says the app shows 'loading...' forever but there are no error messages. Based on what you know about how the frontend calls the backend — what are the three most likely causes?"

State management:

> "A user clicks 'save' and sees a success message, but when they reload the page, their changes are gone. Walk me through the data flow and tell me where the break probably is."

Performance:

> "The app works fine with 10 users but becomes unusably slow with 100. No errors, just slow. What would you investigate?"

**Difficulty level:** High. Best for L3-L5 learners. Requires synthesizing system knowledge.

**After their response:**

- If systematic: "Excellent debugging instinct. You went from [outer layer] to [inner layer] — that's exactly how senior engineers think. The answer here was [X]."
- If they jump to a specific guess: "Interesting — you jumped straight to [their guess]. That's possible, but a more systematic approach would be [framework]. Try: 'Is the request leaving the client? Is it reaching the server? Is the server responding?'"
- If stuck: "No worries — this is hard. Let's break it down. Step 1: Is the problem in the frontend, the backend, or the network? How would you tell?"

---

### Type 4: Teach-Back Prompt

**Purpose:** Maximum learning retention. Teaching something forces you to organize your understanding, identify gaps, and articulate clearly. If you can't teach it, you don't truly understand it.

**When to use:**

- After explaining a concept (verification)
- At the end of a module (consolidation)
- When you suspect the learner memorized but didn't understand

**Template:**

> "Explain [concept] to me as if I'm [persona]. Use your own words — don't repeat what I said."

**Persona options (vary these):**

- "...as if I'm your teammate who missed the meeting"
- "...as if I'm a smart friend who's never written code"
- "...as if you're writing a tweet about it (280 characters)"
- "...as if you're adding a comment in the code for the next developer"
- "...as if I'm 10 years old" (forces extreme simplification)

**Examples:**

> "Explain what an API does to me as if I'm your non-technical friend who just asked 'what do you do at work?'"

> "In one sentence (tweet-length), explain why we use environment variables instead of putting secrets directly in code."

> "You're onboarding a new teammate. They ask: 'Why is the codebase split into all these folders? Why not just put everything in one file?' What do you tell them?"

**Difficulty level:** Very high (cognitively demanding). Best after Prediction or Decision prompts have warmed up. Works for all levels — just adjust the teaching target.

**After their response:**

- Strong explanation: "That's clearer than how I explained it. I especially liked [specific thing they said]. One tiny addition: [extension]."
- Partial understanding: "Good start! You nailed [part 1]. But notice you didn't mention [part 2]. Why do you think that part matters?"
- Memorized, not understood: "I notice you used my exact words. Let me try this: forget everything I said. In YOUR language, from YOUR experience — what is this thing?"

---

### Type 5: What-If Prompt

**Purpose:** Build mental models by exploring consequences. When you ask "what if X changed?", the learner must simulate the system in their head — which means they need to UNDERSTAND the system, not just know facts about it.

**When to use:**

- Deepening understanding after the basics are established
- Testing whether they understand dependencies between parts
- Building intuition about system fragility and resilience

**Template:**

> "What would happen if we [changed/removed/doubled/reversed X]? Walk me through the consequences."

**Examples:**

Removal:

> "What if we deleted the middleware that checks authentication? What would happen — and what wouldn't change?"

Scaling:

> "What if instead of 100 users, you had 1 million? Which part of this architecture breaks FIRST?"

Reversal:

> "What if we moved this logic from the server to the client? What would we gain and what would we lose?"

Edge case:

> "What happens if two users try to edit the same document at the exact same millisecond? Walk me through it."

**Difficulty level:** Highest. Requires deep system understanding. Best for L3-L5.

**After their response:**

- Good analysis: "You traced the consequences correctly. Notice you identified [N] things that would break. Let me add one more you might have missed: [subtle dependency]."
- Surface-level: "You said 'it would break.' I need more. HOW would it break? What's the first error the user would see? What would the logs show?"
- Creative answer: "I hadn't thought of that angle! You're right that [their insight]. That actually connects to a pattern called [pattern name]."

---

## Escalation Protocol

Within a session, escalate reverse prompt types gradually:

```
Session Start
  └── Prediction Prompts (warm-up, low pressure)
       └── Decision Prompts (engage reasoning)
            └── Debug Prompts (apply knowledge)
                 └── What-If Prompts (deepen understanding)
                      └── Teach-Back Prompts (consolidate)
```

**Do not jump levels.** A learner who can't predict what a function does (Type 1) will not benefit from a "what would happen if we removed the database" question (Type 5).

**Exception:** If the learner is L4-L5, you can start at Decision or Debug level. They don't need warm-up.

---

## Response Handling Patterns

### The Validation Sandwich

When a learner answers ANY reverse prompt:

1. **Validate something** — find what's right or reasonable in their answer
2. **Correct/extend** — fill the gap or fix the misconception
3. **Bridge forward** — connect to the next question or concept

**Example:**

> Learner: "I think the API sends data to the database directly."
>
> You: "You're right that data ends up in the database — good instinct. (1-Validate) But there's actually a layer in between: the API sends data to a service layer that validates and transforms it before it touches the database. Think of it like a quality inspector at a factory — nothing goes to storage without being checked first. (2-Correct) So now I'm curious — what kinds of things would the service layer check before saving? (3-Bridge)"

### Handling "I Don't Know"

Never punish "I don't know." It's honest and valuable:

1. "That's totally fair — this is new territory. Let me give you a clue: [hint]."
2. "Good — that tells me we need to back up one step. Let me ask an easier version: [simpler question]."
3. "No worries. Let's approach it differently. [Switch from abstract to concrete example]."

NEVER: "Come on, we just covered this!" or "Think harder!" or any dismissive response.

### Handling Confident Wrong Answers

This is the most delicate situation. The learner thinks they're right:

1. **Acknowledge the confidence:** "I can see you're sure about this — let me push back a little."
2. **Reveal the contradiction:** "If that were true, then [consequence] would have to be true too. But we know [contradictory fact]. How do you reconcile those?"
3. **Let THEM discover the error:** Guide them to the contradiction instead of declaring them wrong.

---

## Anti-Patterns

### Things to NEVER Do in Reverse Prompting

1. **The Machine Gun:** Asking 5+ questions in a row without teaching anything in between. The learner feels interrogated. **Max 2 questions before giving something of value.**

2. **The Gotcha:** Asking a question you know they can't answer just to show how much THEY don't know. Every question should be at or just above their frontier.

3. **The Fake Choice:** "Don't you think X is the best approach?" This isn't a question — it's a lecture dressed as a question. Ask genuine questions with defensible alternatives.

4. **The Rehash:** Asking them to repeat what you just said. "What did I just explain?" tests short-term memory, not understanding. Use Teach-Back instead ("Explain it in YOUR words to a DIFFERENT audience").

5. **The Avalanche:** Explaining for 500 words and then asking "does that make sense?" They'll say yes regardless. Ask SPECIFIC verification questions: "Based on what I just said, where does the token get validated — client or server?"

6. **The Dismiss:** Learner gives a wrong answer and you say "No, the answer is X." Always explain WHY their answer was wrong and connect to what they got right.

---

## Advanced Techniques

### The Deliberate Pause

After asking a reverse prompt, STOP. Do not add "for example..." or "hint..." or soften the question. End your message with the question mark. Let the silence do the work. The discomfort of not knowing IS the learning trigger.

### The Socratic Chain

Link reverse prompts into a chain where each answer feeds the next question:

> Q1: "What does this function return?"
> A1: "An array of users"
> Q2: "And if that array is empty — what happens in the component that called this?"
> A2: "Um... it would show an empty list?"
> Q3: "Close! But look at line 12 — there's no empty check. What would ACTUALLY happen?"
> A3: "Oh! It would crash because it tries to access .name on undefined"
> Q4: "Exactly. So if you were reviewing this PR, what would you flag?"

Each question builds on the previous answer, climbing toward insight.

### The Misconception Plant

Deliberately introduce a plausible but wrong explanation, then ask if they can spot the error:

> "So this middleware runs AFTER the route handler processes the request, right? ...Wait, does it? Take another look at the code and tell me if I'm wrong."

This forces them to evaluate critically instead of accepting authority.

### The Cross-Domain Bridge

After they understand concept X, ask them to find an analogy in a completely different domain:

> "You now understand how load balancing works. Can you think of a situation in everyday life that works the same way? Something where work gets distributed across multiple [things]?"

This builds transferable understanding and reveals whether they grasped the PRINCIPLE, not just the INSTANCE.

---

## Examples by Topic

### Teaching APIs

1. **Prediction:** "You want to get the weather for Cairo. If you had to describe to a computer HOW to ask for that information, what would you tell it? What details would it need?"
2. **Decision:** "Your weather app can either call the weather API every time the user opens the app, or call it once an hour and save the result. Which would you choose? Consider: the weather API charges per request."
3. **Debug:** "The weather shows 'undefined' instead of the temperature. The API is working (you tested it in the browser). What's your first guess?"
4. **What-If:** "What if the weather API goes down for 3 hours? What does your user experience? What could you have built to prevent that?"
5. **Teach-Back:** "Explain APIs to your friend who just asked 'how does the weather app know the temperature?'"

### Teaching Git

1. **Prediction:** "You and a teammate both edit the same file at the same time and try to save your changes. What do you think happens?"
2. **Decision:** "A teammate says 'let's all just push to main.' Another says 'let's use branches.' The project has 4 developers. Whose side are you on?"
3. **Debug:** "You pull the latest code and your app breaks. It worked yesterday. How do you figure out which change broke it?"
4. **What-If:** "What if there was no version control — everyone just edits files on a shared drive. What goes wrong?"
5. **Teach-Back:** "Explain branching to someone who's never used Git. Don't use the word 'branch' — use a different analogy."

### Teaching Database Design

1. **Prediction:** "You're building a bookstore app. What information would you need to save, and how would you organize it?"
2. **Decision:** "User addresses: one table (users + addresses together) or two tables (users and addresses separately)? You know users can have multiple addresses."
3. **Debug:** "Adding a book to a user's wishlist takes 5 seconds. It used to be instant. The database has 1M users now vs 1K when you built it. What's wrong?"
4. **What-If:** "What if we stored everything in one giant table — users, books, orders, reviews, all in the same table? Walk me through why that's a disaster."
5. **Teach-Back:** "Explain a database table to someone who's never seen a spreadsheet."
