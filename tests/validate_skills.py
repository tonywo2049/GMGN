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
PONYTAIL_CONTRACT_FILES = (
    Path("GMGN.md"),
    Path("skills/gmgn/SKILL.md"),
    Path("skills/run-task/SKILL.md"),
    Path("skills/gmgn/references/en/dispatch-and-handoff.md"),
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
    Path("skills/gmgn/references/en/pre-merge-checklist.md"),
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
    write_goal = read("skills/write-goal/SKILL.md")
    write_requirement = read("skills/write-requirement/SKILL.md")
    write_design = read("skills/write-design/SKILL.md")
    close_milestone = read("skills/close-milestone/SKILL.md")
    release = read("skills/release/SKILL.md")
    pre_merge = read("skills/gmgn/references/en/pre-merge-checklist.md")
    critic_role = read("agents/critic.md")
    codex_critic_role = read(".codex/agents/critic.toml")

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
        "The Critic/Reviewer rows above are evaluated only once",
        "An accepted finding fix remains part of that reviewed batch and does not\n"
        "re-enter role selection",
        "bounded\nresolution check does not search for new findings",
        "Do not resume or create a Critic/Reviewer\nfor those fixes",
        "Solution minimality is an acceptance condition across Requirement, Design, and Task",
        "Anything that can be deleted without losing a current accepted outcome is overdesign",
        "Every run-task Coder brief requires `ponytail:ponytail` at `full`",
        "A run-task Reviewer brief\nrequires `ponytail:ponytail-review` when its candidate contains implementation or test-code\nchanges",
        "explicit deliverables",
        "A deliverable is a final object",
        "a real\n  product/operational E2E is a deliverable only when the realized path itself is the Milestone\n  result",
        "Derive deliverables from the\n  WhitePaper and Milestone outcome, never backward from Goal",
        "name the resulting object rather\n  than its acceptance quality",
        "replace planning names\n  with canonical artifact pointers at closure",
        "acceptance picture's scenarios collectively cover every deliverable",
        "Possible future work not yet\n  allocated to a Milestone belongs in the Backlog",
        "A downstream-only item with a receiving\n  Milestone or owner is a Handoff instead",
        "Every Milestone has at least one end-to-end scenario",
        "Goal owns one initiated Milestone's objective, boundary, non-goals, result-based slices",
        "mapping of ROADMAP deliverables and acceptance scenarios into active scope",
        "Requirement\n  owns required observable behavior, quantified parameters, constraints, and decidable\n"
        "  acceptance criteria",
        "Task boundaries follow independently provable outcomes, not API count",
        "All Coder lanes use the same current approved Design Bundle commit",
        "Milestone's final frozen contract",
    ), "GMGN 有效兜底边界", errors)

    require(gmgn, (
        "Every delegated Author, Coder, Critic, Reviewer, Verifier, or Researcher is single-use",
        "Prepare the full role brief before creation",
        "Collect all active findings before changing the candidate",
        "Each semantic change batch or task execution uses `review_policy: single-pass`",
        "Do not resume or create a\nCritic/Reviewer for those fixes",
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
        "A `list_agents` snapshot is allowed only",
        "There is no periodic list interval",
        "ROADMAP sequencing, Milestone allocation, deliverable, dependency, qualitative acceptance picture, Backlog placement, or Handoff placement",
        "Goal objective, boundary, non-goal, result-based slice, or ROADMAP deliverable/acceptance-scenario mapping",
        "Requirement behavior, quantified parameter, constraint, or decidable AC",
        "Requirement, Design, and Task writers keep the least structure",
        "Their fresh Critic\nattempts deletion, reuse, native behavior, or a direct solution",
        "Every run-task Coder brief\nrequires `ponytail:ponytail` at `full`",
        "A run-task Reviewer brief requires\n`ponytail:ponytail-review` when its candidate contains implementation or test-code changes",
        "Missing Ponytail blocks that code task",
        "requires a separate `Contract.md`",
        "same current approved Design Bundle commit",
        "evidence, smallest proposed delta, and affected tasks",
        "`close-milestone` freezes the implementation-matching\nContract as `closed`",
    ), "gmgn 路由契约", errors)
    require(write_task, (
        TASK_HEADER,
        "| AC | task |",
        "Do not put TDD cases",
        "The TDD contract belongs in `Card.md`, not Task",
        "`execution_log` link to its sibling `Log.md`",
        "material decisions\nonly",
        "final evidence summary",
        "`latest_event`\nfield is only a DocStar compatibility pointer",
        "not a\ngeneral event ledger",
        "minimize unnecessary task dependencies, shared writes, and runtime conflicts",
        "The objective is useful parallelism, not more task cards",
        "Never invent empty wrappers, fake interfaces, or new design decisions",
        "more coordination cost than isolation benefit",
        "satisfying it closes the task",
        "Apply the deletion test to every task",
        "Remove a task when all current ACs remain satisfied without its\noutcome",
        "Critic must try deleting or merging each affected task",
        "discovery\ndoes not expand it",
        "another independently testable outcome requires a separately accepted task",
        "API count is not a task boundary",
        "one Contract ID\n  may support provider, consumer, and integration tasks",
        "applicable Contract anchors",
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
        "do not resume or create a Critic/Reviewer for the\nfixes",
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
        "sends no heartbeat when state is unchanged",
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
        "Do not send fixes from that round to another Critic or Reviewer",
        "The final accepted commit records the reviewed commit",
        "The Reviewer runs the prepared deterministic local checks",
        "A fresh Verifier is exceptional, not default",
        "Classify the final candidate as `not-required`\nor `required:<trigger>`",
        "registered skills or available tools required for the task",
        "load them through normal discovery",
        "instead of passing\nanother Skill's internal resource path",
        "Compliance checks are triggered by a real boundary or material state change",
        "Commit the complete candidate locally before review",
        "shortest unambiguous commit reference",
        "a correction commit is not a standalone candidate",
        "valid review may return\nno findings",
        "concrete material harm",
        "smallest sufficient correction",
        "minimum verification plan",
        "sends no heartbeat when observable state is unchanged",
        "Do not query again until a material lifecycle event",
        "There is no periodic list interval",
        "initialize it once in each isolated workspace before source discovery",
        "against the exact assigned workspace",
        "treat returned source as already read",
        "index is absent, stale,\nunsupported, changed after the query, or insufficient",
        "every Coder brief names the registered `ponytail:ponytail` Skill at `full`",
        "A\nReviewer brief names `ponytail:ponytail-review` when its candidate contains implementation or\ntest-code changes",
        "Missing Ponytail blocks that code task",
        "Avoidable R-D-T complexity is material because it propagates downstream",
        "Code that Ponytail can\ndelete while preserving current requirements and safeguards",
    ), "英文派发契约", errors)
    require(roadmap, (
        "explicit **Milestone\n  deliverables**",
        "never infer ROADMAP deliverables backward from a downstream Goal",
        "Name what will exist at the end, not how well it must perform",
        "realized product/operational E2E when that\n  path itself is the final result",
        "The acceptance picture states qualitative success\n  conditions",
        "Evidence is produced downstream and linked at\n  closure",
        "real E2E as a short complete path from start through key actions to an observable\n  result",
        "not as a test path or acceptance document",
        "list\n  that artifact once instead of repeating its contained paths as deliverables",
        "point an internal-code deliverable to its\n  repository when known",
        "number deliverables\n  consecutively and put one item on each line",
        "must cover every deliverable",
        "Milestone acceptance picture",
        "Every Milestone acceptance picture names at least one high-level end-to-end scenario",
        "traverses the full outcome owned by that Milestone",
        "If no full owned path can be stated",
        "must be independently decidable from work owned by that Milestone",
        "Do not prescribe a test framework",
        "Requirement refines scenarios into ACs",
        "Maintain one Backlog for possible future work that is not yet allocated to a Milestone",
        "New ideas enter the Backlog",
        "Record a downstream-only confirmation as a non-blocking Handoff when a receiving",
        "Otherwise keep it in the Backlog",
        "`repository@<accepted-commit>`",
        "release\n  tag and release page",
        "a network or environment uses its applicable stable identity and\n  access pointers",
        "Omit pointers that do not\n  apply",
        "document, report, or tool links directly to the accepted artifact",
    ), "roadmap 验收图景契约", errors)
    require(roadmap_agent, (
        "Milestone deliverables",
        "E2E scenarios",
        "里程碑产出",
    ), "roadmap 界面元数据契约", errors)
    require(write_goal, (
        "Derive Goal only from the approved ROADMAP Milestone and its WhitePaper authority",
        "Requirement, Design, Task, implementation, or evidence may trigger a controlled revision\n"
        "  but cannot silently redefine Goal",
        "Split slices\n  by independently meaningful results, not by team, component, or file",
        "Carry ROADMAP deliverables forward only as mappings; Goal does not redefine them",
        "Map every\n  deliverable to one or more slices",
        "require every slice to contribute to a ROADMAP\n  deliverable or acceptance scenario",
        "Map every ROADMAP acceptance-scenario anchor to one or more slices and a qualitative\n"
        "  observable outcome",
        "Requirement refines that meaning into parameters and decidable ACs",
        "Requirement owns quantified parameters and acceptance conditions",
        "Design\n  owns implementation choices",
        "Task owns work division, order, and status",
        "Resolve before Requirement every open decision owned by Goal",
        "Route upstream-owned gaps to\n  their authority and leave downstream-owned choices to their proper stage",
        "Do not include component or interface design, code\n  structure, test cases, commands, results, task breakdown, live status",
        "or conclusions copied from downstream",
        "ROADMAP-owned deliverables,\n   qualitative acceptance picture",
        "Goal-owned objectives, boundaries, non-goals, result-based slices, ROADMAP\n"
        "   deliverable/acceptance-scenario mappings",
        "deleting all downstream documents leaves Goal's objective and boundary complete",
        "an invalid mapping returns to `roadmap` instead of changing upstream meaning in Goal",
    ), "write-goal 内容边界契约", errors)
    forbid(write_goal, (
        "may redefine Goal",
        "Split slices by team, component, or file",
        "Redefine ROADMAP deliverables inside Goal",
        "Some ROADMAP deliverables need no slice",
        "ROADMAP acceptance scenarios need no slice",
        "Goal owns quantified parameters and acceptance conditions",
        "Goal owns implementation choices",
        "Goal owns work division, order, and status",
        "Push every Goal-owned open decision to Requirement",
        "quantified pass/fail criterion",
        "include conclusions copied from downstream",
    ), "write-goal 内容边界契约", errors)
    require(write_requirement, (
        "Derive Requirement from the approved Goal",
        "Design, Task, implementation, tests, or evidence may trigger a\n"
        "  controlled revision but cannot silently define or redefine Requirement",
        "smallest necessary set of numbered requirements\n  `R1`, `R2`, ...",
        "Each R states one coherent required behavior, capability, or constraint\n"
        "  and names its owning Goal slice or externally imposed invariant",
        "enough observable precondition, action or\n"
        "  inspection, and result to determine pass or fail",
        "Given/When/Then is optional syntax, not a\n  mandatory format",
        "Numeric and static constraints may state their decision rule directly",
        "Use unambiguous observable language",
        "Keep the explicit trace: ROADMAP acceptance scenario → Goal slice → R/AC",
        "No acceptance\n  scenario or in-scope Goal slice may disappear, and no R/AC may be unowned",
        "Preserve upstream-approved invariants and values without silent weakening",
        "Requirement may\n  define quantified parameters it owns",
        "name each value's authority, change boundary, and\n  verification method",
        "ROADMAP remains the authority for the deliverable's identity and final\n"
        "  artifact pointer",
        "only when applicable; do not require fixed sections for absent categories",
        "Resolve every\n  Requirement-owned decision before acceptance",
        "leave implementation choices to Design",
        "Do not invent or prescribe components, modules, interfaces, process structure",
        "task division, execution order, test commands,\n"
        "  runtime results, evidence IDs, live status, or closure history",
        "Delete any R/AC whose removal would not cause a current Goal outcome or externally imposed\n"
        "  invariant to fail",
        "Future possibility, speculative reuse or scale, configurability, and\n"
        "  implementation convenience are not owners",
        "every in-scope Goal slice is covered; any proposed exclusion\n"
        "routes to `write-goal`",
        "every ROADMAP acceptance scenario traces through Goal to R/AC",
        "every AC has a clear pass/fail decision",
        "no Requirement-owned decision is\n  deferred to Design or Task",
        "no implementation choice, execution information, or actual\n"
        "verification result has leaked into Requirement",
    ), "write-requirement 内容边界契约", errors)
    forbid(write_requirement, (
        "can silently define or redefine Requirement",
        "Given/When/Then is mandatory syntax",
        "Every quantified parameter must come from Goal",
        "Requirement cannot define quantified parameters",
        "Requirement owns components, modules, or interfaces",
        "Future possibility and implementation convenience are owners",
        "Defer every Requirement-owned decision to Design",
        "Some ROADMAP acceptance scenarios may disappear",
        "Some in-scope Goal slices may disappear",
        "Allow R/AC to be unowned",
        "Requirement owns the deliverable's identity and final artifact pointer",
        "every current Goal slice is covered or explicitly excluded",
    ), "write-requirement 内容边界契约", errors)
    require(write_design, (
        "Apply the first-sufficient anti-overdesign order from GMGN §7",
        "For every new module,\n  interface, state, configuration item, dependency, or failure mechanism",
        "Future reuse or possible scale is not sufficient",
        "deletion-first overdesign check against the\nsmallest sufficient design",
        "`Design.md` plus required `Contract.md`",
        "The contract itself is mandatory for every such boundary",
        "an `approved` working baseline for implementation",
        "Do not mark the Design-stage Contract `closed` here",
    ), "design 最简方案契约", errors)
    require(close_milestone, (
        "ROADMAP acceptance scenario → Goal slice → AC → task → test → evidence",
        "every ROADMAP acceptance scenario",
        "every ROADMAP deliverable against its accepted result and required canonical pointer",
        "ROADMAP deliverable pointers and acceptance-scenario links to accepted evidence",
        "closed `Log.md` current snapshot and final evidence",
        "every retained Contract ID against its provider implementation",
        "Closure cannot silently rewrite the contract to match code",
        "reconciled implementation-matching Contract marked `closed`",
        "commit the blocker-resolved final\nclosure candidate",
        "Owner acceptance binds to that exact commit",
        "Integrate that exact commit without creating post-acceptance closure content",
    ), "milestone 验收关账契约", errors)
    require(writing_en, (
        "design | contract | task",
        "`approved` means the current shared working baseline",
        "one normative `Contract.md` is\nrequired",
        "outcomes, not API count",
        "The Coder does not edit\nthe shared Design Bundle or create a separate change-request document",
        "`close-milestone` alone marks the final\nimplementation-matching Contract commit `closed`",
    ), "英文 Design/Contract 写作契约", errors)
    require(critic_role, (
        "First determine\nwhether such a boundary exists",
        "If it does not, delete the separate `Contract.md`",
        "If it does,\nthe file is required",
        "delete only duplicated or upstream-unowned contract content",
    ), "Critic Contract 强制边界", errors)
    require(codex_critic_role, (
        "不存在才删除整个 Contract.md",
        "边界存在时必须保留文件",
        "只删除重复或无上游依据的契约内容",
    ), "Codex Critic Contract 强制边界", errors)
    require(pre_merge, (
        "`not-required` or `required:<trigger>`",
        "Missing required evidence blocks integration",
        "complete candidate committed before review",
        "shortest unambiguous commit reference",
        "different\n   integration commit is acceptable only when the reviewed source",
        "current snapshot, material decisions, and final evidence",
        "Did R-D-T criticism apply the deletion test",
        "When the candidate contains\nimplementation or test-code changes",
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
    require(pre_merge, (
        "A full-length commit object ID, diff/content hash,\n   archive checksum, or artifact checksum is not a workflow anchor",
    ), "合并前 Git 锚点门禁", errors)
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
        (Path("skills/write-design/SKILL.md"), "Commit the whole\nDesign-stage candidate locally"),
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
                continue
            skill_parent = path.parent.parent
            if path.name == "SKILL.md" and skill_parent == ROOT / "skills":
                try:
                    resolved.relative_to(path.parent.resolve())
                except ValueError:
                    errors.append(
                        f"{path.relative_to(ROOT)}: Skill 运行时链接越出自身目录 {target}"
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
