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

    def test_rejects_missing_trigger(self) -> None:
        path = self.root / "skills" / "brainstorm" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace("可行性研究", "假设探索")
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("description 缺触发词", result.stdout)

    def test_rejects_run_task_stale_scan_moved_out_of_close_step(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        close_step = next(
            index for index, line in enumerate(lines) if line.startswith("6. **卡关账**:")
        )
        lines[close_step] = "6. **卡关账**:台账与追踪矩阵同批刷新。"
        lines.append(
            "Task.md 过期断言 待执行 未创建 未运行 待确认 机械刷新 git diff --check"
        )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("卡关账前缺少过期断言扫描", result.stdout)

    def test_rejects_close_milestone_guards_moved_out_of_their_sections(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"## 机检与核对\n.*?(?=\n## )",
            "## 机检与核对\n\n只运行项目现有检查。\n",
            text,
            count=1,
            flags=re.S,
        )
        text = re.sub(
            r"## 呈报与收尾\n.*?(?=\n## )",
            "## 呈报与收尾\n\n负责人批准后写接手信息。\n",
            text,
            count=1,
            flags=re.S,
        )
        text += "\nclassification_complete 退出码 Handoff 性质=记述\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone: DocStar 或 Handoff 关账门禁缺失", result.stdout)

    def test_rejects_close_milestone_guard_semantic_regressions(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        original = path.read_text(encoding="utf-8")
        mutations = (
            ("非零 finding 就是红灯", "classification_complete 仅作展示"),
            ("类型必须复用或登记到项目分类映射", "类型可自由填写"),
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


if __name__ == "__main__":
    unittest.main()
