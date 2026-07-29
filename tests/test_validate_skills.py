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
            "skills/run-task/SKILL.md",
            "Routine dispatch, waiting, unchanged status, and successful\n"
            "   intermediate checks are not Log entries",
            "full process history, including every event",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

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
            "Split Tasks to the smallest independently executable and independently acceptable",
            "Split Tasks into convenient implementation batches",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 紧凑索引契约", result.stdout)

    def test_rejects_task_split_contract_drift(self) -> None:
        cases = (
            (
                "Apply the split test",
                "The split test is optional",
            ),
            (
                "maximize parallel execution across the task",
                "minimize parallel execution across the task",
            ),
            (
                "make them separate\n"
                "  Tasks even when one depends on the other",
                "merge them whenever one depends on the other",
            ),
            (
                "no individual task must\n"
                "  satisfy that AC alone",
                "every individual task must\n"
                "  satisfy that AC alone",
            ),
            (
                "Critic must try splitting, deleting, and merging each affected task",
                "Critic must try deleting and merging each affected task",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                result = self.run_isolated_mutation(
                    "skills/write-task/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
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
                "Never create tentative, placeholder, or speculative\n"
                "  task sets",
                "Allow tentative, placeholder, or speculative task sets",
            ),
            (
                "Every in-scope AC must map to at least one task",
                "Allow in-scope ACs to remain unmapped",
            ),
            (
                "Do not\ncopy execution content or history into `Task.md`",
                "Task.md records execution content or history",
            ),
            (
                "do not require the execution ID to equal\n"
                "the Task ID",
                "execution ID must equal the Task ID",
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
                "Design acceptance marks the complete Bundle `approved`, not `closed`",
                "Design acceptance marks the complete Bundle `closed`",
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
                "`approved` means the current shared working baseline",
                "`approved` means the final immutable implementation",
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
                "when one exists, the catalog is required",
                "when one exists, the catalog may be deleted",
            ),
            (
                ".codex/agents/critic.toml",
                "存在时必须保留契约目录",
                "存在时也可删除契约目录",
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
                "Future reuse, possible scale, flexibility, or implementation\n"
                "  convenience is not an owner",
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

    def test_rejects_forced_roadmap_e2e(self) -> None:
        self.replace(
            "skills/roadmap/SKILL.md",
            "Otherwise omit E2E content; never invent one",
            "Otherwise omit E2E content; never invent one\n"
            "- Every Milestone must invent E2E content",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("roadmap 产出与可选 E2E 契约", result.stdout)

    def test_rejects_stage_owned_next_step_or_propagation(self) -> None:
        cases = (
            ("skills/roadmap/SKILL.md", "# ROADMAP: single sequencing authority", "roadmap"),
            ("skills/write-goal/SKILL.md", "# Initiate a milestone and write Goal.md", "write-goal"),
            (
                "skills/write-requirement/SKILL.md",
                "# Requirement.md: single milestone requirement authority",
                "write-requirement",
            ),
            (
                "skills/write-design/SKILL.md",
                "# Design stage: requirements → implementation decisions",
                "write-design",
            ),
            ("skills/write-task/SKILL.md", "# Task.md: milestone task index", "write-task"),
        )
        for relative, heading, label in cases:
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(
                    relative,
                    heading,
                    f"{heading}\n\nCreation then uses **REQUIRED next skill: downstream**.",
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(f"{label} 文档自治契约", result.stdout)
                self.assertIn("含相反契约", result.stdout)

        result = self.run_isolated_mutation(
            "skills/write-goal/SKILL.md",
            "# Initiate a milestone and write Goal.md",
            "# Initiate a milestone and write Goal.md\n\n"
            "Propagate only to affected Requirement documents.",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("write-goal 文档自治契约", result.stdout)

        result = self.run_isolated_mutation(
            "skills/write-design/SKILL.md",
            "# Design stage: requirements → implementation decisions",
            "# Design stage: requirements → implementation decisions\n\n"
            "After Design approval, continue with $write-task.",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("write-design 文档自治契约", result.stdout)

        result = self.run_isolated_mutation(
            "skills/write-requirement/SKILL.md",
            "# Requirement.md: single milestone requirement authority",
            "# Requirement.md: single milestone requirement authority\n\n"
            "Include an index of planned downstream artifacts before those artifacts exist.",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("write-requirement 文档自治契约", result.stdout)

    def test_rejects_roadmap_backlog_or_metadata_drift(self) -> None:
        cases = (
            (
                "skills/roadmap/SKILL.md",
                "New ideas remain in the Backlog until allocated to a Milestone",
                "New ideas bypass the Backlog",
                "roadmap 产出与可选 E2E 契约",
            ),
            (
                "skills/roadmap/agents/openai.yaml",
                "Sequence Milestones, outputs, dependencies, and Backlog",
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
                "later artifacts or evidence cannot silently redefine it",
                "later artifacts or evidence may redefine it",
                "roadmap 产出与可选 E2E 契约",
            ),
            (
                "skills/roadmap/SKILL.md",
                "Link only the WhitePaper boundary and invariant anchors needed for sequencing; "
                "do not\n  restate their text",
                "Restate the WhitePaper boundary and invariants in ROADMAP",
                "roadmap 产出与可选 E2E 契约",
            ),
            (
                "skills/close-milestone/SKILL.md",
                "every ROADMAP deliverable against its accepted result and required canonical pointer",
                "ROADMAP deliverable names without accepted pointers",
                "milestone 验收关账契约",
            ),
            (
                "skills/close-milestone/SKILL.md",
                "A Milestone without a ROADMAP core E2E does not need E2E evidence",
                "A Milestone without a ROADMAP core E2E does not need E2E evidence. "
                "Every Milestone needs E2E evidence",
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
                "Later documents, implementation, or evidence may expose a needed revision but cannot\n"
                "  silently redefine Goal",
                "Later documents, implementation, or evidence may silently redefine Goal",
            ),
            (
                "independently meaningful result slices, not teams, components, files, or work steps",
                "Split slices by team, component, or file",
            ),
            (
                "Cover every ROADMAP deliverable with one or more result slices",
                "Some ROADMAP deliverables need no slice",
            ),
            (
                "When ROADMAP has a core E2E anchor, carry it into the applicable slices",
                "Ignore an existing ROADMAP core E2E",
            ),
            (
                "Keep exact numeric criteria, technical design, task division,\n"
                "  execution, and evidence out of Goal",
                "Goal includes exact numeric criteria",
            ),
            (
                "Resolve every Goal-owned ambiguity into the result, boundary, slices, or Close outcomes",
                "Push every Goal-owned ambiguity to Requirement",
            ),
            (
                "Include only content that either gives Requirement a necessary basis or decides whether the\n"
                "  Milestone can Close",
                "Include unrelated content in Goal",
            ),
            (
                "Delete anything that serves neither purpose",
                "Keep content that serves neither purpose",
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
                "Return WhitePaper- or ROADMAP-owned changes to `gmgn` for routing",
                "Goal-owned deliverables and quantitative acceptance criteria",
            ),
            (
                "Goal-owned results, boundaries, non-goals, result slices, ROADMAP\n"
                "   deliverable/core-E2E mappings, or qualitative Close outcomes",
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
                "Later documents, implementation, tests, or evidence may expose a needed revision but cannot\n"
                "  silently define or redefine Requirement",
                "Later documents, implementation, tests, or evidence can silently define "
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
                "No in-scope Goal result or\n  Close outcome may disappear",
                "Some Goal results or Close outcomes may disappear",
            ),
            (
                "no R/AC may be unowned",
                "Allow R/AC to be unowned",
            ),
            (
                "every in-scope Goal result and Close outcome is covered; any\n"
                "proposed exclusion returns to `gmgn` for routing",
                "every current Goal result is covered or explicitly excluded",
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
                "real call paths for feasibility without redefining upstream\n  meaning",
                "Design may silently redefine Requirement",
            ),
            (
                "not required headings or a document template",
                "Every Design must follow a fixed research funnel",
            ),
            (
                "not required headings or a document template",
                "Every Design must use the same test sequence",
            ),
            (
                "Specify every choice that can\nchange an R/AC",
                "Design may change Requirement-owned acceptance values",
            ),
            (
                "Keep the Bundle `draft` while any implementation-significant decision remains unresolved",
                "Allow unresolved implementation-significant decisions in approved Design",
            ),
            (
                "include commands, full results, candidate chronology, work status, execution history, or\n"
                "closure records",
                "Keep commands, full results, candidate chronology, work status, "
                "execution history, and closure records in Design",
            ),
            (
                "Map each R/AC once in root `Design.md`",
                "Map R/AC only to broad sections",
            ),
            (
                "Do not create an empty file or directory",
                "Always create Contract.md",
            ),
            (
                "Add\narchitecture and module boundaries only when current R/ACs need them",
                "Always add architecture and module boundaries",
            ),
            (
                "add a Bundle index\nonly when linked child artifacts exist",
                "Always add a Bundle index",
            ),
            (
                "Future reuse, possible scale, flexibility, or implementation\n"
                "  convenience is not an owner",
                "Future reuse, possible scale, flexibility, and implementation "
                "convenience are owners",
            ),
            (
                "not required headings or a document template",
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

    def test_rejects_design_closure_drift(self) -> None:
        cases = (
            (
                "If the approved\nBundle permits incompatible implementations of a shared boundary, "
                "it is incomplete",
                "Incompatible conforming implementations are acceptable",
            ),
            (
                "Naming a validator without binding every required entry point does not close "
                "the boundary",
                "Naming a validator closes the boundary without call sites",
            ),
            (
                "global-versus-local rule conflicts",
                "global-versus-local conflicts may be ignored",
            ),
            (
                "If the fix must invent or change Design-owned meaning, it is a new semantic\n"
                "batch",
                "A finding fix may invent new Design meaning without another semantic batch",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                result = self.run_isolated_mutation(
                    "skills/write-design/SKILL.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("design 最简方案契约", result.stdout)

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
                "Routine\nprogress-update cadence never shortens it",
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

    def test_rejects_non_universal_one_hour_wait(self) -> None:
        rule = (
            "Every Codex `wait_agent` call uses "
            "`agent_wait_timeout_ms = 3600000` (1 hour)"
        )
        for relative in (
            "GMGN.md",
            "skills/gmgn/SKILL.md",
            "skills/run-task/SKILL.md",
        ):
            with self.subTest(relative=relative):
                result = self.run_isolated_mutation(
                    relative,
                    rule,
                    "Some Codex `wait_agent` calls use "
                    "`agent_wait_timeout_ms = 3600000` (1 hour)",
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("Agent 等待契约", result.stdout)

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

    def test_rejects_ready_set_priority_drift(self) -> None:
        result = self.run_isolated_mutation(
            "skills/run-task/SKILL.md",
            "closure would make the largest number of currently blocked\n"
            "tasks ready",
            "card title sorts first",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_agent_retirement_and_ownership_drift(self) -> None:
        cases = (
            (
                "A platform-interrupted or hard-failed delegated agent is also retired",
                "A platform-interrupted delegated agent may be resumed",
            ),
            (
                "only one primary orchestrator may\n"
                "mutate shared state and integrate candidates at a time",
                "several primary orchestrators may\n"
                "mutate shared state and integrate candidates at a time",
            ),
        )
        for old, new in cases:
            with self.subTest(new=new):
                result = self.run_isolated_mutation(
                    "skills/gmgn/references/en/dispatch-and-handoff.md", old, new,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("英文派发契约", result.stdout)

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
                "existing unambiguous authority",
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
            "skills/run-task/SKILL.md",
            "A failed, skipped,\ntimed-out, or unavailable required command is not a pass",
            "A failed, skipped, timed-out, or unavailable required command may pass",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

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
