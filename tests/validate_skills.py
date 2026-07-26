#!/usr/bin/env python3
"""Validate GMGN's small set of structural and workflow invariants."""

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
AGENT_WAIT_CONTRACT = (
    "Every Codex `wait_agent` call uses `agent_wait_timeout_ms = 3600000` (1 hour)",
    "routine progress-update cadence never shortens it",
    "A timeout has no workflow meaning",
    "immediately re-arm the same one-hour wait",
    "A timeout alone is not a `list_agents` trigger",
    "one `list_agents` snapshot only when a real scheduling/capacity decision cannot be made "
    "from received lifecycle events or those events conflict",
    "must not interrupt, terminate, or kill an agent merely because it has not returned content",
    "only on explicit user cancellation or concrete evidence",
    "do not report a wait timeout, silence, absence of content, agent count, or `running` status",
)
PONYTAIL_CONTRACT_FILES = (
    Path("GMGN.md"),
    Path("skills/gmgn/SKILL.md"),
    Path("skills/run-task/SKILL.md"),
    Path("skills/gmgn/references/en/code-review.md"),
    Path("agents/coder.md"),
    Path("agents/reviewer.md"),
    Path(".codex/agents/coder.toml"),
    Path(".codex/agents/reviewer.toml"),
)
PONYTAIL_REVERSE_CONTRACT = (
    "If Ponytail is unavailable, continue and accept the candidate",
    "Ponytail 不可用时仍继续并接受候选",
)
GIT_ANCHOR_FILES = (
    Path("GMGN.md"),
    Path("README.md"),
    Path("README.zh-CN.md"),
    Path("skills/brainstorm/SKILL.md"),
    Path("skills/roadmap/SKILL.md"),
    Path("skills/write-goal/SKILL.md"),
    Path("skills/write-requirement/SKILL.md"),
    Path("skills/write-design/SKILL.md"),
    Path("skills/write-task/SKILL.md"),
    Path("skills/gmgn/SKILL.md"),
    Path("skills/run-task/SKILL.md"),
    Path("skills/close-milestone/SKILL.md"),
    Path("skills/release/SKILL.md"),
    Path("skills/gmgn/references/en/writing-contract.md"),
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
    Path("skills/gmgn/references/en/code-review.md"),
    Path("agents/author.md"),
    Path("agents/coder.md"),
    Path("agents/critic.md"),
    Path("agents/reviewer.md"),
    Path("agents/verifier.md"),
    Path(".codex/agents/author.toml"),
    Path(".codex/agents/coder.toml"),
    Path(".codex/agents/critic.toml"),
    Path(".codex/agents/reviewer.toml"),
    Path(".codex/agents/verifier.toml"),
)
LEGACY_HASH_ANCHOR_RULES = (
    "a diff or content hash for a sole writer",
    "a sole writer may use a captured diff or content hash",
    "frozen diff/content hash for a sole writer",
    "freeze a diff/content hash",
    "return the frozen diff/content hash",
    "a sole writer freezes a diff/content hash",
    "single writer freezes a diff/content hash",
    "单 writer 回传冻结 diff/内容哈希",
    "单 writer 冻结 diff/内容哈希",
    "bind owner approval to a commit or hash",
    "immutable commit, content hash, or equivalent version anchor",
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


def forbid(text: str, fragments: tuple[str, ...], label: str, errors: list[str]) -> None:
    normalized = " ".join(text.split()).casefold()
    present = [
        fragment for fragment in fragments
        if " ".join(fragment.split()).casefold() in normalized
    ]
    if present:
        errors.append(f"{label}: 含相反契约 {present}")


def forbid_stage_owned_workflow(text: str, label: str, errors: list[str]) -> None:
    direct_targets = [
        marker
        for skill in sorted(SKILLS - {"gmgn"})
        for marker in (f"`{skill}`", f"${skill}")
        if marker.casefold() in text.casefold()
    ]
    planned_map = re.search(
        r"(?is)(?<!not )\b(?:include|create|add|maintain|record|require)\b"
        r".{0,80}\b(?:map|index|catalog|inventory)\b"
        r".{0,100}\b(?:planned|future|downstream|absent|missing|not yet)\b"
        r"|(?<!not )\b(?:include|create|add|maintain|record|require)\b"
        r".{0,80}\b(?:planned|future|downstream|absent|missing|not yet)\b"
        r".{0,80}\b(?:map|index|catalog|inventory)\b",
        text,
    )
    present = direct_targets
    if planned_map:
        present.append(planned_map.group(0))
    if present:
        errors.append(f"{label}: 含相反契约 {present}")


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
            extra_fields = sorted(set(fields) - {"name", "description"})
            if extra_fields:
                errors.append(f"{relative}: frontmatter 只允许 name 和 description，实际多出 {extra_fields}")
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
    writing_en = read("skills/gmgn/references/en/writing-contract.md")
    roadmap = read("skills/roadmap/SKILL.md")
    roadmap_agent = read("skills/roadmap/agents/openai.yaml")
    readme_zh = read("README.zh-CN.md")
    write_goal = read("skills/write-goal/SKILL.md")
    write_requirement = read("skills/write-requirement/SKILL.md")
    write_design = read("skills/write-design/SKILL.md")
    close_milestone = read("skills/close-milestone/SKILL.md")
    release = read("skills/release/SKILL.md")
    critic_role = read("agents/critic.md")
    codex_critic_role = read(".codex/agents/critic.toml")

    for text, label in (
        (methodology, "GMGN 根规范全局调度契约"),
        (gmgn, "gmgn 路由全局调度契约"),
        (run_task, "run-task 全局调度契约"),
    ):
        require(text, GLOBAL_SCAN_CONTRACT, label, errors)

    for text, label in (
        (methodology, "GMGN 根规范 Agent 等待契约"),
        (gmgn, "gmgn 路由 Agent 等待契约"),
        (run_task, "run-task Agent 等待契约"),
    ):
        require(text, AGENT_WAIT_CONTRACT, label, errors)

    archive_reverse = (
        "Archive documents may be used as authority, context, or evidence",
    )
    require(methodology, (
        "Documents under a project-declared archive root are historical storage, not active authority",
        "Writers, Critics, Reviewers, and Verifiers do not read, cite, or use them as context or\n"
        "evidence",
        "Exclude archive roots from briefs and generated context",
        "restore it to the active tree through its owning authority before use",
    ), "GMGN archive 上下文边界", errors)
    require(gmgn, (
        "Before direct or delegated writing, Critic, Reviewer, or Verifier work",
        "exclude every\nproject-declared archive root from reads, briefs, generated context, authority, and evidence",
        "Never cite archived documents",
        "Restore needed meaning to the active tree through its owning\nauthority before use",
    ), "gmgn archive 上下文边界", errors)
    require(writing_en, (
        "Documents under a project-declared archive root are historical storage only",
        "Writers do not\nread, cite, or use them as authority, context, or evidence",
        "Restore needed meaning to the\nactive tree through its owning authority before use",
    ), "写作 archive 上下文边界", errors)
    require(dispatch_en, (
        "Every Author, Critic, Reviewer, and Verifier brief names project-declared archive roots as\n"
        "excluded paths",
        "Generated context and indexes must honor that exclusion",
        "These roles do not\nread, cite, or use archived documents as authority, context, or evidence",
        "return it to the owning active authority before continuing",
    ), "派发 archive 上下文边界", errors)
    for text, label in (
        (methodology, "GMGN archive 上下文边界"),
        (gmgn, "gmgn archive 上下文边界"),
        (writing_en, "写作 archive 上下文边界"),
        (dispatch_en, "派发 archive 上下文边界"),
    ):
        forbid(text, archive_reverse, label, errors)

    require(methodology, (
        "Completion does not require every non-critical issue to be perfected",
        "When the accepted main path works and an effective fallback keeps a remaining "
        "non-blocking issue within acceptable bounds, stop fixing that issue",
        "The Critic/Reviewer rows above are evaluated only once",
        "An accepted finding fix remains part of that reviewed batch and does not\n"
        "re-enter role selection",
        "bounded\nresolution check does not search for new findings",
        "A fix that only aligns a duplicate\nrepresentation with an existing unambiguous authority",
        "Solution minimality is an acceptance condition for every stage document",
        "A retained item must\nchange that document's own result if removed",
        "Anything removable without weakening the document's purpose is overdesign",
        "Every run-task Coder brief requires `ponytail:ponytail` at `full`",
        "A run-task Reviewer brief\nrequires `ponytail:ponytail-review` when its candidate contains implementation or test-code\nchanges",
        "explicit deliverables",
        "A deliverable is a final object",
        "a real\n  product/operational E2E is a deliverable only when the realized path itself is the Milestone\n  result",
        "A Milestone without such a deliverable has no E2E content",
        "When present, keep only the shortest stable core path",
        "Derive deliverables from the\n  WhitePaper and Milestone outcome",
        "name the resulting object rather\n  than its acceptance quality",
        "replace planning names\n  with canonical artifact pointers at closure",
        "Possible future work not yet\n  allocated to a Milestone belongs in the Backlog",
        "Goal refines one initiated Milestone for exactly two purposes",
        "provide the basis for\n  Requirement and define qualitative Milestone Close criteria",
        "Requirement translates Goal into required observable behavior, quantified parameters",
        "Stage documents do not\ncontain document maps without real children, downstream propagation rules, downstream gates",
        "The GMGN router owns cross-stage routing and impact propagation",
        "`Design.md` is the root Design authority and complete R/AC mapping entry",
        "Add architecture,\n  module boundaries, and `design/<module-id>.md` only when current R/ACs need them",
        "Add a\n  Bundle index only when linked child artifacts exist",
        "If two non-communicating Coders could produce incompatible conforming\n  implementations",
        "consumer validation entries, success/errors, and state effects",
        "each Task row names one independently decidable result",
        "All Coder lanes use the same current approved Design Bundle commit",
        "Milestone's final frozen contract",
    ), "GMGN 有效兜底边界", errors)

    require(gmgn, (
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Prepare the full role brief before creation",
        "Collect all active findings before changing the candidate",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "A fix is mechanical only when it\naligns a duplicate representation",
        "The Critic/Reviewer rows above are evaluated only once",
        "An accepted finding fix remains part of that reviewed batch and does not\n"
        "re-enter role selection",
        "bounded resolution check does not search for new findings",
        "Do not dispatch a Verifier while accepted review blockers remain unresolved",
        "The Reviewer runs the prepared deterministic local checks",
        "A fresh Verifier is exceptional, not default",
        "After accepted fixes, the primary orchestrator checks the fix delta and reruns affected machine checks without another independent round",
        "must not send a progress update while observable state is unchanged",
        "Critic and Reviewer do not maximize finding count",
        "a valid review may return no findings",
        "concrete material harm",
        "accepted effective fallback",
        "Compliance checks run only at a real boundary or material state change",
        "Discovery does not expand an active Card",
        "Close the task as soon as the Card outcome",
        "execution/<card_id>/Card.md",
        "execution/<card_id>/Log.md",
        "ROADMAP sequencing, Milestone allocation, deliverable, dependency, concise acceptance summary, optional core E2E, or Backlog placement",
        "Goal result, boundary, non-goal, result slice, qualitative Close outcome, or ROADMAP deliverable/core-E2E mapping",
        "Requirement behavior, quantified parameter, constraint, or decidable AC",
        "Design structure, implementation-specific parameter or decision, cross-task interface contract, data, or failure path",
        "Every stage writer keeps only content required for that document's own purpose",
        "Stage documents do not contain downstream\npropagation rules, downstream gates, next-stage instructions",
        "Cross-stage routing and impact propagation belong here\nin the GMGN router",
        "Their fresh Critic attempts deletion,\nreuse, native behavior, or a direct solution",
        "Every run-task Coder brief\nrequires `ponytail:ponytail` at `full`",
        "A run-task Reviewer brief requires\n`ponytail:ponytail-review` when its candidate contains implementation or test-code changes",
        "Missing Ponytail blocks that code task",
        "requires\n`design/Contract.md`",
        "same current approved Design Bundle commit",
        "evidence, smallest proposed delta, and affected tasks",
        "`close-milestone` freezes the implementation-matching\nContract as `closed`",
    ), "gmgn 路由契约", errors)
    require(write_task, (
        TASK_HEADER,
        "Derive Task only from the reviewed Requirement, Design, and applicable Contract",
        "changing upstream meaning or making a missing design decision",
        "return the issue to `gmgn` for routing",
        "Keep `Task.md` as a compact Milestone execution index",
        "which independently decidable results must be delivered",
        "which AC, Design, and applicable Contract anchors authorize each result",
        "Keep the parser-facing task header unchanged. Use stable task IDs and the "
        "task-state tokens\n  defined by the writing contract",
        "Replace current status and execution values; never append\n  execution history",
        "one primary result that can be independently judged complete or failed",
        "Split by result and verification boundary, not by file, interface, implementation step",
        "only when\n  each result is independently decidable",
        "Keep only task boundaries supported by the current approved Design",
        "Only when research or\n  selection is itself the current Milestone result",
        "return a missing decision to `gmgn` for routing\n"
        "  before defining implementation tasks",
        "Never create tentative, placeholder, or speculative task sets",
        "- Every in-scope AC must map to at least one task",
        "A task may cover several related ACs and\n  one AC may require several tasks",
        "the Design is\n  not ready for Task planning",
        "`prerequisite` contains only real data, interface, or decision dependencies and must form\n"
        "  an acyclic DAG",
        "Sharing an approved Contract does not by itself create a dependency",
        "Do not\n  freeze execution waves",
        "- Do not copy Requirement, Design, or Contract meaning into Task. Do not put TDD cases,\n"
        "  commands, file scopes, runtime locks, blockers, commits, candidates, review records,\n"
        "  evidence, or progress narratives in `Task.md`",
        "The `execution` column stores only the current execution entry link when one exists",
        "Do not\ncopy execution content or history into `Task.md`",
        "do not require the execution ID to equal\nthe Task ID",
        "Apply the deletion test to every task",
        "Remove a task when deleting its result leaves every\n"
        "  current AC and approved Design result satisfied",
        "Future reuse, possible hardening, and\n  coordination convenience are not task owners",
        "Critic must try deleting or merging each affected task",
    ), "write-task 紧凑索引契约", errors)
    forbid(write_task, (
        "Task may redefine upstream meaning",
        "Do not use stable task IDs or task-state tokens",
        "Not every in-scope AC must map to at least one task",
        "but put commands and file scopes",
        "Allow tentative, placeholder, or speculative task sets",
        "Allow in-scope ACs to remain unmapped",
        "Freeze execution waves in Task",
        "Task.md records execution content or history",
        "execution ID must equal the Task ID",
    ), "write-task 紧凑索引契约", errors)
    require(run_task, (
        "`execution/<card_id>/Card.md` first",
        "`execution/<card_id>/Log.md` second",
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Collect every active review return before editing",
        "Each task execution uses `review_policy: single-pass`",
        "The Critic/Reviewer rows above are evaluated only once",
        "does not re-enter role selection",
        "bounded resolution\ncheck does not search for new findings",
        "existing unambiguous authority",
        "Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain",
        "The Reviewer also runs the prepared deterministic local",
        "A fresh Verifier is exceptional, not default",
        "Classify the\nfinal candidate as `not-required` or `required:<trigger>`",
        "registered skills or available tools required for the task",
        "load them through normal discovery",
        "instead of passing\nanother Skill's internal resource path",
        "An additional pre-integration Verifier is allowed only",
        "Compliance checks are triggered by a real boundary or material state change",
        "Discovery does not expand an active Card",
        "complete original-base-to-candidate commit range",
        "never apply only\nits last correction commit",
        "A sole-writer candidate needs no temporary copy",
        "different integration commit is acceptable only when the reviewed source",
        "Critic and Reviewer do not maximize finding count",
        "a valid review may return no findings",
        "does not broaden the verification plan after the recorded\nrisk is decided",
        "A failed, skipped,\ntimed-out, or unavailable required command is not a pass",
        "The Verifier must leave every tracked file unchanged",
        "Use one `list_agents` snapshot only",
        "No periodic list interval is configured or inferred",
        "Across the confirmed execution set, wait only after",
        "Do not keep a task open to perfect a non-blocking issue when its Card outcome works "
        "and an effective fallback keeps the remaining impact within accepted bounds",
        "A task is complete when its Card contract is satisfied",
        "run `codegraph init <workspace>`\nonce before source discovery",
        "CodeGraph indexing is\nauthorized",
        "Do not share an index between workspaces",
        "target the exact assigned workspace in every query",
        "treat returned source as already read",
        "index is absent, stale, unsupported, changed after the query, or\ninsufficient",
        "Routine dispatch, waiting, unchanged status, and successful\nintermediate checks are not Log entries",
        "`latest_event: [Current](#current)` while active",
        "`[Final Evidence](#final-evidence)` when closed",
        "does not require generated event IDs",
        "write one final evidence summary in `Log.md`",
        "Every Coder brief must require the registered `ponytail:ponytail` Skill at `full`",
        "A Reviewer\nbrief must require `ponytail:ponytail-review` when its candidate contains implementation or\ntest-code changes",
        "A missing\nrequired Skill is a dependency blocker for that code task",
        "loads `ponytail:ponytail` through normal discovery at `full`",
        "Reviewer loads `ponytail:ponytail-review` through normal discovery",
        "code minimality is an explicit acceptance condition",
        "one contract blocker containing only the observed\nevidence, the smallest proposed semantic delta, and affected tasks",
        "do not create a separate change-request document",
        "meaning-preserving clarification",
        "Do not mark the working Contract `closed` during run-task",
    ), "run-task 执行与验证契约", errors)
    require(dispatch_en, (
        "One dispatch, one fresh agent",
        "Prepare the brief before creating the agent",
        "One return ends the agent",
        "collect every active return before editing",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "existing unambiguous authority",
        "The final accepted commit records the reviewed commit",
        "registered skills or available tools required for the task",
        "load them through normal discovery",
        "instead of passing\nanother Skill's internal resource path",
        "use the shared [code-review contract](code-review.md)",
        "Compliance checks are triggered by a real boundary or material state change",
        "Commit the complete candidate locally before review",
        "shortest unambiguous commit reference",
        "a correction commit is not a standalone candidate",
        "valid review may return\nno findings",
        "concrete material harm",
        "smallest sufficient correction",
        "The stage Skill and role definition own role-specific content",
    ), "英文派发契约", errors)
    require(roadmap, (
        "explicit **Milestone\n  deliverables**",
        "Link only the WhitePaper boundary and invariant anchors needed for sequencing",
        "do not\n  restate their text",
        "one concise qualitative acceptance summary",
        "later artifacts or evidence cannot silently redefine it",
        "Name what will exist at the end, not how well it must perform",
        "realized product/operational E2E when that\n  path itself is the final result",
        "The acceptance summary states what counts as the stage\n  result without expanding every close condition",
        "Keep evidence out of planning rows; closure\n  backfill links the accepted result",
        "Write a core E2E only when the realized product or operational path is itself a Milestone\n"
        "  deliverable",
        "Otherwise omit E2E content; never invent one",
        "When applicable, write the core E2E under a stable Markdown anchor as the shortest complete\n"
        "  path from its start through key actions to an observable result",
        "list\n  that artifact once instead of repeating its contained paths as deliverables",
        "point an internal-code deliverable to its\n  repository when known",
        "number deliverables\n  consecutively and put one item on each line",
        "Do not prescribe a test framework",
        "Maintain one Backlog for possible future work that is not yet allocated to a Milestone",
        "New ideas remain in the Backlog until allocated to a Milestone",
        "`repository@<accepted-commit>`",
        "release\n  tag and release page",
        "a network or environment uses its applicable stable identity and\n  access pointers",
        "Omit pointers that do not\n  apply",
        "When a core E2E anchor exists, link it to accepted evidence",
        "document, report, or tool links directly to the accepted artifact",
        "a core E2E appears only\nwhen that path is itself a deliverable",
        "no E2E is fabricated for other Milestones",
    ), "roadmap 产出与可选 E2E 契约", errors)
    require(roadmap_agent, (
        "Sequence Milestones, outputs, dependencies, and Backlog",
        "编排里程碑、产出、依赖与 Backlog",
    ), "roadmap 界面元数据契约", errors)
    require(readme_zh, (
        "只有当实际产品或运营路径\n本身就是产出物时，才写核心 E2E；否则省略",
        "Goal 把当前 Milestone 细化为\nRequirement 依据和定性 Close 标准",
        "产出物、简短验收摘要及按需核心 E2E",
        "适用的回归/E2E 证据",
    ), "中文 README Roadmap 契约", errors)
    forbid(readme_zh, (
        "每个 Milestone 至少一个端到端验收场景",
    ), "中文 README Roadmap 契约", errors)
    forbid(roadmap, (
        "Every Milestone must invent E2E content",
        "later artifacts or evidence may redefine it",
        "New ideas bypass the Backlog",
        "## Handoff",
        "explicit deliverables, priority",
    ), "roadmap 产出与可选 E2E 契约", errors)
    forbid(methodology, (
        "ROADMAP owns Milestone order, priority",
    ), "GMGN Roadmap 最小权威契约", errors)
    require(write_goal, (
        "Derive Goal only from the approved ROADMAP Milestone and its WhitePaper authority",
        "Later documents, implementation, or evidence may expose a needed revision but cannot\n"
        "  silently redefine Goal",
        "Include only content that either gives Requirement a necessary basis or decides whether the\n"
        "  Milestone can Close",
        "Delete anything that serves neither purpose",
        "independently meaningful result slices, not teams, components, files, or work steps",
        "Cover every ROADMAP deliverable with one or more result slices and a qualitative observable\n"
        "  Close outcome",
        "Every slice must contribute to a deliverable or Close outcome",
        "When ROADMAP has a core E2E anchor, carry it into the applicable slices",
        "A\n  Milestone without a ROADMAP core E2E has no E2E content",
        "Resolve every Goal-owned ambiguity into the result, boundary, slices, or Close outcomes",
        "Keep exact numeric criteria, technical design, task division,\n  execution, and evidence out of Goal",
        "Do not include a document map, known gaps, downstream propagation or gates, next-stage\n"
        "  instructions",
        "Return WhitePaper- or ROADMAP-owned changes to `gmgn` for routing",
        "Goal-owned results, boundaries, non-goals, result slices, ROADMAP\n"
        "   deliverable/core-E2E mappings, or qualitative Close outcomes",
        "the refined result, boundary, and non-goals are complete",
        "every ROADMAP deliverable maps to slices and qualitative Close outcomes, every optional core\n"
        "  E2E maps when present",
        "deleting any retained item would remove necessary Requirement input or change the Close\n"
        "  decision",
        "no document map, downstream rule, component, interface, exact criterion, test, task",
        "an invalid mapping returns to `gmgn` for routing instead of changing upstream meaning in\n"
        "  Goal",
    ), "write-goal 内容边界契约", errors)
    forbid(write_goal, (
        "may redefine Goal",
        "may silently redefine Goal",
        "Split slices by team, component, or file",
        "Redefine ROADMAP deliverables inside Goal",
        "Some ROADMAP deliverables need no slice",
        "Ignore an existing ROADMAP core E2E",
        "Goal includes exact numeric criteria",
        "Push every Goal-owned ambiguity to Requirement",
        "Include unrelated content in Goal",
        "Keep content that serves neither purpose",
        "Include the document map and known gaps",
        "Mention absent downstream files as gaps",
        "Creation then uses **REQUIRED next skill",
        "Propagate only to affected Requirement",
        "quantified pass/fail criterion",
        "include downstream propagation requirements",
    ), "write-goal 内容边界契约", errors)
    require(write_requirement, (
        "Derive Requirement only from the approved Goal and explicitly sourced external constraints",
        "Later documents, implementation, tests, or evidence may expose a needed revision but cannot\n"
        "  silently define or redefine Requirement",
        "smallest necessary set of numbered requirements\n  `R1`, `R2`, ...",
        "Each R states one coherent required behavior, capability, or constraint\n"
        "  and names its owning Goal result or external constraint",
        "enough observable precondition, action or\n"
        "  inspection, and result to determine pass or fail",
        "Given/When/Then is optional syntax, not a\n  mandatory format",
        "Numeric and static constraints may state their decision rule directly",
        "Use unambiguous observable language",
        "Keep the explicit trace: Goal result or Close outcome → R/AC",
        "No in-scope Goal result or\n  Close outcome may disappear",
        "Preserve upstream-approved invariants and values without silent weakening",
        "Requirement may\n  define quantified parameters it owns",
        "name each value's authority, change boundary, and\n  verification method",
        "only when applicable; do not require fixed sections for absent categories",
        "Resolve every\n  Requirement-owned decision before acceptance",
        "Do not invent or prescribe components, modules, interfaces, process structure",
        "task division, execution order, test commands,\n"
        "  runtime results, evidence IDs, live status, or closure history",
        "Delete any R/AC whose removal would not cause a current Goal outcome or externally imposed\n"
        "  invariant to fail",
        "Future possibility, speculative reuse or scale, configurability, and\n"
        "  implementation convenience are not owners",
        "every in-scope Goal result and Close outcome is covered",
        "every AC has a clear pass/fail decision",
        "every Requirement-owned decision is resolved",
        "no\ntechnical solution, task, execution information, or actual verification result has leaked\n"
        "into Requirement",
    ), "write-requirement 内容边界契约", errors)
    forbid(write_requirement, (
        "can silently define or redefine Requirement",
        "Given/When/Then is mandatory syntax",
        "Every quantified parameter must come from Goal",
        "Requirement cannot define quantified parameters",
        "Requirement owns components, modules, or interfaces",
        "Future possibility and implementation convenience are owners",
        "Defer every Requirement-owned decision to Design",
        "Some Goal results or Close outcomes may disappear",
        "Allow R/AC to be unowned",
        "Propagate only to affected Design",
        "Creation then uses **REQUIRED next skill",
        "every current Goal result is covered or explicitly excluded",
    ), "write-requirement 内容边界契约", errors)
    require(write_design, (
        "`Design.md` always exists as the root Design authority and complete R/AC mapping entry",
        "Add\narchitecture and module boundaries only when current R/ACs need them",
        "add a Bundle index\nonly when linked child artifacts exist",
        "`design/Contract.md` is required only when current work crosses an independently developed",
        "Do not create an empty file or directory",
        "Every child links to `Design.md`",
        "Design acceptance marks that complete Bundle `approved`",
        "If the approved\nBundle permits incompatible implementations of a shared boundary",
        "not required headings or a document template",
        "Map each R/AC once in root `Design.md`",
        "Future reuse, possible scale, flexibility, or implementation\n"
        "convenience is not an owner",
        "Every applicable cross-unit boundary must close the whole path",
        "Naming a validator without binding every required entry point does not close the boundary",
        "one machine-readable or compilable authority",
        "Markdown\nexplains semantics and does not copy the complete signature",
        "it does not\nimplement production I/O, storage, or providers",
        "Keep the Bundle `draft` while any implementation-significant decision remains unresolved",
        "Do not\ninclude commands, full results, candidate chronology, work status, execution history, or\n"
        "closure records",
        "No implementation-significant question, hidden default, or unapproved parameter remains",
        "Run one Critic round after\nthat integration",
        "physical file\ncount never determines the number of Critics",
        "Critics find any implementation-significant decision still unspecified",
        "global-versus-local rule conflicts",
        "If the fix must invent or change Design-owned meaning, it is a new semantic\nbatch",
        "Adding or changing a public type or Port",
        "Design acceptance marks the complete Bundle `approved`, not `closed`",
    ), "design 最简方案契约", errors)
    forbid(write_design, (
        "Design may silently redefine Requirement",
        "Every Design must follow a fixed research funnel",
        "Every Design must use the same test sequence",
        "Design may change Requirement-owned acceptance values",
        "Task may change authoritative parameters from trial results",
        "Allow unresolved implementation-significant decisions in approved Design",
        "Keep commands, full results, candidate chronology, work status, execution history, and closure records in Design",
        "Map R/AC only to broad sections",
        "Always create Contract.md",
        "Always add architecture and module boundaries",
        "Always add a Bundle index",
        "Every module must have a separate design document",
        "Every interface must have a schema",
        "Future reuse, possible scale, flexibility, and implementation convenience are owners",
        "Every Design must define concurrency, recovery, migration, and performance sections",
    ), "design 最简方案契约", errors)
    for stage_text, stage_label in (
        (roadmap, "roadmap"),
        (write_goal, "write-goal"),
        (write_requirement, "write-requirement"),
        (write_design, "write-design"),
        (write_task, "write-task"),
    ):
        forbid(stage_text, (
            "REQUIRED next skill",
            "Propagate only to affected",
            "Propagate the approved delta only to affected",
        ), f"{stage_label} 文档自治契约", errors)
        forbid_stage_owned_workflow(
            stage_text, f"{stage_label} 文档自治契约", errors,
        )
    require(close_milestone, (
        "every ROADMAP deliverable, Goal Close outcome, in-scope AC, and optional ROADMAP core E2E must map to evidence",
        "A Milestone without a ROADMAP core E2E does not need E2E evidence",
        "ROADMAP deliverable → Goal Close outcome and slice → AC → task → test → evidence",
        "same trace for each optional ROADMAP core E2E",
        "every ROADMAP deliverable against its accepted result and required canonical pointer",
        "ROADMAP deliverable pointers and, when present, core-E2E links to accepted\n  evidence",
        "closed `Log.md` current snapshot and final evidence",
        "every retained Contract ID against its provider implementation",
        "Closure cannot silently rewrite the contract to match code",
        "reconciled implementation-matching Contract marked `closed`",
        "commit the blocker-resolved final\nclosure candidate",
        "Owner acceptance binds to that exact commit",
        "Integrate that exact commit without creating post-acceptance closure content",
    ), "milestone 验收关账契约", errors)
    forbid(close_milestone, (
        "Every Milestone needs E2E evidence",
    ), "milestone 验收关账契约", errors)
    require(writing_en, (
        "design | contract | task",
        "`approved` means the current shared working baseline",
        "Design module: `design/<module-id>.md`",
        "Cross-unit catalog: `design/Contract.md`",
        "Structural authority: `design/schemas/<schema-or-compilable-interface>`",
        "Every child under `design/` links back to it",
        "The stage Skills own Design completeness",
        "Content, not a template",
    ), "英文 Design/Contract 写作契约", errors)
    require(critic_role, (
        "ask what a later Coder must still decide",
        "two conforming but incompatible implementations",
        "closed producer-to-validation-to-state path",
        "delete `design/Contract.md`",
        "when one exists, the catalog is required",
        "global\nand local ordering or error rules",
    ), "Critic Contract 强制边界", errors)
    require(codex_critic_role, (
        "后续 Coder 还需要决定什么",
        "两个实现可能都声称符合却不兼容",
        "闭合权威生产者、派生、所有必需校验入口、错误与状态效果",
        "不存在这种边界时删除 design/Contract.md",
        "存在时必须保留契约目录",
    ), "Codex Critic Contract 强制边界", errors)
    require(run_task, (
        "`not-required` or `required:<trigger>`",
        "Before review, a sole writer commits the complete candidate locally",
        "shortest unambiguous commit reference",
        "integrated content still matches the reviewed candidate",
        "does not make a check pass by removing a required\n"
        "test, weakening an assertion, swallowing an error, or bypassing the real production path",
        "Card.md` unchanged as the stable contract",
        "`ponytail:ponytail-review`",
    ), "合并前双向验证门禁", errors)
    require(release, (
        "deterministic archive whose\nmembers and bytes are fully checked",
        "`artifact-not-fully-machine-checkable`",
        "`installation-or-startup`",
        "build the artifact once",
        "read the final remote state back once",
        "Missing or failed required Verifier evidence blocks publication",
    ), "发布制品独立验证门禁", errors)
    require(methodology, (
        "every review, approval, acceptance, Milestone closure, and release binds to a Git commit or release tag",
        "Commit the candidate locally before independent review",
        "shortest unambiguous commit reference or the tag",
        "never use a\nfull-length commit object ID, diff hash, content hash, archive checksum, or artifact checksum\nas a workflow anchor",
        "Checksums are evidence only",
    ), "GMGN Git 锚点硬门禁", errors)
    require(writing_en, (
        "<HARD-GATE>In a Git-backed GMGN project",
        "every review, approval, acceptance, Milestone\nclosure, and release anchor is a Git commit or release tag",
        "Commit the candidate locally\nbefore independent review",
        "shortest unambiguous commit reference or the tag",
        "Checksums are evidence only",
    ), "英文写作契约 Git 锚点硬门禁", errors)
    require(gmgn, (
        "Commit\nthe complete candidate locally before review",
        "shortest unambiguous\ncommit reference",
        "Full-length commit object IDs, diff/content\nhashes, and checksums are not workflow anchors",
    ), "gmgn 路由 Git 锚点门禁", errors)
    require(run_task, (
        "Before review, a sole writer commits the complete candidate locally",
        "shortest\nunambiguous commit reference",
        "Full-length commit object IDs, diff/content hashes, and\nchecksums are not workflow anchors",
    ), "run-task Git 锚点门禁", errors)
    require(dispatch_en, (
        "Never put a full-length commit object ID, diff hash, content hash, archive checksum, or artifact\nchecksum in the brief or return as a workflow anchor",
        "use an isolated worktree",
    ), "派发 Git 锚点门禁", errors)
    require(release, (
        "Require an accepted Git commit",
        "shortest unambiguous commit reference before tagging and the release tag after\ntagging",
        "checksum is never a workflow anchor; checksums are evidence only",
    ), "发布 Git 锚点门禁", errors)
    require(read("README.md"), (
        "complete candidate is committed locally",
        "shortest unambiguous commit reference",
        "cannot be workflow anchors",
    ), "README Git 锚点门禁", errors)
    require(read("README.zh-CN.md"), (
        "评审前必须把完整候选提交到本地 Git",
        "最短无歧义 commit",
        "不能作为流程锚点",
    ), "中文 README Git 锚点门禁", errors)
    for path, commit_rule in (
        (Path("skills/brainstorm/SKILL.md"), "committing the complete candidate locally"),
        (Path("skills/roadmap/SKILL.md"), "Commit the complete candidate locally"),
        (Path("skills/write-goal/SKILL.md"), "Commit the complete candidate locally"),
        (Path("skills/write-requirement/SKILL.md"), "Commit the complete\ncandidate locally"),
        (Path("skills/write-design/SKILL.md"), "commits one complete immutable Bundle candidate"),
        (Path("skills/write-task/SKILL.md"), "commit the complete candidate locally"),
        (Path("skills/close-milestone/SKILL.md"), "Commit the complete candidate locally"),
    ):
        require(
            read(path),
            (commit_rule, "shortest unambiguous commit reference"),
            f"{path} 候选 commit 门禁",
            errors,
        )
    for path in GIT_ANCHOR_FILES:
        forbid(read(path), LEGACY_HASH_ANCHOR_RULES, f"{path} Git 锚点反向门禁", errors)

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


def validate_ponytail_contract(errors: list[str]) -> None:
    for relative in PONYTAIL_CONTRACT_FILES:
        forbid(read(relative), PONYTAIL_REVERSE_CONTRACT, str(relative), errors)

    install_commands = (
        "codex plugin marketplace add DietrichGebert/ponytail",
        "codex plugin add ponytail@ponytail",
        "claude plugin marketplace add DietrichGebert/ponytail",
        "claude plugin install ponytail@ponytail --scope user",
    )
    for relative in (Path("README.md"), Path("README.zh-CN.md")):
        require(read(relative), install_commands, f"{relative} Ponytail 安装契约", errors)


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
        or reviewer.get("candidate_integrity") != "reviewed-content-unchanged"
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


def validate_review_policy(errors: list[str]) -> None:
    for relative in REVIEW_POLICY_FILES:
        try:
            text = read(relative)
        except AssertionError as exc:
            errors.append(str(exc))
            continue
        require(text, ("review_policy: single-pass",), str(relative), errors)


def validate_roles(errors: list[str]) -> None:
    markdown_commit_rules = {
        "author": "Commit the complete candidate locally",
        "coder": "Commit the complete candidate locally",
        "critic": "locally committed complete candidate",
        "reviewer": "locally committed complete candidate",
        "verifier": "locally committed complete final candidate",
    }
    toml_commit_rules = {
        "author": "评审前必须把完整候选提交到本地 Git",
        "coder": "评审前必须把完整候选提交到本地 Git",
        "critic": "本地已提交完整候选",
        "reviewer": "完整候选必须在评审前提交到本地 Git",
        "verifier": "本地已提交完整最终候选",
    }
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
            require(text, (
                "shortest unambiguous commit",
                "full-length commit object ID",
                "diff/content hash",
                "workflow anchor",
            ), f"{markdown} Git 锚点门禁", errors)
            require(instructions, (
                "最短无歧义 commit",
                "不得把完整对象 ID、diff/内容哈希、压缩包校验和或制品校验和作为流程锚点",
            ), f"{toml} Git 锚点门禁", errors)
            require(
                text, (markdown_commit_rules[role],),
                f"{markdown} 候选 commit 门禁", errors,
            )
            require(
                instructions, (toml_commit_rules[role],),
                f"{toml} 候选 commit 门禁", errors,
            )
            if role in {"author", "critic", "reviewer", "verifier"}:
                require(text, (
                    "Do not read, cite, or use documents under a project-declared archive root as authority,\n"
                    "context, or evidence",
                ), f"{markdown} archive 上下文边界", errors)
                require(instructions, (
                    "不得读取、引用或使用项目声明的 archive 根目录中的文档作为权威、上下文或证据",
                    "先由对应权威恢复到活动目录",
                ), f"{toml} archive 上下文边界", errors)
                forbid(text, (
                    "Archive documents may be used as authority, context, or evidence",
                ), f"{markdown} archive 上下文边界", errors)
                forbid(instructions, (
                    "可以读取、引用或使用项目声明的 archive 根目录中的文档作为权威、上下文或证据",
                ), f"{toml} archive 上下文边界", errors)
            if role == "reviewer":
                require(text, (
                    "deterministic local checks",
                    "valid review may return no findings",
                    "concrete material harm",
                    "accepted effective\nfallback",
                    "smallest sufficient correction",
                    "material content drift invalidates\nthe review",
                    "exact commands, environment, exit codes",
                    "query it first and treat returned source as already read",
                    "exact candidate workspace in every query",
                    "index is absent, stale, unsupported, changed after the query, or insufficient",
                    "For a run-task candidate containing implementation or test-code changes",
                    "require the registered `ponytail:ponytail-review` Skill",
                    "Load `ponytail:ponytail-review`\nthrough normal discovery before reviewing that code",
                    "code\nminimality is an explicit acceptance condition",
                ), str(markdown), errors)
                require(instructions, (
                    "确定性本地测试计划", "没有 finding 是有效结果",
                    "具体实质影响", "已接受的有效兜底", "最小充分修复",
                    "实质内容漂移使本轮无效",
                    "CodeGraph 索引时先查询",
                    "每次查询必须指向准确的候选工作区",
                    "返回源码视为已读取",
                    "当 run-task 候选含实现或测试代码差异时",
                    "要求已注册的 ponytail:ponytail-review Skill",
                    "审查该代码前通过正常发现加载 ponytail:ponytail-review",
                    "Ponytail finding 属于明确验收项",
                ), str(toml), errors)
                if config.get("sandbox_mode") != "workspace-write":
                    errors.append(f"{toml}: Reviewer 运行本地检查需要 workspace-write")
            if role == "verifier":
                require(text, (
                    "required:<trigger>",
                    "Ordinary deterministic local checks belong to the Reviewer",
                    "Do not broaden the plan",
                    "accepted required path",
                    "A failed, skipped, timed-out, or unavailable required command is not a pass",
                    "material content\nchange invalidates verification",
                ), str(markdown), errors)
                require(instructions, (
                    "required:<trigger>", "普通确定性本地检查归 Reviewer",
                    "不扩大计划继续找问题", "已接受且成功验证的必需路径",
                    "失败、跳过、超时或环境缺失的必需检查不是通过",
                    "任何实质内容变化都使验证无效",
                ), str(toml), errors)
            if role == "coder":
                require(text, (
                    "Discovery does not expand the Card",
                    "accepted effective fallback",
                    "another independently\ntestable outcome",
                    "use it first for source location and relationships",
                    "exact assigned workspace in every query",
                    "treat returned source\nas already read",
                    "require the registered `ponytail:ponytail` Skill at `full`",
                    "Load `ponytail:ponytail` through normal discovery before implementation",
                    "without removing required validation, error handling, security, or\naccessibility",
                ), str(markdown), errors)
                require(instructions, (
                    "发现问题不会扩大 Card", "已接受的有效兜底",
                    "不增加另一个可独立测试结果",
                    "CodeGraph 索引时先用它定位源码和代码关系",
                    "每次查询必须指向准确的当前工作区",
                    "返回源码视为已读取",
                    "要求已注册的 ponytail:ponytail Skill 使用 full 模式",
                    "正常发现加载 ponytail:ponytail",
                    "不得删除必需的校验、错误处理、安全或无障碍保护",
                ), str(toml), errors)
            if role == "critic":
                require(text, (
                    "valid review may return no findings",
                    "concrete material harm",
                    "accepted effective\nfallback",
                    "smallest sufficient correction",
                    "deletion-first minimality check",
                    "Possible future use is not sufficient",
                    "avoidable complexity as a\nmaterial acceptance finding",
                ), str(markdown), errors)
                require(instructions, (
                    "没有 finding 是有效结果", "具体实质影响",
                    "已接受的有效兜底", "最小充分修复",
                    "删除优先的最简性检查",
                    "未来可能使用不能作为理由",
                    "属于实质验收 finding",
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
    if config.get("task_columns") != expected_columns:
        errors.append("DocStar task_columns 未采用新 Task 表头")
    expected_execution = {
        "card_fields": {"execution_log": ["execution_log"]},
        "log_fields": {"latest_event": ["latest_event"]},
        "canonical_task_table_only": True,
    }
    if config.get("task_execution") != expected_execution:
        errors.append("DocStar task_execution 未采用紧凑 Log 兼容指针")
    if config.get("archive_globs") != ["[Aa]rchive"]:
        errors.append("DocStar archive_globs 未排除 archive 文档")


def validate_relative_links(errors: list[str]) -> None:
    try:
        config = json.loads(read(".docstar/conventions/conventions.json"))
    except (AssertionError, json.JSONDecodeError):
        return
    archive_globs = config.get("archive_globs")
    if (
        not isinstance(archive_globs, list)
        or not archive_globs
        or any(not isinstance(pattern, str) or not pattern for pattern in archive_globs)
    ):
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
                target_relative = resolved.relative_to(root)
            except ValueError:
                errors.append(f"{relative}: 链接越出仓库 {target}")
                continue
            if is_archived(target_relative):
                errors.append(f"{relative}: 活动文档不得引用 archive 文档 {target}")
                continue
            if not resolved.exists():
                errors.append(f"{relative}: 链接目标不存在 {target}")
                continue
            skill_parent = path.parent.parent
            if path.name == "SKILL.md" and skill_parent == ROOT / "skills":
                try:
                    resolved.relative_to(path.parent.resolve())
                except ValueError:
                    errors.append(
                        f"{relative}: Skill 运行时链接越出自身目录 {target}"
                    )


def main() -> int:
    errors: list[str] = []
    validate_assurance_policy(errors)
    validate_release(errors)
    validate_skills(errors)
    validate_core_contract(errors)
    validate_normative_language_layout(errors)
    validate_ponytail_contract(errors)
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
