# Recorded run environment

## Hardware

- GPU: one NVIDIA GeForce RTX 3090, 24 GB
- GPU driver: 595.71.05
- CPU allocation: 20 AMD EPYC 7642 cores
- RAM: 90 GB
- system disk: 30 GB
- data disk: approximately 1.1 TB allocated

The three model families run sequentially. Counterfactual pairing, audits,
statistical analysis, released-record verification, and paper generation are
CPU-only. Mistral-7B-v0.3 used the largest recorded peak allocation at 15.92
GiB; Phi-4-mini used 7.77 GiB. The initial Qwen run used 8.95 GiB and took
6,773.70 seconds, as recorded before the infrastructure interruption in
`research/EXPERIMENT_LOG.md`. Its later no-op resume rewrote the process-local
completion timer and memory counter but did not change the episode file or its
hash. Mistral's complete process took 7,493.48 seconds. Phi's resumed process
took 5,822.55 seconds, excluding its first 30 checkpointed episodes.

## Software

- Ubuntu 22.04
- Python 3.12
- PyTorch 2.8.0+cu128
- CUDA runtime 12.8
- transformers 4.57.6
- accelerate 1.14.0
- safetensors 0.8.0
- sentencepiece 0.2.2
- json-repair 0.63.4
- ALFWorld 0.4.2
- TextWorld 1.7.0
- NumPy 2.3.2
- SciPy 1.18.1

No Docker image is required. Model identifiers and immutable revisions are in
`configs/confirmation_*.json`. The Python environment, Hugging Face cache,
ALFWorld data, and native outputs belong on the data disk. The 30 GB system
disk is used only for the operating system and small command-line tools.

## Paper build

The manuscripts require XeLaTeX, `latexmk`, BibTeX, and Noto CJK fonts. On
Ubuntu, install `texlive-xetex`, `texlive-latex-extra`, `fonts-noto-cjk`, and
`latexmk`.
