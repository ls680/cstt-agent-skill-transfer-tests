#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    roster = json.loads((PROJECT / "data/confirmation/roster.json").read_text())
    observed = {name: digest(PROJECT / name) for name in roster["method_hashes"]}
    mismatches = {
        name: {"expected": expected, "observed": observed[name]}
        for name, expected in roster["method_hashes"].items()
        if observed[name] != expected
    }
    freeze_config = PROJECT / "configs/confirmation_freeze.json"
    if digest(freeze_config) != roster["config_sha256"]:
        mismatches[str(freeze_config.relative_to(PROJECT))] = {
            "expected": roster["config_sha256"],
            "observed": digest(freeze_config),
        }
    result = {"status": "pass" if not mismatches else "fail", "mismatches": mismatches}
    print(json.dumps(result, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
