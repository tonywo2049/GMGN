---
name: gmgn
description: "Use first to route workflow-driven project work: new projects, product ideas, research, feature development, bug fixes, refactors, WhitePaper, project Decision, ROADMAP, PRD, requirements, design, task docs, coding delegation, launch, release, acceptance, or closure. 凡要按流程推进研发、调研、功能、修 bug、重构、写白皮书/项目决议/ROADMAP/PRD/需求/设计/任务、派活、上线发布、验收关账，或用户说按 GMGN/下一步做什么时使用。"
---

# GMGN router: repository state → next stage

Use observable repository state to select the owning stage, then invoke its specialized Skill.

## Language and shared references

Infer `en` or `zh-CN` from approved project documents, then the user's language. Keep machine
tokens and IDs in English. Load the layout-free
[writing rules](references/en/writing-rules.md) when writing and the
[dispatch contract](references/en/dispatch-and-handoff.md) before delegation.

Exclude every project-declared archive root from direct writing and review context, authority,
and evidence. Delegated work follows the dispatch contract's brief-level exclusion. Restore
needed meaning to the active tree through its owning authority before use.

## Route by observable state

| State | Route |
|---|---|
| New idea; no approved WhitePaper | `brainstorm` |
| Approved WhitePaper; Decision absent or changing | `write-decision` |
| Approved Decision; ROADMAP absent or changing | `roadmap` |
| A `now`, `not-started` Milestone has all prerequisites `closed` with accepted results and needs its combined initiation/Goal approval, or an approved Goal needs revision | `write-goal` |
| Approved Goal exists; Requirement absent or changing | `write-requirement` |
| Requirement reviewed; Design-stage candidate absent or changing | `write-design` |
| Design-stage candidate reviewed; Task absent or changing | `write-task` |
| An initiated Milestone has accepted Task rows that can run, or a target-Milestone lane remains active | `run-task` |
| Every target-Milestone task is closed on one baseline but closure review or integration is incomplete | `close-milestone` |
| An immutable candidate is accepted and distribution is requested | `release` |

When observable evidence shows unfinished work in a closed Milestone, mechanically move it
back to `initiated`, replace its current `accepted_result` with `none`, and route the missing
work through the owning stage below. Reopen only affected Tasks or add missing Tasks. Check
downstream impact without automatically rolling back downstream Milestones.

From `roadmap` onward, record the approved Decision commit and applicable D-IDs; normal stage
context never reads `DecisionLog.md`. A D-ID may apply at any scope. Once present, downstream
artifacts consume it by link instead of redefining its ruling. From `write-goal` onward, also
record `target_milestone_id` and the available Goal, Requirement, Design, applicable Contract,
and Task anchors. A link to another Milestone gives context, not execution authority. Keep
separately initiated Milestones as separate execution sets and closure decisions.

When any later stage changes a current D-ID or selects a new ruling for Decision, route it
through `write-decision` regardless of subject or Milestone scope. Pause only its impact cone
and resume the stage that raised it after owner approval and affected propagation.

## Roles and independent checks

The primary orchestrator keeps context and acts only as the exact relay, mechanical scheduler,
workspace manager, deterministic checker, integration owner, and shared-state updater. It does
not plan solutions, conduct semantic owner dialogue, write document candidates, decide Critic
necessity, or adjudicate findings. One bounded Adjudicator owns those semantic actions for each
case and may remain assigned through owner waits and child dispatches. Independent cases may
use parallel Adjudicators; overlapping declared authority or impact cones remain serialized.
Delegated roles follow the dispatch contract.

Select independent roles by the surface that changed:

| Changed surface | Independent role |
|---|---|
| WhitePaper/Decision/ROADMAP/Goal/Requirement/Design/Task meaning | Critic necessity gate |
| Implementation or test-code diff | Reviewer under the owning execution Skill |
| Recorded `required:<trigger>` classification | Verifier after Review blockers clear |
| Equivalent links, formatting, pointers, or status | Machine checks only |

Before dispatching a Critic, the active Adjudicator identifies a concrete material harm that
the owner has not accepted, that no accepted effective fallback contains, and that independent
criticism could plausibly use to change acceptance or the next action. Dispatch one fresh
Critic only when such a risk can be named or the Adjudicator cannot decide. Otherwise skip
Critic, record one sentence explaining why, and run affected machine checks.

Critic and Reviewer do not maximize finding count. A valid return may contain no findings.
Report an issue only when leaving it unresolved creates concrete material harm, no accepted
effective fallback contains that harm, and a smallest sufficient correction can be stated.
Each semantic candidate batch has at most one Critic round, and each Task execution has
exactly one Reviewer round. The primary orchestrator forwards judgment-bearing returns
unchanged to the active Adjudicator, which rules on findings and fix meaning. The primary
orchestrator checks candidate identity and runs affected machine checks without dispatching
that role again. A fix that introduces new meaning is a separately scoped semantic batch, not
a re-review of the prior batch.

A Verifier is exceptional. Apply the final-candidate classification from the
[assurance policy](references/en/assurance-policy.json) mechanically when recorded facts make
it explicit; route only judgment-dependent trigger applicability to the active Adjudicator.
Use `not-required` or `required:<trigger>` and do not dispatch while relevant Review blockers
remain. The owning stage defines candidate timing and fix handling.

## Minimality gates

Every stage writer keeps only content required for that document's purpose. A retained item
must change the document's result if removed. Stage documents do not contain downstream
propagation rules, downstream gates, next-stage instructions, speculative placeholders, or
document maps without real children. A possible future need is not an owner.

Requirement and Design apply the same deletion test to each R/AC, design element, dependency,
and configuration item. `write-task` solely owns Task necessity and boundary semantics; Task
count itself is not a measure of simplicity or overdesign. `run-task` owns implementation
minimality and its required code tools.

The registered `write-design` Skill owns conditional Design-stage artifact selection,
interface authority, Bundle acceptance, and final Contract reconciliation. This router does
not restate those stage rules.

## Document candidates

The active Adjudicator conducts the owner dialogue and prepares one bounded semantic Author
brief only when the candidate is ready to write. One Author creates, self-checks, commits, and
revises that document candidate while its objective and write boundary remain unchanged. The
primary orchestrator adds only runtime and workspace facts and never drafts the candidate.
Every semantic document change applies the Critic necessity gate. The Adjudicator rules on
accepted findings and sends in-scope fixes to the same Author; the primary orchestrator runs
affected machine checks. Equivalent mechanical propagation does not create another semantic
review. A change that invents new meaning is a new semantic batch owned by its stage.

The primary orchestrator performs links, machine checks, and integration. Do not create an
Integrator role.

## Task execution

`Task.md` is the Milestone index: stable task rows, AC mapping, dependencies, macro status, and
execution pointers. The registered `run-task` Skill solely owns Card/Log materialization,
verification contracts, the dependency-aware ready set, capacity prioritization, writer
lanes, runtime tools, Codex agent monitoring, the single implementation Review,
risk-triggered verification, shared-baseline checks, and Task closure. Do not copy those
rules here.

## Controlled-change routing

Route a semantic change to the single authority that owns it:

| Authority changed | Route |
|---|---|
| WhitePaper problem, goal, scope, invariant, or interpretation | `brainstorm` revision |
| Any current D-ID, or any new ruling selected for Decision regardless of subject or Milestone scope | `write-decision` revision |
| ROADMAP Milestone allocation, outcome, value, deliverable, success signal, horizon, priority, dependency, or Backlog placement | `roadmap` maintenance |
| Goal active boundary, necessary Milestone-local exclusion, ROADMAP deliverable/success-signal coverage, or qualitative Close outcome | `write-goal` revision |
| Requirement behavior, quantified parameter, constraint, or decidable AC | `write-requirement` revision |
| Design structure, implementation decision, interface contract, data, or failure path | `write-design` revision |
| Task division, dependency, AC mapping, status, or execution pointer | `write-task` revision |

The current D-ID takes precedence over the category rows below it. When no D-ID exists and no
new Decision entry is selected, route the meaning to its normal stage authority.

Start from the approved commit, record the semantic delta and impact cone, and update only
affected authority, tasks, code, tests, evidence, and state. Meaning-preserving mechanical
changes use machine checks without reapproval. Reopening a Milestone does not by itself
reopen its normative documents or unaffected work.

For a narrow bug or mechanical one-step change, identify the smallest authority and
acceptance condition, implement it, independently review the diff, add risk-triggered
verification only when required, and refresh state. Do not fabricate the full document chain.

<HARD-GATE>Never skip a missing prerequisite, redefine upstream meaning downstream, execute an
unauthorized Milestone, let a delegated agent self-review, expose an unchecked implementation
combination as the shared baseline, or push, publish, or deploy without explicit authority.</HARD-GATE>

Before every substantive return, self-check the active contract and correct in-scope defects.
Disclose only unresolved material risk; do not output a fixed `Reflection` section.
