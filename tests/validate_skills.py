#!/usr/bin/env python3
"""Validate GMGN's small set of structural and workflow invariants."""

from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import release_metadata


SKILLS = {
    "gmgn", "brainstorm", "roadmap", "write-goal", "write-requirement",
    "write-design", "write-task", "run-task", "close-milestone", "release",
}
ROLES = {"author", "coder", "critic", "reviewer", "verifier"}
TASK_HEADER = "| # | task | spec anchor | prerequisite | status | execution |"
OLD_TASK_HEADER = "| # | task | spec anchor | prerequisite | failing test | status |"
CORE_FILES = (
    Path("skills/gmgn/SKILL.md"),
    Path("skills/write-task/SKILL.md"),
    Path("skills/run-task/SKILL.md"),
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/zh-CN/dispatch-and-handoff.md"),
)


def read(relative: Path | str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"缺少文件: {relative}")
    return path.read_text(encoding="utf-8")


def frontmatter(path: Path) -> dict[str, str]:
    text = read(path)
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.S)
    if not match:
        raise AssertionError(f"{path}: frontmatter 缺失")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise AssertionError(f"{path}: frontmatter 行无冒号")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def require(text: str, fragments: tuple[str, ...], label: str, errors: list[str]) -> None:
    normalized = " ".join(text.split()).casefold()
    missing = [
        fragment for fragment in fragments
        if " ".join(fragment.split()).casefold() not in normalized
    ]
    if missing:
        errors.append(f"{label}: 缺少关键契约 {missing}")


def validate_release(errors: list[str]) -> None:
    try:
        release_metadata(ROOT)
    except ValueError as exc:
        errors.append(f"发布版本门禁失败: {exc}")


def validate_skills(errors: list[str]) -> None:
    actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if actual != SKILLS:
        errors.append(f"skill 集合不一致: expected={sorted(SKILLS)}, actual={sorted(actual)}")
    for name in sorted(SKILLS):
        relative = Path("skills") / name / "SKILL.md"
        try:
            fields = frontmatter(relative)
            if fields.get("name") != name:
                errors.append(f"{relative}: name 必须等于目录名 {name}")
            if not fields.get("description"):
                errors.append(f"{relative}: description 缺失")
            if len(read(relative).splitlines()) > 500:
                errors.append(f"{relative}: 超过 500 行，应拆引用或删重复规则")
            if not (ROOT / "skills" / name / "agents" / "openai.yaml").is_file():
                errors.append(f"skills/{name}/agents/openai.yaml: 缺失")
        except AssertionError as exc:
            errors.append(str(exc))


def validate_core_contract(errors: list[str]) -> None:
    gmgn = read(CORE_FILES[0])
    write_task = read(CORE_FILES[1])
    run_task = read(CORE_FILES[2])
    dispatch_en = read(CORE_FILES[3])
    dispatch_zh = read(CORE_FILES[4])
    roadmap = read("skills/roadmap/SKILL.md")
    write_requirement = read("skills/write-requirement/SKILL.md")
    close_milestone = read("skills/close-milestone/SKILL.md")

    require(gmgn, (
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Prepare the full role brief before creation",
        "Collect all active Critic and Reviewer findings before changing it",
        "Do not dispatch a Verifier while relevant review blockers remain",
        "execution/<card_id>/Card.md",
        "execution/<card_id>/Log.md",
        "A `list_agents` snapshot is allowed only",
        "There is no periodic list interval",
    ), "gmgn 路由契约", errors)
    require(write_task, (
        TASK_HEADER,
        "| AC | task |",
        "Do not put TDD cases",
        "The TDD contract belongs in `Card.md`, not Task",
        "`execution_log` link to its sibling `Log.md`",
        "latest_event",
        "minimize unnecessary task dependencies, shared writes, and runtime conflicts",
        "The objective is useful parallelism, not more task cards",
        "Never invent empty wrappers, fake interfaces, or new design decisions",
        "more coordination cost than isolation benefit",
    ), "write-task 紧凑索引契约", errors)
    require(run_task, (
        "`execution/<card_id>/Card.md` first",
        "`execution/<card_id>/Log.md` second",
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Collect every active review return before editing",
        "Do not dispatch an unchanged role",
        "Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain",
        "does not need another copy",
        "dispatch one fresh Verifier when executable evidence is required",
        "An additional pre-integration Verifier is allowed only",
        "Use one `list_agents` snapshot only",
        "No periodic list interval is configured or inferred",
    ), "run-task 执行与验证契约", errors)
    require(dispatch_en, (
        "One dispatch, one fresh agent",
        "Prepare the brief before creating the agent",
        "One return ends the agent",
        "Collect every active review return before editing",
        "one fresh Verifier on the final candidate when executable evidence is required",
        "Do not query again until a material lifecycle event",
        "There is no periodic list interval",
    ), "英文派发契约", errors)
    require(dispatch_zh, (
        "一次派发，一个全新 agent",
        "创建 agent 前准备完整 brief",
        "一次回传即结束",
        "才调用一次 `list_agents` 获取状态快照",
        "不存在定时查询周期",
    ), "中文派发契约", errors)
    require(roadmap, (
        "Milestone acceptance picture",
        "high-level end-to-end or integration scenarios",
        "must be independently decidable from work owned by that Milestone",
        "Do not prescribe a test framework",
        "Requirement refines scenarios into ACs",
    ), "roadmap 验收图景契约", errors)
    require(write_requirement, (
        "ROADMAP acceptance-scenario anchor",
        "ROADMAP acceptance scenario → Goal slice → R/AC",
        "without copying it as a second AC system",
    ), "requirement 验收追踪契约", errors)
    require(close_milestone, (
        "ROADMAP acceptance scenario → Goal slice → AC → task → test → evidence",
        "covers every ROADMAP acceptance scenario",
        "ROADMAP acceptance-scenario links to accepted evidence",
    ), "milestone 验收关账契约", errors)

    authority = "\n".join(read(path) for path in CORE_FILES)
    if OLD_TASK_HEADER in authority:
        errors.append("核心规则仍含旧 Task 表头")


def validate_roles(errors: list[str]) -> None:
    for role in sorted(ROLES):
        markdown = Path("agents") / f"{role}.md"
        toml = Path(".codex/agents") / f"{role}.toml"
        try:
            text = read(markdown)
            fields = frontmatter(markdown)
            if fields.get("name") != role:
                errors.append(f"{markdown}: name 不一致")
            require(text, ("prepared", "brief", "single return ends"), str(markdown), errors)
            require(read(toml), ("brief", "唯一一次回传后结束"), str(toml), errors)
            if len(text.splitlines()) > 80:
                errors.append(f"{markdown}: 角色契约超过 80 行")
        except AssertionError as exc:
            errors.append(str(exc))


def validate_docstar_adapter(errors: list[str]) -> None:
    relative = Path(".docstar/conventions/conventions.json")
    try:
        config = json.loads(read(relative))
    except (AssertionError, json.JSONDecodeError) as exc:
        errors.append(f"{relative}: JSON 无效或缺失 ({exc})")
        return
    expected_columns = {
        "spec": "spec anchor",
        "prereq": "prerequisite",
        "status": "status",
        "execution": "execution",
    }
    expected_execution = {
        "card_fields": {"execution_log": ["execution_log"]},
        "log_fields": {"latest_event": ["latest_event"]},
        "canonical_task_table_only": True,
    }
    if config.get("task_columns") != expected_columns:
        errors.append("DocStar task_columns 未采用新 Task 表头")
    if config.get("task_execution") != expected_execution:
        errors.append("DocStar task_execution 未采用 Task→Card→Log→latest_event")


def validate_relative_links(errors: list[str]) -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in {".git", "dist"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        visible_lines: list[str] = []
        fenced = False
        for line in text.splitlines():
            if re.match(r"^\s*(```|~~~)", line):
                fenced = not fenced
                continue
            if not fenced:
                visible_lines.append(re.sub(r"`[^`\n]*`", "", line))
        for target in link_pattern.findall("\n".join(visible_lines)):
            target = target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = unquote(target.split("#", 1)[0])
            if not file_part or "<" in file_part or ">" in file_part:
                continue
            resolved = (path.parent / file_part).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: 链接越出仓库 {target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: 链接目标不存在 {target}")


def main() -> int:
    errors: list[str] = []
    validate_release(errors)
    validate_skills(errors)
    validate_core_contract(errors)
    validate_roles(errors)
    validate_docstar_adapter(errors)
    validate_relative_links(errors)
    if errors:
        print("GMGN 校验失败:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("GMGN 轻量契约校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
