---
locale: en
purpose: Allocate the approved telemetry refactor to one outcome-based project Milestone.
upstream: [Decision](Decision.md)
downstream: [Goal](Goal.md)
status: approved
type: roadmap
nature: normative
---

# Roadmap

## Milestones

- **M1** — Correlated and auditable telemetry

| field | value |
|---|---|
| applicable decisions | [D-001](Decision.md), [D-002](Decision.md), [D-003](Decision.md), [D-004](Decision.md), [D-005](Decision.md) |
| horizon | `now` |
| relative priority | `1` |
| prerequisites | `none` |
| state | `initiated` |
| accepted_result | `none` |

### Outcome and allocation value

GMGN has privacy-safe, correlated, and auditable telemetry on macOS and Linux for agent token
use, runtime, token-cache activity, agent-to-agent information transfer, tool use, and each
`exec_command` root shell plus its actually observed process descendants. This allocation makes
resource use and interactions attributable without changing execution or overstating process
observation.

### Deliverables

- Unified correlated records and a collection entry point cover the allocated session, turn,
  agent, dispatch, tool, shell, and observed-process activity.
- Platform-adapted `exec_command` process observation relates the root shell to actually observed
  descendants on Linux and macOS and exposes the observation quality of each run.
- Reporting supports aggregation by agent, tool, and dispatch while making telemetry data quality,
  collection health, and telemetry overhead visible.

### Success signal

One GMGN run can be traced end to end and its allocated resource use and interactions can be
distinguished; Linux and macOS records state their observation quality without converting unknown
omissions into known facts; telemetry failure does not change command behavior; and collected data
stays within [D-002](Decision.md).

## Backlog

None.
