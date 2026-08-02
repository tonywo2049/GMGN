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

The primary orchestrator retains complete context. Outside `run-task`, it conducts semantic
Owner dialogue, analyzes evidence, makes workflow and semantic decisions, schedules agents,
adjudicates Critic and Reviewer findings, integrates accepted candidates, and updates shared
state. It may perform meaning-preserving mechanical edits, but it never writes an upstream
authority, plan, or design candidate. Creation or semantic revision of WhitePaper, Decision,
ROADMAP, Goal, Requirement, Design, Task, or equivalent authority requires an independent
Author. Do not create an Author when no candidate is needed.

Only `run-task` uses a Commander for bounded global judgment and one Runner per Task. The
primary orchestrator creates or resumes Commanders and mechanically creates Runners from
their complete briefs. A Commander is not used in other stages. Delegated roles follow the
dispatch contract.

Select the check path by the surface that changed:

| Changed surface | Check path |
|---|---|
| Fixed WhitePaper/Decision/ROADMAP/Goal/Requirement/Design/Task candidate | Primary orchestrator applies the Critic necessity gate and adjudicates any Critic findings |
| Fixed complete implementation/test candidate in normal `run-task` | Its Runner reviews under `code-review`; independent Reviewer only when explicitly required |
| Recorded `required:<trigger>` classification | Fresh Verifier after relevant review blockers clear |
| Equivalent links, formatting, pointers, or status | Machine checks only |

Before dispatching a Critic, the primary orchestrator identifies concrete material harm that
the Owner has not accepted, no accepted effective fallback contains, and independent criticism
could plausibly change acceptance or the next action. Dispatch one fresh Critic only when that
risk can be named or the primary orchestrator cannot decide. Otherwise skip Critic, record one
sentence explaining why, and run affected machine checks. A meaning-preserving mechanical edit
never needs a Critic.

Critic and Reviewer do not maximize finding count. A valid return may contain no findings.
Report an issue only when leaving it unresolved creates concrete material harm, no accepted
effective fallback contains that harm, and a smallest sufficient correction can be stated.
Each semantic candidate batch has at most one Critic round. The primary orchestrator adjudicates
document findings; the Runner adjudicates in-Task implementation findings. An accepted in-scope
repair returns to the same Author or Coder while objective and write boundary remain unchanged.
After a fix, the adjudicating caller inspects the exact delta and reruns only affected checks.
An omitted stage-owned decision required by an accepted finding remains a repair in the same
batch. Only a change to accepted or upstream authority or a material expansion of the prepared
objective or write boundary creates a separately scoped batch.

A Verifier is exceptional. Apply the final-candidate classification from the
[assurance policy](references/en/assurance-policy.json) mechanically when recorded facts make
it explicit. The primary orchestrator owns classification outside `run-task`; the Runner owns
it for its Task and returns any cross-Task or authority question through the Commander path.
Use `not-required` or `required:<trigger>` and do not dispatch until relevant review blockers
clear. The owning stage defines candidate timing and fix handling.

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

The primary orchestrator conducts Owner dialogue, resolves the candidate meaning, and prepares
one bounded Author brief only when the candidate is ready to write. One independent Author
creates, self-checks, commits, and revises that document candidate while its objective and write
boundary remain unchanged. The Author's self-check is not review.

After the complete candidate is fixed, the primary orchestrator checks identity, runs affected
machine checks, and applies the Critic necessity gate. It adjudicates any Critic findings and
sends an accepted in-scope repair to the same Author. An omitted stage-owned decision required
by that finding remains a repair in the same Author dispatch. It becomes a new semantic batch
only when accepted or upstream authority changes or the prepared objective or write boundary
materially expands. Meaning-preserving links, formatting, pointers, and state mirrors may be
applied mechanically by the primary orchestrator with machine checks only.

For these document candidates, the primary orchestrator performs links, machine checks, and
integration. Do not create an Integrator role.

## Task execution

`Task.md` is the Milestone index: stable task rows, AC mapping, dependencies, macro status, and
execution pointers. The registered `run-task` Skill solely owns Card/Log materialization,
verification contracts, the dependency-aware ready set, capacity prioritization, writer
lanes, runtime tools, Codex agent monitoring, Runner review, risk-triggered verification,
integration by a Commander, shared-baseline checks, and Task closure. On run-task entry, the
primary orchestrator creates a Commander without collecting or analyzing the ready set; the
Commander reads current authority and returns complete Runner briefs. Do not copy the detailed
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
| Task division, dependency, AC mapping, or execution-pointer meaning | `write-task` revision |

The current D-ID takes precedence over the category rows below it. When no D-ID exists and no
new Decision entry is selected, route the meaning to its normal stage authority.

Start from the approved commit, record the semantic delta and impact cone, and update only
affected authority, tasks, code, tests, evidence, and state. Meaning-preserving mechanical
changes, including Task status and execution-pointer refresh, use machine checks under the
active owning stage without reapproval. Reopening a Milestone does not by itself
reopen its normative documents or unaffected work.

For a narrow bug or mechanical one-step change, identify the smallest authority and acceptance
condition. Route implementation through the smallest applicable Task and `run-task`; apply a
meaning-preserving document edit mechanically when allowed, add risk-triggered verification
only when required, and refresh state. Do not fabricate the full document chain.

<HARD-GATE>Never skip a missing prerequisite, redefine upstream meaning downstream, execute an
unauthorized Milestone, let a delegated writer accept its own candidate, expose an unchecked
implementation combination as the shared baseline, or push, publish, or deploy without
explicit authority.</HARD-GATE>

Before every substantive return, self-check the active contract and correct in-scope defects.
Disclose only unresolved material risk; do not output a fixed `Reflection` section.
