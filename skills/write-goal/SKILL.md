---
name: write-goal
description: "Use when an approved ROADMAP exists and the owner explicitly starts or initiates a not-started milestone, phase, or version; create Goal.md with objective decomposition, scope boundary, and slices. ROADMAP 已批且负责人点名启动/开工某个 Milestone、版本或阶段时立项，撰写 Goal、目标拆解、范围边界与切片；触发词包括启动 M2、开做里程碑、立项。"
---

# Initiate a milestone and write Goal.md

<HARD-GATE>The ROADMAP must be approved, the milestone row must exist with `not-started`, and the owner must explicitly start it. Otherwise return to `roadmap`. Work on an uninitiated milestone is out of scope.</HARD-GATE>

## Language and contract

Use the ROADMAP locale unless the owner changes it explicitly. Load the matching
[English](../gmgn/references/en/writing-contract.md) or
[中文](../gmgn/references/zh-CN/writing-contract.md) Goal template. Keep filename `Goal.md`,
`type: goal`, and `nature: normative`.

## One change batch

1. Change the ROADMAP row from `not-started` to `initiated` and record the authorization.
2. Create the milestone directory and `Goal.md` as its single entry document: objective,
   boundary, slices, non-goals, qualitative completion picture, document map, and known gaps.
3. Add reciprocal ROADMAP ↔ Goal links and commit the same batch.

Do not create Requirement, Design, or Task content early. Mention absent downstream files
as gaps; create each only when its stage starts.

## Exit

Self-check the ROADMAP boundary and slices. Run one independent critic with the
locale-matched `critic-brief.md`, resolve findings, obtain primary-orchestrator review,
commit, then **REQUIRED next skill: `write-requirement`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
