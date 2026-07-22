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
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"))

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

    def test_rejects_missing_task_decomposition_objective(self) -> None:
        self.replace(
            "skills/write-task/SKILL.md",
            "The objective is useful parallelism, not more task cards.",
            "The objective is to create as many task cards as possible.",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 紧凑索引契约", result.stdout)

    def test_rejects_missing_roadmap_acceptance_picture(self) -> None:
        self.replace(
            "skills/roadmap/SKILL.md",
            "high-level end-to-end or integration scenarios",
            "general completion notes",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("roadmap 验收图景契约", result.stdout)

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
            "There is no periodic list interval",
            "Use a periodic list interval",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由契约", result.stdout)

    def test_rejects_verifier_before_review_clear(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "Do not dispatch a Verifier while relevant Critic or Reviewer blockers remain",
            "Dispatch a Verifier while review blockers remain",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_unbatched_review_loop(self) -> None:
        self.replace(
            "skills/run-task/SKILL.md",
            "return before editing.",
            "return and edit immediately.",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行与验证契约", result.stdout)

    def test_rejects_second_review_pass(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nAfter fixes, dispatch another fresh Reviewer.\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("单轮审查契约含二次复核指令", result.stdout)

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


if __name__ == "__main__":
    unittest.main()
