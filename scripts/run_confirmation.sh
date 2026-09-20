#!/usr/bin/env bash
set -euo pipefail

: "${ALFWORLD_DATA:?Set ALFWORLD_DATA to the directory containing json_2.1.1}"

python scripts/verify_frozen_method.py
python scripts/audit_confirmation_inputs.py

for config in \
  configs/confirmation_qwen3_4b.json \
  configs/confirmation_phi4_mini.json \
  configs/confirmation_mistral7b.json
do
  python scripts/verify_frozen_method.py
  python scripts/run_structured_transfer.py --config "$config"
  python scripts/audit_run.py --config "$config" --require-no-target-plan
done

python scripts/verify_frozen_method.py
python scripts/analyze_confirmation.py --config configs/confirmation_analysis.json
