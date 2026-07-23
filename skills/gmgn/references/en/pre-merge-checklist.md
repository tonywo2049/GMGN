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

1. **Candidate identity** — Is the content being integrated exactly the reviewed content? Use
   a frozen diff/content hash for a sole writer and the complete base-to-tip diff or ordered
   commit chain for an isolated handoff.
2. **Scope** — Are interfaces, callers, migrations, documentation, and interacting tasks in
   the impact boundary?
3. **Single review barrier** — Was the one Critic/Reviewer round completed, including the
   Reviewer's prepared deterministic local checks, with every finding collected and each
   accepted blocker resolved without a second independent round?
4. **Final content** — Are accepted post-review fixes recorded and affected checks current?
   A changed commit SHA alone does not invalidate evidence when relevant source, build inputs,
   and normative task content still match.
5. **Verification classification** — Is the final candidate classified from the
   [assurance policy](assurance-policy.json) as `not-required` or `required:<trigger>`? When
   required, is current Verifier evidence bound to the blocker-resolved final combination?
   Missing required evidence blocks integration.
6. **No downgrade** — Were tests removed, assertions weakened, errors swallowed, or real paths
   bypassed?
7. **Task/Card/Log split** — Is Task macro-only, Card the stable execution/TDD authority, and
   Log the current snapshot plus history?
8. **Failure isolation** — On conflict or failure, is the previous shared baseline still clean
   and is the failure recorded in Log without expanding Task?
9. **Overdesign** — Can anything be deleted, replaced by standard/native behavior, or shrunk?

Run repository checks required by the project. Only reviewed, blocker-resolved content with
affected post-fix machine checks and any risk-triggered final-candidate evidence may advance
the shared baseline. Refresh Task/Card/Log and traceability in that candidate.
