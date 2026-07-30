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
            "agent_wait_timeout_ms = 3600000",
            "agent_wait_timeout_ms = 60000",
        )
        self.assert_rejected("run-task 关键执行控制")

    def test_rejects_incomplete_wait_lifecycle_controls(self) -> None:
        path = self.root / "skills/run-task/SKILL.md"
        original = path.read_text(encoding="utf-8")
        cases = (
            (
                "immediately\nre-arm the same one-hour wait",
                "wait again eventually",
            ),
            (
                "Use one\n`list_agents` snapshot only when a real scheduling/capacity "
                "decision cannot be made from\nreceived lifecycle events or those events conflict",
                "Use list_agents whenever useful",
            ),
            (
                "do not query again until a material\n"
                "lifecycle event or scheduling condition changes",
                "query again periodically",
            ),
            (
                "Do not interrupt, terminate, or kill an agent merely because it is silent, "
                "slow, has not\nreturned content, or crossed one or more wait timeouts",
                "Stop a slow agent after repeated timeouts",
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

    def test_rejects_missing_two_round_limit(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "Never dispatch a third Reviewer",
            "Continue reviewing until no findings remain",
        )
        self.assert_rejected("run-task 关键执行控制")

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
