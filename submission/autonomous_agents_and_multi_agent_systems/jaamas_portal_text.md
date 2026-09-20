# JAAMAS portal text

## Article type

Research

## Title

Same Words, Different Procedure: Counterfactual Transfer Tests for Reusable
LLM-Agent Skills

## Short title

Counterfactual Tests for Agent Skill Transfer

## Abstract

An agent completing a new task after receiving a reusable skill does not show
that the skill caused success: the base agent may already solve the task, while
semantic retrieval may select a source that repeats target nouns but prescribes
the wrong state transition. We introduce the Counterfactual Skill Transfer Test
(CSTT), a state-matched protocol that crosses source procedural compatibility
with surface similarity on the same native target. Every source is a successful
ALFWorld training trajectory compiled into a role-normalized procedure and a
small executable contract. Each target is reset for no-skill, binding-only,
procedure-matched near/far, and procedure-mismatched near/far conditions. The
binding control shares target grounding and search safeguards but receives no
source procedure, enabling separate estimates of executor-level benefit and
causal skill credit. After two failed pilots and one final mechanism revision,
we froze code, source assignment, three model revisions, a zero-overlap roster,
inference, and decision gates. Confirmation contains 60 untouched native
targets, 3 local model families, 180 paired target-model blocks, and 1,080
episodes. Matched-far skills succeed on 97.8% of blocks versus 10.0% for
surface-near procedural lures, an 87.8-point paired gain (95% target-stratified
bootstrap CI 82.8-93.3; task-clustered randomization p = 1.00 x 10^-6). The
equal-family macro gain is 87.7 points, and the net matched-far effect over
binding-only is 83.3 points with a 0.0% harm rate. CSTT is an evaluation and
credit-assignment instrument, not a retrieval algorithm; evidence is limited to
instance-level transfer in one embodied text environment.

## Keywords

- LLM agents
- Agent skills
- Skill transfer
- Counterfactual evaluation
- Procedural compatibility
- Negative transfer

## Funding

The authors did not receive support from any organization for the submitted
work.

## Competing interests

The authors have no relevant financial or non-financial interests to disclose.

## Author contributions

L.S. contributed to conceptualization, methodology, software, validation,
formal analysis, investigation, data curation, visualization, writing the
original draft, reviewing and editing the manuscript, and project
administration. J.Z. contributed to methodology, validation, and reviewing and
editing the manuscript. Both authors read and approved the final manuscript.

## Data availability

The permanent Zenodo DOI and public GitHub repository URL will be inserted after
the repository and archive have been created. Third-party ALFWorld assets and
model weights are not redistributed; pinned upstream revisions, task
identifiers, paths, licenses, and integrity checks are provided instead.

## Acknowledgements

Leave blank in the portal.

## Related manuscript disclosure

A related manuscript by the same authors, entitled "From Traces to Witnessed
Contracts: Incremental Precondition-Effect Compilation for LLM Agent Skills,"
is currently under consideration at Automated Software Engineering. That
manuscript studies pre-execution detection of defective skill revisions. The
present submission instead studies causal attribution of skill-transfer
benefits through a six-condition counterfactual protocol. The two studies use
disjoint confirmation targets and different methods, estimands, experiments,
figures, tables, endpoints, and results. A copy is supplied for editorial
assessment.
