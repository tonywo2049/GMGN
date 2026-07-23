---
locale: en
purpose: Check the question, environment, criteria, workspace, and evidence before real execution.
upstream: [GMGN](../../../../GMGN.md)
downstream: none
status: approved
type: design
nature: normative
---

# Preflight checklist

Check only facts that can block this run. Do not create evidence for the checklist itself or
repeat a check while its relevant state is unchanged.

1. **Scope** — Is the Card outcome and allowed write scope clear enough to begin?
2. **Existing work** — Will current user changes be preserved?
3. **Writer boundary** — Is there one writer per workspace? Use a separate worktree, baseline,
   and expected HEAD only for concurrent writing or candidate handoff.

Check environment, measurement, permissions, shared resources, and failure classification only
when the Card or prepared command actually depends on them. Record command results and material
limitations in the existing Card Log after execution. Do not start with a real unresolved
blocker.
