---
locale: en
purpose: Unify incremental code-review scope and finding format across Codex, Claude Code, and read-only reviewers.
upstream: [dispatch and handoff](dispatch-and-handoff.md)
downstream: [pre-merge checklist](pre-merge-checklist.md)
status: approved
type: task
nature: normative
---

# Code-review contract: native entry and shared checks

中文版本：[../zh-CN/code-review.md](../zh-CN/code-review.md)

## 1. Select the surface

- Codex Desktop: `/review`.
- Codex CLI: `codex review --uncommitted`, `--commit <sha>`, or `--base <branch>`;
  do not combine a scope flag with a custom prompt.
- Claude Code: an independent read-only reviewer; use `/code-review` only when the user
  has authorized work on a GitHub PR.
- If the native surface is unavailable, dispatch a read-only reviewer; do not skip review.

## 2. Review surface

Before review and before return, run `git rev-parse --show-toplevel`; require the resolved
path to equal the absolute `worktree_path` in the current dispatch. Review the immutable local
commit SHA in
`baseline_anchor..candidate_anchor` range, not whichever uncommitted diff happens to be open.

1. Does the task-card diff satisfy its spec anchor, declared `write_set`,
   `conflict_domains`, and `runtime_locks`?
2. Which outputs, error paths, no-baseline branches, and sibling call paths lack assertions?
3. Can each changed test fail when the implementation is wrong? Mutate only in isolation.
4. Did the change weaken boundary validation, security, data protection, performance, or accessibility?
5. Complexity labels: `delete | stdlib | native | empty abstraction | shrink`.

When `.codegraph/` exists, independently query CodeGraph in the candidate worktree for changed
symbols, their callers, and sibling paths. If the index cannot prove candidate-commit identity,
use it only to navigate. Findings must cite the exact Git diff or checked-out source; tests and
real execution remain the behavioral evidence. Read targeted files directly whenever the task
brief or graph is insufficient.

Report findings and do not modify the reviewed worktree. Each finding contains
`location · evidence · impact · normative fix · priority`. End with `git status --short`
and disclose review-generated caches or side effects.

An advanced `shared_baseline_anchor` first receives a mechanical application attempt in an
isolated temporary combination; it does not by itself force review or `rebase-required`. If
application is not clean, dependency/specification meaning is invalid, or Coder judgment
changes the lane, every affected diff returns to the same Reviewer. A targeted recheck is
valid only for the original accepted blocker surface; a changed integration diff receives
review of all changed hunks. Post-integration verification remains a Verifier responsibility.
