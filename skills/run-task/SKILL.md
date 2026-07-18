---
name: run-task
description: "Use when an approved task card is explicitly confirmed: implement a task, feature, bug fix, refactor, test, or code change through a coding agent and close the card after review. 任务卡已确认要做时开发功能、修复缺陷/修 bug、重构、写测试/写代码、实现任务、完成任务卡；用户说开做这张卡、开始编码、把任务做完时触发。"
---

# Implement one task card

<HARD-GATE>The card must exist in a critic-reviewed and orchestrator-reviewed `Task.md`, and the owner/orchestrator must have confirmed it for execution. Otherwise return to `write-task`. If implementation exposes a changed upstream premise, pause the affected card and route to its authority; do not make code or Task prose silently redefine the specification.</HARD-GATE>

Use the document locale for status updates and the user's language for conversation. Keep
all machine tokens and IDs unchanged.

## Six steps

1. **Compile context** — use `docstar brief <task-id> --preset gmgn-v1 --json` when available;
   otherwise read the card, prerequisites, spec anchors, Design locations, and test path.
2. **Dispatch coder** — fill the locale-matched `coder-brief.md`; the orchestrator delegates
   implementation and retains acceptance/merge. Parallelize only dependency-free cards.
3. **Accept return** — require artifacts/evidence, deviations/decisions, and Reflection.
   Replay targeted commands and inspect the real path proportionally to risk.
4. **Independent code review** — use the native review surface or a read-only reviewer with
   the locale-matched `code-review.md`. Review only the card increment. Findings report; the
   orchestrator decides and sends fixes back to the coder.
5. **Verify** — run the targeted test, relevant integration/startup/E2E path, and any project
   gate. A skipped or unavailable command is not a pass.
6. **Card close** — refresh `Task.md`, traceability, and upstream state in one batch. Re-read
   all of `Task.md` and scan stale assertions: `not-started`, `pending`, `not created`,
   `not run`, `awaiting confirmation`, plus `待执行`, `未创建`, `未运行`, `待确认`, old output,
   and old Reflection. Mechanically refresh them or explain why they remain true. Run
   `git diff --check`, link checks, and `git status --short`; commit by topic. Do not push
   unless explicitly authorized.

## Upstream change during execution

When implementation evidence contradicts an approved premise:

1. Stop the affected card at the current anchor and record the observation, old authority
   anchor, proposed semantic delta, and impact cone.
2. Route WhitePaper to `brainstorm`, ROADMAP to `roadmap`, Goal to `write-goal`, Requirement
   or R-AC meaning to `write-requirement`, Design intent to `write-design`, and Task execution
   authority to `write-task`.
3. Resume only after the changed authority has the review or approval required for its new
   anchor. Update only affected downstream documents, cards, code, tests, evidence, and state;
   do not restart unrelated work.
4. For a meaning-preserving mechanical change, refresh affected representations in the same
   batch and run machine checks without reapproval.

## Exit

If cards remain, continue `run-task` only after the next card is confirmed. When all cards
are `closed` and traceability is full, **REQUIRED next skill: `close-milestone`**.

End every substantive response with **Reflection**: weakest assumption; neglected
counterexample; measured versus inferred.
