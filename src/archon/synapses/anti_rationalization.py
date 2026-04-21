import re

IRON_LAWS = [
    ("should", "Blocked: provide verification method"),
    ("probably", "Blocked: guess detected"),
    ("close enough", "Blocked: exact or not done"),
    ("simple enough to skip", "Blocked: all steps required"),
]

def validate(context):
    text = (context.get("reasoning", "") + " " + context.get("task", "")).lower()
    violations = [rule for phrase, rule in IRON_LAWS if phrase in text]
    if violations:
        return {"action": "halt", "message": f"Blocked: {len(violations)} violation(s)", "violations": violations}
    return {"action": "allow", "message": "OK", "violations": []}
