#!/usr/bin/env python3
"""Validate GMGN's small set of structural and workflow invariants."""

from pathlib import Path
import json
import re
import sys
import tomllib
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
ASSURANCE_POLICY_PATH = Path("skills/gmgn/references/en/assurance-policy.json")
GLOBAL_SCAN_CONTRACT = (
    "Before waiting or acting as a Coder",
    "scans every task in the confirmed execution set",
    "not only the current card or active lane",
    "dispatches every ready, non-conflicting task that fits currently available capacity",
)
ASSURANCE_BINDING_FILES = (
    Path("GMGN.md"),
    Path("skills/gmgn/SKILL.md"),
    Path("skills/run-task/SKILL.md"),
    Path("skills/close-milestone/SKILL.md"),
    Path("skills/release/SKILL.md"),
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/en/code-review.md"),
    Path("skills/gmgn/references/en/pre-merge-checklist.md"),
    Path("skills/gmgn/references/en/pre-close-checklist.md"),
    Path("skills/gmgn/references/en/writing-contract.md"),
    Path("agents/reviewer.md"),
    Path("agents/verifier.md"),
    Path(".codex/agents/reviewer.toml"),
    Path(".codex/agents/verifier.toml"),
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
    methodology = read("GMGN.md")
    gmgn = read(CORE_FILES[0])
    write_task = read(CORE_FILES[1])
    run_task = read(CORE_FILES[2])
    dispatch_en = read(CORE_FILES[3])
    roadmap = read("skills/roadmap/SKILL.md")
    write_requirement = read("skills/write-requirement/SKILL.md")
    close_milestone = read("skills/close-milestone/SKILL.md")
    release = read("skills/release/SKILL.md")
    pre_merge = read("skills/gmgn/references/en/pre-merge-checklist.md")

    for text, label in (
        (methodology, "GMGN 根规范全局调度契约"),
        (gmgn, "gmgn 路由全局调度契约"),
        (run_task, "run-task 全局调度契约"),
        (dispatch_en, "英文派发全局调度契约"),
    ):
        require(text, GLOBAL_SCAN_CONTRACT, label, errors)

    require(methodology, (
        "Completion does not require every non-critical issue to be perfected",
        "When the accepted main path works and an effective fallback keeps a remaining "
        "non-blocking issue within acceptable bounds, stop fixing that issue",
    ), "GMGN 有效兜底边界", errors)

    require(gmgn, (
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Prepare the full role brief before creation",
        "Collect all active findings before changing the candidate",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "Do not send the fixes to another Critic or Reviewer",
        "Record the reviewed anchor, findings and rulings, exact fix delta, and post-fix checks",
        "Do not dispatch a Verifier while accepted review blockers remain unresolved",
        "The Reviewer runs the prepared deterministic local checks",
        "A fresh Verifier is exceptional, not default",
        "After accepted fixes, the primary orchestrator checks the fix delta and reruns affected machine checks without another independent round",
        "must not send a progress update while observable state is unchanged",
        "`candidate_base_anchor..candidate_tip_anchor`",
        "never apply only the last correction commit",
        "A changed commit SHA alone does not invalidate evidence",
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
        "The Reviewer also runs the prepared deterministic local",
        "A fresh Verifier is exceptional, not default",
        "Classify the final candidate from the assurance policy",
        "An additional pre-integration Verifier is allowed only",
        "The transferable candidate is the complete\n`candidate_base_anchor..candidate_tip_anchor` diff",
        "Never apply only the last",
        "A changed commit SHA alone\ndoes not invalidate review or execution evidence",
        "Ignore Task\nstatus, descriptive Log content, and unrelated task rows",
        "An `execution` pointer change is",
        "The Verifier must leave every tracked file unchanged",
        "sends no heartbeat when state is unchanged",
        "Use one `list_agents` snapshot only",
        "No periodic list interval is configured or inferred",
        "Across the confirmed execution set, wait only after",
        "Do not keep a task open to perfect a non-blocking issue when its Card outcome works "
        "and an effective fallback keeps the remaining impact within accepted bounds",
    ), "run-task 执行与验证契约", errors)
    require(dispatch_en, (
        "One dispatch, one fresh agent",
        "Prepare the brief before creating the agent",
        "One return ends the agent",
        "collect every active return before editing",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "Do not send fixes from that round to another Critic or Reviewer",
        "The final anchor records the reviewed anchor",
        "The Reviewer runs the prepared deterministic local checks",
        "A fresh Verifier is exceptional, not default",
        "Classify the final candidate from the assurance policy",
        "`candidate_base_anchor..candidate_tip_anchor`",
        "a correction commit is not a standalone candidate",
        "leaves every tracked file unchanged",
        "sends no heartbeat when observable state is unchanged",
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
        "every ROADMAP acceptance scenario",
        "ROADMAP acceptance-scenario links to accepted evidence",
    ), "milestone 验收关账契约", errors)
    require(pre_merge, (
        "`not-required` or `required:<trigger>`",
        "Missing required evidence blocks integration",
        "blocker-resolved final combination",
        "`candidate_base_anchor..candidate_tip_anchor`",
        "Task status, descriptive Log content, and unrelated rows",
        "If the execution pointer changed",
        "leave tracked files unchanged on both pass and failure",
    ), "合并前双向验证门禁", errors)
    require(release, (
        "`required:final-artifact-or-installation`",
        "dispatch one fresh Verifier before external writes",
        "Missing or failed required Verifier evidence blocks publication",
    ), "发布制品独立验证门禁", errors)

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


def validate_assurance_policy(errors: list[str]) -> dict[str, object] | None:
    try:
        policy = json.loads(read(ASSURANCE_POLICY_PATH))
    except (AssertionError, json.JSONDecodeError) as exc:
        errors.append(f"{ASSURANCE_POLICY_PATH}: assurance policy 无效 ({exc})")
        return None
    if not isinstance(policy, dict):
        errors.append(f"{ASSURANCE_POLICY_PATH}: 顶层必须是对象")
        return None

    schema_version = policy.get("schema_version")
    policy_id = policy.get("policy_id")
    review = policy.get("review")
    reviewer = policy.get("reviewer")
    verifier = policy.get("verifier")
    if schema_version != "gmgn.assurance-policy.v1":
        errors.append(f"{ASSURANCE_POLICY_PATH}: schema_version 无效")
    if not isinstance(policy_id, str) or re.fullmatch(r"[a-z0-9][a-z0-9-]*", policy_id) is None:
        errors.append(f"{ASSURANCE_POLICY_PATH}: policy_id 无效")
    if not isinstance(review, dict) or (
        review.get("policy") != "single-pass"
        or review.get("rounds_per_change") != 1
        or review.get("post_fix_independent_recheck") is not False
        or review.get("post_fix_owner") != "primary-orchestrator"
        or review.get("post_fix_evidence") != "affected-machine-checks"
    ):
        errors.append(f"{ASSURANCE_POLICY_PATH}: 单轮审查与修复后证据策略无效")
    if not isinstance(reviewer, dict) or (
        reviewer.get("execution") != "deterministic-local"
        or reviewer.get("candidate_integrity") != "head-and-diff-unchanged"
    ):
        errors.append(f"{ASSURANCE_POLICY_PATH}: Reviewer 执行或候选完整性策略无效")
    if not isinstance(verifier, dict) or verifier.get("default") is not False:
        errors.append(f"{ASSURANCE_POLICY_PATH}: Verifier 必须是非默认角色")
    else:
        classification = verifier.get("classification")
        triggers = verifier.get("triggers")
        if verifier.get("candidate") != "blocker-resolved-final" or classification != {
            "not_required": "not-required", "required_prefix": "required:",
        }:
            errors.append(f"{ASSURANCE_POLICY_PATH}: Verifier 候选或分类策略无效")
        if (
            not isinstance(triggers, list)
            or not triggers
            or any(
                not isinstance(trigger, str)
                or re.fullmatch(r"[a-z0-9][a-z0-9-]*", trigger) is None
                for trigger in triggers
            )
            or len(triggers) != len(set(triggers))
        ):
            errors.append(f"{ASSURANCE_POLICY_PATH}: Verifier triggers 必须是唯一的 kebab-case token")
    return policy


def validate_review_policy(errors: list[str], policy: dict[str, object] | None) -> None:
    for relative in REVIEW_POLICY_FILES:
        try:
            text = read(relative)
        except AssertionError as exc:
            errors.append(str(exc))
            continue
        require(text, ("review_policy: single-pass",), str(relative), errors)
    if policy is None or not isinstance(policy.get("policy_id"), str):
        return
    policy_id = policy["policy_id"]
    for relative in ASSURANCE_BINDING_FILES:
        try:
            if relative.suffix == ".toml":
                config = tomllib.loads(read(relative))
                instructions = config.get("developer_instructions")
                if not isinstance(instructions, str) or (
                    f"assurance_policy: {policy_id}" not in instructions
                ):
                    errors.append(f"{relative}: assurance policy 绑定缺失或漂移")
            elif frontmatter(relative).get("assurance_policy") != policy_id:
                errors.append(f"{relative}: assurance policy 绑定缺失或漂移")
        except (AssertionError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{relative}: assurance policy 绑定不可读 ({exc})")


def validate_roles(errors: list[str]) -> None:
    for role in sorted(ROLES):
        markdown = Path("agents") / f"{role}.md"
        toml = Path(".codex/agents") / f"{role}.toml"
        try:
            text = read(markdown)
            fields = frontmatter(markdown)
            if fields.get("name") != role:
                errors.append(f"{markdown}: name 不一致")
            toml_text = read(toml)
            try:
                config = tomllib.loads(toml_text)
            except tomllib.TOMLDecodeError as exc:
                errors.append(f"{toml}: TOML 无效 ({exc})")
                continue
            required_types = {
                "name": str,
                "description": str,
                "sandbox_mode": str,
                "developer_instructions": str,
            }
            for key, expected_type in required_types.items():
                if not isinstance(config.get(key), expected_type):
                    errors.append(f"{toml}: {key} 必须是 {expected_type.__name__}")
            instructions = config.get("developer_instructions")
            if not isinstance(instructions, str):
                instructions = ""
            if config.get("sandbox_mode") not in {"read-only", "workspace-write"}:
                errors.append(f"{toml}: sandbox_mode 无效")
            require(text, ("prepared", "brief", "single return ends"), str(markdown), errors)
            require(instructions, ("brief", "唯一一次回传后结束"), str(toml), errors)
            if role == "reviewer":
                require(text, (
                    "deterministic local checks",
                    "exact commands, environment, exit codes",
                    "Any tracked change or anchor/hash drift invalidates the review",
                    "candidate_base_anchor",
                    "candidate_tip_anchor",
                ), str(markdown), errors)
                require(instructions, (
                    "确定性本地测试计划", "原样命令", "任何 tracked 变化或锚/哈希漂移均使本轮无效",
                    "candidate_base_anchor", "candidate_tip_anchor", "不得只审最后一个修订提交",
                ), str(toml), errors)
                if config.get("sandbox_mode") != "workspace-write":
                    errors.append(f"{toml}: Reviewer 运行本地检查需要 workspace-write")
            if role == "verifier":
                require(text, (
                    "required:<trigger>",
                    "Ordinary deterministic local checks belong to the Reviewer",
                    "Any tracked change invalidates verification on both pass and failure",
                ), str(markdown), errors)
                require(instructions, (
                    "required:<trigger>", "普通确定性本地检查归 Reviewer",
                    "成功或失败后的任何 tracked 变化都使验证无效",
                    "生成或刷新 oracle、evidence、attempt",
                ), str(toml), errors)
            if role == "coder":
                require(text, (
                    "candidate_base_anchor", "candidate_tip_anchor",
                    "correction commit\nis not standalone",
                ), str(markdown), errors)
                require(instructions, (
                    "candidate_base_anchor", "candidate_tip_anchor", "修订提交不可单独应用",
                ), str(toml), errors)
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
    policy = validate_assurance_policy(errors)
    validate_release(errors)
    validate_skills(errors)
    validate_core_contract(errors)
    validate_normative_language_layout(errors)
    validate_review_policy(errors, policy)
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
