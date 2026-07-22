---
locale: en
purpose: Introduce GMGN installation, quick use, platform support, and development entry points.
status: approved
type: guide
nature: descriptive
---

# GMGN

**GM, GN.** Good morning, good night.

GMGN is an agentic software-delivery workflow for **Codex (CLI/Desktop)** and
**Claude Code**. Ten composable skills move work from an idea to a closed milestone and then
publish an accepted anchor without repeating closure review.
Hard gates prevent skipped stages, independent review reduces shared blind spots, and
replayable commands bind completion claims to evidence.

中文版本：[README.zh-CN.md](README.zh-CN.md)

```text
idea
 └─ brainstorm → WhitePaper → roadmap
                         └─ write-goal
                            → write-requirement
                            → write-design
                            → write-task
                            → run-task
                            → close-milestone
                            → release (when distribution is authorized)
                            → roadmap (next milestone)
```

`gmgn` is the router: use it when you do not know which stage matches the repository's
current state.

## README and methodology

This README is deliberately short: installation, first use, repository layout, and
development commands. [GMGN.md](GMGN.md) is the normative methodology: roles, document
chains, approval semantics, review rules, and closing discipline. They are linked, not
merged, because they serve different readers and change at different rates.

## Language model

GMGN has one workflow, not separate English and Chinese plugins.

- Skills detect the language from the active project and the user's request.
- Human prose and headings use `en` or `zh-CN`.
- Filenames, IDs, commands, frontmatter keys, enum values, and task-table headers stay
  stable English machine tokens.
- Public repository documents use English-primary files plus `.zh-CN.md` mirrors.
- A project artifact chain normally uses one active locale. If a project requires two
  translated chains, validate each locale tree separately to avoid duplicate IDs.

The shared machine contract is in
[`skills/gmgn/references/en/writing-contract.md`](skills/gmgn/references/en/writing-contract.md)
and its [Chinese mirror](skills/gmgn/references/zh-CN/writing-contract.md). GMGN does not
ship document-layout templates. Each stage skill defines required content and self-checks;
the Author chooses the structure.

## Supported surfaces

| Capability | Codex | Claude Code |
|---|---|---|
| Ten shared skills | Supported | Supported |
| Invocation | Natural language or `$gmgn` | Natural language or `/gmgn:gmgn` |
| Code review | `/review`; CLI: `codex review --uncommitted/--commit/--base` | Independent read-only reviewer; `/code-review` only for an authorized GitHub PR |
| Runtime verification | Project tests, startup, and E2E commands | Project commands; `/verify` where available |
| Plugin manifest | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |

Native review does not replace execution. GMGN still requires project tests and a
replayable verification path. In Codex, a custom review prompt and scope flags are
mutually exclusive; after review, check `git status --short` for generated side effects.
Every delegated role receives a complete brief before creation, returns once, and is retired.
Later authoring, coding, criticism, review, or verification uses a fresh agent without parent
or earlier-agent history. Fresh identity does not mean every role reruns: only roles whose
evidence surface changed are dispatched.

`run-task` continuously fills available capacity from a dependency-aware ready set. `Task.md`
keeps task division, AC mapping, dependencies, macro status, and execution pointers. Each
selected task gets `execution/<card_id>/Card.md` for its stable execution/TDD contract and
`Log.md` for current runtime state plus append-only history. Each Coder attempt uses a fresh
agent. Concurrent writers use explicitly provisioned worktrees; a single non-colliding writer
may use the verified current workspace. When no implementation lane can run in parallel with
useful orchestrator work, the primary session may be that Coder. Worktrees prevent agents
from overwriting the same files/index, but do not solve merge, semantic, interface, or shared
runtime-resource conflicts. The primary session serially owns the shared baseline, `Task.md`,
and traceability. A delegated Coder returns a local commit containing only its prepared write
scope; a primary-session sole Coder may freeze and hash its exact diff. An isolated-lane
candidate is applied to a temporary combination, while a sole-writer candidate already based
on the unchanged shared baseline is the final combination. After review blockers clear, one
fresh Verifier checks it when executable evidence is required. Clean mechanical integration does not
cause identical tests to run twice. Only success atomically advances the shared baseline.
Agent waiting is event-driven: exhaust useful local work, use one longest-safe wait, treat a
timeout only as a liveness checkpoint, and never turn status/list/wait calls into a polling
loop. Use one `list_agents` snapshot only for a scheduling decision, an ambiguous post-timeout
state, or conflicting lifecycle events; do not query again before material state changes.
There is no periodic list interval. Agent progress remains local to its thread; only material
lifecycle events notify the orchestrator.

The reviewed `Task.md` row selects the work; its materialized `Card.md` is the static execution
and TDD authority. Run-task roles receive exact authority pointers, current Log snapshot, and
lane facts, not the parent conversation or a duplicated per-agent handoff.

## Install

### Codex

```bash
codex plugin marketplace add tonywo2049/GMGN
codex plugin add gmgn@GMGN
```

Start a new Codex task, then verify:

```bash
codex plugin list
```

Try:

```text
$gmgn Determine the correct next step for this project.
```

### Claude Code

```bash
claude plugin marketplace add tonywo2049/GMGN
claude plugin install gmgn@GMGN --scope user
```

Start a new session and invoke `/gmgn:gmgn`, or describe the work directly.

### Local development copy

Replace the marketplace source with the repository's absolute path:

```bash
codex plugin marketplace add /absolute/path/to/GMGN
claude plugin marketplace add /absolute/path/to/GMGN
```

Do not install a manual copy of the same skills at the same time; duplicate installations
produce duplicate triggers.

## Upgrade

### GitHub marketplace installation

For Codex, refresh the marketplace and check the installed version:

```bash
codex plugin marketplace upgrade GMGN
codex plugin list
```

If the old version is still listed, reinstall the plugin from the refreshed marketplace:

```bash
codex plugin remove gmgn@GMGN
codex plugin add gmgn@GMGN
codex plugin list
```

For Claude Code, refresh the marketplace and update the plugin:

```bash
claude plugin marketplace update GMGN
claude plugin update gmgn@GMGN --scope user
claude plugin list --json
```

Replace `user` with the same `user`, `project`, or `local` scope that was used for installation.
The administrator controls a `managed`-scope installation; an end user cannot update it.

### Local development marketplace

Pull the source repository first, then refresh the installed copies explicitly:

```bash
git -C /absolute/path/to/GMGN pull --ff-only
codex plugin remove gmgn@GMGN
codex plugin add gmgn@GMGN
codex plugin list
claude plugin marketplace update GMGN
claude plugin update gmgn@GMGN --scope user
claude plugin list --json
```

For Claude Code, replace `user` with the original installation scope; `managed` scope still
requires the administrator. Do not run `codex plugin marketplace upgrade GMGN` for a local-path
marketplace: removing and adding the plugin refreshes its installed copy.

### Release ZIP or manual copy

Marketplace commands do not update a directory unpacked from a release ZIP or copied manually.
Replace the entire old directory with a freshly unpacked complete release, or migrate to the
marketplace installation above. Do not overlay files, keep a manual and marketplace copy at the
same time, or edit platform cache directories.

After any upgrade, start a new Codex task or Claude Code session. An active Claude Code session
may use `/reload-plugins` when that command is supported.

## Uninstall

```bash
codex plugin remove gmgn@GMGN
codex plugin marketplace remove GMGN
claude plugin uninstall gmgn@GMGN --scope user
claude plugin marketplace remove GMGN --scope user
```

## Use

| Request | Skill | Main output |
|---|---|---|
| “I have an idea; research whether it is viable.” | `brainstorm` | WhitePaper |
| “Split the approved WhitePaper into milestones.” | `roadmap` | ROADMAP with Milestone acceptance pictures |
| “Start M1 and define its boundary.” | `write-goal` | Goal.md |
| “Write requirements and acceptance criteria.” | `write-requirement` | Requirement.md |
| “Produce the technical design.” | `write-design` | Design.md |
| “Break the design into task cards.” | `write-task` | Task.md |
| “Implement these ready cards / fix this bug.” | `run-task` | Integrated code, tests, review, and any required verification evidence |
| “The milestone is complete; validate and close it.” | `close-milestone` | Regression, E2E, closure record |
| “Publish the accepted version / retry its release.” | `release` | Reused acceptance evidence, deterministic artifact, tag and release |
| “What should happen next?” | `gmgn` | State diagnosis and routing |

Small bug fixes and narrow one-step changes may use the controlled bypass; they do not
need a fabricated full specification chain. WhitePaper, ROADMAP, milestone initiation,
scope expansion, and closure still require their defined authorization.

## Optional telemetry

### Install and configure

Run these commands from an unpacked GMGN release or repository root:

```bash
python3 telemetry/install.py --dry-run
python3 telemetry/install.py --print-codex-config
python3 telemetry/install.py
python3 telemetry/report.py <session-id...> [--json]
```

`--dry-run` previews the installation. `--print-codex-config` prints the exact block to
merge into the user-level `~/.codex/config.toml`; project-level `otel` configuration is
ignored by Codex. The local Collector stays resident and receives Codex-native
OTLP/HTTP JSON at `/v1/logs`. Before writing, it converts known Codex events to a strict
metadata allowlist; raw OTLP bodies are not stored. The resulting records provide actual API
attempts, native tool-result durations, and task token counters when Codex emits those fields;
traces and metrics are explicitly disabled. After installation, inspect and trust the selected
user-level hooks in Codex `/hooks`. Wait hooks reduce outputs to a privacy-safe
`update | timeout | interrupted | error | unknown` result; they never retain an agent message.

With the default loopback host, open `http://127.0.0.1:4318/` for the local read-only
dashboard. It lists observed sessions and renders task duration, actual task tokens, tool and
skill profiles, GMGN orchestration, DocStar activity, source coverage, and data quality. The
dashboard uses only bundled static assets, makes no external requests, and serves a bounded
privacy-safe projection rather than prompts, commands, tool output, or raw session records.

### Privacy and reports

Codex uses `log_user_prompt=false`. The Collector drops prompts, commands, tool output, error
messages, host and user identity, credentials, and unknown fields. User-level hooks run for
configured session/subagent lifecycle events and matched Bash/Agent/wait events. They store only
timestamps, opaque session/turn/tool IDs, model, hashed project path, byte counts,
success/exit status, classifications, wait outcome, fork policy, and structured GMGN correlation IDs. Models
do not manually write telemetry logs or put them in prompts, `Task.md`, or `Handoff`.

Run the report command only for a user-requested retrospective. It prefers Collector and hook
records, then fills missing fields from session JSONL as an explicitly labelled `unstable
fallback`. Every metric reports its source and coverage. Missing actual token data is
`unknown`, not zero. The report exposes wait outcomes, state-change/timeout counts, maximum
consecutive timeouts, wait-storm count, and actual cumulative-token deltas associated with
model reactivation after a wait result. Wait calls are merged per `tool_use_id`: a structured
hook result is primary and session JSONL fills only uncovered calls, so the same wait is not
counted twice. Legacy unstructured rejection output with no reliable failure status remains
`unknown`; error classification never depends on argument/error message wording. Because current
session token events do not carry a tool call ID, that last association is labelled
`session_sequence_delta` and reports
matched/eligible coverage instead of claiming exact native linkage. Per-tool/skill input/output
token counts remain estimates. After
installation the same reporter is available at `~/.codex/gmgn-telemetry/bin/report.py`.
`--json` changes report format only.

## Repository layout

```text
skills/                         ten cross-platform skills
  */agents/openai.yaml          Codex display metadata and default prompts
  gmgn/references/{en,zh-CN}/   mirrored machine/dispatch contracts and checklists
agents/                         Claude Code plugin subagent roles
.docstar/conventions/           DocStar-compatible GMGN convention set
.codex-plugin/plugin.json       Codex plugin manifest
.claude-plugin/                 Claude Code plugin and marketplace manifests
.codex/agents/                  optional project-scoped Codex role profiles for this repository
.agents/plugins/                Codex marketplace manifest
tests/                          structure, language, platform, and package checks
scripts/package_release.py      deterministic ZIP and SHA-256 builder
telemetry/                      bundled Collector, hooks, installer, reporter, and local dashboard
GMGN.md                         normative methodology
```

Shared workflow rules live in `skills/` and [GMGN.md](GMGN.md). Platform directories
contain discovery, installation, and native-surface adapters only.

## Develop and package

```bash
./tests/validate.sh
python3 -m unittest discover -s tests
python3 scripts/package_release.py --allow-dirty
```

The packager reads the version from the Codex manifest, includes only the release
allowlist, and produces a deterministic ZIP and SHA-256 checksum. Without
`--allow-dirty`, it rejects a dirty worktree.

## DocStar compatibility

[DocStar](https://github.com/tonywo2049/DocStar) is optional. It can check links, graph
semantics, task closure, and bilingual parity using the same machine contract.

```bash
python3 docstar.py check --preset gmgn-v1 --corpus /path/to/gmgn-project
python3 docstar.py dump --preset gmgn-v1 --json --corpus /path/to/gmgn-project
python3 docstar.py brief CARD-ID --baseline COMMIT --preset gmgn-v1 --json --corpus /path/to/gmgn-project
```

When the corpus contains `.docstar/conventions/conventions.json`, the explicit preset is
not required. GMGN remains installable and usable without DocStar. DocStar itself and its
JSON output are unchanged: every invocation performs a fresh full rebuild with no cache.
Telemetry hooks and reporters observe from outside DocStar, recording call count, elapsed
time, command type, and subsequent grep/read activity. `grep_avoided` is descriptive and
does not claim that DocStar caused a grep to be avoided.

For run-task dispatch, DocStar 0.2.3 or later provides a commit-bound brief as the starting
evidence bundle.
It does not forbid an agent from following pointers or reading exact source ranges when more
evidence is needed. If `.codegraph/` exists, GMGN also uses CodeGraph as a role-specific code
locator—baseline for Coder, candidate for Reviewer, and on demand for Verifier—while grounding
claims in source, diffs, tests, and real execution.

## License

MIT
