#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    output = PROJECT / config["output_dir"]
    analysis = json.loads((output / "analysis.json").read_text())
    audit = json.loads((output / "audit.json").read_text())
    causal = analysis["causal_vs_control"]["matched_far"]
    family_effects = analysis["matched_far_minus_lure_near_by_family"]
    gates = {
        "at_least_30_targets": analysis["summary"]["matched_far"]["tasks"] >= 30,
        "native_complete_state_matched": audit["status"] == "pass" and analysis["all_initial_states_matched"],
        "primary_gain_at_least_0_10": analysis["matched_far_minus_lure_near"] >= 0.10,
        "net_causal_effect_at_least_0_08": causal["net_causal_effect"] >= 0.08,
        "harm_rate_at_most_0_05": causal["harm_rate"] <= 0.05,
        "positive_in_four_families": sum(value > 0 for value in family_effects.values()) >= 4,
        "sources_and_actions_auditable": audit["all_actions_native"] and audit["source_assignments_valid"],
    }
    result = {
        "status": "pass" if all(gates.values()) else "fail",
        "gates": gates,
        "metrics": {
            "matched_far_success": analysis["summary"]["matched_far"]["success_rate"],
            "lure_near_success": analysis["summary"]["lure_near"]["success_rate"],
            "primary_gain": analysis["matched_far_minus_lure_near"],
            "net_causal_effect_vs_binding_only": causal["net_causal_effect"],
            "harm_rate_vs_binding_only": causal["harm_rate"],
            "positive_families": sum(value > 0 for value in family_effects.values()),
        },
        "confirmation_may_be_opened": all(gates.values()),
    }
    (output / "development_gate.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not all(gates.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
