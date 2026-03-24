# Receiving Code Review — The Response Protocol

> **Type:** Rigid  
> **Trigger:** When receiving review feedback, before implementing any suggestion

## Iron Law

```
NO IMPLEMENTATION BEFORE VERIFICATION — NO PERFORMATIVE AGREEMENT
```

## Purpose

Defines how to properly respond to code review feedback. Prevents the common anti-pattern of blindly agreeing with and implementing every suggestion without verifying it's correct.

## The Protocol

### Step 1: Read ALL Feedback
- Read every item completely before responding to any
- Don't start implementing after reading the first item
- Identify themes and patterns across feedback

### Step 2: Understand
For each item:
- What exactly is the reviewer suggesting?
- What problem are they identifying?
- What's the proposed solution?

### Step 3: Verify Against Codebase
For each item:
- Check the actual code — does the issue exist as described?
- Check context — is the reviewer seeing the full picture?
- Check tests — do they confirm or contradict the feedback?

### Step 4: Evaluate
For each item:
- Is this correct? (Verify, don't assume)
- Is this relevant? (Does it apply to this context?)
- Is this necessary? (YAGNI check — is it actually used?)
- Is this an improvement? (Does it make things better?)

### Step 5: Respond Technically
For each item:
- **Agree + implement**: "Fixed. [description of change]"
- **Disagree + explain**: "This doesn't apply because [technical reason]"
- **Need clarification**: "Can you clarify [specific question]?"

### Step 6: Implement One at a Time
- Fix one item → run tests → commit
- Don't batch all fixes into one commit
- If any fix breaks tests → revert → investigate

## Forbidden Phrases

| Never Say | Why | Instead Say |
|-----------|-----|-------------|
| "You're absolutely right!" | Performative agreement — you haven't verified | "Fixed. [description]" |
| "Great point!" | Flattery, not engineering | "Agreed, [technical reason]. Fixed." |
| "Thanks for catching that!" | Social pleasantry wastes tokens | "Fixed: [what changed]" |
| "I should have seen that" | Self-deprecation wastes tokens | Just fix it |
| "Absolutely, implementing now" | Agreement before verification | "Verifying... [then implement]" |

## YAGNI Check Protocol

When a reviewer suggests "implementing properly" or "adding X for robustness":
```
1. grep codebase for actual usage of the code in question
2. IF unused → "This code path isn't called anywhere. Remove it? (YAGNI)"
3. IF used → evaluate the suggestion on its merits
4. IF speculative → "This addresses a case that doesn't exist yet. Defer?"
```

## When Feedback is Unclear

If ANY item is unclear:
1. **STOP** — do not implement anything yet
2. **Collect** all unclear items
3. **Ask** about ALL unclear items in one message (not one at a time)
4. **Wait** for clarification before implementing any of them

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "The reviewer is more experienced, they must be right" | Experience doesn't mean infallibility. Verify the suggestion. |
| "It's easier to just implement it" | Easy ≠ correct. Wrong implementations create tech debt. |
| "I don't want to seem difficult" | Technical disagreement is not being difficult. It's engineering. |
| "They'll think I'm ignoring their feedback" | Verification IS respect for feedback. Blind agreement is dismissive. |
