#!/usr/bin/env python3
"""Validate GMGN structure and machine-readable workflow invariants."""

from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import release_metadata, validate_normative_layout


SKILLS = {
    "gmgn",
    "brainstorm",
    "write-decision",
    "roadmap",
    "write-goal",
    "write-requirement",
    "write-design",
    "write-task",
    "run-task",
    "close-milestone",
    "release",
}
ROLES = {"author", "coder", "critic", "reviewer", "researcher", "verifier"}
ROLE_SANDBOX = {
    "author": "workspace-write",
    "coder": "workspace-write",
    "critic": "read-only",
    "reviewer": "workspace-write",
    "researcher": "read-only",
    "verifier": "workspace-write",
}
TASK_HEADER = "| # | task | spec anchor | prerequisite | status | execution |"
OLD_TASK_HEADER = "| # | task | spec anchor | prerequisite | failing test | status |"
ASSURANCE_POLICY = Path("skills/gmgn/references/en/assurance-policy.json")
VERIFIER_TRIGGERS = [
    "artifact-not-fully-machine-checkable",
    "reviewer-unavailable-real-startup-or-e2e",
    "explicit-independent-execution-requirement",
]
WRITING_RULES = Path("skills/gmgn/references/en/writing-rules.md")
RUN_TASK = Path("skills/run-task/SKILL.md")
WRITE_DECISION = Path("skills/write-decision/SKILL.md")
WRITE_DESIGN = Path("skills/write-design/SKILL.md")
DISPATCH_CONTRACT = Path("skills/gmgn/references/en/dispatch-and-handoff.md")
ROADMAP = Path("skills/roadmap/SKILL.md")
WRITE_GOAL = Path("skills/write-goal/SKILL.md")
RELEASE = Path("skills/release/SKILL.md")
CANONICAL_REFERENCES = {
    ASSURANCE_POLICY,
    WRITING_RULES,
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/en/code-review.md"),
}
RUN_TASK_CONTROLS = (
    "create exactly two files for every newly materialized task",
    "The verification contract selects an executable oracle",
    "Treat safe lane saturation as a scheduling invariant",
    "At run-task entry, after Card\npreparation",
    "scan the entire target-Milestone Task set",
    "Inspect every Task, not only the lane or descendants involved\nin the event",
    "dispatch every ready, non-conflicting task",
    "do not leave capacity idle",
    "recompute and\nrefill immediately",
    "event-driven and does not authorize lifecycle polling",
    "Authorization and missing-information pauses follow the dispatch contract",
    "largest number of currently blocked tasks ready",
    "break ties by stable `card_id`",
    "`ponytail:ponytail`",
    "`ponytail:ponytail-review`",
    "`codegraph init <workspace>`",
    "sends the primary orchestrator an interim decision request",
    "Resume the\nsame Coder only when the adjudication preserves its objective and write boundary",
    "Every Codex `wait_agent` call uses\n"
    "the actual tool argument `{\"timeout_ms\": 600000}` (10 minutes) as a maximum wait",
    "An agent\ncompletion or attention event returns early",
    "without calling `list_agents`",
    "If the full ten minutes expires without an event, call `list_agents` once",
    "Handle any completed\nor attention-needed dispatch immediately",
    "return to the same maximum ten-minute `wait_agent` call",
    "Do not call\n`list_agents` more than once for the same timeout",
    "Between lifecycle events and timeout boundaries, do not poll `list_agents`",
    "A message to an active agent must carry authorization, requested information, or\nanother decision permitted by the dispatch contract",
    "Do not infer a shorter polling interval",
    "While any dispatched agent is\n"
    "`running`, do not call `interrupt_agent`, end the orchestration, or return a final task result",
    "time or token budget are not such evidence",
    "does not create or send\n"
    "heartbeat, unchanged `running`, timeout, agent-count, or progress data to the user, Log,\n"
    "telemetry, or another agent",
    "Create exactly one fresh Reviewer",
    "This is the Task execution's only Reviewer round",
    "Never create or dispatch another Reviewer to recheck findings or fixes",
)
RUN_TASK_EXCLUSIVE_MARKERS = (
    "wait_agent",
    "list_agents",
    "interrupt_agent",
    "largest number of currently blocked tasks ready",
    "break ties by stable `card_id`",
    "ponytail:ponytail",
    "ponytail:ponytail-review",
    "codegraph init",
    "commit-bound brief",
)
GMGN_SINGLE_REVIEW_CONTROLS = (
    "Each semantic candidate batch has at most one Critic round",
    "each Task execution has\nexactly one Reviewer round",
    "without dispatching\nthat role again",
)
DISPATCH_SINGLE_REVIEW_CONTROLS = (
    "An initial implementation\ncandidate has one fresh Reviewer dispatch",
    "Accepted finding fixes do not create another\nCritic or Reviewer dispatch",
)
DISPATCH_LIFECYCLE_CONTROLS = (
    "An authorization or missing-information request is an interim\npause, not a terminal return",
    "That primary-\norchestrator decision is sufficient for the agent",
    "The terminal completion return retires the agent",
    "Never resume, reactivate, repurpose, or send\nlater work to a retired agent",
    "applicable authority, scope, checks, and environment validity inputs\nremain unchanged",
    "Otherwise the fixed review surface is invalidated and requires a new brief\nand agent",
)
DISPATCH_ROLE_PROFILE_CONTROLS = (
    "Before creating any delegated agent, the primary orchestrator reads this current\ncontract",
    "the selected platform-specific GMGN\nrole profile",
    "these are the only GMGN agent\nroles",
    "It does not create a generic, unnamed, or ad hoc role",
    "A task name or `dispatch_id` may\ndistinguish instances but does not define another role",
    "The brief must carry\nthe selected profile's applicable instructions",
    "On Codex, read `.codex/agents/<role>.toml`",
    "load `agents/<role>.md` for the\nselected GMGN role",
)
EXTERNAL_AUTHORIZATION_CONTROLS = (
    "One authorization may cover a named set of external operations against an exact target",
    "Expanding the operation set, target, or side effects requires another authorization",
)
RUNTIME_ROLE_ROWS = (
    "| Author, Critic, Reviewer, Verifier | `gpt-5.6-sol` | `max` |",
    "| Coder | `gpt-5.6-terra` | `max` |",
    "| Researcher | `gpt-5.6-terra` | `max` |",
)
RUNTIME_SELECTION_CONTROLS = (
    "reads the current `spawn_agent` schema",
    *RUNTIME_ROLE_ROWS,
    "state the selected `model`, `reasoning_effort`, and a\none-sentence reason in user-visible commentary",
    'call it with `fork_turns: "none"` and pass\nthe selected `model` and `reasoning_effort`',
)
RESEARCHER_CONTROLS = (
    "Researcher** is an information collector only",
    "It does not\n  synthesize across sources, compare, infer, recommend, or decide",
    "The primary orchestrator\n  owns aggregation, analysis, inference, comparison, and conclusions",
    "A Researcher brief defines one bounded collection question",
    "It never asks the Researcher\nfor analysis or a conclusion",
)
ROADMAP_APPROVAL_CONTROLS = (
    "writes one complete recommended candidate without asking the owner to\napprove fields or allocations separately",
    "That approval ratifies the ROADMAP-\nowned allocations and rulings expressed in the candidate",
)
GOAL_APPROVAL_CONTROLS = (
    "Prepare the Goal and proposed initiation as one candidate",
    "do not require a separate initiation authorization",
    "That approval both authorizes the\nMilestone state change and approves Goal meaning",
)
RELEASE_OPERATION_ORDER_CONTROLS = (
    "push the branch and tag together\natomically when the host supports it",
    "create or complete the Release from that tag",
    "upload the\nnamed assets",
    "read the final remote state back once",
)
GMGN_RUN_TASK_ROUTE_CONTROLS = (
    "An initiated Milestone has accepted Task rows that can run",
)
CONTRADICTORY_POLICY_MARKERS = (
    "Any return retires the agent",
    "Every external operation needs separate authorization",
    "scan only the separately confirmed execution set",
    "Every delegated agent inherits the primary orchestrator configuration",
    "Researcher** analyzes and recommends solutions",
)
CODE_REVIEW_SINGLE_CONTROLS = (
    "Each Task execution has exactly one Reviewer\nround",
    "without another Reviewer round",
)
REVIEWER_SINGLE_CONTROLS = (
    "the complete candidate surface",
    "only Reviewer round",
)
CRITIC_SINGLE_CONTROLS = (
    "only Critic round",
)
LATEST_EVENT_VALUES = (
    "latest_event: [Current](#current)",
    "latest_event: [Final Evidence](#final-evidence)",
)
MILESTONE_REOPEN_CONTROLS = (
    "state: closed → initiated when unfinished work is found",
    "replace its current `accepted_result` with `none`",
    "do not roll them back merely because a prerequisite was reopened",
)
DECISION_SCOPE_CONTROLS = (
    "regardless of subject or Milestone scope",
    "Decision may own any current ruling needed by planning or active work",
    "downstream artifacts link the applicable D-ID and keep only their own derived content",
    "Never keep the same ruling normative in both places",
)
DECISION_CONSUMPTION_CONTROLS = (
    "a direct specification for downstream artifacts or an implementation checklist for one\nMilestone",
    "A D-ID creates no Milestone allocation or execution obligation by itself",
    "no Milestone must implement the whole Decision",
)
DECISION_LINK_CONTROLS = (
    "`Decision.md` lists `DecisionLog.md` and its current direct consumer artifacts as downstream",
    "Downstream artifacts link an applicable D-ID without copying its ruling",
)
WRITE_DESIGN_RESEARCH_CONTROLS = (
    "the primary session derives one bounded research scope",
    "observable candidate and source inclusion and exclusion conditions",
    "the primary session dispatches one\nfresh Researcher under the shared dispatch contract to collect the external evidence. It does\nnot search external sources itself",
    "the Researcher to discover up to three credible candidates",
    "whether a candidate or source enters the collection set only by those conditions",
    "The primary session aggregates the returned evidence, compares only what can change the\ndecision, and selects the Design-owned solution",
)
RELEASE_VERIFIER_TRIGGER_CONTROLS = (
    "The `trigger` must exactly match a member of that policy's `verifier.triggers` list",
)
VERIFIER_TRIGGER_FALLBACK_MARKERS = {
    Path("GMGN.md"): (
        "installation, startup,\nnon-machine-checkable artifacts, or another recorded risk may still require one",
    ),
    Path("README.md"): (
        "| Risk-triggered final verification | Installation, startup, E2E, external environments, or artifacts not fully machine-checkable |",
    ),
    Path("README.zh-CN.md"): (
        "| 风险触发的最终验证 | 安装、启动、E2E、外部环境或无法完全机检的制品 |",
    ),
    RELEASE: ("Dispatch one fresh Verifier only for a recorded trigger such as:",),
}


def read(relative: Path | str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"缺少文件: {relative}")
    return path.read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def active_markdown(text: str) -> str:
    without_comments = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(
        r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$",
        "",
        without_comments,
    )


def require_fragments(
    text: str, fragments: tuple[str, ...], label: str, errors: list[str]
) -> None:
    haystack = normalized(text)
    missing = [fragment for fragment in fragments if normalized(fragment) not in haystack]
    if missing:
        errors.append(f"{label}: 缺少 {missing}")


def require_active_fragments(
    text: str, fragments: tuple[str, ...], label: str, errors: list[str]
) -> None:
    require_fragments(active_markdown(text), fragments, label, errors)


def active_policy_files() -> tuple[Path, ...]:
    paths: set[Path] = set()
    for pattern in (
        "GMGN.md",
        "README*.md",
        "skills/**/*.md",
        "skills/**/*.yaml",
        "skills/**/*.json",
        "agents/*.md",
        ".codex/agents/*.toml",
    ):
        for path in ROOT.glob(pattern):
            relative = path.relative_to(ROOT)
            if "archive" not in {part.casefold() for part in relative.parts}:
                paths.add(relative)
    return tuple(sorted(paths))


def frontmatter(relative: Path) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", read(relative), re.S)
    if not match:
        raise AssertionError(f"{relative}: frontmatter 缺失")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise AssertionError(f"{relative}: frontmatter 行无冒号")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_release(errors: list[str]) -> None:
    try:
        release_metadata(ROOT)
    except ValueError as exc:
        errors.append(f"发布版本门禁失败: {exc}")
    try:
        validate_normative_layout(ROOT)
    except ValueError as exc:
        errors.append(str(exc))


def validate_skill_layout(errors: list[str]) -> None:
    actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if actual != SKILLS:
        errors.append(
            f"skill 集合不一致: expected={sorted(SKILLS)}, actual={sorted(actual)}"
        )
    for name in sorted(SKILLS):
        relative = Path("skills") / name / "SKILL.md"
        try:
            fields = frontmatter(relative)
            if fields.get("name") != name:
                errors.append(f"{relative}: name 必须等于目录名 {name}")
            if not fields.get("description"):
                errors.append(f"{relative}: description 缺失")
            extra = sorted(set(fields) - {"name", "description"})
            if extra:
                errors.append(f"{relative}: frontmatter 多出 {extra}")
            if len(read(relative).splitlines()) > 500:
                errors.append(f"{relative}: 超过 500 行")
            agent = relative.parent / "agents/openai.yaml"
            if not (ROOT / agent).is_file():
                errors.append(f"{agent}: 缺失")
        except AssertionError as exc:
            errors.append(str(exc))


def validate_shared_surfaces(errors: list[str]) -> None:
    for relative in sorted(CANONICAL_REFERENCES):
        if not (ROOT / relative).is_file():
            errors.append(f"{relative}: 共享规则文件缺失")

    policy_files = active_policy_files()
    writing_rules = read(WRITING_RULES)
    write_decision = read(WRITE_DECISION)
    write_task = read("skills/write-task/SKILL.md")
    dispatch_contract = read(DISPATCH_CONTRACT)
    require_fragments(
        writing_rules,
        (
            TASK_HEADER,
            *LATEST_EVENT_VALUES,
            *MILESTONE_REOPEN_CONTROLS,
            *DECISION_LINK_CONTROLS,
        ),
        "writing-rules 机器字段",
        errors,
    )
    require_active_fragments(
        writing_rules,
        DECISION_CONSUMPTION_CONTROLS,
        "Decision 下游消费边界",
        errors,
    )
    require_active_fragments(
        write_decision,
        DECISION_SCOPE_CONTROLS,
        "write-decision 决议范围",
        errors,
    )
    require_fragments(write_task, (TASK_HEADER,), "write-task 表头", errors)
    require_active_fragments(
        dispatch_contract,
        (
            *DISPATCH_LIFECYCLE_CONTROLS,
            *DISPATCH_ROLE_PROFILE_CONTROLS,
            *EXTERNAL_AUTHORIZATION_CONTROLS,
            *RUNTIME_SELECTION_CONTROLS,
            *RESEARCHER_CONTROLS,
        ),
        "派发授权与生命周期",
        errors,
    )
    active_dispatch = active_markdown(dispatch_contract)
    for row in RUNTIME_ROLE_ROWS:
        if active_dispatch.count(row) != 1:
            errors.append(f"派发运行时映射必须有且只有一行: {row}")
    require_active_fragments(
        read(ROADMAP),
        ROADMAP_APPROVAL_CONTROLS,
        "ROADMAP 一次批准",
        errors,
    )
    require_active_fragments(
        read(WRITE_GOAL),
        GOAL_APPROVAL_CONTROLS,
        "Goal 合并批准",
        errors,
    )
    require_active_fragments(
        read(RELEASE),
        RELEASE_OPERATION_ORDER_CONTROLS,
        "release 外部操作顺序",
        errors,
    )
    require_active_fragments(
        read(WRITE_DESIGN),
        WRITE_DESIGN_RESEARCH_CONTROLS,
        "write-design 外部调研边界",
        errors,
    )
    require_active_fragments(
        read("skills/gmgn/SKILL.md"),
        GMGN_RUN_TASK_ROUTE_CONTROLS,
        "gmgn run-task 路由",
        errors,
    )

    if (ROOT / "skills/gmgn/references/en/writing-contract.md").exists():
        errors.append("旧 writing-contract.md 不应恢复")
    for relative in policy_files:
        text = read(relative)
        active_text = active_markdown(text)
        if OLD_TASK_HEADER in text:
            errors.append(f"{relative}: 含旧 Task 表头")
        if "writing-contract.md" in text.casefold():
            errors.append(f"{relative}: 引用旧 writing-contract.md")
        if relative != WRITING_RULES:
            copied = [value for value in LATEST_EVENT_VALUES if value in text]
            if copied:
                errors.append(f"{relative}: 复制了 writing-rules 的 latest_event 值 {copied}")
        for legacy in ("review_policy: single-pass", "gmgn-assurance-v1"):
            if legacy in text:
                errors.append(f"{relative}: 含旧审查策略 {legacy}")
        for obsolete_review in (
            "review_mode: full",
            "review_mode: delta",
            "at most two Review rounds",
            "second Review round",
            "fresh delta Review",
            "full and delta review",
        ):
            if obsolete_review.casefold() in active_text.casefold():
                errors.append(f"{relative}: 含已废止多轮审查规则 {obsolete_review}")
        for obsolete in (
            "A closed foundation remains closed.",
            "Only explicit acceptance authorizes integrating",
            "rulings that constrain multiple Milestones and are not already",
            "Do not absorb WhitePaper meaning, ROADMAP allocation",
            "no current material cross-Milestone ruling",
            "One return ends the agent",
            "owner confirms the execution set",
            "one material allocation question at a time",
            "Local installation is a separate authorized operation",
            "Researcher** distinguishes direct observation, sourced fact, and inference",
        ):
            if obsolete in active_text:
                errors.append(f"{relative}: 含已废止规则 {obsolete}")
        for contradiction in CONTRADICTORY_POLICY_MARKERS:
            if contradiction.casefold() in active_text.casefold():
                errors.append(f"{relative}: 含冲突规则 {contradiction}")


def validate_assurance_policy(errors: list[str]) -> None:
    try:
        policy = json.loads(read(ASSURANCE_POLICY))
    except (AssertionError, json.JSONDecodeError) as exc:
        errors.append(f"{ASSURANCE_POLICY}: JSON 无效 ({exc})")
        return
    if not isinstance(policy, dict):
        errors.append(f"{ASSURANCE_POLICY}: 顶层必须是对象")
        return
    expected_keys = {"schema_version", "policy_id", "reviewer", "verifier"}
    if set(policy) != expected_keys:
        errors.append(
            f"{ASSURANCE_POLICY}: 顶层字段应为 {sorted(expected_keys)}"
        )
    if policy.get("schema_version") != "gmgn.assurance-policy.v2":
        errors.append(f"{ASSURANCE_POLICY}: schema_version 无效")
    if policy.get("policy_id") != "gmgn-assurance-v2":
        errors.append(f"{ASSURANCE_POLICY}: policy_id 无效")

    reviewer = policy.get("reviewer")
    expected_reviewer = {
        "required_for": ["implementation-diff", "test-code-diff"],
        "execution": "deterministic-local",
        "candidate_integrity": "reviewed-content-unchanged",
    }
    if reviewer != expected_reviewer:
        errors.append(f"{ASSURANCE_POLICY}: Reviewer 策略无效")

    verifier = policy.get("verifier")
    if not isinstance(verifier, dict) or verifier.get("default") is not False:
        errors.append(f"{ASSURANCE_POLICY}: Verifier 必须默认关闭")
        return
    if verifier.get("candidate") != "blocker-resolved-final":
        errors.append(f"{ASSURANCE_POLICY}: Verifier candidate 无效")
    if verifier.get("classification") != {
        "not_required": "not-required",
        "required_prefix": "required:",
    }:
        errors.append(f"{ASSURANCE_POLICY}: Verifier classification 无效")
    if verifier.get("triggers") != VERIFIER_TRIGGERS:
        errors.append(f"{ASSURANCE_POLICY}: Verifier triggers 必须等于 {VERIFIER_TRIGGERS}")


def validate_verifier_trigger_authority(errors: list[str]) -> None:
    release = active_markdown(read(RELEASE))
    require_fragments(
        release,
        RELEASE_VERIFIER_TRIGGER_CONTROLS,
        "release Verifier trigger 权威",
        errors,
    )
    copied = [trigger for trigger in VERIFIER_TRIGGERS if trigger in release]
    if copied:
        errors.append(f"{RELEASE}: 不得复制 Verifier trigger {copied}")
    for relative, markers in VERIFIER_TRIGGER_FALLBACK_MARKERS.items():
        active_text = active_markdown(read(relative))
        for marker in markers:
            if marker in active_text:
                errors.append(f"{relative}: 含旧 Verifier 宽泛触发描述")


def validate_run_task_controls(errors: list[str]) -> None:
    run_task = read(RUN_TASK)
    require_active_fragments(run_task, RUN_TASK_CONTROLS, "run-task 关键执行控制", errors)
    require_active_fragments(
        read("skills/gmgn/SKILL.md"),
        GMGN_SINGLE_REVIEW_CONTROLS,
        "gmgn 单轮独立审查边界",
        errors,
    )
    require_active_fragments(
        read(DISPATCH_CONTRACT),
        DISPATCH_SINGLE_REVIEW_CONTROLS,
        "派发单轮独立审查边界",
        errors,
    )
    require_active_fragments(
        read("skills/gmgn/references/en/code-review.md"),
        CODE_REVIEW_SINGLE_CONTROLS,
        "code-review 单轮审查边界",
        errors,
    )
    require_active_fragments(
        read("agents/reviewer.md"),
        REVIEWER_SINGLE_CONTROLS,
        "Reviewer 单轮审查边界",
        errors,
    )
    require_active_fragments(
        read("agents/critic.md"),
        CRITIC_SINGLE_CONTROLS,
        "Critic 单轮审查边界",
        errors,
    )
    for relative in active_policy_files():
        if relative == RUN_TASK:
            continue
        text = read(relative).casefold()
        copied = [
            marker
            for marker in RUN_TASK_EXCLUSIVE_MARKERS
            if marker.casefold() in text
        ]
        if copied:
            errors.append(f"{relative}: 复制了 run-task 专属规则 {copied}")

    install_commands = (
        "codex plugin marketplace add DietrichGebert/ponytail",
        "codex plugin add ponytail@ponytail",
        "claude plugin marketplace add DietrichGebert/ponytail",
        "claude plugin install ponytail@ponytail --scope user",
    )
    for relative in (Path("README.md"), Path("README.zh-CN.md")):
        require_fragments(read(relative), install_commands, f"{relative} Ponytail 安装", errors)


def validate_roles(errors: list[str]) -> None:
    for role in sorted(ROLES):
        markdown = Path("agents") / f"{role}.md"
        toml_path = Path(".codex/agents") / f"{role}.toml"
        try:
            fields = frontmatter(markdown)
            text = read(markdown)
            if fields.get("name") != role:
                errors.append(f"{markdown}: name 不一致")
            if len(text.splitlines()) > 80:
                errors.append(f"{markdown}: 超过 80 行")
            require_fragments(
                text, ("prepared", "brief"), str(markdown), errors
            )
            try:
                config = tomllib.loads(read(toml_path))
            except tomllib.TOMLDecodeError as exc:
                errors.append(f"{toml_path}: TOML 无效 ({exc})")
                continue
            for key in ("name", "description", "sandbox_mode", "developer_instructions"):
                if not isinstance(config.get(key), str):
                    errors.append(f"{toml_path}: {key} 必须是字符串")
            if config.get("sandbox_mode") != ROLE_SANDBOX[role]:
                errors.append(
                    f"{toml_path}: sandbox_mode 应为 {ROLE_SANDBOX[role]}"
                )
            instructions = config.get("developer_instructions", "")
            if isinstance(instructions, str) and "brief" not in instructions.casefold():
                errors.append(f"{toml_path}: 缺少 brief 边界")
        except AssertionError as exc:
            errors.append(str(exc))


def validate_docstar_adapter(errors: list[str]) -> None:
    relative = Path(".docstar/conventions/conventions.json")
    try:
        config = json.loads(read(relative))
    except (AssertionError, json.JSONDecodeError) as exc:
        errors.append(f"{relative}: JSON 无效 ({exc})")
        return
    if config.get("task_columns") != {
        "spec": "spec anchor",
        "prereq": "prerequisite",
        "status": "status",
        "execution": "execution",
    }:
        errors.append("DocStar task_columns 无效")
    if config.get("task_execution") != {
        "card_fields": {"execution_log": ["execution_log"]},
        "log_fields": {"latest_event": ["latest_event"]},
        "canonical_task_table_only": True,
    }:
        errors.append("DocStar task_execution 无效")
    if config.get("archive_globs") != ["[Aa]rchive"]:
        errors.append("DocStar archive_globs 无效")
    if config.get("namespaces", {}).get("kind_namespace", {}).get("决议") != "Decision":
        errors.append("DocStar D-ID namespace 无效")
    if config.get("def_forms", {}).get("决议") != r"^-\s*\*\*(D-\d{3})\*\*":
        errors.append("DocStar D-ID 定义格式无效")
    decision_kind = [
        "决议",
        r"(?<![A-Za-z0-9_])D-\d{3}(?![A-Za-z0-9_-])",
        "GMGN decision ID D-NNN",
    ]
    if decision_kind not in config.get("doc_id_kinds", []):
        errors.append("DocStar 未识别 D-ID")
    if "决议" not in config.get("uncovered_kind_exclusions", []):
        errors.append("DocStar 决议覆盖规则无效")


def validate_relative_links(errors: list[str]) -> None:
    try:
        config = json.loads(read(".docstar/conventions/conventions.json"))
    except (AssertionError, json.JSONDecodeError):
        return
    archive_globs = config.get("archive_globs")
    if not isinstance(archive_globs, list) or not archive_globs:
        return

    def is_archived(relative: Path) -> bool:
        return any(
            fnmatchcase(part, pattern)
            for part in relative.parts
            for pattern in archive_globs
        )

    link_pattern = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
    root = ROOT.resolve()
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if any(part in {".git", "dist"} for part in relative.parts) or is_archived(relative):
            continue
        visible: list[str] = []
        fenced = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\s*(```|~~~)", line):
                fenced = not fenced
                continue
            if not fenced:
                visible.append(re.sub(r"`[^`\n]*`", "", line))
        for target in link_pattern.findall("\n".join(visible)):
            target = target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = unquote(target.split("#", 1)[0])
            if not file_part or "<" in file_part or ">" in file_part:
                continue
            resolved = (path.parent / file_part).resolve()
            try:
                target_relative = resolved.relative_to(root)
            except ValueError:
                errors.append(f"{relative}: 链接越出仓库 {target}")
                continue
            if is_archived(target_relative):
                errors.append(f"{relative}: 活动文档不得引用 archive 文档 {target}")
            elif not resolved.exists():
                errors.append(f"{relative}: 链接目标不存在 {target}")
            elif path.name == "SKILL.md" and path.parent.parent == ROOT / "skills":
                try:
                    resolved.relative_to(path.parent.resolve())
                except ValueError:
                    errors.append(f"{relative}: Skill 运行时链接越出自身目录 {target}")


def main() -> int:
    errors: list[str] = []
    validate_release(errors)
    validate_skill_layout(errors)
    validate_shared_surfaces(errors)
    validate_assurance_policy(errors)
    validate_verifier_trigger_authority(errors)
    validate_run_task_controls(errors)
    validate_roles(errors)
    validate_docstar_adapter(errors)
    validate_relative_links(errors)
    if errors:
        print("GMGN 校验失败:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("GMGN 结构与机器契约校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
