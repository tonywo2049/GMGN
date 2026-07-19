#!/usr/bin/env python3
import json
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

    def set_release_version(self, relative_path: str, version: str) -> None:
        path = self.root / relative_path
        document = json.loads(path.read_text(encoding="utf-8"))
        if "plugins" in document:
            plugin_name = json.loads(
                (self.root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )["name"]
            matches = [
                entry
                for entry in document["plugins"]
                if entry.get("name", "").casefold() == plugin_name.casefold()
            ]
            self.assertEqual(len(matches), 1)
            matches[0]["version"] = version
        else:
            document["version"] = version
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def release_drift_version(self) -> str:
        current = json.loads(
            (self.root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"]
        separator = "." if "+" in current else "+"
        return f"{current}{separator}test.drift"

    def test_rejects_claude_marketplace_version_drift(self) -> None:
        self.set_release_version(
            ".claude-plugin/marketplace.json", self.release_drift_version()
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("四处发布版本不一致", result.stdout)

    def test_rejects_consistent_non_semver_release_version(self) -> None:
        for relative_path in (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".agents/plugins/marketplace.json",
            ".claude-plugin/marketplace.json",
        ):
            self.set_release_version(relative_path, "01.2.3")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("SemVer 2.0", result.stdout)

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
            ("A non-zero gate finding", "classification_complete is display only"),
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

    def test_rejects_close_hard_gate_without_target_milestone_scope(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Every hard gate is scoped to the recorded `target_milestone_id`",
            "Every hard gate is global across the project",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone target Milestone 关账范围", result.stdout)

    def test_rejects_run_task_automatic_downstream_expansion(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Cross-milestone references never expand this set automatically",
            "Cross-milestone references automatically expand this set",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task target Milestone 执行集", result.stdout)

    def test_rejects_write_task_downstream_reverse_dependency(self) -> None:
        path = self.root / "skills" / "write-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "A current or upstream Milestone must not depend on downstream",
            "A current or upstream Milestone may depend on downstream",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 跨 Milestone 依赖方向", result.stdout)

    def test_rejects_missing_or_reversed_planned_upstream_dependency_contract(self) -> None:
        path = self.root / "skills" / "write-task" / "SKILL.md"
        original = path.read_text(encoding="utf-8")
        mutations = (
            (
                "an already planned upstream Milestone",
                "an external Milestone with no ROADMAP relationship",
            ),
            (
                "an already planned upstream Milestone",
                "a planned downstream Milestone",
            ),
        )

        for removed, replacement in mutations:
            with self.subTest(replacement=replacement):
                path.write_text(
                    self.replace_required(original, removed, replacement), encoding="utf-8"
                )
                result = self.run_validator()
                self.assertEqual(result.returncode, 1)
                self.assertIn("write-task 跨 Milestone 依赖方向", result.stdout)

    def test_rejects_reopening_closed_m0_for_later_revision(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "do not reopen M0",
            "reopen M0",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("gmgn 路由 M0 历史关账", result.stdout)

    def test_rejects_docstar_global_finding_as_closure_blocker(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "A non-zero gate finding in either of the first two classes blocks",
            "Any non-zero gate finding anywhere in the corpus blocks closure",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone DocStar finding 范围", result.stdout)

    def test_rejects_docstar_unclassified_finding_as_debt(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "If evidence cannot prove\n"
            "`external-pre-existing`, scope classification is incomplete and closure is blocked",
            "If evidence cannot prove `external-pre-existing`, record the finding as debt",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone DocStar finding 范围", result.stdout)

    def test_rejects_target_ac_closed_by_deferred_label_only(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "every target-Milestone AC is completed with evidence",
            "every target-Milestone AC is implemented, explicitly deferred",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("target AC 完成语义", result.stdout)
        self.assertIn("仍允许仅 deferred", result.stdout)

    def test_rejects_chinese_reopen_selection_line_wording(self) -> None:
        path = self.root / "GMGN.zh-CN.md"
        text = path.read_text(encoding="utf-8")
        text += "\n下游发现问题时一律回归选型与架构线续开。\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("残留重开 M0/续开选型线语义", result.stdout)

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

    def test_rejects_missing_global_lane_claim_gate(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "atomically `claim` the `card_id` and canonical `worktree_path`",
            "record the card and worktree in local notes",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 全局 lane claim", result.stdout)

    def test_rejects_waiting_for_local_slot_instead_of_codex_fan_out(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "issue its `create_thread` request before the scheduler's first blocking\n"
            "wait.",
            "The scheduler waits for every local subagent before creating more work.",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 滚动补槽", result.stdout)

    def test_rejects_stale_lane_epoch_entering_review(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "a stale `ownership_epoch`, a missing/wrong `coder_ref`, a changed repository, or\n"
            "a different path is rejected before review or integration.",
            "a stale ownership record may continue into review.",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 候选锚责任", result.stdout)

    def test_rejects_lane_registry_without_git_compare_and_swap(self) -> None:
        path = self.root / "skills" / "run-task" / "scripts" / "lane_registry.py"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            '"update-ref", REGISTRY_REF, new_object_id, expected',
            '"symbolic-ref", REGISTRY_REF, new_object_id, expected',
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("lane_registry.py", result.stdout)

    def test_rejects_copy_ready_document_skeleton(self) -> None:
        path = self.root / "skills" / "gmgn" / "references" / "en" / "writing-contract.md"
        text = path.read_text(encoding="utf-8") + "\n## 5. G-R-D-T templates\n\n### Goal.md\n\n# M1 Goal\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("残留可复制文档骨架", result.stdout)


if __name__ == "__main__":
    unittest.main()
