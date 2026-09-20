# Experiment log

## 2026-09-07 - Paper 07 opened

- Selected matrix cell: skill reuse/composition x evaluation/testing.
- Read all 22 local-corpus records assigned to cross-task transfer through their
  matched taxonomy paths and the abstracts of the closest benchmark, utility,
  provenance, negative-transfer, structural-transfer, and lifecycle studies.
- Chosen gap: unseen-task success alone cannot assign causal credit to a skill
  and does not challenge surface-similar but procedurally wrong retrievals.
- Fixed a 2x2 procedure-match by lexical-similarity design plus a no-skill arm.
- Pilot targets are already exposed `valid_seen` tasks. Confirmation remains
  unselected and no confirmatory claim is permitted from development.

## 2026-09-07 - Development pilot 1 failed

- Ran six exposed targets by five state-matched conditions with Qwen3-4B: 30
  native episodes, all initial signatures equal within target.
- `matched_far` and `lure_near` both succeeded on 2/6 targets. Matched-far net
  causal effect versus no skill was -1/6, with one harmful and no helpful case.
  The fixed feasibility gate therefore failed.
- Raw trajectories identify source-entity anchoring as a direct failure mode.
  On the current heated-apple target, a matched source whose annotation mentioned
  an egg caused repeated manipulation of eggs. On simple placement, matched
  source wording caused location/inventory loops while no skill succeeded.
- Pilot 1 inputs, code snapshot, full decisions, prompts hashes, feedback, and
  analysis are retained. No confirmation target was selected or inspected.

## 2026-09-07 - Development revision 2 specified

- Remove source objective, family label, and concrete entities from the consumed
  skill view while preserving the audited source ID, source text, lexical score,
  and operator signature in the pair record.
- Collapse the successful source trace into role-normalized semantic stages and
  explicitly require current-target binding, novel-location search, and no
  acquisition of a different object type.
- Increase visible execution history from 6 to 12 turns and the common step cap
  from 35 to 40 for all five arms. No target-specific rule is added.
- Re-run the same six exposed targets. Confirmation remains sealed.

## 2026-09-07 - Development pilot 2 failed

- Ran the same six exposed targets under the entity-free role-normalized prompt:
  30 complete native episodes with matched initial states.
- `matched_far`, `lure_near`, and `no_skill` each succeeded on 2/6 targets.
  Matched-far net causal effect was 0, harm was 1/6, and its advantage over the
  surface-near lure was 0. The revision therefore failed its feasibility gate.
- Near and far matched sources compiled to the same semantic stages yet diverged
  on one target, while repeated admissible-action loops remained common. This
  falsifies the proposed prompt-only remedy on the exposed development set.

## 2026-09-07 - Development revision 3 specified before execution

- Compile each real source demonstration into an executable contract containing
  only object count, operation, and placement requirement. Concrete source
  entities and the target gold trajectory remain unavailable to the executor.
- Add an auditable stage filter that binds the contract to the current objective,
  rejects wrong-object actions, performs non-repeating search, and records every
  candidate, rejection, phase, and state transition.
- Add `binding_only`, which receives the same target binding and non-procedural
  safeguards but no source contract. Causal skill credit is now computed against
  this fair control; raw `no_skill` remains an executor-level secondary baseline.
- Increase the common cap to 100 native steps to accommodate exhaustive search.
  This is the third and final permitted mechanism revision. Confirmation remains
  sealed and may be opened only after a separate 30-target development gate.

## 2026-09-07 - Revision 3 mechanism check passed

- Completed 36 native episodes: six exposed targets by six conditions, with all
  initial states matched. Peak reserved GPU memory was 8.03 GiB.
- `matched_near` and `matched_far` each succeeded on 6/6 targets;
  `lure_near` succeeded on 1/6, `lure_far` on 0/6, `binding_only` on 1/6,
  and raw `no_skill` on 2/6. Matched-far minus surface-near lure was +0.833;
  matched-far net effect versus `binding_only` was +0.833 with zero harm.
- Audit exposed an implementation weakness in `binding_only`: when a visited
  receptacle was closed, unvisited navigation was ranked before the admissible
  open action. Before any expanded run, the control was corrected to open the
  current receptacle and to prioritize held-target actions without supplying an
  operation or stage order. This makes the no-source control stronger.
- Failure arms also spent the remaining budget issuing `look` after a source
  contract had completed without satisfying the target. An outcome-preserving,
  auditable early-stop reason was added before the expanded run. The six-task
  mechanism check remains retained under its original code hash and is not used
  for a development-gate or confirmation claim.

## 2026-09-07 - Expanded run restarted after efficiency audit

- The first partial expanded execution showed that an inapplicable source
  operation could alternate between multiple instances of the same device class.
  The partial run was stopped and retained as `expanded_pre_efficiency_fix`.
- Before restarting, the executor was changed to try each same-class location at
  most once per acquire/transform/place stage. The state field and every attempt
  are serialized in the trace. This does not introduce target procedure data and
  changes only the termination time of an already inapplicable source contract.

## 2026-09-07 - Expanded run restarted after device-search audit

- The second partial expanded run reached a light-examination target whose object
  and desk lamp were at different receptacles. A matched contract failed because
  the executor treated the non-navigable lamp as if it were a receptacle name.
  The partial run was stopped and retained as `expanded_pre_device_search_fix`.
- The generic toggle stage now keeps the target in inventory, systematically
  visits previously untried receptacles, opens closed receptacles, and applies
  the admissible target-device action when it appears. It does not know the lamp
  location or read a target plan. Unit coverage was added before the final full
  30-target development run.

## 2026-09-07 - Expanded development gate passed

- Completed all 180 native episodes for 30 targets, six task families, and six
  state-matched conditions. The run used no target expert trajectory and peaked
  at 8.41 GiB reserved GPU memory.
- `matched_far` succeeded on 30/30, `lure_near` on 3/30, `binding_only` on
  5/30, and `no_skill` on 5/30. The fixed primary screen was +0.90; net causal
  effect versus the fair control was +0.833 with zero harmful target pairs.
- The independent audit checked 7,070 turns and passed coverage, initial-state,
  native-action, candidate-partition, source-assignment, and target-plan-absence
  checks. All seven pre-specified development gates passed.

## 2026-09-07 - Confirmation allocation amended before freeze

- The first freeze attempt stopped before writing a roster because strict
  exclusion of every validation task appearing in prior experiment or revision
  evidence left fewer than ten targets in five families.
- The remaining untouched inventory was 9/8/8/8/8/20 across the six configured
  families. The allocation was fixed at 9/8/8/8/8/19, preserving 60 total tasks;
  the omitted two-object target is determined only by the existing salted-hash
  order, not by content or outcomes.
- Because this allocation is unbalanced, an equal-weight six-family macro effect
  and bootstrap interval were added as mandatory robustness gates before the
  confirmation roster was opened. Confirmation data remained unseen.

## 2026-09-07 - Confirmation frozen and input audit passed

- The content-blind roster was written once with 60 targets: 59 official
  `valid_seen` and one official `valid_unseen` task. No target identifier overlaps
  any prior-series or Paper 07 development evidence.
- The complete source-pair file hash is
  `d972c4119df9d7f144a7be895064d3542feee1bb7769b47db4d781db57e149a4`;
  the runtime information-boundary file hash is
  `67ab887b21f1243c1b313acf259f30b33921a4d13a1f9b14b9520be7d8b50c2f`.
- Frozen-method verification and confirmation-input audit passed before model
  inference. No scientific file is permitted to change during confirmation.

## 2026-09-07 - Qwen confirmation completed

- Qwen3-4B-Instruct-2507 completed all 360 episodes and 60 target blocks in
  6,773.70 seconds. Peak allocated CUDA memory was 8.95 GiB.
- Its independent audit checked 14,565 native turns. Coverage, exact initial
  states, selected native actions, candidate partitions, source assignments,
  and required target-plan absence all passed with no failures.
- The episode record hash is
  `e930bd9dc4f82bdc1d68e76e651ce0bcd03bf4e09a36cd241b0e6f423c26e97b`.
  Outcomes remain unopened for combined analysis until all three models finish.

## 2026-09-07 - Infrastructure interruption and exact resume

- The interactive SSH process ended during Phi-4-mini after 30 of 360 records.
  All records were already checkpointed; no scientific input or method file was
  changed and no partial record was accepted.
- The same frozen command was restarted in a detached `screen` session with the
  original Python environment, ALFWorld path, offline model cache, and model
  revision. The runner reverified the method, skipped complete Qwen records, and
  resumed Phi from the first missing condition.
- This event is an infrastructure-only continuation, not a method revision or a
  reason to exclude any target.

## 2026-09-07 - Phi confirmation completed

- Phi-4-mini-instruct completed all 360 episodes and 60 target blocks. The
  resumed process reports 5,822.55 seconds; the first 30 checkpointed episodes
  were produced before the recorded SSH interruption and are not included in
  that process timer. Peak allocated CUDA memory was 7.77 GiB.
- Its independent audit checked 16,527 native turns. Coverage, exact initial
  states, selected native actions, candidate partitions, source assignments,
  and required target-plan absence all passed with no failures.
- The episode record hash is
  `ce22ebfde7f0fb088c5d4fe74c254d30b10daa6429be89604a251dcc5f1f5920`.
  Mistral-7B then began automatically without combined-result analysis.

## 2026-09-07 - Mistral confirmation completed

- Mistral-7B-Instruct-v0.3 completed all 360 episodes and 60 target blocks in
  7,493.48 seconds. Peak allocated CUDA memory was 15.92 GiB.
- Its independent audit checked 15,570 native turns. Coverage, exact initial
  states, selected native actions, candidate partitions, source assignments,
  and required target-plan absence all passed with no failures.
- The episode record hash is
  `90881a7802f462cf3f9258976dfff658bae7247d7b609b3ae8896d648283df76`.

## 2026-09-07 - Frozen confirmation analysis passed

- The accepted data contain 60 untouched targets, three model families, 180
  paired target--model blocks, six conditions, and 1,080 native episodes. The
  three independent audits checked 46,662 turns without a failure.
- Matched-far succeeded on 176/180 blocks (97.8%) and the surface-near
  procedural lure on 18/180 (10.0%). The paired gain was 87.8 percentage
  points, with target-stratified 95% bootstrap CI 82.8--93.3 and one-sided
  task-clustered randomization p = 1.00 x 10^-6.
- The equal-family macro gain was 87.7 points (95% CI 82.7--93.3). Model-level
  gains were 88.3, 88.3, and 86.7 points; all six task-family estimates were
  positive.
- Against binding-only, matched-far produced 150 helpful and zero harmful
  discordances, a net effect of 83.3 points and observed harm rate of 0.0%.
  All 11 frozen coverage, practical-effect, inference, heterogeneity, and harm
  gates passed. No confirmation outcome was used to change the method.
