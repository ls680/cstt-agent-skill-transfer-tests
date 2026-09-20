#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project_name="$(basename "$project_root")"
manifest="$project_root/artifacts/release_manifest.sha256"
archive="$project_root/artifacts/cstt_reproducibility_bundle.tar.gz"
temporary="$project_root/artifacts/cstt_reproducibility_bundle.tmp"

cd "$project_root"
find . -type f \
  ! -path './.git/*' \
  ! -path './.venv/*' \
  ! -path './.pytest_cache/*' \
  ! -path '*/__pycache__/*' \
  ! -path './submission/*/build/*' \
  ! -path './artifacts/release_manifest.sha256' \
  ! -path './artifacts/*.tar.gz' \
  ! -path './artifacts/*.tmp' \
  ! -name '*.aux' ! -name '*.bbl' ! -name '*.blg' \
  ! -name '*.fdb_latexmk' ! -name '*.fls' ! -name '*.log' \
  ! -name '*.out' ! -name '*.xdv' \
  -print0 | sort -z | xargs -0 sha256sum > "$manifest"

tar -C "$project_root/.." \
  --exclude="$project_name/.git" \
  --exclude="$project_name/.venv" \
  --exclude="$project_name/.pytest_cache" \
  --exclude='*/__pycache__' \
  --exclude="$project_name/submission/*/build" \
  --exclude="$project_name/artifacts/*.tar.gz" \
  --exclude="$project_name/artifacts/*.tmp" \
  --exclude='*.aux' --exclude='*.bbl' --exclude='*.blg' \
  --exclude='*.fdb_latexmk' --exclude='*.fls' --exclude='*.log' \
  --exclude='*.out' --exclude='*.xdv' \
  -czf "$temporary" "$project_name"
mv "$temporary" "$archive"

echo "bundle: $archive"
echo "manifest: $manifest"
