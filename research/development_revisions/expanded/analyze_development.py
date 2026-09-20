#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "configs/development.json")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    output = PROJECT / config["output_dir"]
    pairs = json.loads((output / "pairs.json").read_text())
    records = rows(output / "episodes.jsonl")
    expected = {
        (pair["target"]["task_id"], condition)
        for pair in pairs["records"]
        for condition in config["conditions"]
    }
    keys = [(row["task_id"], row["condition"]) for row in records]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("Incomplete or duplicate target-condition coverage")
    by_task: dict[str, dict[str, dict]] = defaultdict(dict)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in records:
        if len(row["turns"]) != row["steps"] or not row["turns"]:
            raise ValueError("Incomplete raw episode")
        grouped[row["condition"]].append(row)
        by_task[row["task_id"]][row["condition"]] = row
    if any(len({row["initial_state_sha256"] for row in block.values()}) != 1 for block in by_task.values()):
        raise ValueError("Initial-state mismatch")
    summary = {
        condition: {
            "tasks": len(group),
            "successes": sum(row["success"] for row in group),
            "success_rate": sum(row["success"] for row in group) / len(group),
            "mean_score": sum(row["score"] for row in group) / len(group),
            "steps": sum(row["steps"] for row in group),
            "input_tokens": sum(row["input_tokens"] for row in group),
            "output_tokens": sum(row["output_tokens"] for row in group),
        }
        for condition, group in grouped.items()
    }
    causal_control = config.get("causal_control", "no_skill")
    causal = {}
    for condition in config["conditions"]:
        if condition == causal_control:
            continue
        helpful = harmful = redundant = shared_failure = 0
        by_family: dict[str, list[int]] = defaultdict(list)
        for block in by_task.values():
            candidate, control = block[condition], block[causal_control]
            delta = int(candidate["success"]) - int(control["success"])
            helpful += delta > 0
            harmful += delta < 0
            redundant += candidate["success"] and control["success"]
            shared_failure += not candidate["success"] and not control["success"]
            by_family[candidate["family"]].append(delta)
        total = len(by_task)
        causal[condition] = {
            "helpful": helpful,
            "harmful": harmful,
            "redundant_success": redundant,
            "shared_failure": shared_failure,
            "net_causal_effect": (helpful - harmful) / total,
            "harm_rate": harmful / total,
            "net_by_family": {family: sum(values) / len(values) for family, values in by_family.items()},
        }
    gain = summary["matched_far"]["success_rate"] - summary["lure_near"]["success_rate"]
    family_advantage = {}
    for block in by_task.values():
        family = block["matched_far"]["family"]
        family_advantage.setdefault(family, []).append(
            int(block["matched_far"]["success"]) - int(block["lure_near"]["success"])
        )
    result = {
        "status": "development_complete",
        "summary": summary,
        "causal_control": causal_control,
        "causal_vs_control": causal,
        "matched_far_minus_lure_near": gain,
        "matched_far_minus_lure_near_by_family": {
            family: sum(values) / len(values) for family, values in family_advantage.items()
        },
        "all_initial_states_matched": True,
        "confirmation_claim_permitted": False,
    }
    if causal_control == "no_skill":
        result["causal_vs_no_skill"] = causal
    (output / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
