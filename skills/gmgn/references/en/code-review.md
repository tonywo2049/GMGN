---
locale: en
purpose: Define review of one fixed implementation and test candidate across supported runtimes.
upstream: [GMGN methodology](../../../../GMGN.md), [dispatch and handoff](dispatch-and-handoff.md)
downstream: [Reviewer role](../../../../agents/reviewer.md)
status: approved
type: task
nature: normative
---

# Code-review contract

## 1. Fix the complete surface

Before Review, the Coder commits and freezes the complete implementation and test candidate
and returns a checkpoint to its Runner. Bind the Review surface to that candidate, original
baseline, Requirement, Design, applicable Contract, Card, declared write boundary, applicable
RED and GREEN checkpoints, and prepared deterministic-check evidence. Never review an
uncommitted mutable diff, only a correction commit, or a writer summary instead of the actual
candidate.

Coder self-checks and successful tests are supporting evidence. They are not review or
acceptance of the Coder's own candidate.

## 2. Select the reviewing path

During normal `run-task`, the Task's Runner reviews the fixed implementation and test
candidate. This is independent of the Coder that wrote it and does not create another role.
Create one independent Reviewer only when the Owner, applicable authority, current workflow
rule, or Commander brief explicitly requires it. Reviewer is used only for implementation and
test candidates; Critic covers normative document meaning.

When an independent Reviewer is required, select the available surface:

- Codex Desktop: `/review` when it can use the prepared fixed surface;
- Codex CLI: `codex review --commit <short-commit>` or `--base <branch>`; do not combine a
  scope flag with a custom prompt;
- Claude Code: an independent no-edit Reviewer that may run prepared commands; use
  `/code-review` only when the Owner authorized work on a GitHub PR; or
- a fresh no-edit Reviewer under the dispatch contract when the native surface is unavailable.

The Reviewer receives no writer or earlier-agent conversation history. A missing required
surface does not justify skipping explicitly required independent Review.

## 3. Review correctness and material harm

Apply every question below to the complete assigned surface:

1. Does it satisfy Requirement, Design, Contract, Card, and the declared write boundary?
2. Does it preserve necessary correctness, regression behavior, safety, data, security,
   accessibility, performance, recovery, compatibility, and resource protections?
3. Can each changed test or executable check reject an incorrect implementation, and are the
   applicable RED/GREEN checkpoints still valid?
4. Is it the simplest sufficient implementation without removable structure?
5. Would leaving an observed issue unresolved create concrete material harm?
6. Does an accepted effective fallback already contain that harm?
7. What is the smallest sufficient correction?

Report a finding only when the answers establish concrete material harm, no accepted effective
fallback, and a smallest sufficient correction. A valid Review may contain no findings. Omit
preference-only, speculative, low-impact, cleanup, refactoring, broader-coverage, or adequately
contained observations when they do not change acceptance or the next action.

## 4. Preserve deterministic evidence

The Runner runs or obtains every prepared targeted, negative, integration, project, and
applicable RED/GREEN replay command. An independent Reviewer may run the same prepared checks
when its brief assigns them. Use a disposable copy when a command may write; otherwise allow
only declared generated or cache paths. Preserve exact command, environment, exit code,
result, limitation, and side effect.

Recompare tracked content only after a command or event that could change it. Material drift
invalidates the Review. A skipped, timed-out, or unavailable required command is not a pass.
Add an exploratory check only for a concrete risk.

## 5. Adjudicate and repair once

The Runner adjudicates in-Task findings and sends an accepted minimum repair to the same
Coder while objective and write boundary remain unchanged. When an independent Reviewer was
required, its return informs that Runner ruling; the Reviewer does not decide its own finding.
The Coder commits a new complete checkpoint. The Runner inspects the exact repair delta and
reruns only affected checks without automatically creating another Reviewer.

An omitted in-scope implementation detail required by an accepted finding remains a repair
while accepted authority, objective, and write boundary remain unchanged. A fix that changes
approved behavior, interface or other upstream authority, Task objective, or write boundary
returns through the primary orchestrator to a Commander and the owning stage.

For integration, any rebase, conflict resolution, or Commander edit that changes candidate
content invalidates the affected Review and other candidate-bound evidence. Re-enter the
affected Runner gates before updating the shared baseline. If integration adds only a merge
commit and candidate content is unchanged, the original Review evidence remains valid. Do not
add a review mode, round field, risk table, or separate candidate-review document.
