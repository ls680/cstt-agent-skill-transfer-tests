#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    if not path.exists():
        raise AssertionError(f"missing release file: {path.relative_to(PROJECT)}")
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_model(config_path: Path, roster_ids: set[str]) -> None:
    config = read_json(config_path)
    output = PROJECT / config["output_dir"]
    episodes_path = output / "episodes.jsonl"
    rows = [json.loads(line) for line in episodes_path.read_text().splitlines() if line.strip()]
    expected = {
        (task_id, condition)
        for task_id in roster_ids
        for condition in config["conditions"]
    }
    observed = [(row["task_id"], row["condition"]) for row in rows]
    assert len(rows) == 360, f"{config['model']['label']}: expected 360 episodes"
    assert len(observed) == len(set(observed)), f"{config['model']['label']}: duplicate episode"
    assert set(observed) == expected, f"{config['model']['label']}: incomplete coverage"

    completion = read_json(output / "completion.json")
    audit = read_json(output / "audit.json")
    run_spec = read_json(output / "run_spec.json")
    assert completion["status"] == "completed"
    assert completion["episodes"] == 360 and completion["target_blocks"] == 60
    assert completion["episodes_sha256"] == sha256(episodes_path)
    assert audit["status"] == "pass" and not audit["failures"]
    recorded_config = run_spec["config"]
    assert recorded_config["model"]["id"] == config["model"]["id"]
    assert recorded_config["model"]["revision"] == config["model"]["revision"]


def verify_pdfs() -> None:
    for relative in ("paper/en/main.pdf", "paper/zh/main.pdf"):
        path = PROJECT / relative
        assert path.exists() and path.stat().st_size > 10_000, f"missing or small PDF: {relative}"
        assert path.read_bytes()[:5] == b"%PDF-", f"invalid PDF signature: {relative}"
    macros = (PROJECT / "paper/results_macros.tex").read_text()
    assert "TBD" not in macros, "paper result macros still contain placeholders"


def main() -> None:
    roster = read_json(PROJECT / "data/confirmation/roster.json")
    roster_ids = {row["task_id"] for row in roster["targets"]}
    assert len(roster_ids) == 60
    analysis_config = read_json(PROJECT / "configs/confirmation_analysis.json")
    for name in analysis_config["model_configs"]:
        verify_model(PROJECT / name, roster_ids)

    summary = read_json(PROJECT / "results/confirmation/analysis/summary.json")
    assert summary["status"] == "pass" and summary["all_gates_pass"]
    assert summary["design"]["episodes"] == 1080
    assert summary["design"]["target_model_blocks"] == 180
    assert all(summary["gates"].values())
    verify_pdfs()
    print("release verification passed: 60 targets, 180 blocks, 1080 episodes, two PDFs")


if __name__ == "__main__":
    main()
