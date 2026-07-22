---
locale: en
purpose: Check the object, environment, measurement, criteria, and runtime management before real execution or decisions based on it.
upstream: [GMGN §8](../../../../GMGN.md)
downstream: none
status: approved
type: design
nature: normative
---

# Preflight checklist

中文版本：[../zh-CN/preflight-checklist.md](../zh-CN/preflight-checklist.md)

For each question record `answer | evidence | owner | unresolved`; a checkbox is not enough.

1. **Question** — What single question does the run answer, and which outputs do not support that conclusion?
2. **Environment reality** — Do versions, configuration, data, permissions, dependencies, and hardware match the assumptions?
3. **Representation–reality alignment** — Can each “fixed/selected/deployed” claim point to its real location?
4. **Measurement fidelity** — Were tests, sampling, clocks, mocks, logs, and judgment scripts calibrated or checked with known samples?
5. **Complete criteria** — Can success, failure, timeout, missing data, and interruption be classified automatically?
6. **Unattended resilience** — How are hangs, silent failures, and resource exhaustion alerted, recovered, and preserved as evidence?
7. **Workspace and locks** — Does `git rev-parse --show-toplevel` equal the absolute
   `worktree_path` from the current dispatch; are its `workspace_mode` and `branch_ref`
   accurate; and are the lane's `write_set`, `conflict_domains`, and `runtime_locks`
   compatible with every active lane?
8. **Global writer claim** — Does the authority-project registry show one active
   `lane_key = project_scope_id + card_id`, with this exact `owner_thread_id`, `owner_run_id`,
   `ownership_epoch`, bound `coder_ref`, current `coder_epoch`, canonical `worktree_path`, and
   `repository_identity`;
   did separate atomic `claim → bind-coder → verify` succeed, and does the original
   `baseline_anchor` still resolve? A clear thread scan is only diagnostic.
   `owner-unreachable` is an unresolved blocker, never permission to reclaim. A queued Codex
   `clientThreadId` must resolve to actual `threadId + hostId` before claim or activation.

Do not start with an unresolved blocker. Every non-blocker has an owner and follow-up point.
