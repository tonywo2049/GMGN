---
locale: en
purpose: Unify incremental code-review scope, execution evidence, and finding format across Codex, Claude Code, and no-edit reviewers.
upstream: [dispatch and handoff](dispatch-and-handoff.md)
downstream: [pre-merge checklist](pre-merge-checklist.md)
status: approved
type: task
nature: normative
---

# Code-review contract: native entry and shared checks

## 1. Select the surface

- Codex Desktop: `/review`.
- Codex CLI: `codex review --uncommitted`, `--commit <sha>`, or `--base <branch>`;
  do not combine a scope flag with a custom prompt.
- Claude Code: an independent no-edit reviewer that may run prepared commands; use
  `/code-review` only when the user
  has authorized work on a GitHub PR.
- If the native surface is unavailable, dispatch an independent no-edit reviewer with the
  execution permissions required by its prepared plan; do not skip review.

## 2. Review surface

Before review, freeze the simplest exact identity for the content named by the brief: a
captured diff/content hash for a sole writer, or the complete base-to-tip diff or ordered
commit chain for an isolated handoff. Confirm the workspace only when candidate handoff or
concurrent writing makes it material. Never review whichever mutable diff happens to be open
or only the last correction commit.

1. Does the task-card diff satisfy its spec anchor and prepared write boundary?
2. Is there concrete correctness, regression, safety, data, accessibility, performance, or
   acceptance harm if an observed issue remains?
3. Does an accepted effective fallback already contain that harm, and what is the smallest
   sufficient correction?
4. Can each changed test fail when the implementation is wrong?

A valid review may return no findings. Omit preference-only, speculative, low-impact, cleanup,
refactoring, broader-coverage, or adequately contained observations when they do not change
acceptance or the next action. Run prepared checks; add exploratory checks only for a concrete
risk. Do not propose a broader redesign when a smaller correction or effective fallback is
sufficient.

When the candidate workspace has a usable `.codegraph/`, query CodeGraph first for changed
symbols, their callers, and sibling paths, and treat returned source as already read. Findings
must cite that source or the exact Git diff; tests and real execution remain the behavioral
evidence. Read targeted files directly when the index is stale, unsupported, changed after the
query, or insufficient.

Run the prepared deterministic local checks that fit the review environment. Do not
intentionally edit workspace files. Prefer a disposable copy when a command may write;
otherwise allow only declared generated/cache paths. Recompare the frozen content identity
only after a command or event that could change it. Any material content drift invalidates the
review. Report exact commands, environment, exit codes, limitations, and side effects together
with material findings; a skipped or unavailable required command is not a pass.

Apply the complete self-checked isolated-lane candidate before review; never apply only its
last correction commit. A sole-writer candidate needs no temporary copy. Resolve an unclean
application or judgment-required conflict with a fresh Coder, then freeze the final review
content. A changed commit SHA alone does not invalidate equivalent source, build inputs, and
normative task content. Each task execution uses `review_policy: single-pass` and has at most
one Reviewer round.
After that round, the primary orchestrator adjudicates once, batches accepted fixes, checks
each resolution against its finding, and runs affected machine checks. Do not dispatch another
Reviewer to recheck those fixes. A fix that changes dependency/specification meaning or
expands behavior beyond the accepted findings becomes a separately scoped change. The primary
orchestrator reruns affected machine checks after accepted fixes. A separate Verifier is not a
default second stage; use it only for a recorded `required:<trigger>` classification on the
blocker-resolved final candidate. The final anchor records the reviewed anchor, findings and
rulings, exact fix delta, post-fix checks, verification classification, and any
trigger-specific evidence.
