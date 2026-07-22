---
locale: en
purpose: Unify incremental code-review scope, execution evidence, and finding format across Codex, Claude Code, and no-edit reviewers.
upstream: [dispatch and handoff](dispatch-and-handoff.md)
downstream: [pre-merge checklist](pre-merge-checklist.md)
status: approved
type: task
nature: normative
assurance_policy: gmgn-assurance-v1
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

Before review, record `git rev-parse --show-toplevel`, HEAD, the frozen diff/content hash, and
tracked status; require the resolved path to equal the absolute workspace in the dispatch.
Review the exact candidate named by the brief: normally `baseline_anchor..candidate_anchor`, or
a captured diff with a recorded content hash for a sole-writer current workspace. Freeze that
workspace during review; never review whichever mutable diff happens to be open.

1. Does the task-card diff satisfy its spec anchor, prepared write boundary, and any declared
   shared-resource constraint?
2. Which outputs, error paths, no-baseline branches, and sibling call paths lack assertions?
3. Can each changed test fail when the implementation is wrong? Mutate only in isolation.
4. Did the change weaken boundary validation, security, data protection, performance, or accessibility?
5. Complexity labels: `delete | stdlib | native | empty abstraction | shrink`.

When `.codegraph/` exists, independently query CodeGraph in the candidate worktree for changed
symbols, their callers, and sibling paths. If the index cannot prove candidate-commit identity,
use it only to navigate. Findings must cite the exact Git diff or checked-out source; tests and
real execution remain the behavioral evidence. Read targeted files directly whenever the task
brief or graph is insufficient.

Run the prepared deterministic local targeted, negative, integration, and project checks that
fit the review environment. Do not intentionally edit any workspace file. Prefer a disposable
copy when a command may write; otherwise allow only declared generated/cache paths. After
execution, recheck repository root, HEAD, frozen diff/content hash, and tracked status. Any
tracked change or anchor/hash drift invalidates the review. Report exact commands, environment,
exit codes, limitations, and side effects together with findings; a skipped or unavailable
required command is not a pass. Each finding contains
`location · evidence · impact · normative fix · priority`. End with `git status --short` and
disclose review-generated caches or other side effects.

Apply the self-checked isolated-lane candidate to a temporary combination before review. A
frozen sole-writer candidate already based on the unchanged shared baseline is the
combination. Resolve an unclean application or judgment-required conflict with a fresh Coder,
then freeze the final review candidate. Reserve its shared baseline and integration position
until integration or abandonment, so the candidate cannot become stale after review. Each task
execution uses `review_policy: single-pass` and has at most one Reviewer round.
After that round, the primary orchestrator adjudicates once, batches accepted fixes, checks
each resolution against its finding, and runs affected machine checks. Do not dispatch another
Reviewer to recheck those fixes. A fix that changes dependency/specification meaning or
expands behavior beyond the accepted findings becomes a separately scoped change. The primary
orchestrator reruns affected machine checks after accepted fixes. A separate Verifier is not a
default second stage; classify it from the [assurance policy](assurance-policy.json) and use it
only for `required:<trigger>` on the blocker-resolved final candidate. The final anchor records
the reviewed anchor, findings and rulings, exact fix delta, post-fix checks, verification
classification, and any policy-triggered evidence.
