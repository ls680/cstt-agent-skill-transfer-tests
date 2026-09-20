# Literature-grounded gap

## Local corpus

The design starts from the 2026-08-31 local Agent Skill lifecycle corpus at
`../autodl_inputs/01_agent_skill_lifecycle`: 255 deduplicated papers, 115 core
papers, and 22 records assigned to cross-task transfer/generalization through
their matched taxonomy paths. The gap is based on stored abstracts and metadata,
not title matching alone.

## Closest work

| Work | Corpus identifier | Existing contribution | Distinction of this study |
|---|---|---|---|
| PolySkill | ICLR 2026 / arXiv:2510.15863 | Separates abstract goals from concrete implementations and reports unseen-site success. | Does not isolate procedural compatibility from lexical similarity and no-skill competence in a crossed same-target test. |
| Break It Down, Pass It On | arXiv:2608.20274 | Studies task/subtask granularity and text/code formats; proposes specificity-plus-abstractness utility. | Predicts average utility from skill/task descriptions, but does not require same-state no-skill and misleading-skill counterfactuals for credit. |
| SkillTrace provenance auditing | arXiv:2608.05204 | Detects expression, implementation, and operational reuse across packages. | Audits provenance, not whether reusing a skill causally improves a new task. |
| Skill Reuse as Compression | arXiv:2605.31509 | Uses MDL-regularized reusable patterns and reports OOD task success. | Optimizes learning; it does not deconfound success under reuse from base success on the same target. |
| SkillLens | arXiv:2605.08386 | Retrieves and adapts multi-granularity skills under sparse mismatch. | Measures system success/cost rather than a factorial procedure-versus-surface transfer test. |
| From Raw Experience to Skill Consumption | arXiv:2605.23899 | Studies utility across extractors, consumers, and domains, including negative transfer. | Broad lifecycle analysis; the proposed experiment supplies an exact same-target causal credit rule and surface-similar procedural lures. |
| Beyond Domains / SkillMigrator | arXiv:2606.17645 | Transfers web skills by layout structure at matched success rate. | Proposes a structural transfer method; this paper evaluates whether any claimed transfer survives causal and contrastive controls. |
| Agent Skills Can Be Harmful | arXiv:2608.11888 | Attributes functional and efficiency regressions with no-skill or matched references. | Failure attribution is adjacent; this study crosses procedure and surface similarity prospectively and measures both positive and negative transfer. |

## Research gap

An unseen-task success rate can credit a skill when the base agent would already
have succeeded, and semantic retrieval can select a source that shares nouns but
prescribes the wrong state transition. A transfer claim therefore needs three
separations on the exact target and initial state: skill versus no skill,
procedure match versus mismatch, and high versus low surface similarity.

The proposed Counterfactual Skill Transfer Test (CSTT) constructs all four
procedure/surface cells from successful real source demonstrations, runs them
with the same target agent, and credits transfer only through paired outcomes.
It evaluates reusable skills; it is not a new skill induction or retrieval
algorithm.
