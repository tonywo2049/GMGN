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

    def test_rejects_release_repeating_closure_review_for_exact_anchor(self) -> None:
        path = self.root / "skills" / "release" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Do not dispatch another closure Author",
            "Dispatch another closure Author",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("release 证据复用契约缺失", result.stdout)

    def test_rejects_exact_anchor_reuse_without_stable_evidence_inputs(self) -> None:
        path = self.root / "skills" / "release" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Only when those inputs are unchanged",
            "Regardless of whether those inputs changed",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("release 证据复用契约缺失", result.stdout)

    def test_rejects_unconditional_full_regression_on_release_retry(self) -> None:
        mutations = (
            ("skills/release/SKILL.md", "Every release retry must rerun full regression."),
            ("GMGN.md", "Every release must rerun full regression."),
            ("GMGN.zh-CN.md", "每次发布必须运行完整回归。"),
            ("GMGN.zh-CN.md", "每次发布都需要完整回归。"),
            ("GMGN.zh-CN.md", "每次发布均应当执行组合审查。"),
        )
        for relative_path, mutation in mutations:
            with self.subTest(path=relative_path):
                path = self.root / relative_path
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\n" + mutation + "\n", encoding="utf-8")
                result = self.run_validator()
                path.write_text(original, encoding="utf-8")
                self.assertEqual(result.returncode, 1)
                self.assertIn("发布不得无条件重做关账审查", result.stdout)

    def test_allows_negated_release_regression_rule(self) -> None:
        mutations = (
            ("GMGN.md", "Not every release must rerun full regression."),
            ("GMGN.zh-CN.md", "并非每次发布都需要完整回归。"),
            ("GMGN.zh-CN.md", "每次发布并非都需要完整回归。"),
            ("GMGN.zh-CN.md", "每次发布不需要组合审查。"),
            ("GMGN.zh-CN.md", "每次发布必须说明不需要完整回归。"),
        )
        for relative_path, mutation in mutations:
            path = self.root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8") + "\n" + mutation + "\n",
                encoding="utf-8",
            )

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_closure_without_persisted_release_evidence_tuple(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "persist the release evidence tuple",
            "summarize release evidence in the current session",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone 缺发布证据交接", result.stdout)

    def test_rejects_public_metadata_without_release_capability(self) -> None:
        mutations = (
            (
                ".codex-plugin/plugin.json",
                (("accepted release", "milestone closure"), ("版本发布", "里程碑关账")),
            ),
            (
                ".claude-plugin/marketplace.json",
                (("accepted release", "closure"), ("版本发布", "关账")),
            ),
        )
        for relative_path, replacements in mutations:
            with self.subTest(path=relative_path):
                path = self.root / relative_path
                original = path.read_text(encoding="utf-8")
                mutated = original
                for old, new in replacements:
                    mutated = self.replace_required(mutated, old, new)
                path.write_text(mutated, encoding="utf-8")
                result = self.run_validator()
                path.write_text(original, encoding="utf-8")
                self.assertEqual(result.returncode, 1)
                self.assertIn("必须描述 release/发布能力", result.stdout)

    def test_rejects_mechanical_release_without_allowed_diff_record(self) -> None:
        path = self.root / "GMGN.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "the exact\n`allowed_diff`",
            "a general\ndiff summary",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("GMGN.md 发布证据复用语义缺失", result.stdout)

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

    def test_rejects_task_execution_log_contract_regressions(self) -> None:
        path = self.root / "skills" / "write-task" / "SKILL.md"
        original = path.read_text(encoding="utf-8")
        mutations = (
            ("replace superseded state", "append every execution event"),
            ("Never accumulate all cards", "Accumulate all cards"),
            ("`nature: descriptive`", "`nature: normative`"),
            ("Promote any discovered semantic change", "Keep any discovered semantic change only in the log"),
        )

        for removed, replacement in mutations:
            with self.subTest(removed=removed):
                path.write_text(
                    self.replace_required(original, removed, replacement), encoding="utf-8"
                )
                result = self.run_validator()
                self.assertEqual(result.returncode, 1)
                self.assertIn("write-task 当前快照与单卡执行日志", result.stdout)

    def test_rejects_run_task_eager_execution_log_read(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Do not read execution history on a normal initial dispatch",
            "Read all execution history on every normal initial dispatch",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行日志读取与集成边界", result.stdout)

    def test_rejects_run_task_whole_log_read_on_resume(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Start at the card's anchored `latest_event`, then extract only that event and links\nneeded for the unresolved cycle; do not ingest the whole log",
            "Ingest the whole execution log on every resume",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行日志读取与集成边界", result.stdout)

    def test_rejects_appended_task_execution_contradictions(self) -> None:
        mutations = (
            (
                "skills/run-task/SKILL.md",
                "Always read the whole execution log and all of Task.md on every initial card dispatch.",
            ),
            (
                "skills/run-task/SKILL.md",
                "每次初次任务卡派发都必须读取整份执行日志和全部 Task.md。",
            ),
            (
                "skills/run-task/SKILL.md",
                "Failed implementation candidates may directly advance shared_baseline_anchor.",
            ),
            (
                "skills/run-task/SKILL.md",
                "失败实现候选可以直接推进 shared_baseline_anchor。",
            ),
            (
                "skills/run-task/SKILL.md",
                "Set runtime lane to node-complete before final Task/log closure batch is committed.",
            ),
            (
                "skills/run-task/SKILL.md",
                "在最终 Task 与日志关账批次提交前把运行态 lane 设为 node-complete。",
            ),
            (
                "skills/write-task/SKILL.md",
                "Task.md must append every detailed attempt.",
            ),
            (
                "skills/write-task/SKILL.md",
                "Use one project-wide execution log.",
            ),
            (
                "skills/write-task/SKILL.md",
                "Task.md 必须追加每次详细尝试。",
            ),
            (
                "skills/write-task/SKILL.md",
                "使用一个项目级执行日志。",
            ),
            (
                "skills/run-task/SKILL.md",
                "Always read the whole execution log\non every initial card dispatch.",
            ),
            (
                "skills/run-task/SKILL.md",
                "Do not skip the Task card, but always read the whole execution log on every initial card dispatch.",
            ),
            (
                "skills/run-task/SKILL.md",
                "不得跳过 Task 卡，但是每次初次任务卡派发都必须读取整份执行日志。",
            ),
        )

        for relative_path, mutation in mutations:
            with self.subTest(path=relative_path, mutation=mutation):
                path = self.root / relative_path
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\n" + mutation + "\n", encoding="utf-8")
                result = self.run_validator()
                path.write_text(original, encoding="utf-8")
                self.assertEqual(result.returncode, 1)
                self.assertIn("Task 执行日志冲突规则", result.stdout)

    def test_allows_explicit_task_execution_guard_sentences(self) -> None:
        guards = {
            "skills/run-task/SKILL.md": (
                "Do not always read the whole execution log on every initial card dispatch.",
                "必须防止每次初次任务卡派发读取整份执行日志。",
                "Failed implementation candidates may not directly advance shared_baseline_anchor.",
                "失败实现候选不可以直接推进 shared_baseline_anchor。",
                "Do not set runtime lane to node-complete before final Task/log closure is committed.",
                "不得在最终 Task 与日志关账提交前把运行态 lane 设为 node-complete。",
            ),
            "skills/write-task/SKILL.md": (
                "Task.md must not append every detailed attempt. Never use a single project-wide execution log.",
                "Task.md 必须不追加每次详细尝试。禁止使用一个项目级执行日志。",
            ),
        }

        for relative_path, sentences in guards.items():
            path = self.root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8") + "\n" + "\n".join(sentences) + "\n",
                encoding="utf-8",
            )

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_run_task_without_first_event_log_creation(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "A successful claim is the card's first durable execution event",
            "A successful claim requires no durable record",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 执行日志读取与集成边界", result.stdout)

    def test_rejects_legacy_task_migration_without_old_anchor(self) -> None:
        path = self.root / "skills" / "write-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Bind `legacy_task_anchor` to the pre-migration commit",
            "Delete the pre-migration version before editing",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 当前快照与单卡执行日志", result.stdout)

    def test_rejects_execution_log_without_exact_task_card_link(self) -> None:
        path = self.root / "skills" / "write-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "`upstream` as a\n  real relative link to the exact Task card anchor",
            "`upstream` as a plain-text card ID",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-task 当前快照与单卡执行日志", result.stdout)

    def test_rejects_close_with_stale_latest_event(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "its `latest_event` must resolve inside that log to the final closure event",
            "its `latest_event` may remain stale after closure",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("close-milestone/SKILL.md", result.stdout)

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

    def test_rejects_new_writer_for_review_fixes(self) -> None:
        path = self.root / "skills" / "write-requirement" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"), "same recorded writer", "replacement writer"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-requirement: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_mandatory_author_for_whitepaper(self) -> None:
        path = self.root / "skills" / "brainstorm" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Prefer the primary\nsession because it already holds the complete Brainstorm context",
            "Always delegate to an Author agent even when the primary\nsession already holds the complete Brainstorm context",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("brainstorm writer 选择", result.stdout)

    def test_rejects_fixed_downstream_author_separation(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nAll downstream document nodes keep an Author agent.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("文档 writer 不得退回固定角色分离", result.stdout)

    def test_rejects_appended_mandatory_author_rule(self) -> None:
        path = self.root / "skills" / "roadmap" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nROADMAP must be written by an Author agent.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("文档 writer 不得退回固定角色分离", result.stdout)

    def test_rejects_each_specification_document_requiring_author(self) -> None:
        path = self.root / "skills" / "roadmap" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nEach specification document must use an Author agent.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("文档 writer 不得退回固定角色分离", result.stdout)

    def test_rejects_appended_chinese_mandatory_author_rule(self) -> None:
        path = self.root / "GMGN.zh-CN.md"
        text = path.read_text(encoding="utf-8") + "\nRequirement 必须由 Author agent 编写。\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("文档 writer 不得退回固定角色分离", result.stdout)

    def test_rejects_document_integration_delegation(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "The primary orchestrator applies accepted mechanical",
            "A delegated worker applies accepted mechanical",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-design: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_removed_role_name_in_skill(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nEvery document candidate requires an Integrator.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("残留已删除的集成角色标识", result.stdout)

    def test_rejects_integrator_ref_in_skill(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nStore integrator_ref on each document candidate.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("残留已删除的集成角色标识", result.stdout)

    def test_rejects_renamed_delegated_merge_worker(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nDelegate accepted-candidate integration to a merge worker.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("集成职责不得委派给 agent/worker", result.stdout)

    def test_rejects_renamed_chinese_integration_agent(self) -> None:
        path = self.root / "skills" / "write-design" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\n将共享基线集成交给集成 agent。\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("集成职责不得委派给 agent/worker", result.stdout)

    def test_allows_delegated_post_integration_verification(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nDelegate a Verifier for post-integration verification.\n"
            "派发 Verifier 做集成后验证。\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_allows_implementation_and_closure_role_boundaries(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nThe orchestrator does not draft implementation code.\n"
            "The primary orchestrator serially integrates accepted implementation cards.\n"
            "Closure requires a closure Author and primary-session integration.\n"
            "主编排者不代做编码。\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_allows_conditional_document_role_guards(self) -> None:
        path = self.root / "skills" / "gmgn" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nFor ROADMAP, the orchestrator must dispatch an Author only when writing was delegated.\n"
            "ROADMAP must receive a new anchor when revised by an Author agent.\n"
            "The primary orchestrator must not edit ROADMAP while its delegated Author is active.\n"
            "Requirement 必须在写作已委派时使用 Author。\n"
            "主编排者不得在受委派 Author 活动时编辑 ROADMAP。\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_claude_author_mandatory_for_every_document(self) -> None:
        path = self.root / "agents" / "author.md"
        text = path.read_text(encoding="utf-8") + (
            "\nThis Author is required for every document node.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("文档 writer 不得退回固定角色分离", result.stdout)

    def test_rejects_restored_claude_integrator_agent(self) -> None:
        path = self.root / "agents" / "integrator.md"
        path.write_text("---\nname: integrator\n---\nremoved role\n", encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("已删除的集成角色 agent 文件不得恢复", result.stdout)

    def test_rejects_codex_author_mandatory_for_every_document(self) -> None:
        path = self.root / ".codex" / "agents" / "author.toml"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            '\n"""\n',
            '\nAuthor 每个规格文档节点都必须使用。\n"""\n',
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("文档 writer 不得退回固定角色分离", result.stdout)

    def test_rejects_restored_codex_integrator_agent(self) -> None:
        path = self.root / ".codex" / "agents" / "integrator.toml"
        path.write_text(
            'name = "removed"\ndescription = "removed"\n',
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("已删除的集成角色 agent 文件不得恢复", result.stdout)

    def test_rejects_writer_self_review_in_document_stage(self) -> None:
        path = self.root / "skills" / "write-goal" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "dispatch an independent Critic",
            "have the recorded writer self-review",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("write-goal: 缺 agent 生命周期约束", result.stdout)

    def test_rejects_missing_task_specific_self_check(self) -> None:
        path = self.root / "skills" / "brainstorm" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "perform a task-specific self-check and correct defects",
            "write a generic compliance summary",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("brainstorm 自检与风险披露", result.stdout)

    def test_rejects_fixed_reflection_footer(self) -> None:
        path = self.root / "skills" / "brainstorm" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nEnd every substantive response with **Reflection**: "
            "weakest assumption; neglected counterexample.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("固定 Reflection 规则回退", result.stdout)

    def test_rejects_fixed_weakest_assumption_field(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + "\nRequire a weakest assumption field.\n"
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("固定 Reflection 规则回退", result.stdout)

    def test_allows_task_specific_weakest_assumption_disclosure(self) -> None:
        path = self.root / "skills" / "close-milestone" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\nA reported material risk may identify its actual weakest assumption.\n"
            "Requirement evidence shows the actual weakest assumption is material.\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_role_risk_trigger_without_conclusion(self) -> None:
        path = self.root / "agents" / "coder.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "change a conclusion, decision, acceptance,\nor downstream work",
            "change a decision, acceptance,\nor downstream work",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/coder.md 自检与风险披露", result.stdout)

    def test_rejects_closure_author_without_unconditional_risk_disclosure(self) -> None:
        path = self.root / "agents" / "author.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "Closure-author returns always state remaining material risks or that none are known.",
            "Closure-author returns follow the ordinary disclosure rule.",
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("agents/author.md 关账风险披露", result.stdout)

    def test_rejects_unconditional_primary_coder_takeover(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(path.read_text(encoding="utf-8"),
            "When\nno implementation lane can currently run in parallel with useful orchestrator work, it may\nexplicitly bind itself as one lane's Coder under the rules below.",
            "It may always bind itself as any lane's Coder.",
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

    def test_rejects_run_task_parent_context_inheritance(self) -> None:
        path = self.root / "skills" / "run-task" / "SKILL.md"
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            'Never use\n`fork_turns="all"` or `fork_context=true` for a run-task role.',
            "Let every run-task role inherit the parent conversation.",
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-task 派发上下文", result.stdout)

    def test_rejects_claude_resume_without_explicit_degradation(self) -> None:
        path = (
            self.root / "skills" / "gmgn" / "references" / "en" /
            "dispatch-and-handoff.md"
        )
        text = self.replace_required(
            path.read_text(encoding="utf-8"),
            "enter the existing `agent-unavailable` explicit-replacement rule; do not claim a targeted\n"
            "  recheck or the same Verifier.",
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
            "restore the preceding clean\n`shared_baseline_anchor`",
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
            "These closure fields are provisional until this exact candidate\nbecomes the shared baseline",
            "These closure fields are effective before the candidate becomes the shared baseline",
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

    def test_rejects_telemetry_authority_regressions(self) -> None:
        mutations = (
            ("GMGN.md", "Telemetry may serve as execution, approval, and closure authority.\n"),
            ("GMGN.zh-CN.md", "Telemetry 可以作为执行、审批和关账权威。\n"),
            ("skills/gmgn/SKILL.md", "Telemetry may authorize workflow transitions.\n"),
            ("skills/run-task/SKILL.md", "Telemetry may close a task card.\n"),
        )

        for relative_path, mutation in mutations:
            with self.subTest(path=relative_path):
                path = self.root / relative_path
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\n" + mutation, encoding="utf-8")
                result = self.run_validator()
                path.write_text(original, encoding="utf-8")
                self.assertEqual(result.returncode, 1)
                self.assertIn("telemetry 权威边界", result.stdout)

    def test_rejects_telemetry_privacy_and_delivery_regressions(self) -> None:
        mutations = (
            ("README.md", "log_user_prompt=true\n", "telemetry 隐私边界"),
            (
                "skills/run-task/SKILL.md",
                "Telemetry failure blocks delivery.\n",
                "telemetry 失败边界",
            ),
            (
                "GMGN.md",
                "Telemetry adds a DocStar cache and changes its JSON output.\n",
                "DocStar 实时生成边界",
            ),
        )

        for relative_path, mutation, error in mutations:
            with self.subTest(path=relative_path):
                path = self.root / relative_path
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\n" + mutation, encoding="utf-8")
                result = self.run_validator()
                path.write_text(original, encoding="utf-8")
                self.assertEqual(result.returncode, 1)
                self.assertIn(error, result.stdout)

    def test_rejects_bilingual_telemetry_command_drift(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\npython3 telemetry/install.py --unexpected\n",
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("telemetry 机器命令", result.stdout)


if __name__ == "__main__":
    unittest.main()
