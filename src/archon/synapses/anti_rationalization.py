"""Anti-rationalization synapse — forbidden-phrase detection (Iron Laws)."""

IRON_LAWS = [
    ("probably", "Blocked: guess detected — remove or provide evidence"),
    ("close enough", "Blocked: exact or not done"),
    ("simple enough to skip", "Blocked: complexity doesn't excuse steps"),
    ("just a", "Blocked: size doesn't predict impact"),
    ("will add later", "Blocked: technical debt — do it now"),
]


def validate(context):
    text = (context.get("reasoning", "") + " " + context.get("task", "")).lower()
    violations = [rule for phrase, rule in IRON_LAWS if phrase in text]
    if violations:
        return {
            "action": "halt",
            "message": f"Rationalization detected: {len(violations)} Iron Law violation(s)",
            "violations": violations,
        }
    return {"action": "allow", "message": "No rationalization detected", "violations": []}
