---
locale: en
purpose: Check scope, evidence, state, risk, and acceptance before Milestone closure.
upstream: [GMGN](../../../../GMGN.md)
downstream: none
status: approved
type: design
nature: normative
---

# Pre-close checklist

1. **Boundary** — Are the target Milestone and its Goal/Requirement/Design/applicable
   Contract/Task anchors fixed, without a cross-Milestone reference expanding scope?
2. **Acceptance picture** — Does every ROADMAP acceptance scenario trace through Goal slices
   and ACs to evidence for the real end-to-end or integration path and relevant failure or
   recovery outcome?
3. **Criteria** — Is every in-scope AC completed, or semantically removed/reassigned at a new
   authority anchor?
4. **Evidence** — Does every retained criterion have a replayable command or real execution
   path, including relevant negative behavior?
5. **Independent challenge** — Are required Critic/Reviewer blockers clear, are Reviewer
   execution results or post-fix machine checks current, and is any risk-triggered
   final-candidate verification current?
6. **State** — Do Task macro status, Card contract, closed Log snapshot/latest event,
   traceability, ROADMAP, and the closing commit agree?
7. **Contract freeze** — Does every retained Contract ID match provider and consumer
   implementations plus conformance/integration evidence, with no semantic mismatch being
   hidden by a closure edit?
8. **Integration** — Are target tasks closed on one shared baseline with no owned integration
   entry or lock left active?
9. **Findings and risk** — Are material structural findings classified as target blockers or
   proved pre-existing external debt, and are remaining risks stated without invention?
10. **Acceptance** — Is owner acceptance bound to the exact closing commit that marks the
    implementation-matching Contract `closed`?

Any unresolved target blocker or unclassified material finding blocks closure. A separate
Handoff is required only when a receiving operator needs information not already owned by an
existing authority.
