#!/usr/bin/env python3
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ValidateSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        config = json.loads(
            (ROOT / ".docstar/conventions/conventions.json").read_text(encoding="utf-8")
        )
        self.archive_globs = tuple(config["archive_globs"])
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "dist", *self.archive_globs,
            ),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "tests/validate_skills.py"], cwd=self.root,
            text=True, capture_output=True,
        )

    def replace(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def run_isolated_mutation(
        self, relative: str, old: str, new: str,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git", "__pycache__", "dist", *self.archive_globs,
                ),
            )
            path = root / relative
            text = path.read_text(encoding="utf-8")
            self.assertIn(old, text)
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            return subprocess.run(
                ["python3", "tests/validate_skills.py"], cwd=root,
                text=True, capture_output=True,
            )

    def test_clean_tree_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_release_version_drift(self) -> None:
        path = self.root / ".claude-plugin/plugin.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["version"] = "0.2.99"
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("四处发布版本不一致", result.stdout)

    def test_rejects_invalid_skill_frontmatter(self) -> None:
        self.replace("skills/gmgn/SKILL.md", "name: gmgn", "name: wrong")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("name 必须等于目录名", result.stdout)

    def test_rejects_old_task_header(self) -> None:
        self.replace(
            "skills/write-task/SKILL.md",
            "| # | task | spec anchor | prerequisite | status | execution |",
            "| # | task | spec anchor | prerequisite | failing test | status |",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("旧 Task 表头", result.stdout)

    def test_rejects_task_tdd_leakage(self) -> None:
        self.replace(
            "skills/write-task/SKILL.md",
            "Do not put TDD cases",
            "Put TDD cases",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 紧凑索引契约", result.stdout)

    def test_rejects_verbose_log_contract(self) -> None:
        self.replace(
            "skills/write-task/SKILL.md",
            "material decisions, and\n  final evidence summary",
            "full process history, including every event",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 紧凑索引契约", result.stdout)

    def test_allows_negated_legacy_log_term(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "# Run confirmed task cards",
            "# Run confirmed task cards\n\n`Log.md` does not use append-only history.",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_missing_codegraph_first_rule(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "returned source as already read",
            "always read every returned source again",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_missing_compact_log_docstar_adapter(self) -> None:
        path = self.root / ".docstar/conventions/conventions.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value.pop("task_execution")
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("紧凑 Log 兼容指针", result.stdout)

    def test_rejects_missing_task_decomposition_objective(self) -> None:
        self.replace(
            "skills/write-task/SKILL.md",
            "Keep `Task.md` as a compact Milestone execution index.",
            "Maximize task count in `Task.md`.",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 紧凑索引契约", result.stdout)

    def test_rejects_task_content_boundary_drift(self) -> None:
        cases = (
            (
                "Use stable task IDs and the task-state tokens\n"
                "  defined by the writing contract",
                "Do not use stable task IDs or task-state tokens",
            ),
            (
                "Every in-scope AC must map to at least one task",
                "Not every in-scope AC must map to at least one task",
            ),
            (
                "Do not put TDD cases,\n"
                "  commands, file scopes",
                "Do not put TDD cases, but put commands and file scopes",
            ),
            (
                "Never create tentative, placeholder, or speculative task sets",
                "Allow tentative, placeholder, or speculative task sets",
            ),
            (
                "Every in-scope AC must map to at least one task",
                "Allow in-scope ACs to remain unmapped",
            ),
            (
                "`Log.md` is not a full process\nhistory",
                "`Log.md` records the full process history",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                result = self.run_isolated_mutation(
                    "skills/write-task/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("write-task 紧凑索引契约", result.stdout)
                self.assertIn("含相反契约", result.stdout)

    def test_rejects_contract_working_and_final_lifecycle_drift(self) -> None:
        cases = (
            (
                "skills/write-design/SKILL.md",
                "an `approved` working baseline for implementation",
                "the final immutable contract before implementation",
            ),
            (
                "skills/run-task/SKILL.md",
                "Do not mark the working Contract `closed` during run-task",
                "Mark the working Contract `closed` during run-task",
            ),
            (
                "skills/close-milestone/SKILL.md",
                "reconciled implementation-matching Contract marked `closed`",
                "leave the final Contract mutable after closure",
            ),
            (
                "skills/gmgn/references/en/writing-contract.md",
                "The Coder does not edit\n"
                "the shared Design Bundle or create a separate change-request document",
                "The Coder must edit the shared Design Bundle and create a separate "
                "change-request document",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_closure_commit_created_after_owner_acceptance(self) -> None:
        result = self.run_isolated_mutation(
            "skills/close-milestone/SKILL.md",
            "Integrate that exact commit without creating post-acceptance closure content",
            "Create the final closure commit after owner acceptance",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("milestone 验收关账契约", result.stdout)

    def test_rejects_critic_deleting_required_contract(self) -> None:
        cases = (
            (
                "agents/critic.md",
                "If it does,\nthe file is required",
                "If it does, the file may be deleted",
            ),
            (
                ".codex/agents/critic.toml",
                "边界存在时必须保留文件",
                "边界存在时也可删除文件",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_solution_minimality_drift(self) -> None:
        cases = (
            (
                "skills/write-requirement/SKILL.md",
                "Delete any R/AC whose removal would not cause a current Goal outcome or externally imposed\n"
                "  invariant to fail",
                "Keep every proposed R/AC",
            ),
            (
                "skills/write-design/SKILL.md",
                "Future reuse, possible scale,\n  flexibility, and implementation "
                "convenience are not owners",
                "Future reuse always justifies new structure",
            ),
            (
                "skills/write-task/SKILL.md",
                "Apply the deletion test to every task",
                "Keep every proposed task",
            ),
            (
                "agents/critic.md",
                "deletion-first minimality check",
                "addition-first completeness check",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_missing_ponytail_code_gate(self) -> None:
        cases = (
            (
                "skills/run-task/SKILL.md",
                "Every Coder brief must require the registered `ponytail:ponytail` Skill at `full`",
                "Coder briefs need no code-minimality Skill",
            ),
            (
                "agents/coder.md",
                "Load `ponytail:ponytail` through normal discovery before implementation",
                "Implement without loading Ponytail",
            ),
            (
                "agents/reviewer.md",
                "Load `ponytail:ponytail-review`\nthrough normal discovery before reviewing that code",
                "Review without loading Ponytail",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_ponytail_reverse_contract(self) -> None:
        cases = (
            (
                "skills/run-task/SKILL.md",
                "silently continue, or accept the code candidate.",
                "silently continue, or accept the code candidate.\n\n"
                "If Ponytail is unavailable, continue and accept the candidate.",
            ),
            (
                ".codex/agents/reviewer.toml",
                "回传前自检，不输出固定 Reflection 段。",
                "Ponytail 不可用时仍继续并接受候选。回传前自检，不输出固定 Reflection 段。",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("含相反契约", result.stdout)

    def test_rejects_missing_ponytail_install_commands(self) -> None:
        cases = (
            (
                "README.md",
                "codex plugin add ponytail@ponytail",
                "codex plugin add ponytail@wrong",
            ),
            (
                "README.zh-CN.md",
                "claude plugin install ponytail@ponytail --scope user",
                "claude plugin install ponytail@wrong --scope user",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("Ponytail 安装契约", result.stdout)

    def test_rejects_missing_roadmap_acceptance_picture(self) -> None:
        self.replace(
            "skills/roadmap/SKILL.md",
            "at least one high-level end-to-end scenario",
            "general completion notes",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("roadmap 验收图景契约", result.stdout)

    def test_rejects_roadmap_backlog_handoff_or_metadata_drift(self) -> None:
        cases = (
            (
                "skills/roadmap/SKILL.md",
                "Otherwise keep it in the Backlog",
                "Otherwise keep it as an unclassified item",
                "roadmap 验收图景契约",
            ),
            (
                "skills/roadmap/agents/openai.yaml",
                "Define Milestone deliverables and full-outcome E2E scenarios",
                "Define a generic project timeline",
                "roadmap 界面元数据契约",
            ),
        )
        for relative, old, new, label in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(label, result.stdout)

    def test_rejects_roadmap_deliverable_authority_or_pointer_drift(self) -> None:
        cases = (
            (
                "skills/roadmap/SKILL.md",
                "never infer ROADMAP deliverables backward from a downstream Goal",
                "infer ROADMAP deliverables from the downstream Goal",
                "roadmap 验收图景契约",
            ),
            (
                "skills/close-milestone/SKILL.md",
                "every ROADMAP deliverable against its accepted result and required canonical pointer",
                "ROADMAP deliverable names without accepted pointers",
                "milestone 验收关账契约",
            ),
        )
        for relative, old, new, label in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(label, result.stdout)

    def test_rejects_goal_content_boundary_drift(self) -> None:
        cases = (
            (
                "Requirement, Design, Task, implementation, or evidence may trigger a controlled revision\n"
                "  but cannot silently redefine Goal",
                "Requirement, Design, Task, implementation, or evidence may redefine Goal",
            ),
            (
                "Split slices\n  by independently meaningful results, not by team, component, or file",
                "Split slices by team, component, or file",
            ),
            (
                "Carry ROADMAP deliverables forward only as mappings; Goal does not redefine them",
                "Redefine ROADMAP deliverables inside Goal",
            ),
            (
                "Map every\n  deliverable to one or more slices",
                "Some ROADMAP deliverables need no slice",
            ),
            (
                "Map every ROADMAP acceptance-scenario anchor to one or more slices and a qualitative\n"
                "  observable outcome",
                "ROADMAP acceptance scenarios need no slice",
            ),
            (
                "Requirement owns quantified parameters and acceptance conditions",
                "Goal owns quantified parameters and acceptance conditions",
            ),
            (
                "Design\n  owns implementation choices",
                "Goal owns implementation choices",
            ),
            (
                "Task owns work division, order, and status",
                "Goal owns work division, order, and status",
            ),
            (
                "Resolve before Requirement every open decision owned by Goal",
                "Push every Goal-owned open decision to Requirement",
            ),
            (
                "qualitative\n  observable outcome",
                "quantified pass/fail criterion",
            ),
            (
                "or conclusions copied from downstream",
                "and include conclusions copied from downstream",
            ),
        )
        for old, new in cases:
            with self.subTest(old=old):
                result = self.run_isolated_mutation(
                    "skills/write-goal/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("write-goal 内容边界契约", result.stdout)
                self.assertIn("含相反契约", result.stdout)

    def test_rejects_goal_controlled_revision_route_drift(self) -> None:
        cases = (
            (
                "ROADMAP-owned deliverables,\n   qualitative acceptance picture",
                "Goal-owned deliverables and quantitative acceptance criteria",
            ),
            (
                "Goal-owned objectives, boundaries, non-goals, result-based slices, ROADMAP\n"
                "   deliverable/acceptance-scenario mappings",
                "Goal-owned objectives and document mapping only",
            ),
        )
        for old, new in cases:
            with self.subTest(old=old):
                result = self.run_isolated_mutation(
                    "skills/write-goal/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("write-goal 内容边界契约", result.stdout)

    def test_rejects_requirement_content_boundary_drift(self) -> None:
        cases = (
            (
                "Design, Task, implementation, tests, or evidence may trigger a\n"
                "  controlled revision but cannot silently define or redefine Requirement",
                "Design, Task, implementation, tests, or evidence can silently define "
                "or redefine Requirement",
            ),
            (
                "Given/When/Then is optional syntax, not a\n  mandatory format",
                "Given/When/Then is mandatory syntax",
            ),
            (
                "Requirement may\n  define quantified parameters it owns",
                "Every quantified parameter must come from Goal",
            ),
            (
                "Do not invent or prescribe components, modules, interfaces, process structure",
                "Requirement owns components, modules, or interfaces and prescribes process structure",
            ),
            (
                "Future possibility, speculative reuse or scale, configurability, and\n"
                "  implementation convenience are not owners",
                "Future possibility and implementation convenience are owners",
            ),
            (
                "Resolve every\n  Requirement-owned decision before acceptance",
                "Defer every Requirement-owned decision to Design",
            ),
            (
                "No acceptance\n  scenario or in-scope Goal slice may disappear, and no R/AC may be unowned",
                "Some ROADMAP acceptance scenarios may disappear",
            ),
            (
                "No acceptance\n  scenario or in-scope Goal slice may disappear, and no R/AC may be unowned",
                "Some in-scope Goal slices may disappear",
            ),
            (
                "No acceptance\n  scenario or in-scope Goal slice may disappear, and no R/AC may be unowned",
                "Allow R/AC to be unowned",
            ),
            (
                "ROADMAP remains the authority for the deliverable's identity and final\n"
                "  artifact pointer",
                "Requirement owns the deliverable's identity and final artifact pointer",
            ),
            (
                "every in-scope Goal slice is covered; any proposed exclusion\n"
                "routes to `write-goal`",
                "every current Goal slice is covered or explicitly excluded",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                result = self.run_isolated_mutation(
                    "skills/write-requirement/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("write-requirement 内容边界契约", result.stdout)
                self.assertIn("含相反契约", result.stdout)

    def test_rejects_design_content_boundary_drift(self) -> None:
        cases = (
            (
                "Design, Task,\n  implementation, tests, or evidence cannot silently "
                "redefine upstream meaning",
                "Design may silently redefine Requirement",
            ),
            (
                "Do not mandate a\n  fixed research funnel or test sequence for every Design",
                "Every Design must follow a fixed research funnel",
            ),
            (
                "Do not mandate a\n  fixed research funnel or test sequence for every Design",
                "Every Design must use the same test sequence",
            ),
            (
                "Design may own implementation-specific choices, configuration, and "
                "derived values that do\n  not change Requirement meaning",
                "Design may change Requirement-owned acceptance values",
            ),
            (
                "Task executes approved values and reports evidence; a needed\n"
                "  change returns to the authority that owns the value",
                "Task may change authoritative parameters from trial results",
            ),
            (
                "Keep commands, full results, candidate chronology, task status, "
                "execution history,\n  and closure records downstream",
                "Keep commands, full results, candidate chronology, task status, "
                "execution history, and closure records in Design",
            ),
            (
                "Map each R/AC as: R/AC → design structure and data → applicable "
                "failure behavior →\n  verification point",
                "Map R/AC only to broad sections",
            ),
            (
                "Keep an interface in Design when one\n  implementation unit owns it; "
                "never create an empty Contract",
                "Always create Contract.md",
            ),
            (
                "Future reuse, possible scale,\n  flexibility, and implementation "
                "convenience are not owners",
                "Future reuse, possible scale, flexibility, and implementation "
                "convenience are owners",
            ),
            (
                "Do not require fixed sections for absent\n  concerns",
                "Every Design must define concurrency, recovery, migration, and "
                "performance sections",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                result = self.run_isolated_mutation(
                    "skills/write-design/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("design 最简方案契约", result.stdout)
                self.assertIn("含相反契约", result.stdout)

    def test_rejects_archive_context_contract_drift(self) -> None:
        reverse = "Archive documents may be used as authority, context, or evidence"
        global_cases = (
            (
                "GMGN.md",
                "Documents under a project-declared archive root are historical storage, "
                "not active authority",
            ),
            (
                "skills/gmgn/SKILL.md",
                "Before direct or delegated writing, Critic, Reviewer, or Verifier work",
            ),
            (
                "skills/gmgn/references/en/writing-contract.md",
                "Documents under a project-declared archive root are historical storage only",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Every Author, Critic, Reviewer, and Verifier brief names project-declared "
                "archive roots as\nexcluded paths",
            ),
        )
        for relative, old in global_cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, reverse)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("archive 上下文边界", result.stdout)
                self.assertIn("含相反契约", result.stdout)

        markdown_rule = (
            "Do not read, cite, or use documents under a project-declared archive root as authority,\n"
            "context, or evidence"
        )
        chinese_rule = (
            "不得读取、引用或使用项目声明的 archive 根目录中的文档作为权威、上下文或证据"
        )
        chinese_reverse = (
            "可以读取、引用或使用项目声明的 archive 根目录中的文档作为权威、上下文或证据"
        )
        for role in ("author", "critic", "reviewer", "verifier"):
            with self.subTest(role=role, surface="markdown"):
                result = self.run_isolated_mutation(
                    f"agents/{role}.md", markdown_rule, reverse,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("archive 上下文边界", result.stdout)
                self.assertIn("含相反契约", result.stdout)
            with self.subTest(role=role, surface="toml"):
                result = self.run_isolated_mutation(
                    f".codex/agents/{role}.toml", chinese_rule, chinese_reverse,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("archive 上下文边界", result.stdout)
                self.assertIn("含相反契约", result.stdout)

    def test_rejects_missing_docstar_archive_filter(self) -> None:
        path = self.root / ".docstar/conventions/conventions.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value.pop("archive_globs")
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("DocStar archive_globs 未排除 archive 文档", result.stdout)

    def test_rejects_missing_fresh_agent_lifecycle(self) -> None:
        self.replace(
            "skills/gmgn/SKILL.md",
            "single-use. Prepare",
            "single-use. Defer",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由契约", result.stdout)

    def test_rejects_periodic_agent_status_polling(self) -> None:
        self.replace(
            "skills/gmgn/SKILL.md",
            "A timeout\nalone is not a `list_agents` trigger",
            "A timeout triggers `list_agents`",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由 Agent 等待契约", result.stdout)

    def test_rejects_short_agent_wait_or_timeout_termination(self) -> None:
        cases = (
            (
                "`agent_wait_timeout_ms = 3600000` (1 hour)",
                "`agent_wait_timeout_ms = 60000` (1 minute)",
            ),
            (
                "routine\nprogress-update cadence never shortens it",
                "routine progress-update cadence shortens it",
            ),
            (
                "must not interrupt, terminate, or kill an agent merely because it has\n"
                "not returned content",
                "may terminate an agent when it has not returned content",
            ),
            (
                "immediately re-arm the same one-hour wait",
                "return from the task after the timeout",
            ),
        )
        for old, new in cases:
            with self.subTest(old=old):
                result = self.run_isolated_mutation(
                    "skills/gmgn/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("gmgn 路由 Agent 等待契约", result.stdout)

    def test_rejects_global_execution_set_scan_drift(self) -> None:
        cases = (
            (
                "GMGN.md",
                "scans every task in the confirmed\nexecution set",
                "scans only the current task",
            ),
            (
                "skills/run-task/SKILL.md",
                "dispatches every ready, non-conflicting task that fits currently available capacity",
                "dispatches only the current lane",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("全局调度契约", result.stdout)

    def test_rejects_missing_fallback_stop_rule(self) -> None:
        cases = (
            (
                "GMGN.md",
                "accepted main\npath works",
                "accepted main path is broken",
            ),
            (
                "GMGN.md",
                "stop fixing that issue",
                "continue improving it until perfect",
            ),
            (
                "skills/run-task/SKILL.md",
                "Card outcome works",
                "Card outcome is broken",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative, old=old):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_findings_or_tasks_that_do_not_converge(self) -> None:
        cases = (
            (
                "agents/critic.md",
                "a valid review may return no findings",
                "every review must return findings",
            ),
            (
                "agents/reviewer.md",
                "accepted effective\nfallback",
                "fallbacks are irrelevant",
            ),
            (
                "agents/verifier.md",
                "Do not broaden the plan",
                "Broaden the plan",
            ),
            (
                "skills/run-task/SKILL.md",
                "Discovery does not expand an active Card",
                "Discovery expands the active Card",
            ),
            (
                "skills/run-task/SKILL.md",
                "A task is complete when its Card contract is satisfied",
                "A task remains open after its Card contract is satisfied",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative, old=old):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_post_fix_review_loop(self) -> None:
        cases = (
            (
                "GMGN.md",
                "An accepted finding fix remains part of that reviewed batch and does not\n"
                "re-enter role selection",
            ),
            (
                "skills/gmgn/SKILL.md",
                "bounded resolution check does not search for new findings",
            ),
            (
                "skills/run-task/SKILL.md",
                "do not resume or create a Critic/Reviewer for the\nfixes",
            ),
        )
        for relative, rule in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(
                    relative,
                    rule,
                    "accepted fixes start another complete Critic/Reviewer round",
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_unchanged_state_primary_heartbeat(self) -> None:
        self.replace(
            "skills/gmgn/SKILL.md",
            "do not report a wait timeout,\n"
            "silence, absence of content, agent count, or `running` status",
            "report each wait timeout and the agent's `running` status",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由 Agent 等待契约", result.stdout)

    def test_rejects_tip_only_candidate_application(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "never apply only\nits last correction commit",
            "apply only its last correction commit",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_boundary_and_candidate_contract_drift(self) -> None:
        cases = (
            (
                "skills/run-task/SKILL.md",
                "Compliance checks are triggered by a real boundary or material state change",
                "Compliance checks run in full whenever any task starts",
            ),
            (
                "skills/run-task/SKILL.md",
                "complete\noriginal-base-to-candidate commit range",
                "tip commit only",
            ),
            (
                "skills/run-task/SKILL.md",
                "different integration commit is acceptable only when the reviewed source",
                "different integration commit is accepted without comparing reviewed source",
            ),
            (
                "skills/gmgn/SKILL.md",
                "Each semantic change batch or task execution uses\n`review_policy: single-pass`",
                "The entire primary session uses\n`review_policy: single-pass`",
            ),
            (
                "agents/reviewer.md",
                "material\ncontent drift invalidates\nthe review",
                "material content drift may be accepted",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative, old=old):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_hash_or_uncommitted_workflow_anchors(self) -> None:
        cases = (
            (
                "skills/run-task/SKILL.md",
                "Before review, a sole writer commits the complete candidate locally",
                "A sole writer may use a captured diff or content hash. "
                "Before review, a sole writer commits the complete candidate locally",
            ),
            (
                "skills/gmgn/references/en/writing-contract.md",
                "Commit the candidate locally\nbefore independent review",
                "Review the uncommitted candidate before creating a commit",
            ),
            (
                "agents/coder.md",
                "return the shortest unambiguous commit reference",
                "return the full-length commit object ID",
            ),
            (
                "skills/roadmap/SKILL.md",
                "Commit the complete candidate locally",
                "Review the mutable candidate before committing it",
            ),
            (
                "README.md",
                "Full-length commit object IDs, diff/content hashes, and checksums cannot be workflow anchors",
                "A sole writer freezes a diff/content hash",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_role_rule_outside_developer_instructions(self) -> None:
        cases = (
            (
                ".codex/agents/coder.toml",
                "发现问题不会扩大 Card",
            ),
            (
                ".codex/agents/reviewer.toml",
                "没有 finding 是有效结果",
            ),
            (
                ".codex/agents/verifier.toml",
                "不扩大计划继续找问题",
            ),
        )
        for relative, rule in cases:
            with self.subTest(relative=relative):
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary) / "repo"
                    shutil.copytree(
                        ROOT, root,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"),
                    )
                    path = root / relative
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(rule, text)
                    instructions_at = text.index('developer_instructions = """')
                    before = text[:instructions_at]
                    after = text[instructions_at:].replace(rule, "允许相反行为。", 1)
                    description_at = before.index('description = "') + len('description = "')
                    before = before[:description_at] + rule + " " + before[description_at:]
                    path.write_text(before + after, encoding="utf-8")
                    checked = subprocess.run(
                        ["python3", "tests/validate_skills.py"], cwd=root,
                        text=True, capture_output=True,
                    )
                    self.assertEqual(
                        checked.returncode, 1, checked.stdout + checked.stderr,
                    )

    def test_rejects_verifier_before_review_clear(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain",
            "Dispatch a Verifier while review blockers remain",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_run_task_required_command_waiver(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "A failed, skipped,\ntimed-out, or unavailable required command is not a pass",
            "A failed, skipped,\ntimed-out, or unavailable required command may pass",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_verifier_required_command_waiver(self) -> None:
        cases = (
            (
                "agents/verifier.md",
                "A failed, skipped, timed-out, or unavailable required command is not a pass",
                "A failed, skipped, timed-out, or unavailable required command may pass",
            ),
            (
                ".codex/agents/verifier.toml",
                "失败、跳过、超时或环境缺失的必需检查不是通过",
                "失败、跳过、超时或环境缺失的必需检查也可通过",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(relative, old, new)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_rejects_verifier_that_changes_tracked_files(self) -> None:
        self.replace(
            "agents/verifier.md",
            "Any material content\nchange invalidates verification on both pass and failure",
            "Material content changes may be accepted after verification",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/verifier.md", result.stdout)

    def test_rejects_missing_required_verifier_gate(self) -> None:
        self.replace(
            "skills/gmgn/references/en/pre-merge-checklist.md",
            "Missing required evidence blocks integration",
            "Missing required evidence may be ignored",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("合并前双向验证门禁", result.stdout)

    def test_rejects_release_without_risk_triggered_artifact_verifier(self) -> None:
        self.replace(
            "skills/release/SKILL.md",
            "`artifact-not-fully-machine-checkable`",
            "`all-artifacts-always-pass`",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("发布制品独立验证门禁", result.stdout)

    def test_rejects_reviewer_without_deterministic_execution(self) -> None:
        self.replace(
            "agents/reviewer.md",
            "exact commands, environment, exit codes",
            "a summary only",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/reviewer.md", result.stdout)

    def test_rejects_default_verifier_policy(self) -> None:
        path = self.root / "skills/gmgn/references/en/assurance-policy.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["verifier"]["default"] = True
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Verifier 必须是非默认角色", result.stdout)

    def test_rejects_unbatched_review_loop(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "return before editing.",
            "return and edit immediately.",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_second_review_pass_policy(self) -> None:
        path = self.root / "skills/gmgn/references/en/assurance-policy.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["review"]["post_fix_independent_recheck"] = True
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("单轮审查与修复后证据策略无效", result.stdout)

    def test_rejects_nonstandard_skill_frontmatter(self) -> None:
        self.replace(
            "skills/close-milestone/SKILL.md",
            "\n---\n\n# Close a milestone",
            "\nassurance_policy: gmgn-assurance-v1\n---\n\n# Close a milestone",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter 只允许 name 和 description", result.stdout)

    def test_rejects_skill_runtime_link_outside_its_directory(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "# Run confirmed task cards",
            "# Run confirmed task cards\n\n[shared policy](../gmgn/references/en/assurance-policy.json)",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Skill 运行时链接越出自身目录", result.stdout)

    def test_rejects_invalid_codex_role_toml(self) -> None:
        path = self.root / ".codex/agents/reviewer.toml"
        path.write_text(path.read_text(encoding="utf-8") + "\ninvalid = [\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("TOML", result.stdout)

    def test_rejects_wrong_codex_role_field_type(self) -> None:
        self.replace(
            ".codex/agents/verifier.toml",
            'sandbox_mode = "workspace-write"',
            "sandbox_mode = 1",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("sandbox_mode", result.stdout)

    def test_rejects_markdown_role_review_policy_drift(self) -> None:
        self.replace(
            "agents/reviewer.md",
            "review_policy: single-pass",
            "review_policy: multi-pass",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/reviewer.md", result.stdout)

    def test_rejects_codex_role_review_policy_drift(self) -> None:
        self.replace(
            ".codex/agents/critic.toml",
            "review_policy: single-pass",
            "review_policy: multi-pass",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn(".codex/agents/critic.toml", result.stdout)

    def test_rejects_translated_normative_mirror(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "zh-CN"
        path.mkdir(parents=True)
        (path / "writing-contract.md").write_text("duplicate\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("规范文档必须只保留英文单一权威", result.stdout)

    def test_rejects_any_non_english_normative_root(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "fr"
        path.mkdir(parents=True)
        (path / "writing-contract.md").write_text("duplicate\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("规范文档必须只保留英文单一权威", result.stdout)

    def test_rejects_old_docstar_adapter(self) -> None:
        path = self.root / ".docstar/conventions/conventions.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["task_columns"] = {
            "spec": "spec anchor", "prereq": "prerequisite",
            "red": "failing test", "status": "status",
        }
        path.write_text(json.dumps(value), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("DocStar task_columns", result.stdout)

    def test_rejects_broken_relative_link(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[bad](missing.md)\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("链接目标不存在", result.stdout)

    def test_ignores_broken_links_inside_archive_roots(self) -> None:
        for relative in ("archive/frozen.md", "nested/Archive/frozen.md"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[bad](missing.md)\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_active_link_to_archive_document(self) -> None:
        archived = self.root / "Archive" / "frozen.md"
        archived.parent.mkdir(parents=True)
        archived.write_text("historical\n", encoding="utf-8")
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n[old](Archive/frozen.md)\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("活动文档不得引用 archive 文档", result.stdout)


if __name__ == "__main__":
    unittest.main()
