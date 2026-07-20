#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def event(timestamp: str, payload_type: str, **payload: object) -> dict:
    return {
        "timestamp": timestamp,
        "type": "event_msg" if payload_type in {
            "task_started",
            "task_complete",
            "token_count",
            "sub_agent_activity",
        } else "response_item",
        "payload": {"type": payload_type, **payload},
    }


class TelemetryReportTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.codex_home = Path(self.temporary.name)
        self.sessions = self.codex_home / "sessions" / "2026" / "07" / "20"
        self.sessions.mkdir(parents=True)
        self.private_prompt = "PRIVATE-SPAWN-PROMPT password=hunter2"
        self.private_arguments = "PRIVATE-ARGUMENTS api_key=secret"
        self.private_output = "PRIVATE-OUTPUT bearer-token"
        self._write_fixture()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_session(self, name: str, entries: list[object]) -> None:
        path = self.sessions / (name + ".jsonl")
        with path.open("w", encoding="utf-8") as stream:
            for entry in entries:
                if isinstance(entry, str):
                    stream.write(entry + "\n")
                else:
                    stream.write(json.dumps(entry) + "\n")

    def call(
        self,
        timestamp: str,
        call_id: str,
        tool: str,
        arguments: object,
        *,
        custom: bool = False,
    ) -> dict:
        payload = {
            "call_id": call_id,
            "name": tool,
            "status": "completed",
        }
        payload["input" if custom else "arguments"] = (
            arguments if isinstance(arguments, str) else json.dumps(arguments)
        )
        return event(
            timestamp,
            "custom_tool_call" if custom else "function_call",
            **payload,
        )

    def output(
        self,
        timestamp: str,
        call_id: str,
        output: object,
        *,
        custom: bool = False,
    ) -> dict:
        return event(
            timestamp,
            "custom_tool_call_output" if custom else "function_call_output",
            call_id=call_id,
            output=output if isinstance(output, str) else json.dumps(output),
        )

    def token_count(
        self,
        timestamp: str,
        input_tokens: int,
        cached_tokens: int,
        output_tokens: int,
        reasoning_tokens: int,
        total_tokens: int,
    ) -> dict:
        return event(
            timestamp,
            "token_count",
            info={
                "total_token_usage": {
                    "input_tokens": input_tokens,
                    "cached_input_tokens": cached_tokens,
                    "output_tokens": output_tokens,
                    "reasoning_output_tokens": reasoning_tokens,
                    "total_tokens": total_tokens,
                }
            },
        )

    def _write_fixture(self) -> None:
        root = [
            {
                "timestamp": "2026-07-20T00:00:00Z",
                "type": "session_meta",
                "payload": {
                    "id": "root-session",
                    "session_id": "historical-task-id",
                    "timestamp": "2026-07-20T00:00:00Z",
                },
            },
            "{malformed-json",
            event(
                "2026-07-20T00:00:01Z",
                "task_started",
                turn_id="root-turn-1",
                started_at=1784505601,
            ),
            self.token_count("2026-07-20T00:00:01.100Z", 10, 2, 3, 1, 13),
            self.call(
                "2026-07-20T00:00:02Z",
                "spawn-root",
                "spawn_agent",
                {
                    "message": self.private_prompt,
                    "fork_context": False,
                    "card_id": "CARD-7",
                    "run_id": "run-9",
                    "lane_key": "methodology:CARD-7",
                    "target_milestone_id": "M2",
                },
            ),
            self.output("2026-07-20T00:00:02.500Z", "spawn-root", {"success": True}),
            event(
                "2026-07-20T00:00:02.600Z",
                "sub_agent_activity",
                agent_thread_id="child-session",
                kind="spawned",
            ),
            event(
                "2026-07-20T00:00:02.700Z",
                "sub_agent_activity",
                agent_thread_id="missing-child",
                kind="spawned",
            ),
            self.output("2026-07-20T00:00:03.400Z", "docstar", {"success": True}),
            self.call(
                "2026-07-20T00:00:03Z",
                "docstar",
                "exec_command",
                {"cmd": "docstar brief CARD-7 --preset gmgn-v1 --json"},
            ),
            self.call(
                "2026-07-20T00:00:04Z",
                "grep",
                "exec_command",
                {"cmd": "rg 'CARD-7' docs"},
            ),
            self.output("2026-07-20T00:00:04.200Z", "grep", {"success": True}),
            self.call(
                "2026-07-20T00:00:05Z",
                "rg-files",
                "exec_command",
                {"cmd": "rg --files docs"},
            ),
            self.output("2026-07-20T00:00:05.100Z", "rg-files", {"success": True}),
            self.call(
                "2026-07-20T00:00:06Z",
                "markdown-read",
                "exec_command",
                {"cmd": "sed -n '1,80p' docs/Task.md"},
            ),
            self.output(
                "2026-07-20T00:00:06.300Z",
                "markdown-read",
                {"success": True, "output": self.private_output},
            ),
            self.call(
                "2026-07-20T00:00:07Z",
                "write",
                "apply_patch",
                self.private_arguments,
                custom=True,
            ),
            self.output(
                "2026-07-20T00:00:07.250Z",
                "write",
                self.private_output,
                custom=True,
            ),
            self.call(
                "2026-07-20T00:00:08Z",
                "wait",
                "wait_agent",
                {"ids": ["child-session"], "timeout_ms": 2000},
            ),
            self.output("2026-07-20T00:00:09.500Z", "wait", {"success": True}),
            self.call(
                "2026-07-20T00:00:10Z",
                "send",
                "send_message",
                {"target": "child-session", "message": self.private_prompt},
            ),
            self.output("2026-07-20T00:00:10.100Z", "send", {"success": True}),
            self.call(
                "2026-07-20T00:00:11Z",
                "skill-one",
                "exec_command",
                {"cmd": "cat /opt/codex/skills/gmgn/SKILL.md"},
            ),
            self.output("2026-07-20T00:00:12Z", "skill-one", "x" * 40),
            self.call(
                "2026-07-20T00:00:13Z",
                "orphan-call",
                "exec_command",
                {"cmd": "printf '%s' " + self.private_arguments},
            ),
            self.output("2026-07-20T00:00:14Z", "orphan-output", self.private_output),
            event(
                "2026-07-20T00:00:15Z",
                "task_complete",
                turn_id="root-turn-1",
                duration_ms=10000,
                started_at=1784505601,
                completed_at=1784505615,
            ),
            event(
                "2026-07-20T00:00:19Z",
                "task_started",
                turn_id="root-turn-2",
                started_at=1784505619,
            ),
            self.call(
                "2026-07-20T00:00:20Z",
                "skill-two",
                "exec_command",
                {"cmd": "sed -n '1,120p' /opt/codex/skills/run-task/SKILL.md"},
            ),
            self.output("2026-07-20T00:00:21Z", "skill-two", "y" * 20),
            self.token_count("2026-07-20T00:00:25Z", 100, 20, 30, 5, 130),
            event(
                "2026-07-20T00:00:25Z",
                "task_complete",
                turn_id="root-turn-2",
                duration_ms=4000,
                started_at=1784505619,
                completed_at=1784505625,
            ),
        ]
        child = [
            {
                "timestamp": "2026-07-20T00:00:02.500Z",
                "type": "session_meta",
                "payload": {"id": "child-session", "session_id": "root-session"},
            },
            event(
                "2026-07-20T00:00:02.500Z",
                "task_started",
                turn_id="child-turn",
                started_at=1784505602,
            ),
            self.output(
                "2026-07-20T00:00:04Z",
                "custom-grep",
                {"success": False, "output": self.private_output},
                custom=True,
            ),
            self.call(
                "2026-07-20T00:00:03Z",
                "custom-grep",
                "exec",
                "grep needle file.md " + self.private_arguments,
                custom=True,
            ),
            self.call(
                "2026-07-20T00:00:04.500Z",
                "spawn-child",
                "spawn_agent",
                {"message": self.private_prompt, "fork_turns": "none"},
            ),
            self.output("2026-07-20T00:00:05Z", "spawn-child", {"success": True}),
            event(
                "2026-07-20T00:00:05.100Z",
                "sub_agent_activity",
                agent_thread_id="grandchild-session",
                kind="spawned",
            ),
            self.token_count("2026-07-20T00:00:07.500Z", 40, 5, 10, 2, 50),
            event(
                "2026-07-20T00:00:07.500Z",
                "task_complete",
                turn_id="child-turn",
                duration_ms=3000,
                started_at=1784505602,
                completed_at=1784505607,
            ),
        ]
        grandchild = [
            {
                "timestamp": "2026-07-20T00:00:05.100Z",
                "type": "session_meta",
                "payload": {"id": "grandchild-session", "session_id": "root-session"},
            },
            event(
                "2026-07-20T00:00:05.100Z",
                "task_started",
                turn_id="grandchild-turn",
                started_at=1784505605,
            ),
            self.token_count("2026-07-20T00:00:07.100Z", 20, 2, 5, 1, 25),
            event(
                "2026-07-20T00:00:07.100Z",
                "task_complete",
                turn_id="grandchild-turn",
                duration_ms=2000,
                started_at=1784505605,
                completed_at=1784505607,
            ),
        ]
        self.write_session("rollout-root-session", root)
        self.write_session("rollout-child-session", child)
        self.write_session("rollout-grandchild-session", grandchild)

    def build_report(self, *session_ids: str, **options: object) -> dict:
        from telemetry.report import build_report

        return build_report(
            list(session_ids),
            codex_home=self.codex_home,
            **options,
        )

    def test_recursive_timing_tokens_and_historical_id(self) -> None:
        report = self.build_report("historical-task-id", follow_window=3)
        self.assertEqual(report["schema_version"], "gmgn.telemetry.report.v1")
        self.assertEqual(report["source"], "session_jsonl_unstable_fallback")
        run = report["runs"][0]
        self.assertEqual(run["session_id"], "root-session")
        self.assertEqual(run["session_counts"], {"main": 1, "descendants": 2, "total": 3})
        self.assertEqual(
            run["timing"],
            {
                "main_wall_elapsed_ms": 24000,
                "completed_turn_duration_ms": 14000,
                "agent_turn_duration_ms": 5000,
            },
        )
        self.assertEqual(
            run["actual_tokens"],
            {"input": 160, "cached": 27, "output": 45, "reasoning": 8, "total": 205},
        )
        self.assertGreater(run["estimated_tool_io_tokens"]["total"], 0)
        self.assertNotIn("estimated", run["actual_tokens"])

    def test_pairs_calls_out_of_order_and_never_reports_payloads(self) -> None:
        report = self.build_report("root-session")
        run = report["runs"][0]
        calls = {call["call_id"]: call for call in run["tool_calls"]}
        self.assertEqual(calls["docstar"]["duration_ms"], 400)
        self.assertEqual(calls["custom-grep"]["duration_ms"], 1000)
        self.assertFalse(calls["custom-grep"]["success"])
        self.assertIsNone(calls["orphan-call"]["end"])
        self.assertIsNone(calls["orphan-call"]["success"])
        self.assertEqual(run["data_quality"]["unpaired_calls"], 2)
        self.assertEqual(run["data_quality"]["malformed_lines"], 1)
        serialized = json.dumps(report, sort_keys=True)
        for secret in (
            self.private_prompt,
            self.private_arguments,
            self.private_output,
            "hunter2",
            "api_key",
            "bearer-token",
        ):
            self.assertNotIn(secret, serialized)
        expected_call_keys = {
            "session_id",
            "call_id",
            "tool",
            "category",
            "start",
            "end",
            "duration_ms",
            "success",
            "estimated_input_tokens",
            "estimated_output_tokens",
        }
        self.assertEqual(set(calls["docstar"]), expected_call_keys)

    def test_classification_skills_docstar_and_gmgn_metrics(self) -> None:
        run = self.build_report("root-session", follow_window=3)["runs"][0]
        categories = {call["call_id"]: call["category"] for call in run["tool_calls"]}
        self.assertEqual(categories["docstar"], "docstar")
        self.assertEqual(categories["grep"], "grep")
        self.assertEqual(categories["rg-files"], "other")
        self.assertEqual(categories["markdown-read"], "read")
        self.assertEqual(categories["wait"], "wait")
        self.assertEqual(categories["send"], "agent")
        self.assertEqual(categories["write"], "write")

        skills = {skill["skill"]: skill for skill in run["skills"]}
        self.assertEqual(skills["gmgn"]["load_duration_ms"], 1000)
        self.assertEqual(skills["gmgn"]["observed_span_ms"], 8000)
        self.assertEqual(skills["gmgn"]["estimated_context_tokens"], 10)
        self.assertEqual(skills["run-task"]["observed_span_ms"], 4000)

        gmgn = run["gmgn"]
        self.assertEqual(gmgn["spawn_calls"], 2)
        self.assertEqual(gmgn["wait_calls"], 1)
        self.assertEqual(gmgn["send_calls"], 1)
        self.assertEqual(gmgn["wait_duration_ms"], 1500)
        self.assertEqual(
            gmgn["fork_context_counts"],
            {"none": 1, "all": 0, "false": 1, "true": 0, "unspecified": 0},
        )
        self.assertEqual(gmgn["identifiers"]["card_id"], ["CARD-7"])
        self.assertEqual(gmgn["identifiers"]["run_id"], ["run-9"])
        self.assertEqual(gmgn["identifiers"]["lane_key"], ["methodology:CARD-7"])
        self.assertEqual(gmgn["identifiers"]["target_milestone_id"], ["M2"])

        docstar = run["docstar"]
        self.assertEqual(docstar["calls"], 1)
        self.assertEqual(docstar["commands"], {"brief": 1})
        self.assertEqual(docstar["grep_calls"], 2)
        self.assertEqual(docstar["grep_read_calls"], docstar["grep_calls"] + docstar["read_calls"])
        self.assertEqual(docstar["follow_up"][0]["grep_read_calls"], 2)
        self.assertEqual(docstar["follow_up"][0]["window"], 3)
        self.assertIsNone(docstar["grep_avoided"])
        self.assertEqual(docstar["causal_status"], "causal_not_measured")

    def test_missing_sessions_and_no_descendants(self) -> None:
        report = self.build_report(
            "historical-task-id",
            "missing-root",
            include_descendants=False,
        )
        root, missing = report["runs"]
        self.assertEqual(root["session_counts"], {"main": 1, "descendants": 0, "total": 1})
        self.assertEqual(root["actual_tokens"]["total"], 130)
        self.assertEqual(root["data_quality"]["missing_sessions"], [])
        self.assertIsNone(missing["session_id"])
        self.assertEqual(missing["data_quality"]["missing_sessions"], ["missing-root"])
        self.assertEqual(report["data_quality"]["missing_sessions"], ["missing-root"])

        recursive = self.build_report("root-session")
        self.assertEqual(
            recursive["data_quality"]["missing_sessions"],
            ["missing-child"],
        )

    def test_cli_json_human_output_and_documented_default(self) -> None:
        command = [
            sys.executable,
            "-m",
            "telemetry.report",
            "historical-task-id",
            "--codex-home",
            str(self.codex_home),
            "--json",
            "--no-descendants",
            "--follow-window",
            "2",
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["runs"][0]["session_counts"]["total"], 1)
        self.assertEqual(report["configuration"]["follow_window"], 2)

        human = subprocess.run(
            command[:-4] + ["--include-descendants"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("主任务墙钟", human.stdout)
        self.assertIn("实际 token", human.stdout)
        self.assertNotIn(self.private_prompt, human.stdout)

        help_result = subprocess.run(
            [sys.executable, "-m", "telemetry.report", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("--include-descendants", help_result.stdout)
        self.assertIn("--no-descendants", help_result.stdout)
        self.assertIn("default: 5", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
