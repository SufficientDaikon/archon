import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from archon.synapses import anti_rationalization, security_awareness, metacognition

def test_anti_rat_blocks():
    result = anti_rationalization.validate({"reasoning": "This should work", "task": "fix"})
    assert result["action"] == "halt", f"Got: {result}"
    print(f"PASS: anti_rationalization blocks")

def test_anti_rat_allows():
    result = anti_rationalization.validate({"reasoning": "I verified by testing", "task": "fix"})
    assert result["action"] == "allow", f"Got: {result}"
    print(f"PASS: anti_rationalization allows")

def test_security():
    result = security_awareness.validate({"code": "password = 'secret'"})
    assert result["action"] == "halt", f"Got: {result}"
    print(f"PASS: security_awareness detects")

def test_metacognition():
    result = metacognition.validate({"has_plan": False, "complexity": "COMPLEX"})
    assert result["action"] == "halt", f"Got: {result}"
    print(f"PASS: metacognition requires plan")

if __name__ == "__main__":
    test_anti_rat_blocks()
    test_anti_rat_allows()
    test_security()
    test_metacognition()
    print("All tests passed")
