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
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "dist", *config["archive_globs"]
            ),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "tests/validate_skills.py"],
            cwd=self.root,
            text=True,
            capture_output=True,
        )

    def replace(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assert_rejected(self, expected: str) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout)

    def test_clean_tree_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_skill_frontmatter_drift(self) -> None:
        self.replace(
            "skills/write-goal/SKILL.md",
            "name: write-goal",
            "name: another-name\nowner: nobody",
        )
        self.assert_rejected("name 必须等于目录名")
        self.assert_rejected("frontmatter 多出")

    def test_rejects_missing_skill_agent_config(self) -> None:
        (self.root / "skills/write-goal/agents/openai.yaml").unlink()
        self.assert_rejected("agents/openai.yaml: 缺失")

    def test_rejects_assurance_review_duplication(self) -> None:
        path = self.root / "skills/gmgn/references/en/assurance-policy.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["review"] = {"max_rounds": 2}
        path.write_text(json.dumps(policy), encoding="utf-8")
        self.assert_rejected("顶层字段应为")

    def test_rejects_invalid_verifier_trigger(self) -> None:
        path = self.root / "skills/gmgn/references/en/assurance-policy.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["verifier"]["triggers"].append("high-risk-behavior")
        path.write_text(json.dumps(policy), encoding="utf-8")
        self.assert_rejected("Verifier triggers 必须等于")

    def test_rejects_verifier_trigger_authority_regression(self) -> None:
        cases = (
            (
                "skills/release/SKILL.md",
                "Dispatch one fresh Verifier only for a recorded trigger such as:",
            ),
            (
                "GMGN.md",
                "installation, startup,\nnon-machine-checkable artifacts, or another recorded risk may still require one",
            ),
            (
                "README.md",
                "| Risk-triggered final verification | Installation, startup, E2E, external environments, or artifacts not fully machine-checkable |",
            ),
            (
                "README.zh-CN.md",
                "| 风险触发的最终验证 | 安装、启动、E2E、外部环境或无法完全机检的制品 |",
            ),
            ("skills/release/SKILL.md", "artifact-not-fully-machine-checkable"),
        )
        for relative, regression in cases:
            with self.subTest(relative=relative, regression=regression):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                path.write_text(original + f"\n{regression}\n", encoding="utf-8")
                self.assert_rejected("Verifier")
                path.write_text(original, encoding="utf-8")

    def test_rejects_decision_consumption_regression(self) -> None:
        cases = (
            (
                "a direct specification for downstream artifacts or an implementation checklist for one\nMilestone",
                "a direct specification for downstream artifacts",
            ),
            (
                "A D-ID creates no Milestone allocation or execution obligation by itself",
                "A D-ID creates a Milestone allocation and execution obligation",
            ),
            ("Milestone must implement the whole Decision", "Milestone implements the Decision"),
        )
        for old, new in cases:
            with self.subTest(rule=old):
                path = self.root / "skills/gmgn/references/en/writing-rules.md"
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected("Decision 下游消费边界")
                path.write_text(original, encoding="utf-8")

    def test_rejects_write_design_research_regression(self) -> None:
        cases = (
            (
                "every semantic revision of the Design-stage Bundle require",
                "selected semantic revisions of the Design-stage Bundle require",
            ),
            (
                "neither\ndelta size nor an already-clear problem waives it",
                "a clear or small delta may skip the research",
            ),
            (
                "A meaning-preserving correction or mechanical change does not alter Design-owned meaning and is\n"
                "outside this trigger",
                "Any small Design change is outside this trigger",
            ),
            (
                "observable candidate and source inclusion and exclusion conditions",
                "general candidate preferences",
            ),
            (
                "The\nAdjudicator does not search external sources itself.",
                "The Adjudicator searches external sources itself.",
            ),
            (
                "Researcher to discover up to three credible candidates",
                "Researcher to collect owner-named candidates",
            ),
            (
                "The same Adjudicator aggregates the returned evidence, compares only what can change the\n"
                "decision, and selects the Design-owned solution",
                "The Researcher compares candidates and selects the Design-owned solution",
            ),
            (
                "Before editing that semantic delta, complete its bounded external research under External\n"
                "   solution research",
                "When needed, consider external research after editing that semantic delta",
            ),
        )
        for old, new in cases:
            with self.subTest(rule=old):
                path = self.root / "skills/write-design/SKILL.md"
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected("write-design 外部调研边界")
                path.write_text(original, encoding="utf-8")

    def test_rejects_run_task_test_first_policy_drift(self) -> None:
        # This protects approved Skill text; it is not task-level RED evidence.
        cases = (
            (
                "every implementation lane\nuses a delegated Coder",
                "the primary orchestrator may implement one lane",
            ),
            (
                "The Coder encodes those approved criteria; it does not define acceptance meaning",
                "The Coder defines acceptance meaning and encodes its own criteria",
            ),
            (
                "structural regression, not behavior TDD evidence",
                "behavior TDD evidence",
            ),
            (
                "no separate\nprimary-orchestrator or Adjudicator approval is required",
                "primary-orchestrator approval is required",
            ),
            (
                "Any result-affecting target-test\nchange invalidates its RED evidence",
                "A result-affecting target-test change preserves its RED evidence",
            ),
            (
                "Reviewer independently replays the same target command",
                "Reviewer trusts the Coder's recorded command",
            ),
        )
        path = self.root / "skills/run-task/SKILL.md"
        original = path.read_text(encoding="utf-8")
        for old, new in cases:
            with self.subTest(rule=old):
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected("run-task 关键执行控制")
        path.write_text(original, encoding="utf-8")

    def test_rejects_run_task_tdd_design_regressions(self) -> None:
        # These are structural regression controls, not behavior-level RED evidence.
        cases = (
            (
                "authority-derived test cases",
                "skills/run-task/SKILL.md",
                "- behavior, defect, algorithm, and interface work records the smallest set of authority-derived\n"
                "  test cases. Each case identifies its exact approved Requirement, AC, Design, Contract, or\n"
                "  Task completion-criterion anchor; scenario or input; observable expected result; and the\n"
                "  wrong behavior it detects. One case may cover multiple anchors, and existing-behavior cases\n"
                "  may already pass, but every changed behavior must have discriminating pre-implementation\n"
                "  failure coverage;",
                "- behavior work records approved tests;",
                "run-task 关键执行控制",
            ),
            (
                "test-only RED and direct continuation",
                "skills/run-task/SKILL.md",
                "For RED-gated work, the initial Coder brief authorizes the complete test and production write\n"
                "boundary. Require the Coder to create and record the test-only RED checkpoint before production\n"
                "work, then continue directly to GREEN in the same dispatch. The Coder does not request or wait\n"
                "for a separate RED approval from the primary orchestrator or Adjudicator.",
                "For RED-gated work, implementation may proceed before later validation.",
                "run-task 关键执行控制",
            ),
            (
                "recorded RED and same-command GREEN",
                "skills/run-task/SKILL.md",
                "After recording RED, freeze the target tests and every helper that can affect their verdict.\n"
                "The Coder implements the smallest sufficient production change and obtains GREEN with the same\n"
                "target command before running required regression checks. Any result-affecting target-test\n"
                "change invalidates its RED evidence. Stop production work, recreate the test-only checkpoint\n"
                "against the original production baseline, record valid RED again, and then continue; never\n"
                "delete, skip, weaken, bypass, or move production logic into a test to obtain GREEN.",
                "After recording RED, implementation may alter tests as needed.",
                "run-task 关键执行控制",
            ),
            (
                "optional refactor rule",
                "skills/run-task/SKILL.md",
                "After the first GREEN, refactor only to correct a concrete structure problem. When refactoring,\n"
                "retain a pre-refactor GREEN checkpoint and rerun the same target and required regression checks;\n"
                "otherwise skip refactoring without creating another checkpoint.",
                "After the first GREEN, refactoring is optional.",
                "run-task 关键执行控制",
            ),
            (
                "edit first, research later exception",
                "skills/write-design/SKILL.md",
                None,
                "\nUrgent revisions may edit first, research later.\n",
                "含 Design/TDD 冲突例外",
            ),
            (
                "implementation before RED, approval later exception",
                "skills/run-task/SKILL.md",
                None,
                "\nProduction implementation before RED is allowed; approval later is sufficient.\n",
                "含 Design/TDD 冲突例外",
            ),
        )
        for name, relative, old, new, expected in cases:
            with self.subTest(case=name):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                if old is None:
                    path.write_text(original + new, encoding="utf-8")
                else:
                    self.assertIn(old, original)
                    path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected(expected)
                path.write_text(original, encoding="utf-8")

    def test_rejects_missing_wait_control(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            '{"timeout_ms": 600000}',
            '{"timeout_ms": 60000}',
        )
        self.assert_rejected("run-task 关键执行控制")

    def test_rejects_incomplete_wait_lifecycle_controls(self) -> None:
        path = self.root / "skills/run-task/SKILL.md"
        original = path.read_text(encoding="utf-8")
        cases = (
            (
                "If the full ten minutes expires without an event, call `list_agents` once",
                "If the full ten minutes expires, immediately wait again",
            ),
            (
                "Between lifecycle events and timeout boundaries, do not poll `list_agents`",
                "Poll list_agents whenever useful",
            ),
            (
                "Do not call\n`list_agents` more than once for the same timeout",
                "Call list_agents repeatedly after a timeout",
            ),
            (
                "While any dispatched agent is\n`running`, do not call `interrupt_agent`, "
                "end the orchestration, or return a final task result",
                "Stop a slow agent after repeated timeouts",
            ),
            (
                "If the snapshot reports `running`, finish any unrelated\nready scheduling "
                "work and return to the same maximum ten-minute `wait_agent` call",
                "If that snapshot reports running, interrupt it to reclaim capacity",
            ),
            (
                "time or token budget are not such evidence",
                "time or token budget permits interruption",
            ),
            (
                "does not create or send\nheartbeat, unchanged `running`, timeout, agent-count, "
                "or progress data to the user, Log,\ntelemetry, or another agent",
                "sends heartbeat progress data while waiting",
            ),
        )
        for old, new in cases:
            with self.subTest(rule=old):
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected("run-task 关键执行控制")
        path.write_text(original, encoding="utf-8")

    def test_rejects_missing_ready_set_priority(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "largest number of currently blocked tasks ready",
            "smallest card first",
        )
        self.assert_rejected("run-task 关键执行控制")

    def test_rejects_missing_continuous_parallel_refill(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "Treat safe lane saturation as a scheduling invariant",
            "Parallel refill is optional",
        )
        self.assert_rejected("run-task 关键执行控制")

    def test_rejects_authorization_flow_regression(self) -> None:
        cases = (
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "The terminal completion return retires the agent",
                "Any return retires the agent",
                "派发授权与生命周期",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "One authorization may cover a named set of external operations against an exact target",
                "Every external operation needs separate authorization",
                "派发授权与生命周期",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "| Researcher | `gpt-5.6-terra` | `max` |",
                "| Researcher | `gpt-5.6-sol` | `high` |",
                "派发授权与生命周期",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Researcher** is an information collector only",
                "Researcher** analyzes and recommends solutions",
                "派发授权与生命周期",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "these are the only\nGMGN agent roles",
                "additional roles may be invented when useful",
                "派发授权与生命周期",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "applicable authority, scope, checks, and environment validity inputs",
                "candidate only",
                "派发授权与生命周期",
            ),
            (
                "skills/release/SKILL.md",
                "push the branch and tag together",
                "perform external operations in any order",
                "release 外部操作顺序",
            ),
            (
                "skills/run-task/SKILL.md",
                "sends the primary orchestrator an interim decision request",
                "returns a terminal result",
                "run-task 关键执行控制",
            ),
            (
                "skills/gmgn/SKILL.md",
                "An initiated Milestone has accepted Task rows that can run",
                "Confirmed Task rows can run",
                "gmgn run-task 路由",
            ),
            (
                "skills/roadmap/SKILL.md",
                "The Author writes one complete\n"
                "recommended candidate without asking the owner to approve fields or allocations separately",
                "asks the owner to approve every allocation",
                "ROADMAP 一次批准",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "It does not forward every return to an Adjudicator",
                "Every return goes to an Adjudicator",
                "派发授权与生命周期",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "If the scheduling pass finds no explicit next\n"
                "consumer, remove the exact GMGN-managed worktree",
                "Keep an unassigned worktree for possible future reuse",
                "派发授权与生命周期",
            ),
            (
                "agents/adjudicator.md",
                "All owner interaction passes through the primary orchestrator as an exact relay",
                "The Adjudicator asks the owner directly",
                "Adjudicator 角色边界",
            ),
            (
                "skills/write-goal/SKILL.md",
                "Prepare the Goal and proposed initiation as one candidate",
                "Require initiation before preparing Goal",
                "Goal 合并批准",
            ),
            (
                "skills/run-task/SKILL.md",
                "scan the entire target-Milestone\nTask set",
                "scan only the separately confirmed execution\nset",
                "run-task 关键执行控制",
            ),
        )
        for relative, old, new, expected in cases:
            with self.subTest(relative=relative, rule=old):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected(expected)
                path.write_text(original, encoding="utf-8")

    def test_rejects_required_rule_hidden_in_inactive_markdown(self) -> None:
        path = self.root / "skills/gmgn/references/en/dispatch-and-handoff.md"
        original = path.read_text(encoding="utf-8")
        required = "| Researcher | `gpt-5.6-terra` | `max` |"
        invalid = "| Researcher | `gpt-5.6-sol` | `high` |"
        for hidden in (
            f"<!-- {required} -->",
            f"```markdown\n{required}\n```",
        ):
            with self.subTest(hidden=hidden.splitlines()[0]):
                path.write_text(
                    original.replace(required, invalid, 1) + f"\n{hidden}\n",
                    encoding="utf-8",
                )
                self.assert_rejected("派发授权与生命周期")
                path.write_text(original, encoding="utf-8")

    def test_rejects_conflicting_rule_alongside_required_rule(self) -> None:
        cases = (
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Any return retires the agent",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Every external operation needs separate authorization",
            ),
            (
                "skills/run-task/SKILL.md",
                "Scan only the separately confirmed execution set",
            ),
        )
        for relative, contradiction in cases:
            with self.subTest(relative=relative, contradiction=contradiction):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                path.write_text(original + f"\n{contradiction}.\n", encoding="utf-8")
                self.assert_rejected("含冲突规则")
                path.write_text(original, encoding="utf-8")

    def test_rejects_missing_single_review_limit(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "Never create or dispatch another Reviewer to recheck findings or fixes",
            "Dispatch another Reviewer to recheck fixes",
        )
        self.assert_rejected("run-task 关键执行控制")

    def test_rejects_single_review_contract_drift(self) -> None:
        cases = (
            (
                "skills/gmgn/SKILL.md",
                "Each semantic candidate batch has at most one Critic round",
                "Each semantic candidate may have two Critic rounds",
                "gmgn 单轮独立审查边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Accepted finding fixes do\nnot create another Critic or Reviewer dispatch",
                "Accepted fixes create another Reviewer dispatch",
                "派发单轮独立审查边界",
            ),
            (
                "skills/gmgn/references/en/code-review.md",
                "Each Task execution has exactly one Reviewer\nround",
                "Each Task execution has two Reviewer rounds",
                "code-review 单轮审查边界",
            ),
            (
                "agents/reviewer.md",
                "only Reviewer round",
                "first Reviewer round",
                "Reviewer 单轮审查边界",
            ),
            (
                "agents/critic.md",
                "only Critic round",
                "first Critic round",
                "Critic 单轮审查边界",
            ),
        )
        for relative, old, new, expected in cases:
            with self.subTest(relative=relative, rule=old):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                self.assert_rejected(expected)
                path.write_text(original, encoding="utf-8")

    def test_rejects_run_task_rule_copied_elsewhere(self) -> None:
        path = self.root / "skills/write-goal/SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nUse `wait_agent` here.\n",
            encoding="utf-8",
        )
        self.assert_rejected("复制了 run-task 专属规则")

    def test_rejects_old_task_header(self) -> None:
        path = self.root / "skills/write-task/SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n| # | task | spec anchor | prerequisite | failing test | status |\n",
            encoding="utf-8",
        )
        self.assert_rejected("含旧 Task 表头")

    def test_rejects_writing_contract_revival(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nSee `writing-contract.md`.\n",
            encoding="utf-8",
        )
        self.assert_rejected("引用旧 writing-contract.md")

    def test_rejects_latest_event_value_copied_elsewhere(self) -> None:
        path = self.root / "skills/write-task/SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n`latest_event: [Current](#current)`\n",
            encoding="utf-8",
        )
        self.assert_rejected("复制了 writing-rules 的 latest_event")

    def test_rejects_missing_milestone_reopen_rule(self) -> None:
        self.replace(
            "skills/gmgn/references/en/writing-rules.md",
            "state: closed → initiated when unfinished work is found",
            "state: closed",
        )
        self.assert_rejected("writing-rules 机器字段")

    def test_rejects_obsolete_irreversible_closure_rule(self) -> None:
        path = self.root / "skills/roadmap/SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nA closed foundation remains closed.\n",
            encoding="utf-8",
        )
        self.assert_rejected("含已废止规则")

    def test_rejects_missing_decision_scope_rule(self) -> None:
        self.replace(
            "skills/write-decision/SKILL.md",
            "regardless of subject or Milestone scope",
            "only for project-wide scope",
        )
        self.assert_rejected("write-decision 决议范围")

    def test_rejects_obsolete_cross_milestone_decision_limit(self) -> None:
        path = self.root / "skills/write-decision/SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nDo not absorb WhitePaper meaning, ROADMAP allocation.\n",
            encoding="utf-8",
        )
        self.assert_rejected("含已废止规则")

    def test_rejects_invalid_role_toml(self) -> None:
        path = self.root / ".codex/agents/reviewer.toml"
        path.write_text('name = "broken"\n', encoding="utf-8")
        self.assert_rejected("sandbox_mode 必须是字符串")

    def test_rejects_role_sandbox_drift(self) -> None:
        self.replace(
            ".codex/agents/reviewer.toml",
            'sandbox_mode = "workspace-write"',
            'sandbox_mode = "read-only"',
        )
        self.assert_rejected("sandbox_mode 应为 workspace-write")

    def test_rejects_docstar_task_column_drift(self) -> None:
        path = self.root / ".docstar/conventions/conventions.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["task_columns"]["execution"] = "handoff"
        path.write_text(json.dumps(config), encoding="utf-8")
        self.assert_rejected("DocStar task_columns 无效")

    def test_rejects_broken_relative_link(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\n[missing](missing.md)\n",
            encoding="utf-8",
        )
        self.assert_rejected("链接目标不存在")

    def test_rejects_active_link_to_archive(self) -> None:
        archive = self.root / "Archive"
        archive.mkdir()
        (archive / "old.md").write_text("# old\n", encoding="utf-8")
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\n[old](Archive/old.md)\n",
            encoding="utf-8",
        )
        self.assert_rejected("活动文档不得引用 archive 文档")


if __name__ == "__main__":
    unittest.main()
