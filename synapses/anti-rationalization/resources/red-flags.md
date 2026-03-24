# Red Flag Thoughts — Quick Reference Checklist

When you catch yourself thinking ANY of these, **STOP** and apply the enforcement protocol.

## 🚩 Testing Red Flags
- [ ] "This is simple enough to skip testing"
- [ ] "I'll add tests later"
- [ ] "The existing tests probably cover this"
- [ ] "Manual testing is sufficient here"
- [ ] "Testing this would be too complex"

## 🚩 Debugging Red Flags
- [ ] "I know what the bug is" (without evidence)
- [ ] "Let me just quickly fix this"
- [ ] "It must be a race condition"
- [ ] "The library has a bug, not my code"
- [ ] "This error message doesn't make sense"

## 🚩 Verification Red Flags
- [ ] "I just checked this"
- [ ] "This should work"
- [ ] "I'm pretty sure this is correct"
- [ ] "The CI/CD will catch any issues"
- [ ] "It compiled/ran without errors"

## 🚩 Planning Red Flags
- [ ] "This is straightforward, no need to plan"
- [ ] "The requirements are obvious"
- [ ] "Let's figure it out as we go"
- [ ] "This is just a quick change"
- [ ] "We don't need a spec for this"

## 🚩 Scope Red Flags
- [ ] "The user probably doesn't need this"
- [ ] "This is good enough"
- [ ] "Close enough"
- [ ] "We can always add this later"
- [ ] "That's out of scope" (without spec reference)

## 🚩 Quality Red Flags
- [ ] "Nobody will notice"
- [ ] "It works, that's what matters"
- [ ] "We can refactor later"
- [ ] "This is just a prototype"
- [ ] "It's just a small change"

## Response Protocol

When a red flag is detected:
1. **STOP** the current action
2. **NAME** the red flag thought
3. **IDENTIFY** which Iron Law it violates
4. **CORRECT** with the proper action
5. **RESUME** with the correct approach
