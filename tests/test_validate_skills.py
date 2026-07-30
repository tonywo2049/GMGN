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
        policy["verifier"]["triggers"].append("Not Valid")
        path.write_text(json.dumps(policy), encoding="utf-8")
        self.assert_rejected("唯一 kebab-case token")

    def test_rejects_missing_wait_control(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            '{"timeout_ms": 3600000}',
            '{"timeout_ms": 60000}',
        )
        self.assert_rejected("run-task 关键执行控制")

    def test_rejects_incomplete_wait_lifecycle_controls(self) -> None:
        path = self.root / "skills/run-task/SKILL.md"
        original = path.read_text(encoding="utf-8")
        cases = (
            (
                'immediately\nre-arm `wait_agent({"timeout_ms": 3600000})`',
                "wait again eventually",
            ),
            (
                "Never call `list_agents`, send a message to the agent, inspect its workspace "
                "or logs, or issue\nanother status query merely to learn progress",
                "Poll list_agents whenever useful",
            ),
            (
                "Do not query again until a\n"
                "material lifecycle event or scheduling condition changes",
                "query again periodically",
            ),
            (
                "While any dispatched agent is\n`running`, do not call `interrupt_agent`, "
                "end the orchestration, or return a final result",
                "Stop a slow agent after repeated timeouts",
            ),
            (
                "If that snapshot reports\n`running`, finish any unrelated ready scheduling "
                "work and return to the same one-hour\n"
                "`wait_agent` call",
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

    def test_rejects_missing_single_review_limit(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "Never create, resume, or dispatch another Reviewer to recheck findings or fixes",
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
                "Accepted finding fixes do not create another\nCritic or Reviewer dispatch",
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
