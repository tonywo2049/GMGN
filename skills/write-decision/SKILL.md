---
name: write-decision
description: "Use after WhitePaper approval and before ROADMAP, or whenever later work discovers or changes a project-level product, business, protocol, or architecture ruling that constrains multiple Milestones. Create or revise root Decision.md as current authority and DecisionLog.md as descriptive accepted-change history. 白皮书批准后、ROADMAP 之前，或后续工作发现/改变约束多个 Milestone 的项目级产品、业务、协议或架构决议时，创建或受控修订 Decision.md 与 DecisionLog.md。"
---

# Project decision authority

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

## Decide jurisdiction before content

First apply the GMGN authority table. Do not absorb WhitePaper meaning, ROADMAP allocation,
single-Milestone Goal or Requirement meaning, local Design choices, or Task state merely
because those decisions have consequences.

For a candidate not already owned elsewhere, answer:

1. Could applicable Milestones choose differently without contradiction?
2. Would the ruling still matter if the current Milestone disappeared?
3. Does it constrain a shared project object, protocol, identity, security, compatibility,
   or other authority used by multiple Milestones?

The primary orchestrator recommends the jurisdiction and option, explains the real
alternatives and cross-Milestone consequences, then asks the owner one material question at a
time. Do not create an Ask document. The owner makes the final ruling.

## Decision.md content

Keep the complete current set of accepted project-level rulings needed by current planning or
active work. Do not speculate about decisions no current work needs. Define each ruling as one
DocStar-compatible list entity:

```markdown
- **D-001** <short name>
  - Applies to: <Milestones or shared project objects>
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

1. Read the approved WhitePaper, current `Decision.md`, and only the Log history needed to
   preserve IDs or understand the proposed delta.
2. Resolve material jurisdiction and ruling questions with the owner.
3. Write the complete current Decision candidate. In revision mode, change only affected
   entries.
4. Process the semantic candidate through the registered `gmgn` Skill's shared document-
   candidate and dispatch rules. A selected Critic checks jurisdiction, current meaning,
   deletion, and impact.
5. Present the committed candidate and remaining material risks—or that none are known—for
   owner approval.
6. After approval, append the compact Log event using the approved semantic commit, apply
   mechanical state and reciprocal links, and commit that approval record. Do not reopen
   semantic review for this mechanical record.

Return the approved decision delta and its impact cone to `gmgn`; the router propagates only
affected downstream authority and resumes the stage that raised the change.

## Exit

Before returning, confirm that every retained D-ID passes the jurisdiction and deletion
tests; no current material cross-Milestone ruling needed by ROADMAP or active work remains
unresolved; `Decision.md` contains current meaning only; `DecisionLog.md` contains history
only; IDs are unique and never reused; and normal downstream context does not depend on the
Log.
