"""The doctor --hooks diagnostic matrix must itself be green in CI."""

from archon.core.hook_diagnostics import CHECKS, run_diagnostics


def test_all_diagnostics_pass():
    results = run_diagnostics()
    failures = [f"{r.name}: {r.detail}" for r in results if not r.passed]
    assert not failures, "hook diagnostics failed:\n" + "\n".join(failures)


def test_matrix_covers_every_hook():
    covered = {check.script for check in CHECKS}
    expected = {
        "session_boot.py",
        "prompt_router.py",
        "guard_bash.py",
        "guard_write.py",
        "quality_bash.py",
        "quality_write.py",
        "completion_gate.py",
        "todo_track.py",
        "agent_context.py",
        "session_end.py",
        "pre_compact.py",
    }
    assert expected <= covered, f"uncovered hooks: {expected - covered}"


def test_result_shape_is_stable():
    results = run_diagnostics()
    assert results, "no results returned"
    for r in results:
        assert isinstance(r.name, str) and r.name
        assert isinstance(r.passed, bool)
        assert isinstance(r.detail, str)
