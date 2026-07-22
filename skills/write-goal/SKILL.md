---
name: write-goal
description: "Use when an approved ROADMAP exists and the owner explicitly starts or initiates a not-started milestone, phase, or version; create Goal.md with objective decomposition, scope boundary, and slices. Also use for a controlled semantic revision of an existing Goal authority. ROADMAP 已批且负责人点名启动/开工某个 Milestone、版本或阶段时立项，撰写 Goal、目标拆解、范围边界与切片；也用于既有 Goal 权威的受控语义修订。触发词包括启动 M2、开做里程碑、立项。"
---

# Initiate a milestone and write Goal.md

<HARD-GATE>Creation mode requires an approved ROADMAP, a `not-started` milestone row, and explicit owner initiation; otherwise return to `roadmap`. Revision mode requires an existing initiated Goal and its approved ROADMAP anchor, but does not require re-initiation. If the changed meaning belongs to WhitePaper or ROADMAP, return to `brainstorm` or `roadmap` before editing Goal. Work on an uninitiated milestone is out of scope.</HARD-GATE>

## Language and contract

Use the ROADMAP locale unless the owner changes it explicitly. Load the English-only
layout-free [writing contract](../gmgn/references/en/writing-contract.md). Keep filename
`Goal.md`, `type: goal`, and `nature: normative`.

## One change batch

The recorded writer performs one semantic batch:

1. Change the ROADMAP row from `not-started` to `initiated` and record the owner authorization.
2. Create the milestone directory and `Goal.md` as its single entry document. It must answer:
   objective, boundary, slices, non-goals, document map, known gaps, and how every ROADMAP
   acceptance-scenario anchor maps to one or more Goal slices. Goal may clarify the active
   boundary but must not copy or redefine the ROADMAP outcome. The writer chooses the section
   structure.
3. Add reciprocal ROADMAP ↔ Goal links and return one anchored candidate.

Do not create Requirement, Design, or Task content early. Mention absent downstream files
as gaps; create each only when its stage starts.

## Writer and critic loop

Record the ROADMAP anchor and owner initiation. The primary session may write directly, or it
prepares a complete brief and creates one fresh Author when the bounded
handoff creates real value. The writer self-checks before return; a delegated Author ends on
return, so later correction uses the primary session or a fresh Author with a new brief. Freeze
the candidate and dispatch one fresh independent Critic from a prepared brief. Collect all
findings before editing, adjudicate once, and batch accepted blocker fixes. The primary
orchestrator checks each resolution without dispatching a second Critic, then reviews the
anchored candidate, applies accepted mechanical propagation, and runs machine checks.

## Controlled revision

1. Start from the old Goal anchor and record the trigger, semantic delta, affected slices,
   documents, and evidence, plus the proposed new anchor.
2. Route WhitePaper-owned meaning to `brainstorm` revision mode and ROADMAP-owned sequencing,
   cross-milestone allocation, dependency, or qualitative milestone-row meaning to `roadmap`
   maintenance mode. Resume here after the required upstream approval; do not patch that
   meaning into Goal.
3. Revise only Goal-owned objectives, boundaries, slices, non-goals, acceptance-scenario
   mapping, or document mapping. Preserve unaffected content.
4. If the delta changes a decision or reasonable understanding, run the independent critic
   and primary-orchestrator review against the affected content and bind it to a new anchor.
   Old review remains attached to the old anchor.
5. Propagate only to affected Requirement, Design, Task, implementation, test, evidence, and
   state representations. Review and verify that impact cone only; do not rerun unrelated
   stages.

Meaning-preserving mechanical changes use same-batch link, hash, and status refresh plus
machine checks without reapproval.

## Exit

Require the recorded writer to self-check the ROADMAP boundary and slices, and confirm that
every ROADMAP acceptance scenario maps to Goal slices without changing its meaning. If that
mapping is not valid, return to `roadmap` instead of hiding the gap in Goal. For creation or a
semantic revision, run the fresh-agent writer/Critic loop using the English-only dispatch
contract, obtain primary-orchestrator review, and integrate only when required by
workspace topology. Creation then uses **REQUIRED next skill:
`write-requirement`**. A revision returns to the stage that raised it and continues through
the affected path only.

Before every substantive return, perform a task-specific self-check and correct defects. Do
not output a fixed `Reflection` section. Disclose only material unresolved risks that could
change the conclusion, decision, acceptance, or downstream work; otherwise omit the
disclosure. Approval, acceptance, and closure always state remaining material risks or that
none are known.
