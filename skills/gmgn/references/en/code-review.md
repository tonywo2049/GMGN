---
locale: en
purpose: Define the single independent implementation Review surface, evidence, and finding format across supported runtimes.
upstream: [GMGN methodology](../../../../GMGN.md), [dispatch and handoff](dispatch-and-handoff.md)
downstream: [Reviewer role](../../../../agents/reviewer.md)
status: approved
type: task
nature: normative
---

# Code-review contract

## 1. Select the surface

- Codex Desktop: `/review`.
- Codex CLI: `codex review --commit <short-commit>` or `--base <branch>`; do not combine a
  scope flag with a custom prompt.
- Claude Code: an independent no-edit Reviewer that may run prepared commands; use
  `/code-review` only when the user authorized work on a GitHub PR.
- If the native surface is unavailable, dispatch an independent no-edit Reviewer with the
  permissions required by its prepared plan; do not skip Review.

Every Review is a fresh dispatch under the
[dispatch contract](dispatch-and-handoff.md). Each Task execution has exactly one Reviewer
round. The Reviewer never inherits writer or earlier-agent conversation history.

## 2. Review the complete candidate

Before Review, commit and freeze the complete implementation and test-code candidate. Bind the
brief to that candidate and its applicable Requirement, Design, Contract, Card, write
boundary, and prepared checks. Never review an uncommitted mutable diff or only a correction
commit.

Apply every question below to the assigned surface:

1. Does it satisfy its Requirement, Design, Contract, Card, and prepared write boundary?
2. Can each changed test or executable check fail when the implementation is wrong?
3. Does leaving an observed issue unresolved cause concrete correctness, regression, safety,
   data, accessibility, performance, or acceptance harm?
4. Does an accepted effective fallback already contain that harm?
5. What is the smallest sufficient correction?

A valid Review may return no findings. Omit preference-only, speculative, low-impact,
cleanup, refactoring, broader-coverage, or adequately contained observations when they do not
change acceptance or the next action. Do not propose a broader redesign when a smaller
correction or effective fallback is sufficient.

Run every deterministic targeted, negative, integration, and project check required by the
prepared brief. Add exploratory checks only for a concrete risk. A skipped, timed-out, or
unavailable required tool or command is not a pass.

## 3. Preserve and return evidence

Do not intentionally edit workspace files. Prefer a disposable copy when a command may write;
otherwise allow only declared generated or cache paths. Recompare tracked content with the
candidate only after a command or event that could change it. Material content drift
invalidates the Review.

Return material findings or explicit no-findings coverage together with exact commands,
environment, exit codes, limitations, and side effects. The return identifies the reviewed
candidate. Interim questions follow the dispatch contract. The primary orchestrator forwards
material findings unchanged to the active Adjudicator, which adjudicates them and the semantic
sufficiency of accepted fixes. The primary orchestrator checks candidate identity and runs
affected machine checks without another Reviewer round. A `no findings` return follows the
owning execution Skill's deterministic transition without a mandatory Adjudicator hop.
