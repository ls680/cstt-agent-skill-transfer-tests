#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest


PROJECT = Path(__file__).resolve().parents[1]


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def rate(group: list[dict]) -> float:
    return sum(row["success"] for row in group) / len(group)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "configs/confirmation_analysis.json")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    pairs = json.loads((PROJECT / config["pairs_path"]).read_text())
    roster = json.loads((PROJECT / config["roster_path"]).read_text())
    task_ids = [row["task_id"] for row in roster["targets"]]
    families = list(dict.fromkeys(row["family"] for row in roster["targets"]))
    family_by_task = {row["task_id"]: row["family"] for row in roster["targets"]}
    conditions = ["no_skill", "binding_only", "matched_near", "matched_far", "lure_near", "lure_far"]
    all_rows = []
    audit_status = {}
    model_labels = []
    for config_name in config["model_configs"]:
        model_config = json.loads((PROJECT / config_name).read_text())
        label = model_config["model"]["label"]
        model_labels.append(label)
        output = PROJECT / model_config["output_dir"]
        audit = json.loads((output / "audit.json").read_text())
        audit_status[label] = audit["status"]
        for row in rows(output / "episodes.jsonl"):
            all_rows.append({**row, "model": label})

    expected = {
        (task_id, model, condition)
        for task_id in task_ids for model in model_labels for condition in conditions
    }
    keys = [(row["task_id"], row["model"], row["condition"]) for row in all_rows]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("Incomplete or duplicate confirmation coverage")
    blocks: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in all_rows:
        blocks[(row["task_id"], row["model"])][row["condition"]] = row
        grouped[row["condition"]].append(row)
    if any(len({row["initial_state_sha256"] for row in block.values()}) != 1 for block in blocks.values()):
        raise ValueError("Initial-state mismatch in confirmation")

    paired = []
    for (task_id, model), block in sorted(blocks.items()):
        paired.append({
            "task_id": task_id,
            "family": family_by_task[task_id],
            "model": model,
            "no_skill": int(block["no_skill"]["success"]),
            "binding_only": int(block["binding_only"]["success"]),
            "matched_near": int(block["matched_near"]["success"]),
            "matched_far": int(block["matched_far"]["success"]),
            "lure_near": int(block["lure_near"]["success"]),
            "lure_far": int(block["lure_far"]["success"]),
            "primary_delta": int(block["matched_far"]["success"]) - int(block["lure_near"]["success"]),
            "causal_delta": int(block["matched_far"]["success"]) - int(block["binding_only"]["success"]),
        })
    primary = np.array([row["primary_delta"] for row in paired], dtype=float)
    observed = float(primary.mean())

    rng = np.random.default_rng(config["seed"])
    family_matrices = []
    for family in families:
        family_tasks = [task_id for task_id in task_ids if family_by_task[task_id] == family]
        matrix = np.array([
            [next(row["primary_delta"] for row in paired if row["task_id"] == task_id and row["model"] == model)
             for model in model_labels]
            for task_id in family_tasks
        ], dtype=float)
        family_matrices.append(matrix)
    boot_sum = np.zeros(config["bootstrap_samples"], dtype=float)
    boot_n = 0
    family_boot_means = []
    for matrix in family_matrices:
        choices = rng.integers(0, matrix.shape[0], size=(config["bootstrap_samples"], matrix.shape[0]))
        sampled = matrix[choices]
        boot_sum += sampled.sum(axis=(1, 2))
        boot_n += matrix.shape[0] * matrix.shape[1]
        family_boot_means.append(sampled.mean(axis=(1, 2)))
    boot = boot_sum / boot_n
    ci_low, ci_high = (float(value) for value in np.quantile(boot, [0.025, 0.975]))
    macro_observed = float(np.mean([matrix.mean() for matrix in family_matrices]))
    macro_boot = np.mean(np.stack(family_boot_means, axis=0), axis=0)
    macro_ci_low, macro_ci_high = (
        float(value) for value in np.quantile(macro_boot, [0.025, 0.975])
    )

    cluster_values = np.array([
        sum(row["primary_delta"] for row in paired if row["task_id"] == task_id)
        for task_id in task_ids
    ], dtype=float)
    observed_sum = float(cluster_values.sum())
    exceed = 0
    completed = 0
    chunk = 10000
    while completed < config["randomization_samples"]:
        current = min(chunk, config["randomization_samples"] - completed)
        signs = rng.integers(0, 2, size=(current, len(cluster_values)), dtype=np.int8) * 2 - 1
        exceed += int(np.sum(signs @ cluster_values >= observed_sum - 1e-12))
        completed += current
    randomization_p = (exceed + 1) / (config["randomization_samples"] + 1)
    helpful_primary = sum(row["matched_far"] and not row["lure_near"] for row in paired)
    reverse_primary = sum(row["lure_near"] and not row["matched_far"] for row in paired)
    discordant = helpful_primary + reverse_primary
    mcnemar_p = float(binomtest(helpful_primary, discordant, 0.5, alternative="greater").pvalue) if discordant else 1.0

    by_model = {
        model: sum(row["primary_delta"] for row in paired if row["model"] == model) /
        sum(row["model"] == model for row in paired)
        for model in model_labels
    }
    by_family = {
        family: sum(row["primary_delta"] for row in paired if row["family"] == family) /
        sum(row["family"] == family for row in paired)
        for family in families
    }
    helpful = sum(row["causal_delta"] > 0 for row in paired)
    harmful = sum(row["causal_delta"] < 0 for row in paired)
    causal_net = (helpful - harmful) / len(paired)
    harm_rate = harmful / len(paired)
    summary = {
        condition: {
            "episodes": len(group),
            "successes": sum(row["success"] for row in group),
            "success_rate": rate(group),
            "mean_steps": sum(row["steps"] for row in group) / len(group),
            "input_tokens": sum(row["input_tokens"] for row in group),
            "output_tokens": sum(row["output_tokens"] for row in group),
        }
        for condition, group in grouped.items()
    }
    gates = {
        "complete_1080_episodes": len(all_rows) == 1080 and len(paired) == 180,
        "all_audits_pass": all(value == "pass" for value in audit_status.values()),
        "primary_gain_at_least_0_10": observed >= 0.10,
        "bootstrap_95ci_positive": ci_low > 0,
        "family_macro_gain_at_least_0_10": macro_observed >= 0.10,
        "family_macro_bootstrap_95ci_positive": macro_ci_low > 0,
        "randomization_p_at_most_0_01": randomization_p <= 0.01,
        "net_causal_effect_at_least_0_05": causal_net >= 0.05,
        "harm_rate_at_most_0_08": harm_rate <= 0.08,
        "positive_in_two_models": sum(value > 0 for value in by_model.values()) >= 2,
        "positive_in_four_families": sum(value > 0 for value in by_family.values()) >= 4,
    }
    result = {
        "status": "pass" if all(gates.values()) else "fail",
        "design": {
            "targets": len(task_ids),
            "models": model_labels,
            "target_model_blocks": len(paired),
            "episodes": len(all_rows),
            "conditions": conditions,
        },
        "summary": summary,
        "primary": {
            "comparison": "matched_far_minus_lure_near",
            "effect": observed,
            "bootstrap_95ci": [ci_low, ci_high],
            "family_macro_effect": macro_observed,
            "family_macro_bootstrap_95ci": [macro_ci_low, macro_ci_high],
            "task_clustered_randomization_p_one_sided": randomization_p,
            "paired_mcnemar_p_one_sided": mcnemar_p,
            "matched_only_successes": helpful_primary,
            "lure_only_successes": reverse_primary,
            "by_model": by_model,
            "by_family": by_family,
        },
        "causal_vs_binding_only": {
            "helpful": helpful,
            "harmful": harmful,
            "net_effect": causal_net,
            "harm_rate": harm_rate,
        },
        "audit_status": audit_status,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
    }
    output = PROJECT / config["output_dir"]
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    with (output / "paired_blocks.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not all(gates.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
