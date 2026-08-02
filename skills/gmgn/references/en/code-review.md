---
locale: en
purpose: Define direct review of one fixed implementation/test candidate by the active Adjudicator across supported runtimes.
upstream: [GMGN methodology](../../../../GMGN.md), [dispatch and handoff](dispatch-and-handoff.md)
downstream: [Adjudicator role](../../../../agents/adjudicator.md)
status: approved
type: task
nature: normative
---

# Code-review contract

## 1. Fix the complete surface

The same active Adjudicator that owns the execution case directly reviews the complete fixed
implementation and test candidate. Before review, the Coder commits and freezes it, returns a
candidate checkpoint, and waits. Bind the surface to the candidate, Requirement, Design,
applicable Contract, Card, declared write boundary, original baseline, applicable RED and
GREEN checkpoints, and prepared deterministic-check evidence. Never review an uncommitted
mutable diff, only a correction commit, or a writer's summary instead of the candidate.

Coder self-checks and successful tests are supporting evidence. They are not review or
acceptance of the Coder's own candidate.

## 2. Run deterministic commands without semantic judgment

The primary orchestrator verifies candidate identity and runs the prepared targeted, negative,
integration, project, and applicable RED/GREEN replay commands. Use a disposable copy when a
command may write; otherwise allow only declared generated paths. Preserve and send
the exact command, environment, exit code, result, limitation, and side effect to the active
Adjudicator. Recompare tracked content only after a command or event that could change it.
Material drift invalidates the evidence. A skipped, timed-out, or unavailable required command
is not a pass.

These results are deterministic evidence only. The primary orchestrator does not interpret
them, make findings, review code or tests, or accept the candidate.

## 3. Direct semantic review

The active Adjudicator reads the fixed candidate and exact evidence under this contract and
the owning `run-task` Skill. It checks:

1. correctness and regression behavior against Requirement, Design, Contract, Card, and the
   declared write boundary;
2. necessary safety, data, security, accessibility, performance, recovery, and compatibility
   protections;
3. whether each changed test or executable check can identify a wrong implementation and the
   applicable RED/GREEN evidence remains valid;
4. Contract and acceptance consistency; and
5. whether the code is the simplest sufficient implementation without removable structure.

A finding exists only when leaving the issue unresolved causes concrete material harm, no
accepted effective fallback contains that harm, and the smallest sufficient correction can be
stated. Otherwise accept. Omit preference-only, speculative, low-impact, cleanup, refactoring,
broader-coverage, or adequately contained observations when they do not change acceptance or
the next action.

## 4. Repair within the same case

Return an accepted finding to the same Coder while objective and write boundary remain
unchanged. The Coder applies the minimum repair and commits a new complete candidate checkpoint.
The primary orchestrator reruns only checks affected by the finding or repair and forwards the
exact evidence. The same Adjudicator then inspects the exact fix delta and affected surfaces;
it does not dispatch another assessment agent or recheck unchanged work.

A repair that changes approved behavior, interface authority, objective, or write boundary
returns to the owning stage or requires a new dispatch. Do not add a review mode, round field,
risk table, or separate candidate-review data structure.
