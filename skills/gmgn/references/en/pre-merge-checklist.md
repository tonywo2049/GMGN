---
locale: en
purpose: Check integration, verification strength, claim truth, tool degradation, and complexity before parallel output enters a shared baseline.
upstream: [GMGN §7](../../../../GMGN.md), [code review](code-review.md)
downstream: none
status: approved
type: design
nature: normative
---

# Pre-merge checklist

中文版本：[../zh-CN/pre-merge-checklist.md](../zh-CN/pre-merge-checklist.md)

1. **Workspace provenance** — Do `project_scope_id`, `lane_key`, `run_id`, `card_id`,
   `worktree_path`, `branch_ref`, `baseline_anchor`, and `candidate_anchor` identify the exact
   reviewed lane, and did its root assertion pass at start and return; is `candidate_anchor` a
   resolvable local commit containing only the card `write_set`; and do `repository_identity`
   and the still-resolvable original baseline match the claim?
2. **Ownership freshness** — Does registry verify still match `owner_thread_id`, `owner_run_id`,
   `ownership_epoch`, the exact bound `coder_ref`, and canonical path; did the worker stop at
   `candidate-awaiting-anchor`; was the candidate recorded by atomic `anchor` before an exact
   `review-authorized`; and were another owner, stale epoch, missing/wrong Coder, or replaced
   repository rejected before review and integration?
3. **Two-phase baseline safety** — Was the accepted commit first applied to an isolated
   temporary combination based on the current clean `shared_baseline_anchor`, without advancing
   it? A baseline advance alone is not `rebase-required`; was that state used only after an
   unclean application, invalid dependency/specification meaning, or needed Coder judgment?
4. **Integration completeness** — Is the impact larger than the file diff; are interfaces, callers, migrations, docs, and interacting lanes covered?
5. **No verification downgrade** — Were tests removed, assertions weakened, errors swallowed, or real paths bypassed?
6. **Claim–disk alignment** — Do completion state, files, test output, and the Git diff agree, with branch acceptance still distinct from `closed`?
7. **Operation–shape fit** — How do commands degrade for paths, empty/large sets, duplicate names, and failure codes?
8. **Name, number, and ownership provenance** — Do mechanism names, key numbers, semantic ownership, `conflict_domains`, and `runtime_locks` point to their authorities?
9. **Overdesign scan** — Check `delete | stdlib | native | empty abstraction | shrink` separately.

The single Integrator runs mechanical checks including `git diff --check` and
`git status --short` in the temporary combination. The same lane Verifier receives that
current dispatch's `workspace_mode`, `worktree_path`, and `branch_ref` and runs affected
interaction and project gates there. On conflict/failure, abort or discard the temporary
candidate and prove the original shared workspace clean. Only a verified candidate plus
ledger refresh may atomically advance `shared_baseline_anchor` and become `node-complete` /
`closed`; an unverified combination never becomes the shared baseline.
