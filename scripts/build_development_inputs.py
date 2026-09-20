#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
from cstt import alfworld_objective_from_task_id, build_pair_record  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def demonstration(data_root: Path, entry: dict) -> dict:
    trajectory_path = (data_root / entry["gamefile"]).with_name("traj_data.json")
    trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
    annotation = trajectory["turk_annotations"]["anns"][0]
    actions = []
    for item in trajectory["plan"]["high_pddl"]:
        discrete = item["discrete_action"]
        name = str(discrete["action"])
        args = [str(value) for value in discrete.get("args", [])]
        actions.append(f"{name}({', '.join(args)})")
    return {
        **entry,
        "task_description": str(annotation["task_desc"]),
        "actions": actions,
        "evidence_source": "official ALFRED high-level successful plan",
        "trajectory_sha256": digest(trajectory_path),
    }


def target_record(data_root: Path, entry: dict) -> dict:
    """Read target language only; never serialize its expert action plan."""
    trajectory_path = (data_root / entry["gamefile"]).with_name("traj_data.json")
    trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
    annotation = trajectory["turk_annotations"]["anns"][0]
    reconstructed = alfworld_objective_from_task_id(entry["task_id"])
    return {
        **entry,
        "task_description": str(annotation["task_desc"]),
        "reconstructed_objective": reconstructed,
        "target_input_source": "human task annotation only; expert plan not serialized",
        "trajectory_sha256": digest(trajectory_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "configs/development.json")
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text())
    manifest_path = (PROJECT / config["manifest"]).resolve()
    inventory_path = (PROJECT / config["inventory"]).resolve()
    manifest = json.loads(manifest_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    data_root = Path(os.environ["ALFWORLD_DATA"])
    source_entries = [
        {
            "task_id": row["task_id"],
            "family": row["family"],
            "gamefile": row["task_id"],
        }
        for row in inventory["tasks"]
        if row["environment"] == "alfworld"
        and row["official_split"] == "train"
        and row["family"] in config["families"]
    ]
    roster_path = None
    if "target_roster" in config:
        roster_path = (PROJECT / config["target_roster"]).resolve()
        roster = json.loads(roster_path.read_text())
        targets = [
            {"task_id": row["task_id"], "family": row["family"], "gamefile": row["task_id"]}
            for row in roster["targets"]
        ]
    else:
        targets = []
        for family in config["families"]:
            family_targets = [row for row in manifest["alfworld"]["dev"] if row["family"] == family]
            if len(family_targets) < config["tasks_per_family"]:
                raise ValueError(f"Insufficient development targets for {family}")
            targets.extend(family_targets[: config["tasks_per_family"]])
    source_ids = {row["task_id"] for row in source_entries}
    if source_ids & {row["task_id"] for row in targets}:
        raise ValueError("Source/target overlap")
    sources = [demonstration(data_root, row) for row in source_entries]
    records = []
    for target in targets:
        target_with_text = target_record(data_root, target)
        records.append(build_pair_record(target_with_text, sources))
    output = PROJECT / config["output_dir"]
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "evidence": config["evidence"],
        "config_sha256": digest(config_path),
        "manifest_sha256": digest(manifest_path),
        "inventory_sha256": digest(inventory_path),
        "target_roster_sha256": digest(roster_path) if roster_path else None,
        "source_count": len(sources),
        "target_count": len(records),
        "records": records,
    }
    (output / "pairs.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    runtime_payload = {
        **{key: value for key, value in payload.items() if key != "records"},
        "information_boundary": (
            "target identity plus source IDs, lexical scores, entity-free skill text, and procedural contracts only"
        ),
        "records": [
            {
                "target": {
                    key: pair["target"][key]
                    for key in ("task_id", "family", "gamefile")
                },
                "sources": {
                    condition: {
                        key: source[key]
                        for key in ("task_id", "lexical_similarity", "procedural_contract", "skill_text")
                    }
                    for condition, source in pair["sources"].items()
                },
            }
            for pair in records
        ],
    }
    (output / "runtime_pairs.json").write_text(json.dumps(runtime_payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output / "pairs.json"), "targets": len(records)}, indent=2))


if __name__ == "__main__":
    main()
