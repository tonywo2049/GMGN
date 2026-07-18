#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ValidateSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"),
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

    def test_rejects_malformed_openai_yaml(self) -> None:
        path = self.root / "skills" / "gmgn" / "agents" / "openai.yaml"
        path.write_text(
            'interface:\n  display_name: "GMGN\n  short_description: "工作流"\n'
            '  default_prompt: "请用 $gmgn"\n',
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("YAML 标量无效", result.stdout)

    def test_rejects_malformed_role_toml(self) -> None:
        path = self.root / ".codex" / "agents" / "reviewer.toml"
        path.write_text('name = "unterminated\n', encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("TOML 无效", result.stdout)

    def test_rejects_invalid_role_semantics(self) -> None:
        path = self.root / ".codex" / "agents" / "reviewer.toml"
        text = path.read_text(encoding="utf-8")
        text = text.replace('name = "GMGN Code Reviewer"', "name = 1")
        text = text.replace('sandbox_mode = "read-only"', 'sandbox_mode = "workspace-wirte"')
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("字段类型无效", result.stdout)
        self.assertIn("sandbox_mode 无效", result.stdout)

    def test_rejects_missing_claude_plugin_agent(self) -> None:
        (self.root / "agents" / "author.md").unlink()

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/author.md", result.stdout)

    def test_rejects_missing_trigger(self) -> None:
        path = self.root / "skills" / "brainstorm" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace("可行性研究", "假设探索")
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("description 缺触发词", result.stdout)

    def test_rejects_run_task_stale_scan_moved_out_of_close_step(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"^6\. \*\*Card close\*\*.*?(?=\n\n## Exit)",
            "6. **Card close** — refresh the ledger and matrix.",
            text,
            count=1,
            flags=re.M | re.S,
        )
        text += (
            "Task.md stale assertions not-started not created not run awaiting confirmation "
            "Mechanically refresh git diff --check\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("卡关账前缺少过期断言扫描", result.stdout)

    def test_rejects_close_milestone_guards_moved_out_of_their_sections(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"## Machine checks and checklist\n.*?(?=\n## )",
            "## Machine checks and checklist\n\nRun existing checks only.\n",
            text,
            count=1,
            flags=re.S,
        )
        text = re.sub(
            r"## Presentation and close\n.*?(?=\n## )",
            "## Presentation and close\n\nWrite receiving state after owner approval.\n",
            text,
            count=1,
            flags=re.S,
        )
        text += "\nclassification_complete non-zero gate finding Handoff type: handoff nature: descriptive\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone: DocStar 或 Handoff 关账门禁缺失", result.stdout)

    def test_rejects_close_milestone_guard_semantic_regressions(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        original = path.read_text(encoding="utf-8")
        mutations = (
            ("a non-zero gate finding", "classification_complete is display only"),
            ("reuse a registered type/token", "invent any type token"),
        )

        for removed, replacement in mutations:
            with self.subTest(removed=removed):
                path.write_text(original.replace(removed, replacement), encoding="utf-8")
                result = self.run_validator()
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "close-milestone: DocStar 或 Handoff 关账门禁缺失",
                    result.stdout,
                )

    def test_rejects_missing_controlled_change_route(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace(
            "| Goal objective, boundary, slice, non-goal, or completion picture | `write-goal` revision mode |",
            "| Goal objective, boundary, slice, non-goal, or completion picture | `roadmap` maintenance mode |",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由: 受控变更规则缺失", result.stdout)

    def test_rejects_approval_following_file_instead_of_version(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "en" / "writing-contract.md"
        text = path.read_text(encoding="utf-8").replace(
            "File-content change alone does not require reapproval.",
            "Every file-content change requires reapproval.",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("writing-contract.md: 受控变更规则缺失", result.stdout)

    def test_rejects_missing_stage_revision_protocol(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace(
            "## Controlled revision",
            "## Design notes",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-design 修订态: 受控变更规则缺失", result.stdout)

    def test_rejects_new_author_for_review_fixes(self) -> None:
        path = self.root / "skills" / "write-requirement" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace("same Author", "replacement Author")
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-requirement: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_orchestrator_taking_over_execution(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace(
            "leave command execution to the Reviewer/Verifier",
            "have the orchestrator replay targeted commands",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_copy_ready_document_skeleton(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "en" / "writing-contract.md"
        text = path.read_text(encoding="utf-8") + "\n## 5. G-R-D-T templates\n\n### Goal.md\n\n# M1 Goal\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("残留可复制文档骨架", result.stdout)


if __name__ == "__main__":
    unittest.main()
