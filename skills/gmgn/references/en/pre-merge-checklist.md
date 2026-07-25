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

1. **Candidate identity** — Was the complete candidate committed before review and identified
   by the shortest unambiguous commit reference? For an isolated handoff, is the complete
   base-to-candidate commit range present? A full-length commit object ID, diff/content hash,
   archive checksum, or artifact checksum is not a workflow anchor.
2. **Scope** — Are applicable Contract IDs, interfaces, callers, migrations, documentation,
   and interacting tasks in the impact boundary?
3. **Single review barrier** — Was the one Critic/Reviewer round completed, including the
   Reviewer's prepared deterministic local checks, with every finding collected and each
   accepted blocker resolved without a second independent round?
4. **Final content** — Are accepted post-review fixes recorded and affected checks current?
   Does Git confirm that the integrated content matches the reviewed commit? A different
   integration commit is acceptable only when the reviewed source, build inputs, and
   normative task content are unchanged.
5. **Verification classification** — Is the final candidate classified as `not-required` or
   `required:<trigger>`? When required, is current Verifier evidence bound to the
   blocker-resolved final combination? Missing required evidence blocks integration.
6. **No downgrade** — Were tests removed, assertions weakened, errors swallowed, or real paths
   bypassed?
7. **Authority split** — Is Task macro-only, Card the stable execution/TDD authority, the
   implementation conformant with the current approved Design Bundle/Contract anchor, and Log
   limited to the current snapshot, material decisions, and final evidence?
8. **Failure isolation** — On conflict or failure, is the previous shared baseline still clean
   and is the failure recorded in Log without expanding Task?
9. **Overdesign** — Did R-D-T criticism apply the deletion test? When the candidate contains
   implementation or test-code changes, did the Reviewer load `ponytail:ponytail-review`? Can
   anything still be deleted, replaced by standard/native behavior, or shrunk without losing a
   current accepted outcome or required safeguard?

Run repository checks required by the project. Only reviewed, blocker-resolved content with
affected post-fix machine checks and any risk-triggered final-candidate evidence may advance
the shared baseline. Refresh Task/Card/Log and traceability in that candidate.
