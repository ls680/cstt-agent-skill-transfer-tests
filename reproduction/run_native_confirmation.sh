#!/usr/bin/env bash
set -euo pipefail

: "${ALFWORLD_DATA:?Set ALFWORLD_DATA to the directory containing json_2.1.1}"
: "${HF_HOME:?Set HF_HOME to the Hugging Face cache on the data disk}"

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
export HF_HUB_OFFLINE=1
bash scripts/run_confirmation.sh

