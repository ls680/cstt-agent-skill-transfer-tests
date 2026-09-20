# Reproducing CSTT

The release supports exact CPU-only verification of released records and a
full native replication on one RTX 3090.

- Source repository: https://github.com/ls680/cstt-agent-skill-transfer-tests
- Versioned archive: https://doi.org/10.5281/zenodo.22852634

## 1. Verify released records

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . -r environment/requirements-analysis.txt
pytest -q
python scripts/verify_frozen_method.py
python scripts/audit_confirmation_inputs.py
python scripts/audit_run.py --config configs/confirmation_qwen3_4b.json --require-no-target-plan
python scripts/audit_run.py --config configs/confirmation_phi4_mini.json --require-no-target-plan
python scripts/audit_run.py --config configs/confirmation_mistral7b.json --require-no-target-plan
python scripts/analyze_confirmation.py --config configs/confirmation_analysis.json
python scripts/render_paper_assets.py
bash paper/build.sh
python scripts/verify_release.py
```

The final command reconstructs all paired blocks, success rates, causal effects,
task-clustered randomization inference, target-stratified bootstrap intervals,
task-family macro results, and every frozen confirmation gate.

## 2. Rebuild paper assets separately

```bash
python scripts/render_paper_assets.py
bash paper/build.sh
```

Outputs are `paper/en/main.pdf` and `paper/zh/main.pdf`.

## 3. Repeat native confirmation

First construct the exact sibling layout expected by the frozen runner:

```bash
bash reproduction/prepare_workspace.sh /absolute/path/to/new/cstt-workspace
cd /absolute/path/to/new/cstt-workspace/07_counterfactual_transfer_tests
```

Install the native requirements and the package, place ALFWorld and the three
model revisions on the data disk, then run:

```bash
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r environment/requirements-native.txt
python -m pip install -e .
export ALFWORLD_DATA=/data/alfworld
export HF_HOME=/data/huggingface
bash reproduction/run_native_confirmation.sh
```

The runners checkpoint each completed condition. Restarting the same command
validates existing records and resumes missing conditions. A new run is an
independent replication: dependency, model-runtime, or simulator changes can
produce different trajectories.
