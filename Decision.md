---
locale: en
purpose: Record the current project rulings that govern execution telemetry collection.
upstream: [GMGN](GMGN.md)
downstream: none
status: draft
type: decision
nature: normative
---

# Decisions

- **D-001** Correlated execution telemetry
  - Applies to: Execution telemetry correlation and evidence
  - Decision: Maintain a stable correlation chain from session to turn to agent session/dispatch to tool call to `exec_command` to the root shell to observed process descendants. `exec_command` runs through a GMGN wrapper that propagates `session_id`, `turn_id`, `agent_session_id`, `dispatch_id`, and `tool_call_id`. Observed execution events are primary; static command parsing does not establish actual process execution, and unlinked records remain unlinked.

- **D-002** Shell telemetry privacy boundary
  - Applies to: Collection and storage of shell execution telemetry
  - Decision: Full shell command text and process `argv` may be stored only after credential redaction. Environment variable values are never collected. `stdout` and `stderr` bodies are not stored; only byte count, line count, truncation state, and exit-related metadata may be retained. Unsafe or unclassifiable fields are dropped.

- **D-003** Process observation granularity
  - Applies to: Shell and operating-system process observation
  - Decision: Subject to D-002, retain raw shell text and actually observed operating-system process nodes, including PID, PPID, executable, redacted `argv`, start, end, duration, exit code or signal, parent-child edges, and coverage. Shell builtins, functions, and control flow do not receive separate events. Inferred possible commands are not observed processes and must not be mixed with them.

- **D-004** Platform fidelity
  - Applies to: Platform observation and aggregation
  - Decision: On Linux, the wrapper targets reliable descendant `fork`, `clone`, `exec`, and `exit` tracing. On macOS, observation is unprivileged and best-effort, installs no Endpoint Security system extension, and may miss short-lived descendants. Every `exec_command` run exposes its coverage quality and known limitations without claiming completeness beyond what the observer can establish; possible omissions that the observer cannot establish remain unknown. Aggregation must distinguish Linux reliable-tracing records from macOS best-effort records and must not label either platform's records complete. Windows is out of scope.

- **D-005** Execution semantics
  - Applies to: Command execution and telemetry operation
  - Decision: Telemetry failure, observer failure, collector outage, or quota exhaustion must neither prevent command execution nor alter `stdin`, `stdout`, `stderr`, signals, working directory, child behavior, exit code, or error propagation. Telemetry errors remain separate and coverage-visible. Performance overhead is observable.
