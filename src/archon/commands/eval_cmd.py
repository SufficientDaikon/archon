"""``archon eval`` — evaluate hook-layer behavior from the invocation logs.

The miniature ADK-eval: ``archon eval classifier`` summarizes how the
classifier behaved on real prompts (tier distribution, synapse activation)
and — for log records that stored the full stripped prompt
(``logging/log_prompts=true``, untruncated) — replays them through the
CURRENT classifier to report drift after tuning. Truncated prompts are never
replayed: their word count differs, so replaying them would fabricate drift.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import typer

from archon.core.hooks_bridge import HooksBridgeError, load_shared
from archon.utils.output import (
    console,
    is_json,
    json_envelope,
    make_table,
    print_error,
    print_json,
)
from archon.utils.paths import get_archon_home

eval_app = typer.Typer(help="Evaluate hook-layer behavior from invocation logs.")


def _load_router_records(logs_dir: Path, days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    records: list[dict] = []
    if not logs_dir.is_dir():
        return records
    for path in sorted(logs_dir.glob("hooks-*.jsonl")):
        try:
            stamp = datetime.strptime(path.stem, "hooks-%Y.%m.%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if stamp < cutoff - timedelta(days=1):
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("hook") == "prompt_router":
                    records.append(record)
        except OSError:
            continue
    return records


def evaluate_classifier(logs_dir: Path, days: int) -> dict | None:
    """Pure evaluation: summarize router records and replay stored prompts.

    Returns the result dict, or None when no records exist. Separated from
    the command so it is testable without console capture (commands produce
    data; presentation is a separate concern).
    """
    records = _load_router_records(logs_dir, days)
    if not records:
        return None

    tiers = Counter(r.get("tier", "?") for r in records)
    synapse_counts: Counter = Counter()
    for r in records:
        synapse_counts.update(r.get("synapses", []))

    # Drift replay: only untruncated stored prompts are honest to re-classify
    replayable = [
        r for r in records if r.get("stripped_prompt") and not r.get("prompt_truncated", False)
    ]
    skipped = len(records) - len(replayable)
    drift: list[dict] = []
    replay_error = ""
    if replayable:
        try:
            classifier = load_shared("classifier")
            for r in replayable:
                new_tier = classifier.classify_complexity(r["stripped_prompt"])
                if new_tier != r.get("tier"):
                    drift.append(
                        {
                            "preview": r.get("preview", "")[:60],
                            "old_tier": r.get("tier", "?"),
                            "new_tier": new_tier,
                        }
                    )
        except HooksBridgeError as exc:
            replay_error = str(exc)

    return {
        "records": len(records),
        "days": days,
        "tier_distribution": dict(tiers),
        "synapse_activation": dict(synapse_counts),
        "replayed": len(replayable),
        "skipped_not_stored": skipped,
        "drift": drift,
        "replay_error": replay_error or None,
    }


@eval_app.command("classifier")
def classifier_cmd(
    days: int = typer.Option(30, "--days", help="How many days of logs to evaluate."),
) -> None:
    """Summarize classifier behavior; replay stored prompts to detect drift."""
    data = evaluate_classifier(get_archon_home() / "logs", days)

    if data is None:
        print_error(
            f"No prompt_router log records in the last {days} day(s). "
            "Hook logging fills them in as you work (logging/enabled)."
        )
        raise typer.Exit(1)

    tiers = Counter(data["tier_distribution"])
    synapse_counts = Counter(data["synapse_activation"])
    replayable_count = data["replayed"]
    skipped = data["skipped_not_stored"]
    drift = data["drift"]
    replay_error = data["replay_error"] or ""
    records_count = data["records"]

    if is_json():
        print_json(json_envelope(command="eval", data=data))
        return

    console.print()
    console.rule("[bold cyan]Classifier Evaluation[/bold cyan]")
    console.print(f"  {records_count} classification(s) in the last {days} day(s)")
    console.print()

    total = sum(tiers.values())
    tier_rows = [
        [tier, str(count), f"{count / total:.0%}"]
        for tier, count in sorted(tiers.items(), key=lambda kv: -kv[1])
    ]
    console.print(
        make_table("Tier distribution", [("Tier", "bold"), ("N", ""), ("%", "")], tier_rows)
    )
    console.print()

    if synapse_counts:
        syn_rows = [
            [synapse, str(count), f"{count / total:.0%}"]
            for synapse, count in sorted(synapse_counts.items(), key=lambda kv: -kv[1])
        ]
        console.print(
            make_table(
                "Synapse activation",
                [("Synapse", "bold"), ("N", ""), ("% of prompts", "")],
                syn_rows,
            )
        )
        console.print()

    if replay_error:
        console.print(f"  [yellow]⚠[/yellow] Replay unavailable: {replay_error}")
    elif replayable_count:
        console.print(
            f"  Drift replay: {replayable_count} prompt(s) re-classified with the current "
            f"classifier, {len(drift)} changed tier, {skipped} skipped (prompt not stored)."
        )
        if drift:
            console.print(
                make_table(
                    "Tier drift",
                    [("Prompt", "dim"), ("Was", "bold"), ("Now", "bold")],
                    [[d["preview"], d["old_tier"], d["new_tier"]] for d in drift[:20]],
                )
            )
    else:
        console.print(
            f"  Drift replay: 0 replayable records ({skipped} skipped — full prompts are "
            "stored only with logging/log_prompts=true)."
        )
    console.print()
