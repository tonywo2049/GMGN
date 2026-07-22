#!/usr/bin/env python3
"""Validate GMGN's small set of structural and workflow invariants."""

from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import release_metadata, validate_normative_layout


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
)
REVIEW_POLICY_FILES = (
    Path("GMGN.md"),
    Path("skills/gmgn/SKILL.md"),
    Path("skills/run-task/SKILL.md"),
    Path("skills/release/SKILL.md"),
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/en/code-review.md"),
    Path("agents/coder.md"),
    Path("agents/critic.md"),
    Path("agents/reviewer.md"),
    Path(".codex/agents/coder.toml"),
    Path(".codex/agents/critic.toml"),
    Path(".codex/agents/reviewer.toml"),
)
FORBIDDEN_SECOND_REVIEW_FRAGMENTS = (
    "a semantic recheck uses a fresh critic",
    "re-review only changed semantic scope",
    "a fresh replacement role checks only",
    "review only the changed implementation scope with a fresh reviewer",
    "later semantic/diff recheck uses a fresh agent",
    "any required recheck uses a fresh agent",
    "create a fresh reviewer for the affected diff",
    "accepted fixes use another fresh coder and only affected review roles",
    "dispatch another fresh reviewer",
    "后续复核新建 critic",
    "定向复核只在",
    "后续审查新建 reviewer",
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
    roadmap = read("skills/roadmap/SKILL.md")
    write_requirement = read("skills/write-requirement/SKILL.md")
    close_milestone = read("skills/close-milestone/SKILL.md")

    require(gmgn, (
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Prepare the full role brief before creation",
        "Collect all active findings before changing the candidate",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "Do not send the fixes to another Critic or Reviewer",
        "Record the reviewed anchor, findings and rulings, exact fix delta, and post-fix checks",
        "Do not dispatch a Verifier while accepted review blockers remain unresolved",
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
        "Each task execution uses `review_policy: single-pass`",
        "do not dispatch another Critic or Reviewer to recheck the fixes",
        "Reserve that shared baseline and integration position",
        "Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain",
        "itself the combination",
        "dispatch one fresh Verifier when executable evidence is required",
        "An additional pre-integration Verifier is allowed only",
        "Use one `list_agents` snapshot only",
        "No periodic list interval is configured or inferred",
    ), "run-task 执行与验证契约", errors)
    require(dispatch_en, (
        "One dispatch, one fresh agent",
        "Prepare the brief before creating the agent",
        "One return ends the agent",
        "collect every active return before editing",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "Do not send fixes from that round to another Critic or Reviewer",
        "The final anchor records the reviewed anchor",
        "one fresh Verifier on the final candidate when executable evidence is required",
        "Do not query again until a material lifecycle event",
        "There is no periodic list interval",
    ), "英文派发契约", errors)
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


def validate_normative_language_layout(errors: list[str]) -> None:
    try:
        validate_normative_layout(ROOT)
    except ValueError as exc:
        errors.append(str(exc))
    if not (ROOT / "README.zh-CN.md").is_file():
        errors.append("README.zh-CN.md 必须保留")


def validate_review_policy(errors: list[str]) -> None:
    for relative in REVIEW_POLICY_FILES:
        try:
            text = read(relative)
        except AssertionError as exc:
            errors.append(str(exc))
            continue
        require(text, ("review_policy: single-pass",), str(relative), errors)

    policy_surfaces = [ROOT / "GMGN.md"]
    policy_surfaces.extend((ROOT / "skills").rglob("*.md"))
    policy_surfaces.extend((ROOT / "agents").glob("*.md"))
    policy_surfaces.extend((ROOT / ".codex/agents").glob("*.toml"))
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in policy_surfaces if path.is_file()
    ).casefold()
    conflicts = [
        fragment for fragment in FORBIDDEN_SECOND_REVIEW_FRAGMENTS
        if fragment.casefold() in combined
    ]
    if conflicts:
        errors.append(f"单轮审查契约含二次复核指令: {conflicts}")


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
    validate_normative_language_layout(errors)
    validate_review_policy(errors)
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
