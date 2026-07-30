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
ROLES = {"author", "coder", "critic", "reviewer", "verifier"}
ROLE_SANDBOX = {
    "author": "workspace-write",
    "coder": "workspace-write",
    "critic": "read-only",
    "reviewer": "workspace-write",
    "verifier": "workspace-write",
}
TASK_HEADER = "| # | task | spec anchor | prerequisite | status | execution |"
OLD_TASK_HEADER = "| # | task | spec anchor | prerequisite | failing test | status |"
ASSURANCE_POLICY = Path("skills/gmgn/references/en/assurance-policy.json")
WRITING_RULES = Path("skills/gmgn/references/en/writing-rules.md")
RUN_TASK = Path("skills/run-task/SKILL.md")
WRITE_DECISION = Path("skills/write-decision/SKILL.md")
CANONICAL_REFERENCES = {
    ASSURANCE_POLICY,
    WRITING_RULES,
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/en/code-review.md"),
}
RUN_TASK_CONTROLS = (
    "create exactly two files for every newly materialized task",
    "The verification contract selects an executable oracle",
    "scan the entire confirmed execution set",
    "dispatch every ready, non-conflicting task",
    "largest number of currently blocked tasks ready",
    "break ties by stable `card_id`",
    "`ponytail:ponytail`",
    "`ponytail:ponytail-review`",
    "`codegraph init <workspace>`",
    "Every Codex `wait_agent` call uses\n"
    "`agent_wait_timeout_ms = 3600000` (1 hour)",
    "immediately\nre-arm the same one-hour wait",
    "A timeout alone is not a `list_agents` trigger",
    "Use one\n"
    "`list_agents` snapshot only when a real scheduling/capacity decision cannot be made from\n"
    "received lifecycle events or those events conflict",
    "do not query again until a material\n"
    "lifecycle event or scheduling condition changes",
    "Do not interrupt, terminate, or kill an agent merely because it is silent, slow, has not\n"
    "returned content, or crossed one or more wait timeouts",
    "review_mode: full",
    "review_mode: delta",
    "Never dispatch a third Reviewer",
)
RUN_TASK_EXCLUSIVE_MARKERS = (
    "wait_agent",
    "list_agents",
    "agent_wait_timeout_ms",
    "largest number of currently blocked tasks ready",
    "break ties by stable `card_id`",
    "ponytail:ponytail",
    "ponytail:ponytail-review",
    "codegraph init",
    "commit-bound brief",
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
DECISION_LINK_CONTROLS = (
    "`Decision.md` lists `DecisionLog.md` and its current direct consumer artifacts as downstream",
    "Downstream artifacts link an applicable D-ID without copying its ruling",
)


def read(relative: Path | str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"缺少文件: {relative}")
    return path.read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def require_fragments(
    text: str, fragments: tuple[str, ...], label: str, errors: list[str]
) -> None:
    haystack = normalized(text)
    missing = [fragment for fragment in fragments if normalized(fragment) not in haystack]
    if missing:
        errors.append(f"{label}: 缺少 {missing}")


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
    require_fragments(
        write_decision,
        DECISION_SCOPE_CONTROLS,
        "write-decision 决议范围",
        errors,
    )
    require_fragments(write_task, (TASK_HEADER,), "write-task 表头", errors)

    if (ROOT / "skills/gmgn/references/en/writing-contract.md").exists():
        errors.append("旧 writing-contract.md 不应恢复")
    for relative in policy_files:
        text = read(relative)
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
        for obsolete in (
            "A closed foundation remains closed.",
            "Only explicit acceptance authorizes integrating",
            "rulings that constrain multiple Milestones and are not already",
            "Do not absorb WhitePaper meaning, ROADMAP allocation",
            "no current material cross-Milestone ruling",
        ):
            if obsolete in text:
                errors.append(f"{relative}: 含已废止规则 {obsolete}")


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
    triggers = verifier.get("triggers")
    if (
        not isinstance(triggers, list)
        or not triggers
        or len(triggers) != len(set(triggers))
        or any(
            not isinstance(trigger, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9-]*", trigger) is None
            for trigger in triggers
        )
    ):
        errors.append(f"{ASSURANCE_POLICY}: Verifier triggers 必须是唯一 kebab-case token")


def validate_run_task_controls(errors: list[str]) -> None:
    run_task = read(RUN_TASK)
    require_fragments(run_task, RUN_TASK_CONTROLS, "run-task 关键执行控制", errors)
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
