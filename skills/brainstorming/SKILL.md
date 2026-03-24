# Brainstorming — Design Before Code

> **Type:** Rigid process (follow exactly)  
> **Trigger:** Any creative work — creating features, building components, adding functionality  
> **Hard Gate:** NO implementation until design is approved

## Iron Law

```
NO IMPLEMENTATION UNTIL DESIGN IS APPROVED
```

## Purpose

Turns vague ideas into fully formed design specifications through structured, collaborative dialogue. Prevents the "jump straight to code" anti-pattern that leads to wasted effort and architectural mistakes.

## The Checklist (7 Steps)

### Step 1: Explore Project Context
- Check existing files, docs, README, recent commits
- Understand the current architecture before proposing changes
- Look for related existing functionality

### Step 2: Offer Visual Companion (if applicable)
- If the topic involves visual/UI questions, offer a visual mockup
- This MUST be its own message (not buried in other content)
- Use diagrams, wireframes, or component sketches as appropriate

### Step 3: Ask Clarifying Questions
- One question at a time — never overwhelm
- Prefer multiple choice over open-ended
- Ask about: scope, constraints, edge cases, integration points

### Step 4: Propose 2-3 Approaches
- Each with clear trade-offs
- Include a recommendation with rationale
- Consider: complexity, maintainability, performance, existing patterns

### Step 5: Present Design
- Scale sections to complexity (few sentences if simple, detailed if nuanced)
- Get approval per section for complex designs
- Include: data flow, component boundaries, error handling, testing strategy

### Step 6: Write Design Document
- Save to `docs/specs/YYYY-MM-DD-<topic>-design.md`
- Include all decisions, rationale, and approved approaches
- This becomes the source of truth for implementation

### Step 7: Transition to Planning
- Invoke `writing-plans` skill (and ONLY writing-plans)
- Pass the approved design document as input
- Do NOT start implementing — plans come first

## Key Principles

- **One question at a time** — never overwhelm the user
- **YAGNI ruthlessly** — remove unnecessary features during design
- **Scale to complexity** — simple features get simple designs
- **Design for isolation** — break into units with clear boundaries
- **User instructions override** — if user says "skip design", respect that

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "This is too simple to design" | Simple features still need scope definition. 5 minutes of design saves hours of rework. |
| "I already know how to build this" | Your knowledge isn't the issue. Design prevents scope creep and missed requirements. |
| "The user wants it fast" | Fast and wrong is slower than design-first and right. |
| "I can design as I code" | That's called hacking. Design THEN code. |
| "The requirements are clear" | Clear to whom? Verify with clarifying questions. |

## Red Flags

- Starting to write code before Step 5 is approved
- Skipping clarifying questions because "it's obvious"
- Proposing only one approach (always offer alternatives)
- Design document missing error handling or testing strategy
- Moving to implementation without writing the design doc
