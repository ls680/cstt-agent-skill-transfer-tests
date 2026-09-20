# Data dictionary

## Confirmation inputs

- `confirmation/roster.json`: one-time frozen target identifiers, official
  split labels, family quotas, selection rule, and scientific-file hashes.
- `confirmation/excluded_prior_targets.json`: target identifiers found in prior
  lifecycle-paper or Paper 07 development evidence. These are exclusion
  evidence, not model inputs.
- `confirmation/pairs.json`: complete offline audit record, including source
  descriptions, operator signatures, lexical scores, contracts, and target
  annotation provenance.
- `confirmation/runtime_pairs.json`: the only pair surface consumed by formal
  native runs. It contains target identity plus source IDs, lexical scores,
  entity-free skill text, and procedural contracts. It contains no source
  objective, source entity names, target expert plan, or target outcome.
- `confirmation/input_audit.json`: deterministic audit of roster coverage,
  zero-overlap exclusions, pair assignments, lexical ordering, contract
  contrasts, and the runtime information boundary.

ALFWorld game data and model weights are not redistributed. `gamefile` values
are relative identifiers under the user-provided `ALFWORLD_DATA` directory.

