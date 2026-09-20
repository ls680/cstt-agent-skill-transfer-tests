# Development protocol

Frozen for development on 2026-09-07. Confirmation targets are not selected or
opened during this stage.

## Research question

Can a same-target counterfactual test distinguish genuine procedural transfer
from base-agent competence and surface-triggered negative transfer on tasks the
source skill never executed?

## Unit and 2x2 design

The unit is one target task, one frozen model, and six state-matched runs. All
source skills come from successful ALFWorld training demonstrations. Sources
are selected without target outcomes:

| Condition | Procedure | Surface similarity |
|---|---|---|
| `matched_near` | same task-family operator signature | highest within matched pool |
| `matched_far` | same task-family operator signature | lowest within matched pool |
| `lure_near` | different task-family operator signature | highest within mismatched pool |
| `lure_far` | different task-family operator signature | lowest within mismatched pool |

`no_skill` is an unfiltered base-agent condition. `binding_only` receives the
same target-entity binding, wrong-object rejection, and loop suppression as the
structured executor but no source procedure. Similarity is transparent unigram
cosine over the real source and target objectives. A source skill exposes a
role-normalized operator sequence and executable contract compiled from a real
successful training demonstration. Source entity names, source objective, target
gold plan, and target outcome are absent from the consumed skill.

## Causal outcomes

All six conditions reset the same native game and must have the same initial
observation, objective, and admissible-command signature. For a target/model:

- helpful transfer: a skill condition succeeds and `binding_only` fails;
- harmful transfer: a skill condition fails and `binding_only` succeeds;
- redundant success: both succeed;
- shared failure: both fail.

The net causal success effect is helpful minus harmful, divided by all paired
targets. Comparisons with raw `no_skill` are executor-level effects; causal skill
credit uses `binding_only`, which shares non-procedural safeguards. Raw
skill-conditioned success cannot by itself be called transfer.

## Development process and gate

Pilot 1 uses one already exposed `valid_seen` target per six ALFWorld families
with Qwen3-4B. Up to three mechanism revisions are permitted, using only
previously exposed development targets. A revision may change skill rendering,
agent interface, or the causal report, but every failed version is retained.
Revision 3 is the last permitted revision: all arms use the same local action
selector; source-skill arms additionally use an auditable stage filter compiled
only from the source operator contract. Every candidate, rejected action, stage,
and state update is logged.

The frozen design advances only after an expanded development run of at least 30
targets satisfies all of the following:

- every run is native, complete, and state matched;
- `matched_far` success is at least 10 points above `lure_near`;
- `matched_far` net causal effect versus `binding_only` is at least +0.08;
- `matched_far` harm rate is at most 0.05;
- the matched-versus-lure advantage is positive in at least four of six families;
- source operator signatures, source IDs, target IDs, and prompts are auditable.

Development gates are practical screens, not confirmatory significance claims.
Failure after three mechanism revisions stops Paper 07 and advances the matrix.

## Planned confirmation

Only after the development gate passes, freeze source pool, source selection,
skill renderer, agent prompts, model revisions, statistics, exclusions, and
gates. Select content-blind target IDs not used for Paper 07 development and not
present in Papers 01--06 experiment evidence where the inventory permits.

The intended primary comparison is `matched_far` versus `lure_near` on success,
paired by target and model. Confirmation must cover at least 60 target tasks,
three local model families, all six ALFWorld families, and at least 180 complete
target-model blocks. It will use a task-clustered paired randomization test and a
target-stratified bootstrap. Minimum gates are a 10-point primary gain, positive
95% interval, p<=0.01, matched-far net causal effect at least +0.05, harm rate at
most 0.08, and positive primary gain in at least two model families and four task
families. A failed primary gate cannot be rescued by a secondary analysis.

## Claim boundary

This experiment tests instance-level transfer within ALFWorld. It does not by
itself establish cross-environment or cross-website transfer, and it cannot
separate model limitations from skill quality without reporting each model.
The fixed source demonstrations and target tasks are not a population estimate
for marketplace skills. The paper will not claim that lexical similarity is
always harmful or that CSTT is a skill retrieval method.
