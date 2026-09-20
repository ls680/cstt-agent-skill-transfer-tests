#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
sha256sum --check artifacts/release_manifest.sha256
gzip --test artifacts/cstt_reproducibility_bundle.tar.gz
tar -tzf artifacts/cstt_reproducibility_bundle.tar.gz >/dev/null
echo "release manifest and archive passed"

