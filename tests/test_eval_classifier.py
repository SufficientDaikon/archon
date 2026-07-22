"""Tests for archon eval classifier — log summarization and drift replay.

Assertions run against the pure evaluate_classifier() function (commands
produce data; rendering is presentation). One CLI-level test covers the
no-records exit code.
"""

import json
from datetime import datetime, timezone

import pytest
from typer.testing import CliRunner

from archon.cli import app
from archon.commands.eval_cmd import evaluate_classifier

runner = CliRunner()


def write_log(home, records):
    logs = home / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    path = logs / f"hooks-{today}.jsonl"
    with open(path, "a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record) + "\n")


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("ARCHON_HOME", str(tmp_path))
    return tmp_path


def router_record(tier, prompt=None, truncated=False, synapses=None):
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "hook": "prompt_router",
        "event": "UserPromptSubmit",
        "project": "test-12345678",
        "duration_ms": 5,
        "ok": True,
        "tier": tier,
        "mode": "direct",
        "skills": [],
        "synapses": synapses or [],
        "word_count": 3,
        "preview": (prompt or "some prompt here")[:80],
    }
    if prompt is not None:
        record["stripped_prompt"] = prompt
        record["prompt_truncated"] = truncated
    return record


class TestEvaluateClassifier:
    def test_no_records_returns_none(self, home):
        assert evaluate_classifier(home / "logs", days=30) is None

    def test_cli_exits_nonzero_without_records(self, home):
        result = runner.invoke(app, ["eval", "classifier"])
        assert result.exit_code == 1

    def test_summary_reports_distribution(self, home):
        write_log(
            home,
            [
                router_record("TRIVIAL"),
                router_record("TRIVIAL"),
                router_record("COMPLEX", synapses=["metacognition", "anti-rationalization"]),
                {"hook": "guard_bash", "decision": "allow"},  # non-router: ignored
            ],
        )
        data = evaluate_classifier(home / "logs", days=30)
        assert data["records"] == 3
        assert data["tier_distribution"] == {"TRIVIAL": 2, "COMPLEX": 1}
        assert data["synapse_activation"] == {"metacognition": 1, "anti-rationalization": 1}

    def test_drift_replay_detects_change(self, home):
        # Logged as COMPLEX but the prompt is trivially short -> current
        # classifier disagrees -> drift entry.
        write_log(home, [router_record("COMPLEX", prompt="hi there")])
        data = evaluate_classifier(home / "logs", days=30)
        assert data["replayed"] == 1
        assert len(data["drift"]) == 1
        assert data["drift"][0]["old_tier"] == "COMPLEX"
        assert data["drift"][0]["new_tier"] == "TRIVIAL"

    def test_matching_tier_no_drift(self, home):
        write_log(home, [router_record("TRIVIAL", prompt="hi there")])
        data = evaluate_classifier(home / "logs", days=30)
        assert data["replayed"] == 1
        assert data["drift"] == []

    def test_truncated_prompts_skipped_not_replayed(self, home):
        # A truncated prompt must never be replayed — it would fake drift.
        write_log(
            home,
            [
                router_record("EXPERT", prompt="hi", truncated=True),
                router_record("TRIVIAL"),
            ],
        )
        data = evaluate_classifier(home / "logs", days=30)
        assert data["replayed"] == 0
        assert data["skipped_not_stored"] == 2
        assert data["drift"] == []

    def test_old_logs_outside_window_ignored(self, home):
        logs = home / "logs"
        logs.mkdir(parents=True)
        (logs / "hooks-2020.01.01.jsonl").write_text(
            json.dumps(router_record("EXPERT")) + "\n", encoding="utf-8"
        )
        assert evaluate_classifier(logs, days=7) is None

    def test_corrupt_lines_skipped(self, home):
        write_log(home, [router_record("TRIVIAL")])
        logs = home / "logs"
        today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
        with open(logs / f"hooks-{today}.jsonl", "a", encoding="utf-8") as fh:
            fh.write("not json at all\n")
        data = evaluate_classifier(logs, days=30)
        assert data["records"] == 1
