# Autonomous Agents and Multi-Agent Systems manuscript

This directory contains the journal-specific English manuscript for
*Autonomous Agents and Multi-Agent Systems* (JAAMAS). The original English and
Chinese manuscripts under `paper/en/` and `paper/zh/` remain unchanged.

## Format decisions

- Springer Nature LaTeX template, December 2024 distribution
- `\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}`
- Numbered citations, as requested in the journal instructions
- Author title page with affiliations, correspondence, and Liang Song's ORCID
- Unstructured abstract within the journal's 150--250 word range
- Six indexing keywords
- Generative-AI assistance disclosed in Experimental Design
- Funding, competing interests, author contributions, availability, ethics,
  and consent statements included
- One embedded vector figure named `Fig1.pdf`

The source is flat and self-contained. It does not use `\input` or `\include`;
all macros and tables needed for compilation are in `main.tex`.

## Build

Run:

```bash
./build.sh
```

The build fails on unresolved references, unresolved citations, overfull boxes,
or fatal LaTeX errors.

## Required companion file

JAAMAS requires a separate one- to two-page Information Sheet for every
submission. The prepared sheet is stored in
`submission/autonomous_agents_and_multi_agent_systems/` together with the cover
letter and portal metadata.

Guidance checked on 20 September 2026:

- https://link.springer.com/journal/10458/submission-guidelines
- https://link.springer.com/journal/10458/aims-and-scope
- https://www.springernature.com/gp/authors/campaigns/latex-author-support
