---
locale: en
purpose: Check real evidence, trust surfaces, orthogonal review, residual risk, invariants, and state consistency before irreversible closure.
upstream: [GMGN §3](../../../../GMGN.md)
downstream: none
status: approved
type: design
nature: normative
---

# Pre-close checklist

中文版本：[../zh-CN/pre-close-checklist.md](../zh-CN/pre-close-checklist.md)

1. **Target boundary** — Are `target_milestone_id`, its Goal/Requirement/Design/Task anchors,
   owned cards, closing anchor, and target-scoped finding set recorded? Did any cross-Milestone
   reference improperly expand execution or closure scope?
2. **Reality coverage** — Does every target-Milestone closure criterion have a real test,
   startup, or E2E path and exact command?
3. **Trust surfaces closed** — Was each target Design acceptance point's source, validation,
   failure behavior, owner, and negative evidence replayed?
4. **Orthogonal challenge** — Did at least one critic, reviewer, or external source use a frame independent of the author?
5. **Residual risk** — Which unresolved risk could still change closure; what is its impact,
   evidence strength, and cheapest next falsification step? If none is known, is that stated
   without inventing one?
6. **Invariant family** — Does each target-level invariant have positive and negative evidence, not only a happy path?
7. **Text and state consistency** — Were the target Task, matrix, ROADMAP row, Decision,
   Handoff, and version anchors refreshed together?
8. **Integration convergence** — Are the target Milestone's integration entries empty, are
   there no active, `rebase-required`, or `integration-conflict` lanes or held locks it owns,
   and are all its cards closed on one `shared_baseline_anchor`?
9. **Downstream debt** — Is every downstream-only question a non-blocking TODO/Handoff with
   receiving Milestone/owner, trigger, possible impact, and default assumption where useful?
   Was any still-in-scope AC mislabeled `deferred` instead of being completed or removed/
   reassigned through a controlled semantic change at a new authority anchor?
10. **Structural measurement boundary** — Is every DocStar finding recorded with evidence and
    exactly one GMGN classification: `target-scoped | candidate-introduced-or-polluted |
    external-pre-existing`? Was `external-pre-existing` used only when both external scope and
    a pre-candidate anchor were proved? If not, is scope classification incomplete and closure
    blocked rather than the finding recorded as debt? DocStar `classification_complete` alone
    does not answer these questions.

Any unresolved target blocker, `target-scoped` finding, `candidate-introduced-or-polluted`
finding, or incomplete scope classification blocks closure. A proved `external-pre-existing`
finding does not.
Only after owner acceptance may the target state become `closed`.
