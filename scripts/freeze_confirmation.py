#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_task_ids(value: Any, found: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "task_id" and isinstance(item, str) and item.startswith("json_2.1.1/"):
                found.add(item)
            collect_task_ids(item, found)
    elif isinstance(value, list):
        for item in value:
            collect_task_ids(item, found)


def ids_in_file(path: Path) -> set[str]:
    found: set[str] = set()
    try:
        if path.suffix == ".jsonl":
            with path.open(encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if line.strip():
                        collect_task_ids(json.loads(line), found)
        else:
            collect_task_ids(json.loads(path.read_text(encoding="utf-8")), found)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return set()
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text())
    gate_path = (PROJECT / config["development_gate"]).resolve()
    gate = json.loads(gate_path.read_text())
    if gate["status"] != "pass" or not gate["confirmation_may_be_opened"]:
        raise RuntimeError("Development gate did not authorize confirmation selection")

    excluded: set[str] = set()
    evidence_files = []
    for root_name in config["evidence_roots"]:
        root = (PROJECT / root_name).resolve()
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in {".json", ".jsonl"}:
                continue
            found = {
                task_id for task_id in ids_in_file(path)
                if "/valid_seen/" in task_id or "/valid_unseen/" in task_id
            }
            if found:
                excluded.update(found)
                evidence_files.append({
                    "path": str(path.relative_to(PROJECT.parent)),
                    "sha256": digest(path),
                    "target_ids_found": len(found),
                })

    inventory_path = (PROJECT / config["inventory"]).resolve()
    inventory = json.loads(inventory_path.read_text())
    eligible = [
        row for row in inventory["tasks"]
        if row["environment"] == "alfworld"
        and row["official_split"] in config["eligible_splits"]
        and row["family"] in config["families"]
        and row["task_id"] not in excluded
    ]
    family_quotas = config["family_quotas"]
    if set(family_quotas) != set(config["families"]):
        raise ValueError("family_quotas must cover exactly the configured families")
    selected = []
    for family in config["families"]:
        candidates = [row for row in eligible if row["family"] == family]
        candidates.sort(key=lambda row: hashlib.sha256(
            f"{config['selection_salt']}\0{row['task_id']}".encode()
        ).hexdigest())
        quota = family_quotas[family]
        if len(candidates) < quota:
            raise RuntimeError(f"Only {len(candidates)} untouched targets remain for {family}")
        selected.extend(candidates[:quota])

    output = (PROJECT / config["output_dir"]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    exclusion_payload = {
        "prior_target_count": len(excluded),
        "prior_target_ids": sorted(excluded),
        "evidence_files": evidence_files,
    }
    exclusions_path = output / "excluded_prior_targets.json"
    exclusions_path.write_text(json.dumps(exclusion_payload, ensure_ascii=False, indent=2) + "\n")
    roster = {
        "status": "frozen_confirmation_roster",
        "frozen_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "selection_rule": "lowest salted SHA-256 within family after evidence exclusions",
        "selection_salt": config["selection_salt"],
        "family_quotas": family_quotas,
        "allocation_note": config["allocation_note"],
        "target_count": len(selected),
        "split_counts": dict(Counter(row["official_split"] for row in selected)),
        "family_counts": dict(Counter(row["family"] for row in selected)),
        "config_sha256": digest(config_path),
        "inventory_sha256": digest(inventory_path),
        "development_gate_sha256": digest(gate_path),
        "exclusions_sha256": digest(exclusions_path),
        "method_hashes": {
            name: digest((PROJECT / name).resolve()) for name in config["method_files"]
        },
        "targets": selected,
    }
    roster_path = output / "roster.json"
    roster_path.write_text(json.dumps(roster, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in roster.items() if key != "targets"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
