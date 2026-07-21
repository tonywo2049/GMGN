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
        self.telemetry_data = self.codex_home / "gmgn-telemetry" / "data"
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

    def otel_value(self, value: object) -> dict:
        if isinstance(value, bool):
            return {"boolValue": value}
        if isinstance(value, int):
            return {"intValue": str(value)}
        return {"stringValue": value}

    def otel_record(
        self,
        session_id: str,
        event_name: str,
        timestamp: str,
        **attributes: object,
    ) -> dict:
        values = {
            "conversation.id": session_id,
            "event.name": event_name,
            "event.timestamp": timestamp,
            **attributes,
        }
        return {
            "timeUnixNano": "1784505600000000000",
            "attributes": [
                {
                    "key": key,
                    "value": value
                    if isinstance(value, dict)
                    else self.otel_value(value),
                }
                for key, value in values.items()
            ],
        }

    def write_otel(self, records: list[dict]) -> None:
        self.telemetry_data.mkdir(parents=True, exist_ok=True)
        envelope = {
            "schema_version": "gmgn-otel-envelope-v1",
            "received_at": "2026-07-20T00:00:30Z",
            "signal": "logs",
            "content_type": "application/json",
            "body": {
                "resourceLogs": [
                    {"scopeLogs": [{"logRecords": records}]},
                ]
            },
        }
        path = self.telemetry_data / "2026-07-20.jsonl"
        path.write_text(json.dumps(envelope) + "\n", encoding="utf-8")

    def write_flat_otel(self, records: list[dict]) -> None:
        self.telemetry_data.mkdir(parents=True, exist_ok=True)
        path = self.telemetry_data / "otel-2026-07-20.jsonl"
        path.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

    def write_hooks(self, records: list[dict]) -> None:
        self.telemetry_data.mkdir(parents=True, exist_ok=True)
        path = self.telemetry_data / "hooks-2026-07-20.jsonl"
        path.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
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
                    "message": (
                        self.private_prompt
                        + "\ncard_id: PROMPT-CARD\nrun_id: PROMPT-RUN"
                    ),
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
            self.output("2026-07-20T00:00:09.500Z", "wait", "Wait timed out."),
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
                {
                    "message": self.private_prompt + "\ncard_id: CHILD-PROMPT-CARD",
                    "fork_turns": "none",
                },
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

    def _write_primary_telemetry_fixture(self) -> None:
        root_sse = self.otel_record(
            "root-session",
            "codex.sse_event",
            "2026-07-20T00:00:24Z",
            **{
                "event.kind": "response.completed",
                "input_token_count": 70,
                "cached_token_count": 10,
                "output_token_count": 20,
                "tool_token_count": 90,
            },
        )
        records = [
            self.otel_record(
                "root-session",
                "codex.api_request",
                "2026-07-20T00:00:03Z",
                duration_ms=120,
                **{"http.response.status_code": 200},
            ),
            root_sse,
            root_sse,
            self.otel_record(
                "root-session",
                "codex.tool_result",
                "2026-07-20T00:00:03.400Z",
                tool_name="exec_command",
                call_id="docstar",
                duration_ms=400,
                success="true",
                arguments={"length": 40, "redacted": True},
                output={"length": 80, "redacted": True},
            ),
            self.otel_record(
                "root-session",
                "codex.tool_result",
                "2026-07-20T00:00:12Z",
                tool_name="exec_command",
                call_id="skill-one",
                duration_ms=1000,
                success="true",
                arguments={"length": 32, "redacted": True},
                output={"length": 40, "redacted": True},
            ),
            self.otel_record(
                "child-session",
                "codex.api_request",
                "2026-07-20T00:00:04Z",
                duration_ms=80,
                **{"http.response.status_code": 200},
            ),
            self.otel_record(
                "child-session",
                "codex.sse_event",
                "2026-07-20T00:00:07Z",
                **{
                    "event.kind": "response.completed",
                    "input_token_count": 30,
                    "cached_token_count": 4,
                    "output_token_count": 8,
                    "reasoning_token_count": 2,
                    "tool_token_count": 38,
                },
            ),
            self.otel_record(
                "child-session",
                "codex.tool_result",
                "2026-07-20T00:00:04Z",
                tool_name="exec",
                call_id="custom-grep",
                duration_ms=900,
                success="false",
                arguments={"length": 24, "redacted": True},
                output={"length": 16, "redacted": True},
            ),
        ]
        self.write_otel(records)
        hooks = [
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:01Z",
                "event": "SessionStart",
                "session_id": "root-session",
                "classification": "other",
                "input_bytes": 0,
                "output_bytes": 0,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:02Z",
                "event": "PreToolUse",
                "session_id": "root-session",
                "turn_id": "root-turn-1",
                "tool_name": "spawn_agent",
                "tool_use_id": "spawn-root",
                "classification": "agent",
                "fork_context": False,
                "card_id": "CARD-7",
                "run_id": "run-9",
                "lane_key": "methodology:CARD-7",
                "target_milestone_id": "M2",
                "input_bytes": 100,
                "output_bytes": 0,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:03.400Z",
                "event": "PostToolUse",
                "session_id": "root-session",
                "turn_id": "root-turn-1",
                "tool_name": "Bash",
                "tool_use_id": "docstar",
                "classification": "docstar",
                "docstar_subcommand": "brief",
                "input_bytes": 40,
                "output_bytes": 80,
                "success": True,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:04.200Z",
                "event": "PostToolUse",
                "session_id": "root-session",
                "turn_id": "root-turn-1",
                "tool_name": "Bash",
                "tool_use_id": "grep-hook-only",
                "classification": "grep",
                "input_bytes": 20,
                "output_bytes": 10,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:06.300Z",
                "event": "PostToolUse",
                "session_id": "root-session",
                "turn_id": "root-turn-1",
                "tool_name": "Bash",
                "tool_use_id": "markdown-read",
                "classification": "markdown_read",
                "input_bytes": 20,
                "output_bytes": 40,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:12Z",
                "event": "PostToolUse",
                "session_id": "root-session",
                "turn_id": "root-turn-1",
                "tool_name": "Bash",
                "tool_use_id": "skill-one",
                "classification": "skill_load",
                "skill_name": "gmgn",
                "input_bytes": 32,
                "output_bytes": 40,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:21Z",
                "event": "PostToolUse",
                "session_id": "root-session",
                "turn_id": "root-turn-2",
                "tool_name": "Bash",
                "tool_use_id": "unlinked-skill-two",
                "classification": "skill_load",
                "skill_name": "run-task",
                "input_bytes": 28,
                "output_bytes": 20,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:02.500Z",
                "event": "SessionStart",
                "session_id": "child-session",
                "classification": "other",
                "input_bytes": 0,
                "output_bytes": 0,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:04.500Z",
                "event": "PreToolUse",
                "session_id": "child-session",
                "turn_id": "child-turn",
                "tool_name": "spawn_agent",
                "tool_use_id": "spawn-child",
                "classification": "agent",
                "fork_turns": "none",
                "input_bytes": 50,
                "output_bytes": 0,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:04Z",
                "event": "PostToolUse",
                "session_id": "child-session",
                "turn_id": "child-turn",
                "tool_name": "Bash",
                "tool_use_id": "not-custom-grep",
                "classification": "grep",
                "input_bytes": 24,
                "output_bytes": 16,
            },
        ]
        self.write_hooks(hooks + [hooks[2]])

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
        self.assertEqual(gmgn["wait"]["result_counts"]["timeout"], 1)
        self.assertEqual(gmgn["wait"]["max_consecutive_timeouts"], 1)
        self.assertFalse(gmgn["wait"]["wait_storm_detected"])
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

    def test_wait_results_storms_and_reactivation_tokens(self) -> None:
        entries = [
            {
                "timestamp": "2026-07-20T01:00:00Z",
                "type": "session_meta",
                "payload": {"id": "wait-session"},
            },
            event(
                "2026-07-20T01:00:00Z",
                "task_started",
                turn_id="wait-turn",
                started_at=1784509200,
            ),
            self.call(
                "2026-07-20T01:00:01Z",
                "wait-1",
                "wait_agent",
                {"timeout_ms": 30000},
            ),
            self.output("2026-07-20T01:00:02Z", "wait-1", "Wait timed out."),
            self.token_count("2026-07-20T01:00:02.100Z", 100, 80, 10, 2, 110),
            self.call(
                "2026-07-20T01:00:03Z",
                "wait-2",
                "wait_agent",
                {"timeout_ms": 30000},
            ),
            self.output(
                "2026-07-20T01:00:04Z",
                "wait-2",
                {"timed_out": True},
            ),
            self.token_count("2026-07-20T01:00:04.100Z", 200, 160, 20, 4, 220),
            self.call(
                "2026-07-20T01:00:05Z",
                "wait-3",
                "wait_agent",
                {"timeout_ms": 30000},
            ),
            self.output("2026-07-20T01:00:06Z", "wait-3", "Wait completed."),
            self.token_count("2026-07-20T01:00:06.100Z", 300, 240, 30, 6, 330),
            self.call(
                "2026-07-20T01:00:07Z",
                "send-after-wait",
                "send_message",
                {"target": "agent-1", "message": self.private_prompt},
            ),
            self.output(
                "2026-07-20T01:00:07.100Z",
                "send-after-wait",
                {"success": True},
            ),
            self.token_count("2026-07-20T01:00:07.200Z", 400, 320, 40, 8, 440),
            event(
                "2026-07-20T01:00:08Z",
                "task_complete",
                turn_id="wait-turn",
                completed_at=1784509208,
            ),
        ]
        self.write_session("rollout-wait-session", entries)

        run = self.build_report("wait-session")["runs"][0]
        wait = run["gmgn"]["wait"]
        self.assertEqual(
            wait["result_counts"],
            {
                "update": 1,
                "timeout": 2,
                "interrupted": 0,
                "error": 0,
                "unknown": 0,
            },
        )
        self.assertEqual(
            wait["state_change_counts"],
            {"changed": 1, "unchanged": 2, "unknown": 0},
        )
        self.assertEqual(wait["max_consecutive_timeouts"], 2)
        self.assertEqual(wait["wait_storm_count"], 1)
        self.assertTrue(wait["wait_storm_detected"])
        self.assertEqual(
            wait["reactivation"],
            {
                "tokens": {
                    "input": 300,
                    "cached": 240,
                    "output": 30,
                    "reasoning": 6,
                    "total": 330,
                },
                "matched_waits": 3,
                "eligible_waits": 3,
                "coverage": "observed",
                "source": "session_jsonl_unstable_fallback",
                "linkage": "session_sequence_delta",
            },
        )

    def test_wait_argument_rejection_is_an_error(self) -> None:
        entries = [
            {
                "timestamp": "2026-07-20T02:00:00Z",
                "type": "session_meta",
                "payload": {"id": "wait-error-session"},
            },
            self.call(
                "2026-07-20T02:00:01Z",
                "wait-error",
                "wait_agent",
                {"timeout_ms": 1},
            ),
            self.output(
                "2026-07-20T02:00:01.100Z",
                "wait-error",
                "timeout_ms must be at least 10000",
            ),
            self.call(
                "2026-07-20T02:00:02Z",
                "wait-timeout-status",
                "wait_agent",
                {"timeout_ms": 30000},
            ),
            self.output(
                "2026-07-20T02:00:03Z",
                "wait-timeout-status",
                {"status": "timed_out"},
            ),
        ]
        self.write_session("rollout-wait-error-session", entries)

        wait = self.build_report("wait-error-session")["runs"][0]["gmgn"]["wait"]
        self.assertEqual(wait["result_counts"]["error"], 1)
        self.assertEqual(wait["result_counts"]["timeout"], 1)
        self.assertEqual(wait["state_change_counts"]["unknown"], 1)
        self.assertEqual(wait["state_change_counts"]["unchanged"], 1)
        self.assertEqual(wait["reactivation"]["coverage"], "unknown")

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

    def test_collector_and_hooks_are_primary_with_field_fallback_and_dedup(self) -> None:
        self._write_primary_telemetry_fixture()
        report = self.build_report("historical-task-id", follow_window=3)
        run = report["runs"][0]

        self.assertEqual(report["source"], "mixed")
        self.assertEqual(run["api_calls"]["count"], 2)
        self.assertEqual(run["api_calls"]["duration_ms"], 200)
        self.assertEqual(run["native_tool_results"]["count"], 3)
        self.assertEqual(run["native_tool_results"]["duration_ms"], 2300)
        self.assertEqual(
            run["actual_tokens"],
            {"input": 120, "cached": 16, "output": 33, "reasoning": 8, "total": 153},
        )
        token_fields = run["coverage"]["actual_tokens"]["fields"]
        self.assertIn("collector_otel", token_fields["input"]["source"])
        self.assertIn("session_jsonl_unstable_fallback", token_fields["input"]["source"])
        self.assertIn("session_jsonl_unstable_fallback", token_fields["reasoning"]["source"])
        self.assertTrue(run["sources"]["session_jsonl_unstable_fallback"]["used"])

        calls = {call["call_id"]: call for call in run["tool_calls"]}
        self.assertEqual(calls["docstar"]["duration_ms"], 400)
        self.assertEqual(calls["docstar"]["category"], "docstar")
        self.assertEqual(calls["custom-grep"]["category"], "unclassified")
        self.assertEqual(
            run["coverage"]["native_hook_linkage"]["coverage"],
            "partial",
        )

        skills = {skill["skill"]: skill for skill in run["skills"]}
        self.assertEqual(skills["gmgn"]["load_duration_ms"], 1000)
        self.assertEqual(skills["gmgn"]["load_duration_source"], "collector_otel")
        self.assertEqual(skills["gmgn"]["observed_span_ms"], 9000)
        self.assertEqual(skills["gmgn"]["estimated_context_tokens"], 10)
        self.assertTrue(skills["gmgn"]["estimated_context_tokens_is_estimate"])
        self.assertIsNone(skills["run-task"]["load_duration_ms"])
        self.assertEqual(skills["run-task"]["linkage"], "unlinked")

        self.assertEqual(run["gmgn"]["spawn_calls"], 2)
        self.assertEqual(run["gmgn"]["wait_calls"], 1)
        self.assertEqual(run["gmgn"]["send_calls"], 1)
        self.assertEqual(run["docstar"]["calls"], 1)
        self.assertEqual(run["docstar"]["follow_up"][0]["grep_read_calls"], 2)

    def test_unknown_tokens_are_null_and_otel_only_session_is_reportable(self) -> None:
        empty_home = Path(self.temporary.name) / "empty-codex"
        session_dir = empty_home / "sessions"
        session_dir.mkdir(parents=True)
        (session_dir / "no-token.jsonl").write_text(
            json.dumps(
                {
                    "timestamp": "2026-07-20T00:00:00Z",
                    "type": "session_meta",
                    "payload": {"id": "no-token"},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        from telemetry.report import build_report

        unknown = build_report(["no-token"], codex_home=empty_home)["runs"][0]
        self.assertEqual(unknown["actual_tokens"], dict.fromkeys(
            ("input", "cached", "output", "reasoning", "total"), None
        ))
        self.assertEqual(unknown["coverage"]["actual_tokens"]["coverage"], "unknown")

        self.write_otel(
            [
                self.otel_record(
                    "otel-only",
                    "codex.api_request",
                    "2026-07-20T00:00:01Z",
                    duration_ms=50,
                    **{"http.response.status_code": 200},
                )
            ]
        )
        only = self.build_report("otel-only")["runs"][0]
        self.assertEqual(only["session_id"], "otel-only")
        self.assertEqual(only["api_calls"]["count"], 1)
        self.assertIsNone(only["actual_tokens"]["total"])
        self.assertEqual(only["data_quality"]["missing_sessions"], [])

    def test_flat_otel_schema_agent_hook_and_unknown_event_are_fail_closed(self) -> None:
        empty_home = Path(self.temporary.name) / "flat-codex"
        data_dir = empty_home / "gmgn-telemetry" / "data"
        data_dir.mkdir(parents=True)
        records = [
            {
                "schema_version": "gmgn-otel-event-v1",
                "received_at": "2026-07-20T00:00:02Z",
                "timestamp": "2026-07-20T00:00:01Z",
                "conversation_id": "flat-session",
                "event_name": "codex.api_request",
                "model": "gpt-test",
                "attributes": {
                    "duration_ms": 25,
                    "success": False,
                    "attempt": 1,
                    "endpoint": "/responses",
                },
            },
            {
                "schema_version": "gmgn-otel-event-v1",
                "received_at": "2026-07-20T00:00:03Z",
                "conversation_id": "flat-session",
                "event_name": "codex.unknown_event",
                "attributes": {"gen_ai.usage.input_tokens": 999999},
            },
            {
                "schema_version": "gmgn-otel-event-v1",
                "received_at": "2026-07-20T00:00:04Z",
                "conversation_id": "flat-session",
                "event_name": "codex.websocket_request",
                "model": "gpt-test",
                "attributes": {
                    "duration_ms": 10,
                    "status": 200,
                },
            },
        ]
        (data_dir / "2026-07-20.jsonl").write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )
        hooks = [
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:01.500Z",
                "event": "PreToolUse",
                "session_id": "flat-session",
                "tool_name": "Agent",
                "tool_use_id": "agent-call",
                "classification": "agent",
                "fork_context": False,
            },
            {
                "schema_version": "gmgn-hook-event-v1",
                "timestamp": "2026-07-20T00:00:02Z",
                "event": "PostToolUse",
                "session_id": "flat-session",
                "tool_name": "wait_agent",
                "tool_use_id": "wait-call",
                "classification": "agent",
                "agent_action": "wait",
                "wait_result": "timeout",
            },
        ]
        (data_dir / "hooks-2026-07-20.jsonl").write_text(
            "".join(json.dumps(hook) + "\n" for hook in hooks),
            encoding="utf-8",
        )
        from telemetry.report import build_report, render_human

        run = build_report(["flat-session"], codex_home=empty_home)["runs"][0]

        self.assertEqual(run["api_calls"]["count"], 2)
        self.assertEqual(run["api_calls"]["success"], 1)
        self.assertEqual(run["api_calls"]["failure"], 1)
        self.assertEqual(run["gmgn"]["spawn_calls"], 1)
        self.assertEqual(run["gmgn"]["wait_calls"], 1)
        self.assertEqual(run["gmgn"]["wait"]["result_counts"]["timeout"], 1)
        self.assertEqual(run["gmgn"]["wait"]["reactivation"]["coverage"], "unknown")
        self.assertIsNone(run["actual_tokens"]["input"])
        self.assertIsNone(run["timing"]["completed_turn_duration_ms"])
        human = render_human({"runs": [run]})
        self.assertIn("wait 1（unknown ms）", human)
        self.assertIn("timeout 1", human)

    def test_structured_identifiers_ignore_adversarial_prompt_text(self) -> None:
        run = self.build_report("root-session")["runs"][0]
        identifiers = run["gmgn"]["identifiers"]
        self.assertEqual(identifiers["card_id"], ["CARD-7"])
        self.assertEqual(identifiers["run_id"], ["run-9"])
        serialized = json.dumps(identifiers, sort_keys=True)
        self.assertNotIn("PROMPT-CARD", serialized)
        self.assertNotIn("PROMPT-RUN", serialized)
        self.assertNotIn("CHILD-PROMPT-CARD", serialized)

    def test_human_output_shows_sources_coverage_and_skill_estimates(self) -> None:
        self._write_primary_telemetry_fixture()
        from telemetry.report import render_human

        human = render_human(self.build_report("root-session", follow_window=3))
        self.assertIn("数据源", human)
        self.assertIn("coverage", human)
        self.assertIn("fallback", human)
        self.assertIn("skill 调用", human)
        self.assertIn("gmgn", human)
        self.assertIn("estimate", human)
        self.assertIn("DocStar follow-up grep/read", human)
        self.assertIn("causal_not_measured", human)


if __name__ == "__main__":
    unittest.main()
