---
name: write-requirement
description: "Use after Goal.md is approved to analyze, clarify, create, or change functional/non-functional requirements, PRD/product requirements, requirement pool, user stories, acceptance criteria, or ACs in Requirement.md. Goal.md 已批准后写/补需求分析、PRD/产品需求文档、需求池、用户故事、验收标准/AC，或做受控需求变更。"
---

# Requirement.md: single milestone requirement authority

<HARD-GATE>An approved, commit-bound `Goal.md` and the current approved Decision must exist for an initiated milestone. If either authority is missing or requirement work exposes a changed WhitePaper, Decision, ROADMAP, or Goal premise, stop and return the issue to `gmgn` for routing. Do not prescribe implementation structures in requirements or redefine upstream meaning here.</HARD-GATE>

## Language and writing rules

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing rules. Use the Goal locale for artifact prose. Keep filename `Requirement.md`,
`type: requirement`, and `nature: normative`.

## Requirement content

- Derive Requirement within the boundaries of the approved Goal, applicable D-IDs, explicitly
  sourced external constraints, and confirmed Owner answers obtained through the clarification
  process below. Translate a D-ID into R/AC only when it creates observable behavior or a
  Requirement-owned constraint; an architecture-only ruling remains linked input for Design.
  Later documents, implementation, tests, or evidence may expose a needed revision but cannot
  silently define or redefine Requirement.
- Translate every Goal Close outcome into the smallest necessary set of numbered requirements
  `R1`, `R2`, ... . Each R states one coherent required behavior, capability, or constraint
  and names its owning Goal Close outcome or external constraint. Goal grouping creates no
  separate requirement or trace target.
- Give each R decidable ACs `R1-AC1`, ... using enough observable precondition, action or
  inspection, and result to determine pass or fail. Given/When/Then is optional syntax, not a
  mandatory format. Numeric and static constraints may state their decision rule directly.
  Use unambiguous observable language; terms such as reasonable, complete, sufficient,
  high-performance, or robust require a decidable definition. Include rejection, failure,
  recovery, or unchanged-state conditions only when required by the current outcome or invariant.
- Keep the explicit trace: Goal Close outcome → R/AC. No Close outcome may disappear, and no
  R/AC may be unowned.
- Preserve upstream-approved invariants and values without silent weakening. Link an inherited
  value to its upstream authority. For a Requirement-owned threshold, state its value, unit,
  applicable scope or measurement conditions, and pass/fail criterion.
- Analyze Requirement-owned actors, scenarios, behavior, constraints, parameters, and AC
  choices here; their absence from Goal is expected. Include functional, non-functional,
  and parameter/constraint content only when applicable; do not require fixed sections for
  absent categories. Link Goal exclusions instead of creating a Requirement non-goal. Route
  changed upstream meaning upstream.
- Do not invent or prescribe components, modules, interfaces, process structure, code layout,
  data structures, implementation choices, task division, execution order, test commands,
  runtime results, evidence IDs, live status, or closure history. Upstream-defined domain or
  system names may be referenced without making Requirement their design authority.
- Delete any R/AC whose removal would not cause a current Goal Close outcome or externally
  imposed invariant to fail. Future possibility, speculative reuse or scale, configurability,
  and implementation convenience are not owners.

## Clarification and translation

Before creating or semantically revising R/AC, the assigned Adjudicator builds the most
complete candidate meaning allowed by the approved authorities. Do not start with a routine
question checklist. For each unresolved point:

- remove it if it is not needed for a Goal Close outcome or accepted constraint;
- derive it without asking when an approved authority already decides it;
- when it is Requirement-owned and the viable choices would not materially change product
  meaning or acceptance, choose the simplest sufficient option needed to make R/AC decidable;
- ask the Owner through the primary orchestrator's exact relay only when two or more upstream-
  consistent choices remain and the choice would materially change observable behavior, a
  constraint, a parameter, or an AC.

Combine choices that have the same background and consequences into one higher-level
decision. Re-evaluate the remaining questions after each answer instead of sending a fixed
checklist.

Each Owner question starts with one paragraph that combines the relevant background and
concrete scenario. It then explains why the decision is needed, describes the product or
acceptance effect of each viable option, gives a recommendation, and ends with one clear
question. Use self-contained plain language. Explain any unavoidable domain term where it
appears. Do not require the Owner to interpret R/AC notation or implementation details.
Implementation choices belong to Design.

After the Owner answers, the Adjudicator translates it into an exact Author brief for the
smallest sufficient R/AC change and Goal Close trace. The Owner decides the product meaning;
the Author owns its formalization. Do not ask the Owner to review or approve individual R/AC.

## Writer and review-selection loop

Record the Decision and Goal commits, then use the registered `gmgn` Skill's shared document-
candidate and dispatch rules. When Owner input was required, override the normal necessity
gate and dispatch one fresh independent Critic to compare the question, answer, and resulting
R/AC for omitted, added, or changed meaning. Otherwise use the shared Critic necessity gate.
The Adjudicator rules on findings. The primary orchestrator checks accepted links, mappings,
candidate identity, and state.

## Controlled revision

1. Return meaning outside Requirement authority, including a changed D-ID, to `gmgn` for routing before editing.
2. For Requirement-owned meaning, start from the old commit and record the trigger, semantic
   delta, affected R/AC IDs, and proposed new commit.
3. Revise only affected requirements, criteria, parameters, constraints, and traceability.
   Do not re-analyze unaffected Goal Close outcomes.
4. A delta that changes a decision or reasonable understanding follows the writer/review-
   selection loop and receives Adjudicator acceptance at a new commit. Old review remains
   attached to the old commit.
Meaning-preserving mechanical changes use same-batch link, ID reference, and status
refresh plus machine checks without reapproval.

## Exit

Require one completion check: every Goal Close outcome is covered; any proposed exclusion
returns to `gmgn` for routing; every applicable D-ID is linked; every R/AC has an upstream
owner and passes the deletion test; every AC has a clear pass/fail decision; every inherited
number links its authority; every Requirement-owned threshold is measurable; every
Requirement-owned decision is resolved; every confirmed Owner answer is represented in R/AC without omitted, added, or
changed meaning; and no technical solution, task, execution information, or actual
verification result has leaked into Requirement. For creation or a semantic revision, run
the writer/review-selection loop using the English-only dispatch contract; when Critic is
required, tell it to emphasize upstream consistency, acceptance quality, and deletion of any
R/AC that does not serve a current Goal Close outcome. Obtain Adjudicator acceptance, then let
the primary orchestrator integrate only when required by
workspace topology.
