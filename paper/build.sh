#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
for language in en zh; do
  cd "$project_dir/paper/$language"
  latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
  if rg -n 'There were undefined references|Citation .* undefined|Reference .* undefined|Overfull \\hbox|Missing character:' main.log; then
    echo "paper/$language/main.log contains unresolved references, missing glyphs, or overfull boxes" >&2
    exit 1
  fi
done

