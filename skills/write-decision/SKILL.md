---
name: write-decision
description: "Use after WhitePaper approval and before ROADMAP, or whenever any current or proposed ruling should be recorded for downstream consumption, regardless of subject or Milestone scope. Create or revise root Decision.md as current authority and DecisionLog.md as descriptive accepted-change history. 白皮书批准后、ROADMAP 之前，或任意范围的现行或候选决议需要供下游消费时，创建或受控修订 Decision.md 与 DecisionLog.md。"
---

# Decision authority

<HARD-GATE>Creation requires an approved WhitePaper commit. Revision requires the current
approved Decision authority. The human owner decides both whether a candidate belongs here
and which option is accepted. Pause only downstream work whose result could change while a
material candidate is unresolved. If the candidate changes the WhitePaper problem, goal,
scope, harm order, or invariant, return it to `gmgn` for upstream revision first.</HARD-GATE>

## Language and artifacts

Load the registered `gmgn` Skill and follow its writing rules. Use the WhitePaper locale.
Maintain these project-root artifacts:

- `Decision.md`: `type: decision`, `nature: normative`; current accepted rulings only.
- `DecisionLog.md`: `type: decision`, `nature: descriptive`; accepted change history only.

They form one controlled change batch. Normal downstream stages read `Decision.md`, not
`DecisionLog.md`. Read the Log only to preserve ID history or investigate a change.

## Place a ruling in Decision

Decision may own any current ruling needed by planning or active work, including a ruling
limited to one Milestone, requirement, module, interface, implementation, or Task. Scope is
not a jurisdiction filter.

Keep a candidate only when it is an explicit choice among material alternatives and one or
more downstream artifacts must obey or link it. Do not turn derived content, document state,
execution status, evidence, commands, or history into a ruling.

Once recorded:

- `Decision.md` owns the current ruling;
- downstream artifacts link the applicable D-ID and keep only their own derived content; and
- any later change to that D-ID returns to `write-decision`.

A stage may retain a decision in its normal authority when it is not recorded in
`Decision.md`. Never keep the same ruling normative in both places.

The primary orchestrator recommends the option, scope, and downstream consequence, then asks
the Owner one material question at a time when the ruling itself is unresolved. Do not create
an Ask document or reject a Decision candidate merely because its scope is narrow. The Owner
makes the final ruling.

## Decision.md content

Keep the complete current set of accepted rulings explicitly recorded in Decision and needed
by current planning or active work. Do not speculate about decisions no current work needs.
Define each ruling as one DocStar-compatible list entity:

```markdown
- **D-001** <short name>
  - Applies to: <downstream Milestones, artifacts, modules, interfaces, Tasks, or shared objects>
  - Decision: <unambiguous current ruling>
```

Add `Implications` only when the consequence is not obvious. Add one concise reason only when
it prevents likely misinterpretation. Do not add per-entry status, owner, dates, options,
supersession chains, affected-document inventories, or copied downstream requirements and
design. Document status carries approval; Git and `DecisionLog.md` carry history.

Never renumber or reuse a D-ID. When a ruling changes, replace its current content under the
same ID. When it is retired, remove it from `Decision.md`; its ID remains reserved by the Log.
If no additional ruling beyond WhitePaper is needed, say so without inventing a D-ID.

## DecisionLog.md content

Append one compact event for each accepted D-ID creation, change, or retirement:

```text
date | D-ID | created/changed/retired | change summary | reason | approved decision commit
```

Do not copy the full old or new ruling, record rejected options, or turn the Log into a
parallel authority. Exact diffs remain in Git. A log event mentioning a D-ID is a reference,
not another bold D-ID definition.

## Authoring and approval

1. The primary orchestrator reads the approved WhitePaper, current `Decision.md`, and only the Log
   history needed to preserve IDs or understand the proposed delta.
2. It resolves material ruling and downstream-scope questions with the Owner.
3. It prepares one Author brief; the independent Author writes the complete current Decision
   candidate. In revision mode, change only affected entries.
4. Process the semantic candidate through the registered `gmgn` Skill's shared document-
   candidate and dispatch rules. The primary orchestrator checks necessity, current meaning,
   deletion priority, clarity, and impact, applies the Critic necessity gate, adjudicates any
   Critic finding, and returns an accepted in-scope repair to the same Author.
5. After accepting the candidate, the primary orchestrator presents it and remaining material
   risks—or that none are known—for Owner approval.
6. After approval, the same Author appends the compact Log event using the approved semantic
   commit. The primary orchestrator applies mechanical state and reciprocal links and
   integrates the approval record. Do not reopen semantic review for this mechanical record.

Return the approved decision delta and its impact cone to `gmgn`; the router propagates only
affected downstream authority and resumes the stage that raised the change.

## Exit

Before returning, confirm that every retained D-ID is an explicit ruling needed by current
work and passes the deletion test; no ruling is normative in both Decision and a downstream
artifact; `Decision.md` contains current meaning only; `DecisionLog.md` contains history only;
IDs are unique and never reused; and normal downstream context does not depend on the Log.
