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
                "Normal Task execution does not use an Author. The Coder creates or resumes Card/Log,\nmechanically updates only its accepted Task row's execution pointer and macro status",
                "the primary orchestrator may implement one lane",
            ),
            (
                "This setup has no standalone preparation checkpoint",
                "The Coder returns a preparation checkpoint for Runner confirmation",
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
                "The Coder does not request or wait for separate RED approval from the\nRunner, Commander, or primary orchestrator, and does not return an interim RED checkpoint for\nconfirmation.",
                "The Coder returns RED and waits for Runner confirmation.",
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
                "production-unchanged RED and direct continuation",
                "skills/run-task/SKILL.md",
                "The initial Coder brief names the exact accepted Task row and limits its `Task.md` write to\n"
                "`execution` and macro `status`. For RED-gated work, it authorizes the complete Task-local\n"
                "document, test, and production write boundary. Require the Coder to create and record the\n"
                "production-unchanged RED checkpoint before production work, then continue directly to GREEN\n"
                "in the same dispatch. The Coder does not request or wait for separate RED approval from the\n"
                "Runner, Commander, or primary orchestrator, and does not return an interim RED checkpoint for\n"
                "confirmation.",
                "For RED-gated work, implementation may proceed before later validation.",
                "run-task 关键执行控制",
            ),
            (
                "recorded RED and same-command GREEN",
                "skills/run-task/SKILL.md",
                "After recording RED, freeze target tests and every helper that can affect their verdict. The\n"
                "Coder implements the smallest sufficient production change and obtains GREEN with the same\n"
                "target command before required regression checks. Any result-affecting target-test change\n"
                "invalidates RED evidence. Stop production work, recreate the production-unchanged checkpoint\n"
                "against the original production baseline, record valid RED again, and then continue. Never\n"
                "delete, skip, weaken, bypass, or move production logic into a test to obtain GREEN.",
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
                "Create the role by its exact installed name: `gmgn_commander`",
                "Create the role by its task label instead of an installed Agent name",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "named-Agent selector (`agent_type` in runtimes that expose the field)",
                "task message alone without a named-Agent selection",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                'set `fork_turns="none"`',
                'set `fork_turns="all"`',
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Model, reasoning effort, sandbox, and stable role instructions come from the installed TOML",
                "Model and reasoning effort are repeated in every brief",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Resolved workflow selections belong in the brief; the selected procedures do not.",
                "Every brief repeats the selected workflow procedures.",
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
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Author, Coder, Critic, Researcher, Reviewer, and Verifier do not create agents.",
                "Every role may create agents whenever the platform permits it.",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "The TOML sandbox is the requested\nruntime mode; active parent permissions plus the workflow and brief remain the operative\nboundaries.",
                "The TOML sandbox alone is the operative permission boundary.",
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
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "A Commander never creates another Commander.",
                "A Runner may create or resume a Commander.",
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
            (
                "skills/run-task/SKILL.md",
                "A Commander return\nseparates any caller-only mechanical workspace preparation from each complete Runner brief.",
                "A Commander copies caller-only workspace preparation into every Runner brief.",
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
        required = "Create the role by its exact installed name: `gmgn_commander`"
        invalid = "Create the role without an installed Agent name"
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
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Commander may be used only in run-task",
            ),
            (
                "skills/run-task/SKILL.md",
                "Scan only the separately confirmed execution set",
            ),
            (
                "skills/run-task/SKILL.md",
                "Create one pull request per commit",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "A replacement Runner creates a new Task branch",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "Delete every Task branch when its Runner exits",
            ),
            (
                "skills/run-task/SKILL.md",
                "Mix the upstream semantic change into the Runner pull request",
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
        path = self.root / ".codex/agents/gmgn_coder.toml"
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
                relative = f".codex/agents/gmgn_{role}.toml"
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

    def test_rejects_role_runtime_and_agent_tool_drift(self) -> None:
        cases = (
            (
                ".codex/agents/gmgn_coder.toml",
                'model = "gpt-5.6-luna"',
                'model = "gpt-5.6-sol"',
                "model 应为 gpt-5.6-luna",
            ),
            (
                ".codex/agents/gmgn_commander.toml",
                'model_reasoning_effort = "max"',
                'model_reasoning_effort = "high"',
                "model_reasoning_effort 应为 max",
            ),
            (
                ".codex/agents/gmgn_commander.toml",
                'name = "gmgn_commander"',
                'name = "commander"',
                "name 应为 gmgn_commander",
            ),
        )
        for relative, old, new, expected in cases:
            with self.subTest(relative=relative, field=old):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(original.replace(old, new, 1), encoding="utf-8")
                try:
                    self.assert_rejected(expected)
                finally:
                    path.write_text(original, encoding="utf-8")

        commander = self.root / ".codex/agents/gmgn_commander.toml"
        original = commander.read_text(encoding="utf-8")
        commander.write_text(original + "\n[agents]\nenabled = false\n", encoding="utf-8")
        self.assert_rejected("不应覆盖 [agents]")

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
            (".codex/agents/gmgn_critic.toml", "不审查实现代码", "可以审查实现代码"),
            (
                ".codex/agents/gmgn_reviewer.toml",
                "按照任务书指定的 code-review contract 和权威，独立审查一份固定的实现与测试候选。",
                "按照任务书指定的规范审查规则和权威，独立审查一份固定的规范文档候选。",
            ),
        )
        for relative, old, new in cases:
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn(old, original)
                path.write_text(
                    original.replace(old, new, 1),
                    encoding="utf-8",
                )
                try:
                    self.assert_rejected(f"{relative}: 角色边界")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_rejects_leaf_profile_agent_setting_drift(self) -> None:
        for role in ("author", "coder", "researcher", "verifier", "critic", "reviewer"):
            relative = f".codex/agents/gmgn_{role}.toml"
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn("enabled = false", original)
                path.write_text(
                    original.replace("enabled = false", "enabled = true", 1),
                    encoding="utf-8",
                )
                try:
                    self.assert_rejected("[agents].enabled 必须为 false")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_rejects_leaf_profile_creation_instruction_drift(self) -> None:
        for role in ("author", "coder", "researcher", "verifier", "critic", "reviewer"):
            relative = f".codex/agents/gmgn_{role}.toml"
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                self.assertIn("不创建其他 Agent", original)
                path.write_text(
                    original.replace("不创建其他 Agent", "可自行创建其他 Agent", 1),
                    encoding="utf-8",
                )
                try:
                    self.assert_rejected(f"{relative}: 角色边界")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_rejects_commander_runner_coder_profile_boundary_drift(self) -> None:
        cases = (
            (
                ".codex/agents/gmgn_commander.toml",
                "创建任意已定义的命名 Agent",
                "不得创建任何 Agent",
            ),
            (
                ".codex/agents/gmgn_commander.toml",
                "同一 Commander dispatch 内执行对应的 owning Skill",
                "把上游工作退回主 Session",
            ),
            (
                ".codex/agents/gmgn_commander.toml",
                "当前 Workflow 决定你所在的阶段和具体职责",
                "Commander 只能用于 run-task",
            ),
            (
                ".codex/agents/gmgn_commander.toml",
                "将准备指令与 Runner 任务书分开返回",
                "将准备指令复制进 Runner 任务书",
            ),
            (
                ".codex/agents/gmgn_runner.toml",
                "不得创建 Commander",
                "可以创建 Commander",
            ),
            (
                ".codex/agents/gmgn_runner.toml",
                "不得更新共享基线",
                "可以更新共享基线",
            ),
            (
                ".codex/agents/gmgn_runner.toml",
                "把精确 closure facts 返回同一 Coder 写入 Log 和 Task 状态",
                "Runner 自己写入 Log 和 Task 状态",
            ),
            (
                ".codex/agents/gmgn_coder.toml",
                "不执行远端写入",
                "执行远端写入",
            ),
            (
                ".codex/agents/gmgn_coder.toml",
                "Task.md 只改自己行的 execution/status",
                "Task.md 可以修改任意任务行",
            ),
            (
                ".codex/agents/gmgn_coder.toml",
                "有效 RED 记录后不返回确认，直接继续 GREEN",
                "RED 后返回 Runner 等待确认",
            ),
            (
                ".codex/agents/gmgn_coder.toml",
                "无法建立有效 RED 时，不得开始生产实现",
                "无效 RED 也可以继续生产实现",
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
                "Any stage may select one Commander for a bounded planning, scheduling, conflict, upstream-\nreturn, or integration matter.",
                "Commander may be used only in run-task.",
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
                "agents/commander.md",
                "keep caller-only mechanical workspace setup separate from\neach Runner brief.",
                "copy caller-only mechanical workspace setup into\neach Runner brief.",
            ),
            (
                "agents/coder.md",
                "Before recording a checkpoint as behavior RED",
                "Any failing checkpoint is behavior RED",
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

    def test_rejects_git_collaboration_boundary_drift(self) -> None:
        cases = (
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "The branch and pull request belong to\n"
                "the Task-repository change, not to an agent identity.",
                "The branch and pull request belong to each transient agent identity.",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/run-task/SKILL.md",
                "creates or marks ready the single pull request for that repository",
                "creates one pull request for every candidate commit",
                "run-task 关键执行控制",
            ),
            (
                "skills/gmgn/references/en/writing-rules.md",
                "It never embeds the commit reference of the same commit that\n"
                "contains that Log update.",
                "It embeds the current commit reference in that same commit.",
                "writing-rules 机器字段",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "resumes the same branch and pull request instead of creating another pair.",
                "creates another branch and pull request instead of resuming the existing pair.",
                "Commander/Runner 权威边界",
            ),
            (
                "skills/gmgn/references/en/dispatch-and-handoff.md",
                "After verified integration, remove the managed worktree and delete its no-longer-needed local\n"
                "Task branch only after native Git or host evidence proves the candidate integrated.",
                "Delete the Task branch before integration finishes.",
                "Commander/Runner 权威边界",
            ),
        )
        for relative, old, new, expected in cases:
            with self.subTest(relative=relative, rule=old):
                self.replace(relative, old, new)
                self.assert_rejected(expected)

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
