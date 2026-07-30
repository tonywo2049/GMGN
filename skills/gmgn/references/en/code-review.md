---
locale: en
purpose: Define full and bounded material-fix delta Review surfaces, evidence, and finding format across supported runtimes.
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
[dispatch contract](dispatch-and-handoff.md). The Reviewer never inherits writer or earlier
Reviewer conversation history.

## 2. Select the Review mode

Use `review_mode: full` for the complete candidate before its first implementation Review.
Bind the brief to the committed candidate and applicable Requirement, Design, Contract, Card,
write boundary, and prepared checks.

Use `review_mode: delta` only when the owning stage requests its second and final Review round
for a material-fix delta. Bind the brief to:

- the original reviewed candidate;
- the current fixed candidate;
- accepted findings and rulings;
- the complete cumulative fix delta;
- the direct impact boundary; and
- affected checks.

A delta Reviewer verifies only that accepted first-round findings are resolved and that the
cumulative fix delta introduced no regression in its direct impact. It does not repeat the
full Review, search or report unrelated pre-existing problems, broaden the original surface,
or inherit the prior Review conversation. The owning stage decides whether this mode is
required and owns the two-round limit.

## 3. Review the assigned surface

Before Review, commit and freeze the complete assigned candidate. Never review an uncommitted
mutable diff or only the last correction commit.

For a full candidate, apply every question below to the assigned surface. For a delta, apply
them only to the accepted first-round findings, cumulative fix delta, and regressions caused
by that delta:

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

Run every tool and deterministic targeted, negative, integration, and project check required
by the prepared brief. Add exploratory checks only for a concrete risk. A skipped, timed-out,
or unavailable required tool or command is not a pass.

## 4. Preserve and return evidence

Do not intentionally edit workspace files. Prefer a disposable copy when a command may write;
otherwise allow only declared generated or cache paths. Recompare tracked content with the
candidate only after a command or event that could change it. Material content drift
invalidates the Review.

Return material findings or explicit no-findings coverage together with exact commands,
environment, exit codes, limitations, and side effects. The return identifies the reviewed
candidate and, for delta mode, the cumulative delta boundary. One return ends the Reviewer.
