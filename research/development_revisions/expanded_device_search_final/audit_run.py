#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SKILL_CONDITIONS = {"matched_near", "matched_far", "lure_near", "lure_far"}


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def action_state(value: dict) -> dict:
    """Exclude locations inferred from the next turn's newly visible actions."""
    return {key: item for key, item in value.items() if key != "known_target_locations"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--require-no-target-plan", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    output = PROJECT / config["output_dir"]
    pairs_path = (PROJECT / config["pairs_path"]).resolve() if "pairs_path" in config else output / "pairs.json"
    pairs = json.loads(pairs_path.read_text())
    episodes = rows(output / "episodes.jsonl")
    pair_by_task = {row["target"]["task_id"]: row for row in pairs["records"]}
    expected = {
        (task_id, condition)
        for task_id in pair_by_task
        for condition in config["conditions"]
    }
    observed = [(row["task_id"], row["condition"]) for row in episodes]
    failures: list[str] = []
    if len(observed) != len(set(observed)) or set(observed) != expected:
        failures.append("coverage_or_uniqueness")
    for task_id, pair in pair_by_task.items():
        if args.require_no_target_plan and any(key in pair["target"] for key in ("actions", "plan", "gold_plan")):
            failures.append(f"target_plan_exposed:{task_id}")
    initial_by_task: dict[str, str] = {}
    turns_checked = 0
    for episode in episodes:
        task_id, condition = episode["task_id"], episode["condition"]
        pair = pair_by_task[task_id]
        previous = initial_by_task.setdefault(task_id, episode["initial_state_sha256"])
        if previous != episode["initial_state_sha256"]:
            failures.append(f"initial_state_mismatch:{task_id}")
        if len(episode["turns"]) != episode["steps"]:
            failures.append(f"turn_count:{task_id}:{condition}")
        if condition in SKILL_CONDITIONS:
            source = pair["sources"][condition]
            if episode["source_task_id"] != source["task_id"] or episode["source_contract"] != source["procedural_contract"]:
                failures.append(f"source_mismatch:{task_id}:{condition}")
            if episode["source_task_id"] == task_id or "/train/" not in episode["source_task_id"]:
                failures.append(f"source_overlap_or_split:{task_id}:{condition}")
        elif episode["source_task_id"] is not None or episode["source_contract"] is not None:
            failures.append(f"control_received_source:{task_id}:{condition}")
        prior_after = None
        for turn in episode["turns"]:
            turns_checked += 1
            executor = turn["executor"]
            admissible = set(turn["admissible_actions"])
            candidates = set(executor["candidates"])
            rejected = {row["action"] for row in executor["rejected"]}
            if not candidates <= admissible or turn["action"] not in candidates:
                failures.append(f"non_native_action:{task_id}:{condition}:{turn['turn']}")
            if candidates & rejected or candidates | rejected != admissible:
                failures.append(f"filter_partition:{task_id}:{condition}:{turn['turn']}")
            state_on_entry = executor.get("state_on_entry", executor["state_before"])
            if prior_after is not None and action_state(prior_after) != action_state(state_on_entry):
                failures.append(f"state_chain:{task_id}:{condition}:{turn['turn']}")
            if "state_after_observation" in executor:
                before_locations = set(state_on_entry["known_target_locations"])
                after_locations = set(executor["state_after_observation"]["known_target_locations"])
                if not before_locations <= after_locations:
                    failures.append(f"observation_state:{task_id}:{condition}:{turn['turn']}")
            prior_after = executor["state_after"]
    result = {
        "status": "pass" if not failures else "fail",
        "episodes": len(episodes),
        "target_blocks": len(pair_by_task),
        "turns_checked": turns_checked,
        "all_initial_states_matched": not any(value.startswith("initial_state_mismatch") for value in failures),
        "all_actions_native": not any(value.startswith("non_native_action") for value in failures),
        "candidate_partitions_complete": not any(value.startswith("filter_partition") for value in failures),
        "source_assignments_valid": not any(
            value.startswith(("source_mismatch", "source_overlap_or_split", "control_received_source"))
            for value in failures
        ),
        "target_plan_absent_required": args.require_no_target_plan,
        "failures": sorted(set(failures)),
    }
    (output / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
