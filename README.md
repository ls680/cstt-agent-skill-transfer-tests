# Counterfactual Skill Transfer Tests

Paper 07 workspace.

- Working English title: *Same Words, Different Procedure: Counterfactual Transfer Tests for Reusable LLM-Agent Skills*
- Working Chinese title: 《同词不同法：面向可复用 LLM Agent 技能的反事实迁移测试》
- Matrix cell: skill reuse/composition x evaluation/testing
- Current status: frozen three-model confirmation passed; final manuscript and
  release package prepared

The paper asks whether success on an unseen task is genuinely caused by a
reused skill, rather than by base-agent competence or lexical overlap. Each
target is evaluated from the same initial state with no skill and with four
real source skills crossing procedural compatibility and surface similarity.

No paper-level claim will be made from development data. The method and gates
must pass development and be frozen before confirmation targets are selected.

The development gate passed. The confirmation method, target roster,
source assignments, model revisions, statistics, and gates are frozen under
`data/confirmation/`. Formal execution contains 60 untouched targets, three
model families, six conditions per target--model block, and 1,080 native
episodes. All three independent trajectory audits and all 11 frozen decision
gates passed. A procedurally matched but lexically far source achieved 97.8%
success versus 10.0% for a lexically near procedural lure, a paired gain of
87.8 percentage points (95% target-stratified bootstrap CI 82.8--93.3;
task-clustered randomization p = 1.00 x 10^-6). The net gain over the fair
binding-only control was 83.3 points with zero observed harmful discordances.

Prepared delivery entry points:

- English manuscript source: `paper/en/main.tex`
- Chinese manuscript source: `paper/zh/main.tex`
- Reproduction instructions: `REPRODUCE.md`
- Environment record: `environment/RUN_ENVIRONMENT.md`
- Protocol and evidence boundaries: `research/`
- Release scripts: `artifacts/`

Journal submission and release preparation:

- JAAMAS manuscript: `paper/autonomous_agents_and_multi_agent_systems/main.pdf`
- JAAMAS submission package: `submission/autonomous_agents_and_multi_agent_systems/`
- Public repository: https://github.com/ls680/cstt-agent-skill-transfer-tests
- Versioned archive: https://doi.org/10.5281/zenodo.22852634
- Release license: Apache-2.0
