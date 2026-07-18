---
locale: en
purpose: Check real evidence, trust surfaces, orthogonal review, assumptions, invariants, and state consistency before irreversible closure.
upstream: [GMGN §3](../../../../GMGN.md)
downstream: none
status: approved
type: design
nature: normative
---

# Pre-close checklist

中文版本：[../zh-CN/pre-close-checklist.md](../zh-CN/pre-close-checklist.md)

1. **Reality coverage** — Does every closure criterion have a real test, startup, or E2E path and exact command?
2. **Trust surfaces closed** — Was each Design acceptance point's source, validation, failure behavior, owner, and negative evidence replayed?
3. **Orthogonal challenge** — Did at least one critic, reviewer, or external source use a frame independent of the author?
4. **Weakest assumption** — Which assumption most threatens the conclusion; was its counterexample tested or recorded as debt?
5. **Invariant family** — Does each top-level invariant have positive and negative evidence, not only a happy path?
6. **Text and state consistency** — Were Task, matrix, ROADMAP, Decision, Handoff, and version anchors refreshed together?

Any blocker, non-zero gate finding, or unclassified normative document blocks closure.
Only after owner acceptance may the state become `closed`.
