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

    def replace_required(self, text: str, old: str, new: str) -> str:
        self.assertIn(old, text, f"mutation source missing: {old!r}")
        mutated = text.replace(old, new)
        self.assertNotEqual(mutated, text, "mutation did not change fixture")
        return mutated

    def sub_required(self, pattern: str, replacement: str, text: str, *, flags: int = 0) -> str:
        mutated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
        self.assertEqual(count, 1, f"mutation pattern did not match: {pattern!r}")
        self.assertNotEqual(mutated, text, "mutation did not change fixture")
        return mutated

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
        text = self.replace_required(text, 'name = "GMGN Code Reviewer"', "name = 1")
        text = self.replace_required(
            text, 'sandbox_mode = "read-only"', 'sandbox_mode = "workspace-wirte"'
        )
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

    def test_rejects_claude_writer_without_worktree_isolation(self) -> None:
        path = self.root / "agents" / "coder.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"), "isolation: worktree\n", ""
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("writer 必须显式 isolation: worktree", result.stdout)

    def test_rejects_missing_trigger(self) -> None:
        path = self.root / "skills" / "brainstorm" / "SKILL.md"
        text = self.replace_required(path.read_text(encoding="utf-8"), "可行性研究", "假设探索")
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("description 缺触发词", result.stdout)

    def test_rejects_run_task_stale_scan_moved_out_of_close_step(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = self.sub_required(
            r"^## 4\. Serialize integration, then close the card\n.*?(?=\n## )",
            "## 4. Serialize integration, then close the card\n\nClose it immediately.\n",
            text,
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
        text = self.sub_required(
            r"## Machine checks and checklist\n.*?(?=\n## )",
            "## Machine checks and checklist\n\nRun existing checks only.\n",
            text,
            flags=re.S,
        )
        text = self.sub_required(
            r"## Presentation and close\n.*?(?=\n## )",
            "## Presentation and close\n\nWrite receiving state after owner approval.\n",
            text,
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
                path.write_text(
                    self.replace_required(original, removed, replacement), encoding="utf-8"
                )
                result = self.run_validator()
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    "close-milestone: DocStar 或 Handoff 关账门禁缺失",
                    result.stdout,
                )

    def test_rejects_missing_controlled_change_route(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "| Goal objective, boundary, slice, non-goal, or completion picture | `write-goal` revision mode |",
            "| Goal objective, boundary, slice, non-goal, or completion picture | `roadmap` maintenance mode |",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由: 受控变更规则缺失", result.stdout)

    def test_rejects_approval_following_file_instead_of_version(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "en" / "writing-contract.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "File-content change alone does not require reapproval.",
            "Every file-content change requires reapproval.",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("writing-contract.md: 受控变更规则缺失", result.stdout)

    def test_rejects_missing_stage_revision_protocol(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "## Controlled revision",
            "## Design notes",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-design 修订态: 受控变更规则缺失", result.stdout)

    def test_rejects_new_author_for_review_fixes(self) -> None:
        path = self.root / "skills" / "write-requirement" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"), "same Author", "replacement Author"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-requirement: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_orchestrator_taking_over_execution(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "It does not write implementation",
            "It writes implementation",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_milestone_wide_single_card_barrier(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + "\nImplement one task card\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("milestone-wide 单卡串行屏障", result.stdout)

    def test_rejects_ready_set_refill_waiting_for_lane_close(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Recompute the ready set after every agent return, integration, conflict, or block.",
            "Recompute the ready set only after the active lane closes.",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 滚动补槽", result.stdout)

    def test_rejects_writer_without_exact_baseline_head(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "and requires\n`git rev-parse HEAD` to equal that exact commit.",
            "and records HEAD without comparing it to the approved baseline.",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 工作区基线锁", result.stdout)

    def test_rejects_claude_resume_without_explicit_degradation(self) -> None:
        path = (
            self.root / "skills" / "gmgn" / "references" / "en" /
            "dispatch-and-handoff.md"
        )
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "enter the existing `agent-unavailable` explicit-replacement rule; do not claim a targeted\n"
            "  recheck, the same Verifier, or the same Integrator.",
            "silently create a replacement and treat it as the original agent.",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("dispatch-and-handoff.md", result.stdout)

    def test_rejects_unconditional_rebase_on_baseline_advance(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "An advanced shared baseline does not by itself require a rebase.",
            "If shared baseline advanced, enter `rebase-required`.",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 两阶段集成", result.stdout)

    def test_rejects_integration_failure_without_clean_restore(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "leave the original\n`shared_baseline_anchor` unchanged",
            "advance the original `shared_baseline_anchor` despite failure",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 两阶段集成", result.stdout)

    def test_rejects_missing_local_candidate_commit(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "parseable local commit SHA as immutable `candidate_anchor`",
            "uncommitted working tree as candidate",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 候选锚责任", result.stdout)

    def test_rejects_card_only_general_verifier(self) -> None:
        path = self.root / "agents" / "verifier.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "This general Verifier may run document checks, run-task candidate/integration evidence, or\n`close-milestone` regression.",
            "This Verifier only handles run-task cards.",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/verifier.md", result.stdout)

    def test_rejects_post_integration_without_current_dispatch_path(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "current `worktree_path`",
            "original card `worktree_path`",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 两阶段集成", result.stdout)

    def test_rejects_worktree_as_conflict_solver(self) -> None:
        path = self.root / "GMGN.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "A worktree isolates files and the index. It does not resolve Git merge\nconflicts",
            "A worktree resolves merge conflicts",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("worktree 误写成冲突解决机制", result.stdout)

    def test_rejects_card_closed_before_integration(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "Only now set the card work status to `closed`",
            "Set the card work status to `closed` before integration",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("卡关账前缺少过期断言扫描", result.stdout)

    def test_rejects_missing_integration_queue(self) -> None:
        path = (
            self.root / "skills" / "gmgn" / "references" / "en" /
            "dispatch-and-handoff.md"
        )
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "integration_queue_ref",
            "merge_queue",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("integration_queue_ref", result.stdout)

    def test_rejects_copy_ready_document_skeleton(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "en" / "writing-contract.md"
        text = path.read_text(encoding="utf-8") + "\n## 5. G-R-D-T templates\n\n### Goal.md\n\n# M1 Goal\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("残留可复制文档骨架", result.stdout)


if __name__ == "__main__":
    unittest.main()
