---
locale: en
purpose: Check candidate identity, review, verification, state, and complexity before shared-baseline integration.
upstream: [GMGN](../../../../GMGN.md), [code review](code-review.md)
downstream: none
status: approved
type: design
nature: normative
assurance_policy: gmgn-assurance-v1
---

# Pre-merge checklist

1. **Candidate identity** — Does the review candidate contain the full
   `candidate_base_anchor..candidate_tip_anchor` diff or complete ordered commit chain, rather
   than only the last correction commit, and resolve from the expected workspace, task, and
   prepared write boundary?
2. **Scope** — Are interfaces, callers, migrations, documentation, and interacting tasks in
   the impact boundary?
3. **Single review barrier** — Was the one Critic/Reviewer round completed, including the
   Reviewer's prepared deterministic local checks, with every finding collected and each
   accepted blocker resolved without a second independent round?
4. **Final combination** — Is this either an isolated-lane candidate applied to the current
   reserved shared baseline or a frozen sole-writer candidate already based on that unchanged
   baseline, with the reviewed anchor and post-review fix delta recorded? If the application
   changed only the commit SHA, does relevant source, build input, and normative task content
   still match? Task status, descriptive Log content, and unrelated rows do not by themselves
   invalidate task-authority evidence. If the execution pointer changed, does it resolve to the
   same normative Card or preserve that Card's authority anchors, completion criterion, and TDD
   contract?
5. **Verification classification** — Is the final candidate classified from the
   [assurance policy](assurance-policy.json) as `not-required` or `required:<trigger>`? When
   required, is current Verifier evidence bound to the blocker-resolved final combination?
   Missing required evidence blocks integration.
6. **No downgrade** — Were tests removed, assertions weakened, errors swallowed, or real paths
   bypassed?
7. **Task/Card/Log split** — Is Task macro-only, Card the stable execution/TDD authority, and
   Log the current snapshot plus history?
8. **Failure isolation** — On conflict or failure, is the previous shared baseline still clean
   and is the failure recorded in Log without expanding Task? Did every Reviewer or Verifier
   leave tracked files unchanged on both pass and failure?
9. **Overdesign** — Can anything be deleted, replaced by standard/native behavior, or shrunk?

Run repository checks such as `git diff --check` and `git status --short` in the temporary
combination. Only the reviewed, blocker-resolved combination with affected post-fix machine
checks and any risk-triggered final-candidate evidence may advance the shared baseline. Refresh
Task/Card/Log and traceability in that candidate.
