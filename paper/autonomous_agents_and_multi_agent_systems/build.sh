#!/usr/bin/env bash
set -euo pipefail

paper_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$paper_dir"

latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

if rg -n 'LaTeX Warning: (Citation|Reference).*undefined|There were undefined references|Rerun to get cross-references right|Overfull \\hbox' main.log; then
  echo "Manuscript build contains unresolved references or overfull boxes." >&2
  exit 1
fi

echo "JAAMAS manuscript build passed: $paper_dir/main.pdf"
