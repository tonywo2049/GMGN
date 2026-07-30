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
**Claude Code**. Eleven composable skills move work from an idea to a closed milestone and then
publish an accepted commit without repeating closure review.
Hard gates prevent skipped stages, independent review reduces shared blind spots, and
replayable commands bind completion claims to evidence.

中文版本：[README.zh-CN.md](README.zh-CN.md)

```text
idea
 └─ brainstorm → WhitePaper
    → write-decision → Decision
    → roadmap → ROADMAP
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
- Public normative documents use English as their single source; only the README keeps an
  English/Chinese pair.
- A project artifact chain normally uses one active locale. If a project requires two
  translated chains, validate each locale tree separately to avoid duplicate IDs.

The shared writing rules are
[`skills/gmgn/references/en/writing-rules.md`](skills/gmgn/references/en/writing-rules.md).
GMGN does not ship translated normative mirrors or document-layout templates. Each stage skill
defines required content and self-checks; the Author chooses the structure and may write
project artifacts in the active locale.

`Decision.md` may hold any accepted ruling selected for downstream consumption, regardless
of subject or Milestone scope. Downstream artifacts link applicable D-IDs instead of
redefining those rulings. `DecisionLog.md` records only accepted changes and is not normal
downstream context.

Every ROADMAP Milestone maps to WhitePaper and applicable D-IDs, states one outcome and its value, names necessary
deliverables and one result-level success signal, and separates `now | next | later`,
relative priority, and real dependencies. The orchestrator proposes the map and asks the
human owner one material allocation question at a time. ROADMAP does not own an E2E path.

Each stage document adds one kind of information: Decision records rulings explicitly
centralized for downstream use; ROADMAP allocates partially ordered Milestones and their
outcomes; Goal refines the active Milestone into Requirement input and qualitative Close
criteria; Requirement defines observable behavior and decidable ACs; Design resolves or
links the technical decisions needed to implement them; Task indexes independently
completable results, dependencies, status, and execution links. Stage documents do not
contain downstream gates, propagation rules, next-stage instructions, or speculative
placeholders.

The Design stage always produces root `Design.md`. Add `design/<module-id>.md` only for a
useful module authority. A boundary between independently developed units requires
`design/Contract.md`; split contracts and `design/schemas/` authorities are conditional.
No empty scaffolding is created. The complete linked files form one reviewed Design Bundle.
It is ready only when independent Coders no longer need to invent a public or cross-unit
decision and would produce compatible results from the same authority.
The Design-stage Contract is an approved working baseline. Coding evidence may revise it
through `write-design`; Milestone closure reconciles it with provider/consumer code and marks
the reviewed implementation-matching commit as `closed`.

## Supported surfaces

| Capability | Codex | Claude Code |
|---|---|---|
| Eleven shared skills | Supported | Supported |
| Invocation | Natural language or `$gmgn` | Natural language or `/gmgn:gmgn` |
| Code review and deterministic local checks | `/review`; CLI: `codex review --commit/--base` plus project commands | Independent reviewer plus project commands; `/code-review` only for an authorized GitHub PR |
| Risk-triggered final verification | Installation, startup, E2E, external environments, or artifacts not fully machine-checkable | Project commands; `/verify` where available |
| Plugin manifest | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` |

Every delegated role follows the
[dispatch contract](skills/gmgn/references/en/dispatch-and-handoff.md): prepare the brief
first, create a fresh single-use agent, and bind its return to an immutable candidate. An
implementation candidate gets at most two Review rounds: one fresh full Review and, only when
needed, one fresh cumulative fix-delta Review that cannot open unrelated findings. Mechanical
fixes use affected machine checks; there is no third Review round. A Verifier remains
risk-triggered under
[`gmgn-assurance-v2`](skills/gmgn/references/en/assurance-policy.json). Full and delta review
surfaces are defined by the
[code-review contract](skills/gmgn/references/en/code-review.md).

`Task.md` remains a Milestone index. For confirmed rows, `run-task` creates a stable
`Card.md` execution and verification contract plus a replaceable `Log.md`, then owns ready-set
scheduling, isolated writer lanes, runtime tools, monitoring, review, integration, and
closure. A Task closes only after the reviewed content is integrated and every
project-declared required check passes against that exact shared-baseline candidate. The
complete rules live in [`run-task`](skills/run-task/SKILL.md).

A closed Milestone returns to `initiated` when unfinished work is found. Its current
`accepted_result` is cleared, only affected work is reopened, and downstream Milestones are
changed only when impact analysis shows they are affected. Owner closure review is a review
checkpoint, not an irrevocable decision.

R-D-T minimality is enforced by GMGN itself. Code minimality uses the external
[Ponytail](https://github.com/DietrichGebert/ponytail) plugin; its installation is required for
run-task code work. Exact Ponytail, CodeGraph, and DocStar runtime rules are kept only in
`run-task`.

## Install

### Codex

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
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
claude plugin marketplace add DietrichGebert/ponytail
claude plugin install ponytail@ponytail --scope user
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
| “Record this decision for downstream work.” | `write-decision` | Current Decision authority and descriptive DecisionLog |
| “Split the approved WhitePaper and Decision into milestones.” | `roadmap` | ROADMAP with outcome Milestones, success signals, horizons, priority, and real dependencies |
| “Start M1 and define its boundary.” | `write-goal` | Goal.md with Requirement input and qualitative Close criteria |
| “Write requirements and acceptance criteria.” | `write-requirement` | Observable requirements and decidable ACs |
| “Produce the technical design.” | `write-design` | Required technical decisions in root Design.md plus conditional authorities |
| “Break the design into tasks.” | `write-task` | Task.md execution index |
| “Implement these ready cards / fix this bug.” | `run-task` | Integrated code, tests, review, and any required verification evidence |
| “The milestone is complete; validate and close it.” | `close-milestone` | Applicable regression/E2E evidence, reviewed Contract state, closure record |
| “Publish the accepted version / retry its release.” | `release` | Reused acceptance evidence, deterministic artifact, tag and release |
| “What should happen next?” | `gmgn` | State diagnosis and routing |

Small bug fixes and narrow one-step changes may use the controlled bypass; they do not
need a fabricated full specification chain. WhitePaper, Decision, ROADMAP, milestone initiation,
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
skills/                         eleven cross-platform skills
  */agents/openai.yaml          Codex display metadata and default prompts
  gmgn/references/en/           English shared writing, dispatch, review, and assurance contracts
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
python3 scripts/package_release.py --set-version 0.2.19
```

The packager reads the version from the Codex manifest, includes only the release allowlist,
and produces a deterministic ZIP and SHA-256 checksum. The checksum is artifact-integrity
evidence, never a workflow anchor. `--set-version` validates SemVer and synchronizes the four
existing release declarations. Without `--allow-dirty`, the command rejects a dirty worktree.

## DocStar compatibility

[DocStar](https://github.com/tonywo2049/DocStar) is optional. The bundled
`.docstar/conventions/conventions.json` is the adapter for this GMGN version and includes
D-ID indexing. Copy it into a Decision-aware project corpus, then run:

```bash
python3 docstar.py check --corpus /path/to/gmgn-project
python3 docstar.py dump --json --corpus /path/to/gmgn-project
python3 docstar.py brief CARD-ID --baseline COMMIT --json --corpus /path/to/gmgn-project
```

Use `--preset gmgn-v1` only when the installed preset declares equivalent Decision rules.
GMGN remains installable and usable without DocStar. DocStar itself and its JSON output are
unchanged: every invocation performs a fresh full rebuild with no cache.
Telemetry hooks and reporters observe from outside DocStar, recording call count, elapsed
time, command type, and subsequent grep/read activity. `grep_avoided` is descriptive and
does not claim that DocStar caused a grep to be avoided.

CodeGraph is an optional source-navigation aid. Task-execution use of DocStar and CodeGraph is
defined by [`run-task`](skills/run-task/SKILL.md).

## License

MIT
