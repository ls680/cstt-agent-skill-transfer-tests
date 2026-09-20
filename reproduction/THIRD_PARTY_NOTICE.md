# Third-party notice

The reproducibility archive contains experiment code, metadata, target/source
identifiers, derived role-normalized skills, and recorded native interaction
logs. It does not bundle ALFWorld game data, Hugging Face model weights, CUDA,
PyTorch, TextWorld, or the ALFWorld Python package.

Users must obtain those dependencies from their official distributions and
accept the applicable licenses. Model repository names and immutable revisions
are recorded in `configs/confirmation_*.json`. ALFWorld task identifiers in the
released records are necessary to replay the exact native games but are not a
substitute for the original dataset.

The two modules under `reproduction/vendor/skilllineage/` are exact frozen
copies of the lightweight local model and environment adapters consumed during
confirmation. `reproduction/prepare_workspace.sh` restores the historical
sibling directory expected by the hashed runner, then verifies the frozen
method before use.

