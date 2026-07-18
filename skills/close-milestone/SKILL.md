---
name: close-milestone
description: "Use when every milestone card is closed and traceability is full to perform release acceptance, full regression/E2E, combined review, milestone/stage/version closure, launch readiness, or ROADMAP backfill. 所有任务卡已关账后用于里程碑/阶段/版本完成、收尾/关账/验收、跑回归/E2E、准备上线、发版/发布；普通单卡收尾不触发。"
---

# Close a milestone

<HARD-GATE>Every card must be `closed`, and every in-scope AC must have a task, test, and evidence row. Otherwise return to `run-task`. Closure is an owner-accepted, version-anchored declaration; do not infer it from green unit tests.</HARD-GATE>

## Establish evidence first

- Run the complete project regression at the closing revision.
- Run milestone-level startup/E2E through the real product path, including negative and
  recovery cases required by the specification.
- Record exact commands, environment, revision, exit codes, and result summaries.
- Run an independent combined review across Requirement, Design, Task, code, and evidence.

## Three closure disciplines

1. Scope: every AC is implemented, explicitly deferred, or removed by owner decision.
2. Evidence: every closure criterion has a replayable real verification path.
3. State: Task, matrix, ROADMAP, Decision, version anchors, and Handoff refresh together.

## Machine checks and checklist

When DocStar is available, run `check --preset gmgn-v1 --json` and relevant gates. Verify
`classification_complete`; a non-zero gate finding or command exit code is a red light, not
an informational note. When DocStar is absent, run equivalent repository link/table checks
and disclose that substitution. Complete the locale-matched `pre-close-checklist.md`.

## Presentation and close

Present scope, evidence, known debt, weakest assumption, and the version anchor to the
owner. Only after explicit acceptance:

- set the milestone and normative chain to `closed` where appropriate;
- create/update Handoff with `type: handoff`, `nature: descriptive`, one-line state,
  baseline, completed work, remaining work, risks, authority pointers, and next command;
- if DocStar uses a project classification mapping, reuse a registered type/token;
- commit the same batch. Do not push, publish, deploy, or release unless separately authorized.

## Exit

Update ROADMAP with closure evidence and the receiving state. **REQUIRED next skill:
`roadmap`** for maintenance or the next milestone.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
