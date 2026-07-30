---
name: roadmap
description: "Use after owner approval of WhitePaper and the project Decision authority to create or maintain the project roadmap: outcome Milestones, deliverables, success signals, now/next/later horizons, relative priority, real dependencies, accepted-result links, and a curated Backlog. 白皮书和项目决议权威均已批准后，通过逐项人工裁决编排结果型里程碑、产出、成功信号、规划时域、相对优先级、真实依赖和受控 Backlog。"
---

# ROADMAP: project-level allocation authority

<HARD-GATE>Approved, commit-bound WhitePaper and Decision authorities must exist. If either is missing, or ROADMAP work exposes a WhitePaper premise or cross-Milestone ruling that must change, stop and return the issue to `gmgn` for routing. ROADMAP stays at project-allocation level. It does not contain detailed Close conditions, R-AC IDs, behavior or performance thresholds, technical design, task breakdown, executable tests, evidence, or an end-to-end path.</HARD-GATE>

## Language and writing rules

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing rules. Use the active locale for artifact prose. Use `ROADMAP.md`, `type: roadmap`,
`nature: normative`, and `status: draft` until approved.

## Working rhythm

The primary orchestrator first reads the approved Decision and its WhitePaper authority plus
current project facts, then forms a recommended Milestone map and a list of unresolved
allocation decisions. It remains in dialogue with the human owner and asks one question at a
time before writing the candidate.

Ask only when the answer can change a Milestone boundary, `now | next | later` placement,
relative priority, a real dependency, an explicit deferral, a decision-relevant external
commitment, or the meaning of a success signal. Each question gives one recommended option,
the other real options, and the Roadmap consequence of each. Do not ask for facts already
decided by WhitePaper, Decision, or repository evidence, mechanical representation choices, or
Requirement, Design, Task, test, and execution decisions.

Challenge a feature list presented as an outcome, an artificial serial dependency, a distant
forecast presented as a precise commitment, and a candidate outside the approved WhitePaper
or Decision. Record ROADMAP-owned allocation rulings in the candidate; do not create a
separate Ask or ROADMAP-specific decision log. `DecisionLog.md` is maintained only by
the project Decision stage. Do not write or approve a Roadmap while a material decision within this ask
scope remains unresolved.

## Milestone content

Each Milestone must make these facts unambiguous without requiring a fixed table or section
layout:

- stable Milestone ID; the ID is identity, not execution order;
- the applicable WhitePaper or D-ID anchor;
- one expected outcome and why it merits allocation;
- only the deliverables necessary for that outcome and present by Milestone Close;
- one concise result-level success signal;
- `horizon: now | next | later`;
- relative priority within the same horizon;
- real prerequisite Milestone IDs, or `none`;
- `state: not-started` at creation; and
- `accepted_result: none` until Close.

Derive deliverables from the approved WhitePaper, applicable D-IDs, Milestone outcome, and
recorded ROADMAP-owned rulings. Do not ask the owner merely to choose a document shape,
artifact name, or other mechanical representation.

A success signal states the smallest observable product, user, operational, or organizational
result that would show the allocation is working. It may be quantitative when the number is a
strategic outcome target. It is not a detailed Close criterion or test oracle: Goal refines
the initiated Milestone into Close outcomes, Requirement defines decidable ACs, and
Milestone closure evaluates their evidence.

ROADMAP does not own an E2E path. When an end-to-end user or operational result matters, state
that result and its success signal here; Goal and Requirement own the Close outcome and
observable behavior, and the verification stages select sufficient evidence.

## Horizons, priority, and dependencies

`now` is the current planning commitment. `next` and `later` are adjustable forecasts, not
execution authorization or promises of exact dates, versions, or implementation identities.
Only a `now`, `not-started` Milestone whose declared prerequisites are all `closed` with an
`accepted_result` is eligible for explicit owner initiation through the Milestone initiation
stage. Moving a Milestone into or out of `now` is a semantic Roadmap decision.

Priority expresses relative value within one horizon. Equal priority is allowed. Priority,
display order, and Milestone IDs never create a dependency. Dependencies record only real
prerequisites and form a partial order; Milestones with no dependency relationship may
proceed in parallel when separately authorized.

## Backlog and maintenance

Keep one Backlog only for concrete candidates that fit the approved WhitePaper and Decision but are not
allocated to a Milestone. A Backlog item creates no downstream authority. At every semantic
Roadmap revision and Milestone Close, allocate, merge, or delete stale candidates. An idea
that changes WhitePaper or Decision meaning returns to `gmgn` for routing instead of entering
Backlog.

At Milestone Close, the closure stage supplies one canonical accepted-result entry. ROADMAP
mechanically changes that Milestone to `state: closed` and replaces `accepted_result: none`
with that single link. It does not copy commit, release, network, environment, or evidence
details. Equivalent state, link, and formatting maintenance preserves existing approval and
uses machine checks.

## Approval and revision

Creation and semantic revision use the registered `gmgn` Skill's shared document-candidate
and dispatch rules. After the owner rulings above are complete, write one full candidate
rather than confirming fields one by one. Present that candidate and remaining material
risks—or that none are known—for one final owner approval bound to its commit.

In revision mode, ask only about decisions changed by the delta. ROADMAP owns Milestone
allocation, outcome, value, deliverables, success signals, horizons, relative priority,
dependencies, and Backlog placement. Preserve unaffected Milestones and prior approval. A
change to WhitePaper or Decision authority returns to `gmgn`.

## Exit

Before approval, confirm:

- every Milestone maps to WhitePaper and applicable D-IDs and has one outcome, necessary
  deliverables, one success signal, horizon, relative priority, prerequisites, state, and
  accepted-result field;
- every `now` allocation and other material human decision has an explicit owner ruling;
- dependencies are real and acyclic, while unrelated Milestones remain unordered;
- Backlog contains only current, in-scope, unallocated candidates; and
- ROADMAP contains no per-Milestone owner, E2E path, detailed Close condition, Requirement,
  Design, Task, test, execution, or evidence content.
