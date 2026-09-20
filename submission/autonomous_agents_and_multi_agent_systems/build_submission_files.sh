#!/usr/bin/env bash
set -euo pipefail

submission_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
paper_dir="$(cd "$submission_dir/../../paper/autonomous_agents_and_multi_agent_systems" && pwd)"
build_dir="$submission_dir/build"

mkdir -p "$build_dir"

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$build_dir" "$submission_dir/jaamas_information_sheet.tex"
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$build_dir" "$submission_dir/jaamas_cover_letter.tex"

cp "$paper_dir/main.pdf" "$submission_dir/jaamas_main_manuscript.pdf"
cp "$build_dir/jaamas_information_sheet.pdf" "$submission_dir/jaamas_information_sheet.pdf"
cp "$build_dir/jaamas_cover_letter.pdf" "$submission_dir/jaamas_cover_letter.pdf"

source_zip_tmp_dir="$(mktemp -d "$submission_dir/.jaamas_source_zip.XXXXXX")"
source_zip_tmp="$source_zip_tmp_dir/jaamas_main_manuscript_latex.zip"
zip -j -q "$source_zip_tmp" \
  "$paper_dir/main.tex" \
  "$paper_dir/main.bbl" \
  "$paper_dir/references.bib" \
  "$paper_dir/sn-jnl.cls" \
  "$paper_dir/sn-mathphys-num.bst" \
  "$paper_dir/Fig1.pdf"
mv "$source_zip_tmp" "$submission_dir/jaamas_main_manuscript_latex.zip"
rmdir "$source_zip_tmp_dir"

if [ "$(pdfinfo "$submission_dir/jaamas_information_sheet.pdf" | awk '/^Pages:/ {print $2}')" -gt 2 ]; then
  echo "JAAMAS Information Sheet exceeds two pages." >&2
  exit 1
fi

echo "Submission PDFs and LaTeX source ZIP built."
