---
locale: en
purpose: Define observable behavior and decidable acceptance criteria for M1 correlated and auditable telemetry.
upstream: [Goal](Goal.md)
downstream: none
status: draft
type: requirement
nature: normative
---

# M1 Requirements

## R1 — Agent identity and elapsed time

**Authority:** [Goal Close outcome 1](Goal.md#close-outcomes); [D-001](Decision.md).

For every agent session actually observed by a source, telemetry must distinguish the
`agent_session_id`, role and agent path, source-established parent relationship, start time,
end time when the session has ended, wall-clock elapsed duration, and current or terminal
status. A session without a source-proven parent remains unlinked or explicitly unknown.
Relationships among session, turn, agent session, dispatch, tool call, `exec_command` run, and
process exist only where the source establishes them; missing relationships remain unlinked or
unknown and are not inferred.

- **R1-AC1:** Given a source observes an active agent session and an ended agent session, when
  their records and report are inspected, each session is individually identifiable by
  `agent_session_id` and shows its source-provided role and path, start time, wall-clock elapsed
  duration, and current or terminal status. The ended session also shows its observed end time
  and an elapsed duration equal to end minus start; the active session has no fabricated end
  time and its elapsed duration is measured through the report observation time.
- **R1-AC2:** Given the source proves one parent relationship and observes another session
  without a provable parent, and proves only some links in a session-to-process correlation
  chain, inspection preserves the proven parent and correlation links while marking the other
  parent and links unlinked or unknown; it contains no inferred parent or correlation link.

## R2 — Per-agent token and cache accounting

**Authority:** [Goal Close outcomes 1 and 3](Goal.md#close-outcomes); [D-001](Decision.md).

For each observed agent, telemetry must present source-provided input, output, reasoning, and
total tokens separately from cache-read and cache-write input tokens. It must preserve whether
token observations are cumulative snapshots or deltas so that cumulative snapshots are not
summed repeatedly. A field the source does not provide is unavailable or unknown rather than
zero, while a source-reported zero remains zero. Aggregation for root agents, descendants,
roles, or dispatches counts each source observation once and retains its source and quality.

- **R2-AC1:** Given source observations containing nonzero token values, a true zero, and an
  omitted token or cache field, inspection of the affected agent shows the provided input,
  output, reasoning, total, cache-read input, and cache-write input values in their separate
  categories, preserves the true zero, and labels the omitted field unavailable or unknown
  rather than reporting zero.
- **R2-AC2:** Given a source emits multiple cumulative snapshots for one counter and an explicit
  delta for another counter, inspection identifies the snapshot and delta semantics and the
  resulting totals include each source-defined change once; the cumulative snapshot values are
  not added to one another as independent usage.
- **R2-AC3:** Given one source observation is reachable through root, descendant, role, and
  dispatch groupings, inspection of each applicable aggregate counts that observation once and
  retains a trace to its source and reported quality.

## R3 — Observed agent transfers

**Authority:** [Goal Close outcomes 1 and 3](Goal.md#close-outcomes); [D-001](Decision.md) and
[D-006](Decision.md).

Every agent-to-agent transfer actually observed by the platform must expose its sender,
recipient, observed transfer behavior, ordering or timing, delivery or result status, and any
available payload. Observed spawn or dispatch, send or follow-up, and result or completion
behaviors remain distinguishable without treating unobserved messages as transfers. Payload
text is credential-redacted. If a body cannot be safely classified or redacted, its safe
metadata remains available and the body is explicitly unavailable or redacted rather than
empty. Hidden reasoning and context not exposed by the platform are not collected.

- **R3-AC1:** Given the platform reports transfers representing spawn or dispatch, send or
  follow-up, and result or completion behavior, inspection shows a separate observed transfer
  for each with its sender, recipient, distinguishable behavior, ordering or timing,
  delivery or result status, and safely available payload.
- **R3-AC2:** Given observed transfers with a safe payload, a credential-bearing payload, and a
  body that cannot be safely classified or redacted, inspection retains safe transfer metadata,
  preserves the safe payload, redacts the credential, and marks the unsafe body unavailable or
  redacted without representing it as an empty message.
- **R3-AC3:** Given agent lifecycle activity or static prompts for which the platform exposes no
  transfer, plus hidden reasoning or context not exposed as payload, inspection contains no
  inferred transfer and no hidden reasoning or unexposed context.

## R4 — Tool-use accounting

**Authority:** [Goal Close outcomes 1 and 3](Goal.md#close-outcomes); [D-001](Decision.md).

Every tool call actually observed by a source must be attributable to its source-established
agent, dispatch, and turn and must retain a stable `tool_call_id` when the source supplies one.
Its observable accounting includes tool identity, start and end times, duration, and completed,
error, or cancelled state. Source-provided request or result size, line count, truncation, exit,
and error metadata is retained; missing metadata remains unknown or unavailable. Acceptance of
a general tool call does not require retention of arbitrary request or result bodies. Shell and
process observations for `exec_command` are governed by R5.

- **R4-AC1:** Given source-observed tool calls that complete, fail, and are cancelled, inspection
  shows each call's source-established agent, dispatch, and turn relationship, stable
  `tool_call_id` when supplied, tool identity, start and end times, duration, and matching
  terminal state without inventing a missing relationship or identifier.
- **R4-AC2:** Given a non-`exec_command` tool observation for which the source provides some
  request or result size, line, truncation, exit, and error metadata but omits other fields,
  inspection preserves the provided metadata and marks omitted metadata unknown or unavailable;
  pass or fail does not depend on retaining arbitrary request or result bodies.

## R5 — `exec_command` shell and process observation

**Authority:** [Goal Close outcomes 1, 2, and 3](Goal.md#close-outcomes);
[D-001](Decision.md), [D-002](Decision.md), [D-003](Decision.md), [D-004](Decision.md), and
[D-005](Decision.md).

Every observed `exec_command` run must retain source-established correlation, credential-redacted
raw shell text, its root shell, and actually observed operating-system process nodes and parent
edges. A process observation covers PID, PPID, executable, credential-redacted `argv`, start,
end, duration, exit code or signal, and observation coverage. Shell builtins and control flow
are not represented as separate processes, and inferred possible commands are not mixed into
the observed process tree. Environment variable values are never collected. `stdout` and
`stderr` bodies are not retained; only their byte counts, line counts, truncation state, and
exit-related metadata are retained. Unsafe fields are dropped.

On Linux, descendant `fork`, `clone`, `exec`, and `exit` observation targets reliable tracing;
known observer loss or errors remain visible, and absence of a reported loss does not justify a
claim of completeness. On macOS, observation is unprivileged best-effort, uses no Endpoint
Security helper, and may leave possible short-lived descendants unknown. Every run exposes its
platform, observer mode, coverage quality, and known limitations, and neither platform is
reported as complete. Telemetry, observer, collector, or quota failure remains separate from
command execution and does not change command semantics. Telemetry overhead is observable
without a numeric acceptance threshold.

- **R5-AC1:** Given an `exec_command` run whose source observes a root shell, child processes,
  parent edges, shell builtins or control flow, and possible commands that were not observed as
  processes, inspection shows the source-established correlation, redacted raw shell text, root
  shell, and each observed process with PID, PPID, executable, redacted `argv`, start, end,
  duration, exit code or signal, and coverage. It shows the observed parent edges and contains
  no separate process for a builtin or control-flow construct and no inferred process.
- **R5-AC2:** Given a run containing credentials in shell text or process `argv`, environment
  variable values, `stdout` and `stderr` output, and a field that cannot be handled safely,
  inspection shows credential-redacted shell text and `argv`, no environment values or output
  bodies, the observed byte counts, line counts, truncation state, and exit metadata, and no
  unsafe field.
- **R5-AC3:** Given a controlled Linux run with descendant `fork`, `clone`, `exec`, and `exit`
  activity and a separately reported observer loss or error, inspection represents the
  source-observed descendant activity, identifies Linux reliable descendant tracing, exposes
  the loss or error and resulting coverage limitation, and does not label the run complete.
- **R5-AC4:** Given a macOS run that includes an observed descendant and a possible unobserved
  short-lived descendant, inspection identifies macOS, unprivileged best-effort observation,
  its coverage quality and known limits, records only the observed descendant, leaves the
  possible omission unknown, and does not label the run complete or require an Endpoint
  Security helper.
- **R5-AC5:** Given the same deterministic command is exercised with healthy telemetry and with
  each induced telemetry, observer, collector, or quota failure, inspection shows unchanged
  command `stdin`, `stdout`, `stderr`, signals, working directory, child behavior, exit code,
  and error propagation; each telemetry failure is separately visible, and a telemetry-overhead
  observation remains available without applying a pass threshold.

## R6 — Reporting and data quality

**Authority:** [Goal Close outcome 3](Goal.md#close-outcomes); [D-001](Decision.md),
[D-002](Decision.md), [D-004](Decision.md), [D-005](Decision.md), and [D-006](Decision.md).

Consumers must be able to aggregate by agent, role or path, dispatch, tool, and `exec_command`
run and trace results to source records while inspecting token, cache, time, transfer, tool, and
process observations. Totals count a source observation once. Field and record source,
availability or quality, and observation limitations must distinguish observed values, known
missing data, and unknown or unavailable data; fallback or inference does not raise a fidelity
label. Collector health exposes ingestion and observer errors, dropped and rejected records,
quota exhaustion or collection stoppage, retained-data boundaries, and telemetry overhead. If
telemetry fails, already available reporting remains readable and does not appear fresh or
healthy.

- **R6-AC1:** Given a known set of source records containing agent time, token and cache use,
  transfers, tool calls, and `exec_command` process observations, inspection can group the data
  by agent, role or path, dispatch, tool, and `exec_command` run, trace every reported value to
  its source record, and reconcile totals without counting any source observation twice.
- **R6-AC2:** Given source data containing an observed value, a known missing value, an unknown
  or unavailable value, and a fallback or inferred observation, inspection distinguishes each
  source, availability or quality state, and applicable limitation, and assigns no higher
  fidelity to the fallback or inference than its source supports.
- **R6-AC3:** Given ingestion and observer errors, dropped and rejected records, quota
  exhaustion or collection stoppage after an earlier report, inspection exposes those health
  conditions, the retained-data boundary, and telemetry overhead; the earlier report remains
  readable and is visibly not fresh or healthy.

## Goal traceability

| Goal Close outcome | Requirement and AC coverage |
|---|---|
| [1](Goal.md#close-outcomes) | R1 (R1-AC1, R1-AC2); R2 (R2-AC1, R2-AC2); R3 (R3-AC1); R4 (R4-AC1); R5 (R5-AC1) |
| [2](Goal.md#close-outcomes) | R5 (R5-AC3, R5-AC4) |
| [3](Goal.md#close-outcomes) | R2 (R2-AC1, R2-AC2, R2-AC3); R3 (R3-AC1, R3-AC2, R3-AC3); R4 (R4-AC1, R4-AC2); R5 (R5-AC2, R5-AC5); R6 (R6-AC1, R6-AC2, R6-AC3) |
