---
locale: en
purpose: Check candidate identity, review, verification, state, and complexity before shared-baseline integration.
upstream: [GMGN](../../../../GMGN.md), [code review](code-review.md)
downstream: none
status: approved
type: design
nature: normative
---

# Pre-merge checklist

中文版本：[../zh-CN/pre-merge-checklist.md](../zh-CN/pre-merge-checklist.md)

1. **Candidate identity** — Does the reviewed candidate resolve from the expected baseline,
   workspace, task, and prepared write boundary?
2. **Scope** — Are interfaces, callers, migrations, documentation, and interacting tasks in
   the impact boundary?
3. **Review barrier** — Were all active Critic/Reviewer findings collected and blockers cleared
   before any Verifier dispatch?
4. **Final combination** — Is this either an isolated-lane candidate applied to the current
   shared baseline or a frozen sole-writer candidate already based on that unchanged baseline?
5. **Verification boundary** — Is one fresh Verifier checking the final combination when
   executable evidence is required? If another boundary exists, is its risk reason recorded?
6. **No downgrade** — Were tests removed, assertions weakened, errors swallowed, or real paths
   bypassed?
7. **Task/Card/Log split** — Is Task macro-only, Card the stable execution/TDD authority, and
   Log the current snapshot plus history?
8. **Failure isolation** — On conflict or failure, is the previous shared baseline still clean
   and is the failure recorded in Log without expanding Task?
9. **Overdesign** — Can anything be deleted, replaced by standard/native behavior, or shrunk?

Run repository checks such as `git diff --check` and `git status --short` in the temporary
combination. Only the review-cleared and, when required, independently verified combination
may advance the shared baseline. Refresh Task/Card/Log and traceability in that candidate.
