#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 /absolute/path/to/new/workspace" >&2
  exit 2
fi

workspace="$1"
case "$workspace" in
  /*) ;;
  *) echo "workspace must be an absolute path" >&2; exit 2 ;;
esac

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
paper_root="$workspace/07_counterfactual_transfer_tests"
shared_root="$workspace/01_skilllineage/src/skilllineage"
python_bin="${PYTHON:-python3}"

if [[ -e "$paper_root" || -e "$workspace/01_skilllineage" ]]; then
  echo "destination already contains a Paper 07 or shared dependency directory" >&2
  exit 2
fi

mkdir -p "$paper_root" "$shared_root"
cp -a "$project_root/." "$paper_root/"
cp "$project_root/reproduction/vendor/skilllineage/"*.py "$shared_root/"

cd "$paper_root"
"$python_bin" scripts/verify_frozen_method.py
"$python_bin" scripts/audit_confirmation_inputs.py
echo "isolated workspace prepared at $workspace"
