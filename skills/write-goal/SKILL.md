---
name: write-goal
description: "Use when an approved ROADMAP exists and the owner explicitly starts or initiates a not-started milestone, phase, or version; create Goal.md with objective decomposition, scope boundary, and slices. Also use for a controlled semantic revision of an existing Goal authority. ROADMAP 已批且负责人点名启动/开工某个 Milestone、版本或阶段时立项，撰写 Goal、目标拆解、范围边界与切片；也用于既有 Goal 权威的受控语义修订。触发词包括启动 M2、开做里程碑、立项。"
---

# Initiate a milestone and write Goal.md

<HARD-GATE>Creation mode requires an approved ROADMAP commit, a `not-started` milestone row, and explicit owner initiation; otherwise return to `roadmap`. Revision mode requires an existing initiated Goal and its approved ROADMAP commit, but does not require re-initiation. If the changed meaning belongs to WhitePaper or ROADMAP, return to `brainstorm` or `roadmap` before editing Goal. Work on an uninitiated milestone is out of scope.</HARD-GATE>

## Language and contract

Before writing, load the registered `gmgn` Skill through normal discovery and follow its local
writing contract. Use the ROADMAP locale unless the owner changes it explicitly. Keep filename
`Goal.md`, `type: goal`, and `nature: normative`.

## Goal content

- Derive Goal only from the approved ROADMAP Milestone and its WhitePaper authority.
  Requirement, Design, Task, implementation, or evidence may trigger a controlled revision
  but cannot silently redefine Goal.
- State the intended change, active boundary, non-goals, and result-based slices. Split slices
  by independently meaningful results, not by team, component, or file.
- Carry ROADMAP deliverables forward only as mappings; Goal does not redefine them. Map every
  deliverable to one or more slices, and require every slice to contribute to a ROADMAP
  deliverable or acceptance scenario.
- Map every ROADMAP acceptance-scenario anchor to one or more slices and a qualitative
  observable outcome. Requirement refines that meaning into parameters and decidable ACs.
- State only upstream-derived capabilities and qualitative constraints needed to bound
  downstream work. Requirement owns quantified parameters and acceptance conditions; Design
  owns implementation choices; Task owns work division, order, and status. Goal may reference
  a number already approved upstream without becoming its parameter authority.
- Resolve before Requirement every open decision owned by Goal. Route upstream-owned gaps to
  their authority and leave downstream-owned choices to their proper stage.
- Include the document map and known gaps. Do not include component or interface design, code
  structure, test cases, commands, results, task breakdown, live status, research history,
  candidate comparisons, closure history, or conclusions copied from downstream.

## One change batch

The recorded writer performs one semantic batch:

1. Change the ROADMAP row from `not-started` to `initiated` and record the owner authorization.
2. Create the milestone directory and `Goal.md` as its single entry document, following
   `Goal content`. The writer chooses the section structure.
3. Add reciprocal ROADMAP ↔ Goal links and return one committed candidate.

Do not create Requirement, Design, or Task content early. Mention absent downstream files
as gaps; create each only when its stage starts.

## Writer and critic loop

Record the ROADMAP commit and owner initiation. The primary session may write directly, or it
prepares a complete brief and creates one fresh Author when the bounded
handoff creates real value. The writer self-checks before return; a delegated Author ends on
return, so later correction uses the primary session or a fresh Author with a new brief.
Commit the complete candidate locally and dispatch one fresh independent Critic from a
prepared brief that names the shortest unambiguous commit reference. Collect all
findings before editing, adjudicate once, and batch accepted blocker fixes. The primary
orchestrator checks each resolution without dispatching a second Critic, then reviews the
committed candidate, applies accepted mechanical propagation, and runs machine checks.

## Controlled revision

1. Start from the old Goal commit and record the trigger, semantic delta, affected slices,
   documents, and evidence, plus the proposed new commit.
2. Route WhitePaper-owned meaning to `brainstorm` revision mode and ROADMAP-owned deliverables,
   qualitative acceptance picture, sequencing, cross-milestone allocation, or dependency to
   `roadmap` maintenance mode. Resume here after the required upstream approval; do not patch
   that meaning into Goal.
3. Revise only Goal-owned objectives, boundaries, non-goals, result-based slices, ROADMAP
   deliverable/acceptance-scenario mappings, or document mapping. Preserve unaffected content.
4. If the delta changes a decision or reasonable understanding, run the independent critic
   and primary-orchestrator review against the affected content and bind it to a new commit.
   Old review remains attached to the old commit.
5. Propagate only to affected Requirement, Design, Task, implementation, test, evidence, and
   state representations. Review and verify that impact cone only; do not rerun unrelated
   stages.

Meaning-preserving mechanical changes use same-batch link and status refresh plus
machine checks without reapproval.

## Exit

Require the recorded writer to confirm:

- deleting all downstream documents leaves Goal's objective and boundary complete;
- every ROADMAP deliverable and acceptance scenario maps to slices, and every slice
  contributes to at least one of them;
- Requirement only needs to refine the stage results, not invent them;
- every Goal-owned open decision is resolved before Requirement;
- no component, interface, test, task, or implementation result leaks into Goal; and
- an invalid mapping returns to `roadmap` instead of changing upstream meaning in Goal.

For creation or a semantic revision, run the fresh-agent writer/Critic loop using the
English-only dispatch contract, obtain primary-orchestrator review, and integrate only when
required by workspace topology. Creation then uses **REQUIRED next skill:
`write-requirement`**. A revision returns to the stage that raised it and continues through
the affected path only.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
