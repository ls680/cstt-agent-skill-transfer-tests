#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = PROJECT / "data/confirmation"
    roster = json.loads((data / "roster.json").read_text())
    excluded = set(json.loads((data / "excluded_prior_targets.json").read_text())["prior_target_ids"])
    full = json.loads((data / "pairs.json").read_text())
    runtime = json.loads((data / "runtime_pairs.json").read_text())
    roster_ids = [row["task_id"] for row in roster["targets"]]
    expected_family_counts = roster["family_quotas"]
    observed_family_counts = Counter(row["family"] for row in roster["targets"])
    expected_target_count = sum(expected_family_counts.values())
    failures = []
    if len(roster_ids) != expected_target_count or len(roster_ids) != len(set(roster_ids)):
        failures.append("roster_size_or_uniqueness")
    if excluded & set(roster_ids):
        failures.append("prior_evidence_overlap")
    if dict(observed_family_counts) != expected_family_counts:
        failures.append("family_quota")
    full_by_id = {row["target"]["task_id"]: row for row in full["records"]}
    runtime_by_id = {row["target"]["task_id"]: row for row in runtime["records"]}
    if set(full_by_id) != set(roster_ids) or set(runtime_by_id) != set(roster_ids):
        failures.append("pair_roster_mismatch")
    for task_id in roster_ids:
        pair = full_by_id[task_id]
        runtime_pair = runtime_by_id[task_id]
        if any(key in pair["target"] for key in ("actions", "plan", "gold_plan")):
            failures.append(f"target_plan_serialized:{task_id}")
        if set(runtime_pair["target"]) != {"task_id", "family", "gamefile"}:
            failures.append(f"runtime_target_surface:{task_id}")
        for condition, source in pair["sources"].items():
            if "/train/" not in source["task_id"] or source["task_id"] == task_id:
                failures.append(f"invalid_source:{task_id}:{condition}")
            runtime_source = runtime_pair["sources"][condition]
            expected_keys = {"task_id", "lexical_similarity", "procedural_contract", "skill_text"}
            if set(runtime_source) != expected_keys:
                failures.append(f"runtime_source_surface:{task_id}:{condition}")
        if pair["sources"]["matched_near"]["family"] != pair["target"]["family"]:
            failures.append(f"near_procedure_mismatch:{task_id}")
        if pair["sources"]["matched_far"]["family"] != pair["target"]["family"]:
            failures.append(f"far_procedure_mismatch:{task_id}")
        if pair["sources"]["lure_near"]["family"] == pair["target"]["family"]:
            failures.append(f"near_lure_not_mismatched:{task_id}")
        if pair["sources"]["lure_far"]["family"] == pair["target"]["family"]:
            failures.append(f"far_lure_not_mismatched:{task_id}")
        if pair["sources"]["matched_near"]["lexical_similarity"] < pair["sources"]["matched_far"]["lexical_similarity"]:
            failures.append(f"matched_similarity_order:{task_id}")
        if pair["sources"]["lure_near"]["lexical_similarity"] < pair["sources"]["lure_far"]["lexical_similarity"]:
            failures.append(f"lure_similarity_order:{task_id}")
        if pair["sources"]["matched_near"]["procedural_contract"] != pair["sources"]["matched_far"]["procedural_contract"]:
            failures.append(f"matched_contract_disagreement:{task_id}")
        if pair["sources"]["matched_far"]["procedural_contract"] == pair["sources"]["lure_near"]["procedural_contract"]:
            failures.append(f"lure_contract_not_contrastive:{task_id}")
    result = {
        "status": "pass" if not failures else "fail",
        "roster_tasks": len(roster_ids),
        "prior_evidence_overlap": len(excluded & set(roster_ids)),
        "family_counts": dict(observed_family_counts),
        "expected_family_counts": expected_family_counts,
        "full_pairs_sha256": digest(data / "pairs.json"),
        "runtime_pairs_sha256": digest(data / "runtime_pairs.json"),
        "runtime_information_boundary": runtime["information_boundary"],
        "failures": sorted(set(failures)),
    }
    (data / "input_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
