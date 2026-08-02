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

    def test_rejects_assurance_review_block_substitutes(self) -> None:
        path = self.root / "skills/gmgn/references/en/assurance-policy.json"
        original = path.read_text(encoding="utf-8")
        for key in ("candidate_review", "review"):
            with self.subTest(key=key):
                policy = json.loads(original)
                policy[key] = {"required": True}
                path.write_text(json.dumps(policy), encoding="utf-8")
                self.assert_rejected("顶层字段应为")
        path.write_text(original, encoding="utf-8")

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
                "observable candidate and source inclusion and\nexclusion conditions",
                "general candidate preferences",
            ),
            (
                "the primary orchestrator performs\nthe bounded collection or creates one Researcher when independent or parallel collection is\nuseful.",
                "The Researcher always selects the collection strategy.",
            ),
            (
                "A Researcher brief authorizes discovery of up to three credible candidates",
                "Researcher to collect owner-named candidates",
            ),
            (
                "The primary orchestrator aggregates collected evidence, compares only what can change the\n"
                "decision, and selects the Design-owned solution",
                "The Researcher compares candidates and selects the Design-owned solution",
            ),
            (
                "inspect source code and tests relevant to the current problem at an\n"
                "explicitly checked upstream release, version, or commit",
                "inspect documentation for a current software release",
            ),
            (
                "keep the smallest closed code slice",
                "keep the selected source files",
            ),
            (
                "exact reuse boundary at the smallest stable and useful file, module, or symbol granularity",
                "general reuse scope",
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

    def test_rejects_in_scope_repair_boundary_regression(self) -> None:
        cases = (
            (
                "skills/gmgn/SKILL.md",
                "A fix that introduces new meaning or widens the write boundary is a separately scoped case.\n"
                "A change that invents new meaning is a new semantic case owned by its stage.",
            ),
            (
                "skills/write-design/SKILL.md",
                "If a fix must invent or change Design-owned meaning, it is a new semantic case under Controlled revision.",
            ),
        )
        for relative, contradiction in cases:
            with self.subTest(relative=relative, contradiction=contradiction):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                path.write_text(original + f"\n{contradiction}\n", encoding="utf-8")
                self.assert_rejected("范围内 finding 修复边界")
                path.write_text(original, encoding="utf-8")

    def test_rejects_run_task_test_first_policy_drift(self) -> None:
        # This protects approved Skill text; it is not task-level RED evidence.
        cases = (
            (
                "Normal Task execution does not use an Author. The Coder creates or resumes Card/Log, writes the",
                "the primary orchestrator may implement one lane",
            ),
            (
                "The Coder encodes the accepted criteria; it does not define acceptance meaning",
                "The Coder defines acceptance meaning and encodes its own criteria",
            ),
            (
                "structural\nregression, not behavior TDD evidence",
                "behavior TDD evidence",
            ),
            (
                "The Coder does not request or wait\nfor separate RED approval from the Runner, Commander, or primary orchestrator.",
                "The Coder waits for separate RED approval.",
            ),
            (
                "Any result-affecting target-test change\ninvalidates RED evidence",
                "A result-affecting target-test change preserves its RED evidence",
            ),
            (
                "Replay the target command at the RED checkpoint and final candidate",
                "Trust the Coder's recorded command",
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
                "  may already pass, but every changed behavior needs discriminating pre-implementation failure\n"
                "  coverage;",
                "- behavior work records approved tests;",
                "run-task 关键执行控制",
            ),
            (
                "test-only RED and direct continuation",
                "skills/run-task/SKILL.md",
                "For RED-gated work, the initial Coder brief authorizes the complete test and production write\n"
                "boundary. Require the Coder to create and record the test-only RED checkpoint before production\n"
                "work, then continue directly to GREEN in the same dispatch. The Coder does not request or wait\n"
                "for separate RED approval from the Runner, Commander, or primary orchestrator.",
                "For RED-gated work, implementation may proceed before later validation.",
                "run-task 关键执行控制",
            ),
            (
                "recorded RED and same-command GREEN",
                "skills/run-task/SKILL.md",
                "After recording RED, freeze target tests and every helper that can affect their verdict. The\n"
                "Coder implements the smallest sufficient production change and obtains GREEN with the same\n"
                "target command before required regression checks. Any result-affecting target-test change\n"
                "invalidates RED evidence. Stop production work, recreate the test-only checkpoint against the\n"
                "original production baseline, record valid RED again, and then continue. Never delete, skip,\n"
                "weaken, bypass, or move production logic into a test to obtain GREEN.",
                "After recording RED, implementation may alter tests as needed.",
                "run-task 关键执行控制",
            ),
            (
                "optional refactor rule",
                "skills/run-task/SKILL.md",
                "After the first GREEN, refactor only to correct a concrete structure problem. When\n"
                "refactoring, retain a pre-refactor GREEN checkpoint and rerun the same target and required\n"
                "regression checks; otherwise skip refactoring without creating another checkpoint.",
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
                "If the full ten minutes expires without an event, the caller calls `list_agents` once.",
                "If the full ten minutes expires, immediately wait again",
            ),
            (
                "Between lifecycle events and timeout boundaries, do not poll `list_agents`",
                "Poll list_agents whenever useful",
            ),
            (
                "Do not call `list_agents` more than once for the same timeout.",
                "Call list_agents repeatedly after a timeout",
            ),
            (
                "A running dispatch remains unfinished work. Do not call `interrupt_agent`, end orchestration,\n"
                "or return a final Task result while a required direct agent is `running`.",
                "Stop a slow agent after repeated timeouts",
            ),
            (
                "If the snapshot reports `running`,\nfinish unrelated ready work at that level and return to the same maximum ten-minute\n"
                "`wait_agent` call.",
                "If that snapshot reports running, interrupt it to reclaim capacity",
            ),
            (
                "a session time or token budget are not such\nevidence",
                "time or token budget permits interruption",
            ),
            (
                "Do not send heartbeat, unchanged `running`, timeout, agent-count, or routine progress\n"
                "data to the Owner, Log, telemetry, or another agent.",
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
            "the largest\nnumber of currently blocked Tasks ready",
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
                "A terminal completion retires the agent.",
                "Any return retires the agent",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "One authorization may cover a named set of external operations against an exact target",
                "Every external operation needs separate authorization",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "| Commander, Runner, Author, Critic, Reviewer, Verifier | `gpt-5.6-sol` | `max` |",
                "| Commander, Runner, Author, Critic, Reviewer, Verifier | `gpt-5.6-terra` | `high` |",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "| Coder, Researcher | `gpt-5.6-terra` | `max` |",
                "| Coder, Researcher | `gpt-5.6-sol` | `high` |",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "It does not synthesize, compare, infer, recommend, or select.",
                "Researcher** analyzes and recommends solutions",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "These are the only GMGN agent roles.",
                "additional roles may be invented when useful",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/release/SKILL.md",
                "push the branch and tag together",
                "perform external operations in any order",
                "release 外部操作顺序",
            ),
            (
                "skills/run-task/SKILL.md",
                "it returns a structured `needs_commander` event for cross-Task or shared-",
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
                "The independent Author writes one complete recommended candidate without asking the Owner to\n"
                "approve fields or allocations separately.",
                "asks the owner to approve every allocation",
                "ROADMAP 一次批准",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "If the scheduling pass finds no explicit next consumer, remove\n"
                "the exact GMGN-managed worktree.",
                "Keep an unassigned worktree for possible future reuse",
                "Commander/Runner 权威边界",
            ),
            (
                "agents/commander.md",
                "Only the primary\norchestrator creates, resumes, or retires a Commander.",
                "Any Runner creates, resumes, or retires a Commander.",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/write-goal/SKILL.md",
                "Prepare the Goal and proposed initiation as one candidate",
                "Require initiation before preparing Goal",
                "Goal 合并批准",
            ),
            (
                "skills/run-task/SKILL.md",
                "The Commander scans the entire\ntarget-Milestone Task set",
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
        required = "| Coder, Researcher | `gpt-5.6-terra` | `max` |"
        invalid = "| Coder, Researcher | `gpt-5.6-sol` | `high` |"
        for hidden in (
            f"<!-- {required} -->",
            f"```markdown\n{required}\n```",
        ):
            with self.subTest(hidden=hidden.splitlines()[0]):
                path.write_text(
                    original.replace(required, invalid, 1) + f"\n{hidden}\n",
                    encoding="utf-8",
                )
                self.assert_rejected("Commander/Runner 权威边界")
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

    def test_rejects_candidate_review_boundary_drift(self) -> None:
        cases = (
            (
                "GMGN.md",
                "The primary\norchestrator records the Commander result mechanically and does not repeat integration or\n"
                "semantic review.",
                "The primary orchestrator performs a second integration and semantic review.",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "An Author or Coder remains assigned after a candidate checkpoint",
                "A candidate checkpoint retires its writer for later reactivation",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/code-review.md",
                "The Runner adjudicates in-Task findings and sends an accepted minimum repair to the same\nCoder",
                "Return an accepted finding to a fresh Coder",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/run-task/SKILL.md",
                "Ordinary deterministic local execution belongs to the Runner; Coder output remains supporting",
                "Ordinary deterministic local execution belongs to the primary orchestrator",
                "run-task 关键执行控制",
            ),
            (
                "agents/verifier.md",
                "checks belong to the caller.",
                "checks belong to the Verifier",
                "Commander/Runner 权威边界",
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
        path = self.root / ".codex/agents/coder.toml"
        path.write_text('name = "broken"\n', encoding="utf-8")
        self.assert_rejected("sandbox_mode 必须是字符串")

    def test_rejects_role_sandbox_drift(self) -> None:
        cases = (
            ("commander", "workspace-write", "read-only"),
            ("runner", "workspace-write", "read-only"),
            ("author", "workspace-write", "read-only"),
            ("coder", "workspace-write", "read-only"),
            ("verifier", "workspace-write", "read-only"),
            ("reviewer", "workspace-write", "read-only"),
            ("critic", "read-only", "workspace-write"),
            ("researcher", "read-only", "workspace-write"),
        )
        for role, expected, wrong in cases:
            with self.subTest(role=role):
                relative = f".codex/agents/{role}.toml"
                self.replace(
                    relative,
                    f'sandbox_mode = "{expected}"',
                    f'sandbox_mode = "{wrong}"',
                )
                self.assert_rejected(f"sandbox_mode 应为 {expected}")
                self.replace(
                    relative,
                    f'sandbox_mode = "{wrong}"',
                    f'sandbox_mode = "{expected}"',
                )

    def test_rejects_unregistered_role_profiles(self) -> None:
        markdown = self.root / "agents/extra.md"
        toml = self.root / ".codex/agents/extra.toml"
        markdown.write_text("---\nname: extra\n---\n", encoding="utf-8")
        self.assert_rejected("Claude 角色集合不一致")
        markdown.unlink()
        toml.write_text('name = "extra"\n', encoding="utf-8")
        self.assert_rejected("Codex 角色集合不一致")

    def test_rejects_legacy_role_words_on_active_surfaces(self) -> None:
        path = self.root / "GMGN.md"
        original = path.read_text(encoding="utf-8")
        legacy_role = "adjud" + "icator"
        path.write_text(original + f"\nIndependent {legacy_role} role.\n", encoding="utf-8")
        self.assert_rejected("含已删除角色词")

    def test_rejects_critic_reviewer_profile_boundary_drift(self) -> None:
        cases = (
            (".codex/agents/critic.toml", "只用于文档/语义", "可审实现与测试"),
            (".codex/agents/reviewer.toml", "不审规范文档", "可审规范文档"),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                self.replace(relative, old, new)
                self.assert_rejected(f"{relative}: 角色边界")

    def test_rejects_leaf_profile_agent_creation_drift(self) -> None:
        cases = (
            (".codex/agents/author.toml", "不得创建其他 Agent。", "可创建其他 Agent。"),
            (".codex/agents/coder.toml", "不得创建其他 Agent。", "可创建其他 Agent。"),
            (
                ".codex/agents/researcher.toml",
                "禁止修改项目文件或创建其他 Agent。",
                "可修改项目文件或创建其他 Agent。",
            ),
            (
                ".codex/agents/verifier.toml",
                "不要编辑 tracked files 或创建其他 Agent。",
                "可编辑 tracked files 或创建其他 Agent。",
            ),
            (
                ".codex/agents/critic.toml",
                "只审指定规范文档含义及最小必要的上下游上下文；不得编辑文件、扩大产品范围、裁决自己的 finding 或创建其他 Agent。",
                "只审指定规范文档含义及最小必要的上下游上下文；可编辑文件、扩大产品范围、裁决自己的 finding 或创建其他 Agent。",
            ),
            (
                ".codex/agents/reviewer.toml",
                "只审固定实现与测试候选；不得创建其他 Agent，也不主动编辑工作区。",
                "只审固定实现与测试候选；可创建其他 Agent，也可主动编辑工作区。",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                try:
                    self.assert_rejected(f"{relative}: 角色边界")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_rejects_commander_runner_coder_profile_boundary_drift(self) -> None:
        cases = (
            (
                ".codex/agents/commander.toml",
                "只有不改变候选内容的 merge 才可复用原证据",
                "任意 merge 都可复用原证据",
            ),
            (
                ".codex/agents/commander.toml",
                "集成时严格按现有锁、最新共享基线、最终候选、Git commit/tree 身份、绑定门禁、更新共享基线、释放锁的顺序执行。",
                "集成时严格按更新共享基线、现有锁、最新共享基线、最终候选、Git commit/tree 身份、绑定门禁、释放锁的顺序执行。",
            ),
            (
                ".codex/agents/runner.toml",
                "主 Session 创建或恢复适用 Commander",
                "Runner 自己创建或恢复 Commander",
            ),
            (
                ".codex/agents/runner.toml",
                "可直接创建 Coder、Researcher 和风险触发的 Verifier；",
                "不得直接创建 Coder、Researcher 和风险触发的 Verifier；",
            ),
            (
                ".codex/agents/runner.toml",
                "只有 Owner、适用权威、当前流程或 Commander brief 明确要求时才创建独立 Critic 或 Reviewer。",
                "可无条件创建独立 Critic 或 Reviewer。",
            ),
            (
                ".codex/agents/runner.toml",
                "不得创建 Commander、Author、Runner、未命名角色或上述范围以外的 Agent。",
                "可创建 Commander、Author、Runner、未命名角色或上述范围以外的 Agent。",
            ),
            (
                ".codex/agents/coder.toml",
                "不关闭 Task",
                "可关闭 Task",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                try:
                    self.assert_rejected(f"{relative}: 角色边界")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_rejects_commander_runner_boundary_drift(self) -> None:
        cases = (
            (
                "skills/gmgn/SKILL.md",
                "Only `run-task` uses a Commander for bounded global judgment and one Runner per Task.",
                "Every stage uses a Commander for global judgment.",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "only the primary orchestrator creates, resumes, and retires a Commander;",
                "a Runner creates, resumes, and retires a Commander;",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "A Runner never creates a Commander, Author, another Runner, or any unnamed role.",
                "A Runner may create a Commander, Author, another Runner, or an unnamed role.",
            ),
            (
                "skills/gmgn/references/en/code-review.md",
                "Reviewer is used only for implementation and\ntest candidates; Critic covers normative document meaning.",
                "Reviewer is used for document candidates.",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "`needs_commander` and `ready_for_integration` are transient events, not Task, Card, Log, or\nworkflow states.",
                "needs_commander and ready_for_integration are workflow states.",
            ),
            (
                "skills/run-task/SKILL.md",
                "1. acquire the existing integration lock;",
                "1. update the shared baseline before acquiring the lock;",
            ),
            (
                "GMGN.md",
                "The primary\norchestrator records the Commander result mechanically and does not repeat integration or\nsemantic review.",
                "The primary orchestrator performs a second integration and semantic review.",
            ),
            (
                "agents/coder.md",
                "Do not create other agents.",
                "Create other agents when useful.",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative, rule=old):
                self.replace(relative, old, new)
                self.assert_rejected("Commander/Runner 权威边界")

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
