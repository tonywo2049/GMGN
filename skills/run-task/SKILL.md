---
name: run-task
description: "Use when an approved task card is explicitly confirmed: implement a task, feature, bug fix, refactor, test, or code change through a coding agent and close the card after review. 任务卡已确认要做时开发功能、修复缺陷/修 bug、重构、写测试/写代码、实现任务、完成任务卡；用户说开做这张卡、开始编码、把任务做完时触发。"
---

# Implement one task card

<HARD-GATE>The card must exist in a critic-reviewed and orchestrator-reviewed `Task.md`, and the owner/orchestrator must have confirmed it for execution. Otherwise return to `write-task`. If implementation exposes a changed upstream premise, pause the affected card and route to its authority; do not make code or Task prose silently redefine the specification.</HARD-GATE>

Use the document locale for status updates and the user's language for conversation. Keep
all machine tokens and IDs unchanged.

The primary orchestrator keeps card state, agent refs, adjudication, acceptance, and merge
control. It does not write implementation, repair review findings, run verification in place
of the Verifier, or perform mechanical ledger edits in place of the Integrator.

## Six steps

1. **Compile context** — use `docstar brief <task-id> --preset gmgn-v1 --json` when available;
   otherwise read the card, prerequisites, spec anchors, Design locations, and test path.
2. **Dispatch coder** — at `ready-to-dispatch`, use the locale-matched dispatch contract;
   record `coder_ref` and enter `coder-active`. Require one approved card, allowed paths,
   failing-first discrimination, first-sufficient implementation, real call path, exact
   verification, and no remote writes. Parallelize only dependency-free cards.
3. **Accept return** — at `coder-returned`, require artifacts/evidence,
   deviations/decisions, and Reflection. Return missing or out-of-scope work to the same
   Coder; otherwise compare the returned paths and persisted evidence to the dispatch,
   create `candidate-anchored`, and leave command execution to the Reviewer/Verifier.
4. **Independent code review** — dispatch a read-only Reviewer and retain `reviewer_ref`.
   Use the locale-matched `code-review.md` and review only the card increment. At
   `reviewer-returned`, the orchestrator adjudicates findings and resumes the same Coder in
   `coder-revising`; blocker fixes return to the same Reviewer in `reviewer-rechecking`.
   A native review surface without a resumable identity performs a full review each time and
   cannot be treated as a targeted same-Reviewer recheck.
5. **Verify** — after review blockers clear, dispatch an independent Verifier as
   `verifier-active`. It runs the targeted test, relevant integration/startup/E2E and
   negative path, plus project gates at the candidate anchor, then returns exact commands,
   environment, exit codes, and limitations as `verifier-returned`. A skipped or unavailable
   command is not a pass. Verification failure returns to the same Coder and repeats affected
   review and verification.
6. **Card close** — after primary-orchestrator acceptance, dispatch an Integrator to refresh
   `Task.md`, traceability, and upstream state in one batch. Re-read
   all of `Task.md` and scan stale assertions: `not-started`, `pending`, `not created`,
   `not run`, `awaiting confirmation`, plus `待执行`, `未创建`, `未运行`, `待确认`, old output,
   and old Reflection. Mechanically refresh them or explain why they remain true. Run
   `git diff --check`, link checks, and `git status --short`; prepare or create the topic
   commit under repository policy. The orchestrator verifies the integration and marks
   `node-complete`. Do not push unless explicitly authorized.

## Upstream change during execution

When implementation evidence contradicts an approved premise:

1. Stop the affected card at the current anchor and record the observation, old authority
   anchor, proposed semantic delta, and impact cone.
2. Route WhitePaper to `brainstorm`, ROADMAP to `roadmap`, Goal to `write-goal`, Requirement
   or R-AC meaning to `write-requirement`, Design intent to `write-design`, and Task execution
   authority to `write-task`.
3. Resume only after the changed authority has the review or approval required for its new
   anchor. Resume the same `coder_ref`; update only affected downstream documents, cards,
   code, tests, evidence, and state; do not restart unrelated work. If that Coder is unavailable,
   enter `agent-unavailable` and perform an explicit replacement handoff.
4. For a meaning-preserving mechanical change, refresh affected representations in the same
   batch and run machine checks without reapproval.

## Exit

If cards remain, continue `run-task` only after the next card is confirmed. When all cards
are `closed` and traceability is full, **REQUIRED next skill: `close-milestone`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
