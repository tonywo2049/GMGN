#!/usr/bin/env python3
from __future__ import annotations

from datetime import timedelta
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / "telemetry" / "collector.py"
HOOK = ROOT / "telemetry" / "hook.py"
INSTALLER = ROOT / "telemetry" / "install.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compact_json_bytes(value: object) -> int:
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return len(encoded)


class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.collector = load_module("gmgn_test_collector", COLLECTOR)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary.name) / "otel"
        self.server = None
        self.thread = None
        self.start_server()

    def tearDown(self) -> None:
        self.stop_server()
        self.temporary.cleanup()

    def start_server(self, **overrides: object) -> None:
        self.stop_server()
        options = {
            "host": "127.0.0.1",
            "port": 0,
            "data_dir": self.data_dir,
            "retention_days": 7,
            "max_body_bytes": 4096,
            "max_write_bytes": 4096,
            "max_data_bytes": 1024 * 1024,
            "read_timeout_seconds": 1.0,
            "max_concurrent_requests": 4,
        }
        options.update(overrides)
        self.data_dir = Path(options["data_dir"])
        self.server = self.collector.create_server(**options)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address[:2]

    def stop_server(self) -> None:
        if self.server is None:
            return
        self.server.shutdown()
        self.server.server_close()
        if self.thread is not None:
            self.thread.join(timeout=5)
        self.server = None
        self.thread = None

    def request(
        self,
        method: str,
        path: str,
        body: bytes = b"",
        content_type: str = "application/json",
    ) -> tuple[int, bytes, dict[str, str]]:
        connection = http.client.HTTPConnection(self.host, self.port, timeout=5)
        headers = {"Content-Type": content_type} if body else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        response_headers = {key.lower(): value for key, value in response.getheaders()}
        connection.close()
        return response.status, payload, response_headers

    def post_json(self, path: str, payload: object) -> tuple[int, bytes, dict[str, str]]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self.request("POST", path, body)

    def otel_value(self, value: object) -> dict:
        if isinstance(value, bool):
            return {"boolValue": value}
        if isinstance(value, int):
            return {"intValue": str(value)}
        if isinstance(value, float):
            return {"doubleValue": value}
        return {"stringValue": value}

    def otel_attributes(self, values: dict[str, object]) -> list[dict]:
        return [
            {"key": key, "value": self.otel_value(value)}
            for key, value in values.items()
        ]

    def log_record(
        self,
        event_name: str = "codex.tool_result",
        attributes: dict[str, object] | None = None,
    ) -> dict:
        values: dict[str, object] = {
            "event.name": event_name,
            "event.timestamp": "2026-07-20T01:02:03.456Z",
            "conversation.id": "conversation-123",
            "model": "gpt-test",
        }
        if attributes:
            values.update(attributes)
        return {
            "timeUnixNano": "1784518923456000000",
            "attributes": self.otel_attributes(values),
        }

    def logs_payload(
        self,
        records: list[object],
        resource_attributes: dict[str, object] | None = None,
    ) -> dict:
        resource_log: dict[str, object] = {
            "scopeLogs": [{"logRecords": records}],
        }
        if resource_attributes is not None:
            resource_log["resource"] = {
                "attributes": self.otel_attributes(resource_attributes)
            }
        return {"resourceLogs": [resource_log]}

    def records(self, data_dir: Path | None = None) -> list[dict]:
        directory = data_dir or self.data_dir
        records = []
        for path in sorted(directory.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        return records

    def test_health_and_empty_logs(self) -> None:
        status, body, headers = self.request("GET", "/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {})
        self.assertEqual(headers["content-type"], "application/json")

        status, body, _ = self.post_json("/v1/logs", {"resourceLogs": []})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {})
        self.assertEqual(self.records(), [])

    def test_flat_schema_drops_sensitive_and_unknown_fields(self) -> None:
        secrets = {
            "prompt-secret",
            "command-secret",
            "tool-output-secret",
            "error-secret",
            "host-secret",
            "person@example.test",
            "account-secret",
            "auth-secret",
            "unknown-secret",
        }
        record = self.log_record(
            attributes={
                "tool_name": "exec_command",
                "call_id": "call-123",
                "source": "mcp",
                "duration_ms": 15.5,
                "success": True,
                "output_length": 2048,
                "output_line_count": 12,
                "mcp_server": "docstar",
                "mcp_server_origin": "local",
                "tool_origin": "codex",
                "prompt": "prompt-secret",
                "command": "command-secret",
                "output": "tool-output-secret",
                "error.message": "error-secret",
                "auth.key.present": "auth-secret",
                "unknown.field": "unknown-secret",
            }
        )
        record["body"] = {"stringValue": "tool-output-secret"}
        record["unknownRecordField"] = "unknown-secret"
        payload = self.logs_payload(
            [record],
            {
                "host.name": "host-secret",
                "user.email": "person@example.test",
                "account.id": "account-secret",
                "user.id": "account-secret",
                "api_key_present": "auth-secret",
            },
        )

        status, _, _ = self.post_json("/v1/logs", payload)
        self.assertEqual(status, 200)
        stored = self.records()[0]
        self.assertEqual(
            set(stored),
            {
                "schema_version",
                "received_at",
                "event_name",
                "conversation_id",
                "timestamp",
                "model",
                "attributes",
            },
        )
        self.assertEqual(stored["schema_version"], "gmgn-otel-event-v1")
        self.assertEqual(stored["event_name"], "codex.tool_result")
        self.assertEqual(stored["conversation_id"], "conversation-123")
        self.assertEqual(stored["timestamp"], "2026-07-20T01:02:03.456Z")
        self.assertEqual(stored["model"], "gpt-test")
        self.assertEqual(
            stored["attributes"],
            {
                "call_id": "call-123",
                "duration_ms": 15.5,
                "mcp_server": "docstar",
                "mcp_server_origin": "local",
                "output_length": 2048,
                "output_line_count": 12,
                "source": "mcp",
                "success": True,
                "tool_name": "exec_command",
                "tool_origin": "codex",
            },
        )
        serialized = json.dumps(stored, ensure_ascii=False)
        self.assertNotIn("resourceLogs", serialized)
        for secret in secrets:
            self.assertNotIn(secret, serialized)

        def collect_keys(value: object) -> set[str]:
            keys = set()
            if isinstance(value, dict):
                keys.update(value)
                for child in value.values():
                    keys.update(collect_keys(child))
            elif isinstance(value, list):
                for child in value:
                    keys.update(collect_keys(child))
            return keys

        stored_keys = collect_keys(stored)
        for field_name in (
            "body",
            "prompt",
            "command",
            "output",
            "error.message",
            "host.name",
            "user.email",
            "account.id",
            "user.id",
            "api_key_present",
            "auth.key.present",
            "unknown.field",
        ):
            self.assertNotIn(field_name, stored_keys)

    def test_event_whitelist_retains_only_event_specific_metadata(self) -> None:
        query_secret = "query-auth-secret"
        records = [
            self.log_record("codex.conversation_starts"),
            self.log_record(
                "codex.api_request",
                {
                    "duration_ms": 250,
                    "success": True,
                    "attempt": 2,
                    "endpoint": f"https://api.example.test/v1/responses?key={query_secret}",
                    "status": "ok",
                    "http.response.status_code": 200,
                    "tool_name": "must-drop",
                },
            ),
            self.log_record(
                "codex.sse_event",
                {
                    "event.kind": "response.completed",
                    "gen_ai.usage.input_tokens": 100,
                    "gen_ai.usage.cache_read.input_tokens": 20,
                    "gen_ai.usage.cache_write.input_tokens": 5,
                    "gen_ai.usage.output_tokens": 30,
                    "codex.usage.reasoning_output_tokens": 7,
                    "codex.usage.total_tokens": 157,
                    "duration_ms": 8,
                    "status": "must-drop",
                },
            ),
            self.log_record(
                "codex.user_prompt",
                {"prompt": "never-store", "output_length": 99},
            ),
            self.log_record(
                "codex.tool_decision",
                {
                    "tool_name": "exec_command",
                    "call_id": "call-decision",
                    "source": "model",
                    "success": True,
                },
            ),
        ]

        status, _, _ = self.post_json("/v1/logs", self.logs_payload(records))
        self.assertEqual(status, 200)
        stored = self.records()
        self.assertEqual(
            [item["event_name"] for item in stored],
            [
                "codex.conversation_starts",
                "codex.api_request",
                "codex.sse_event",
                "codex.user_prompt",
                "codex.tool_decision",
            ],
        )
        self.assertEqual(stored[0]["attributes"], {})
        self.assertEqual(
            stored[1]["attributes"],
            {
                "attempt": 2,
                "duration_ms": 250,
                "endpoint": "/v1/responses",
                "http.response.status_code": 200,
                "status": "ok",
                "success": True,
            },
        )
        self.assertEqual(stored[3]["attributes"], {})
        self.assertEqual(
            stored[4]["attributes"],
            {
                "call_id": "call-decision",
                "source": "model",
                "tool_name": "exec_command",
            },
        )
        serialized = json.dumps(stored, ensure_ascii=False)
        self.assertNotIn(query_secret, serialized)
        self.assertNotIn("never-store", serialized)
        self.assertNotIn("must-drop", serialized)
        self.assertEqual(
            stored[2]["attributes"],
            {
                "codex.usage.reasoning_output_tokens": 7,
                "codex.usage.total_tokens": 157,
                "duration_ms": 8,
                "event.kind": "response.completed",
                "gen_ai.usage.cache_read.input_tokens": 20,
                "gen_ai.usage.cache_write.input_tokens": 5,
                "gen_ai.usage.input_tokens": 100,
                "gen_ai.usage.output_tokens": 30,
            },
        )

        websocket = self.log_record(
            "codex.websocket_event",
            {
                "event.kind": "response.completed",
                "input_token_count": 12,
                "output_token_count": 3,
            },
        )
        status, _, _ = self.post_json("/v1/logs", self.logs_payload([websocket]))
        self.assertEqual(status, 200)
        websocket_record = self.records()[-1]
        self.assertEqual(websocket_record["event_name"], "codex.websocket_event")
        self.assertEqual(websocket_record["attributes"]["input_token_count"], 12)

    def test_codex_string_scalars_are_strictly_normalized(self) -> None:
        records = [
            self.log_record(
                "codex.websocket_request",
                {
                    "duration_ms": "15.5",
                    "success": "true",
                    "status_code": "200",
                },
            ),
            self.log_record(
                "codex.sse_event",
                {
                    "event.kind": "response.completed",
                    "input_token_count": "12",
                    "output_token_count": "3",
                    "tool_token_count": "0",
                },
            ),
        ]
        status, _, _ = self.post_json("/v1/logs", self.logs_payload(records))
        self.assertEqual(status, 200)
        stored = self.records()
        self.assertEqual(
            stored[0]["attributes"],
            {"duration_ms": 15.5, "status_code": 200, "success": True},
        )
        self.assertEqual(
            stored[1]["attributes"],
            {
                "event.kind": "response.completed",
                "input_token_count": 12,
                "output_token_count": 3,
                "tool_token_count": 0,
            },
        )

    def test_mixed_batch_drops_unknown_and_unrelated_events(self) -> None:
        unrelated_api = {
            "attributes": self.otel_attributes(
                {
                    "event.name": "codex.api_request",
                    "event.timestamp": "2026-07-20T01:02:03.456Z",
                    "duration_ms": 9,
                }
            )
        }
        payload = self.logs_payload(
            [
                self.log_record("codex.startup_phase"),
                unrelated_api,
                self.log_record(
                    "codex.tool_result",
                    {"tool_name": "exec_command", "success": True},
                ),
            ]
        )
        status, _, _ = self.post_json("/v1/logs", payload)
        self.assertEqual(status, 200)
        self.assertEqual(
            self.records(),
            [
                {
                    "schema_version": "gmgn-otel-event-v1",
                    "received_at": self.records()[0]["received_at"],
                    "event_name": "codex.tool_result",
                    "conversation_id": "conversation-123",
                    "timestamp": "2026-07-20T01:02:03.456Z",
                    "model": "gpt-test",
                    "attributes": {"success": True, "tool_name": "exec_command"},
                }
            ],
        )

    def test_path_schema_content_type_and_body_size_fail_closed(self) -> None:
        for path, root in (
            ("/v1/traces", "resourceSpans"),
            ("/v1/metrics", "resourceMetrics"),
            ("/v1/unknown", "resourceLogs"),
        ):
            with self.subTest(path=path):
                status, _, _ = self.post_json(path, {root: []})
                self.assertEqual(status, 404)

        status, _, _ = self.request(
            "POST",
            "/v1/logs",
            b"binary-secret",
            "application/x-protobuf",
        )
        self.assertEqual(status, 415)
        status, _, _ = self.request("POST", "/v1/logs", b"{not-json")
        self.assertEqual(status, 400)
        status, _, _ = self.request(
            "POST", "/v1/logs", b'{"resourceLogs":[],"resourceLogs":[]}'
        )
        self.assertEqual(status, 400)
        status, _, _ = self.post_json("/v1/logs", {"resourceLogs": [], "extra": []})
        self.assertEqual(status, 400)
        oversized = json.dumps({"resourceLogs": [], "padding": "x" * 5000}).encode()
        status, _, _ = self.request("POST", "/v1/logs", oversized)
        self.assertEqual(status, 413)
        self.assertEqual(self.records(), [])

    def test_invalid_inner_structures_return_400_without_partial_write(self) -> None:
        valid = self.log_record()
        invalid_documents = (
            {"resourceLogs": [None]},
            {"resourceLogs": [{}]},
            {"resourceLogs": [{"scopeLogs": {}}]},
            {"resourceLogs": [{"scopeLogs": [None]}]},
            {"resourceLogs": [{"scopeLogs": [{}]}]},
            {"resourceLogs": [{"scopeLogs": [{"logRecords": {}}]}]},
            {"resourceLogs": [{"scopeLogs": [{"logRecords": [None]}]}]},
            self.logs_payload([{"attributes": {}}]),
            self.logs_payload([{"attributes": [None]}]),
            self.logs_payload(
                [{"attributes": [{"key": "event.name", "value": {}}]}]
            ),
            self.logs_payload(
                [
                    {
                        "attributes": [
                            {
                                "key": "event.name",
                                "value": {"stringValue": "codex.tool_result"},
                                "extra": True,
                            }
                        ]
                    }
                ]
            ),
            self.logs_payload(
                [
                    {
                        "attributes": [
                            {"key": "event.name", "value": {"stringValue": 3}}
                        ]
                    }
                ]
            ),
            self.logs_payload([self.log_record(attributes={"success": "yes"})]),
            {"resourceLogs": [{"scopeLogs": [{"logRecords": [valid, None]}]}]},
        )
        for document in invalid_documents:
            with self.subTest(document=document):
                status, _, _ = self.post_json("/v1/logs", document)
                self.assertEqual(status, 400)
                self.assertEqual(self.records(), [])

    def test_private_permissions_and_retention(self) -> None:
        status, _, _ = self.post_json("/v1/logs", self.logs_payload([self.log_record()]))
        self.assertEqual(status, 200)
        output = next(self.data_dir.glob("*.jsonl"))
        self.assertEqual(stat.S_IMODE(self.data_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

        retention_dir = Path(self.temporary.name) / "retention"
        retention_dir.mkdir()
        expired_collector = retention_dir / "2000-01-01.jsonl"
        expired_hook = retention_dir / "hooks-2000-01-01.jsonl"
        undated = retention_dir / "hooks.jsonl"
        for path in (expired_collector, expired_hook, undated):
            path.write_text("old\n", encoding="utf-8")
        store = self.collector.JsonlStore(retention_dir, 2, 4096, 8192)
        self.assertFalse(expired_collector.exists())
        self.assertFalse(expired_hook.exists())
        self.assertTrue(undated.exists())
        self.assertEqual(store.directory_size(), len(b"old\n"))

    def test_normalized_write_limit_and_directory_quota(self) -> None:
        write_dir = Path(self.temporary.name) / "write-limit"
        self.start_server(data_dir=write_dir, max_write_bytes=64)
        status, _, _ = self.post_json("/v1/logs", self.logs_payload([self.log_record()]))
        self.assertEqual(status, 413)
        self.assertEqual(self.records(write_dir), [])

        quota_dir = Path(self.temporary.name) / "quota"
        quota_dir.mkdir()
        seed = quota_dir / "seed.bin"
        seed.write_bytes(b"x" * 128)
        self.start_server(data_dir=quota_dir, max_data_bytes=128)
        status, _, _ = self.post_json("/v1/logs", self.logs_payload([self.log_record()]))
        self.assertEqual(status, 507)
        self.assertEqual(seed.read_bytes(), b"x" * 128)
        self.assertEqual(self.records(quota_dir), [])

    def test_read_timeout_and_concurrency_limit(self) -> None:
        self.start_server(read_timeout_seconds=0.05, max_concurrent_requests=1)
        with socket.create_connection((self.host, self.port), timeout=2) as connection:
            connection.settimeout(2)
            connection.sendall(
                b"POST /v1/logs HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: 100\r\n\r\n{"
            )
            response = connection.recv(4096)
        self.assertIn(b" 408 ", response.split(b"\r\n", 1)[0])

        deadline = time.monotonic() + 1
        acquired = False
        while time.monotonic() < deadline and not acquired:
            acquired = self.server.request_slots.acquire(timeout=0.05)
        self.assertTrue(acquired)

        class FakeRequest:
            def __init__(self) -> None:
                self.sent = b""
                self.closed = False

            def sendall(self, value: bytes) -> None:
                self.sent += value

            def shutdown(self, how: int) -> None:
                return

            def close(self) -> None:
                self.closed = True

        request = FakeRequest()
        try:
            self.server.process_request(request, ("127.0.0.1", 1))
        finally:
            self.server.request_slots.release()
        self.assertIn(b" 503 ", request.sent.split(b"\r\n", 1)[0])
        self.assertTrue(request.closed)


class HookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hook = load_module("gmgn_test_hook", HOOK)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temporary.name) / "data"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_hook(
        self,
        payload: object = None,
        raw: bytes = b"",
        retention_days: int = 7,
        output_dir: Path | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        if payload is not None:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        destination = output_dir or self.output_dir
        result = subprocess.run(
            [
                sys.executable,
                str(HOOK),
                "--output-dir",
                str(destination),
                "--retention-days",
                str(retention_days),
            ],
            input=raw,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"")
        return result

    def read_records(self) -> list[dict]:
        records = []
        for path in sorted(self.output_dir.glob("hooks-*.jsonl")):
            records.extend(
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        return records

    def bash_payload(self, command: str) -> dict:
        return {
            "hookEventName": "PostToolUse",
            "sessionId": "session-1",
            "turnId": "turn-1",
            "toolName": "Bash",
            "toolUseId": "use-1",
            "model": "gpt-test",
            "cwd": "/private/secret/project",
            "toolInput": {"command": command},
            "toolResponse": {"output": "private-tool-output", "exitCode": 0},
            "prompt": "private-user-prompt",
        }

    def test_docstar_metadata_and_privacy(self) -> None:
        payload = self.bash_payload("docstar brief T0.7 --preset gmgn-v1 --json")
        self.run_hook(payload)
        record = self.read_records()[0]

        self.assertEqual(record["schema_version"], "gmgn-hook-event-v1")
        self.assertEqual(record["event"], "PostToolUse")
        self.assertEqual(record["session_id"], "session-1")
        self.assertEqual(record["turn_id"], "turn-1")
        self.assertEqual(record["tool_name"], "Bash")
        self.assertEqual(record["tool_use_id"], "use-1")
        self.assertEqual(record["model"], "gpt-test")
        self.assertEqual(record["classification"], "docstar")
        self.assertEqual(record["docstar_subcommand"], "brief")
        self.assertEqual(record["exit_code"], 0)
        self.assertTrue(record["success"])
        self.assertEqual(record["input_bytes"], compact_json_bytes(payload["toolInput"]))
        self.assertEqual(record["output_bytes"], compact_json_bytes(payload["toolResponse"]))
        self.assertEqual(
            record["project_path_hash"],
            hashlib.sha256(payload["cwd"].encode("utf-8")).hexdigest(),
        )

        serialized = json.dumps(record, ensure_ascii=False)
        for secret in (
            "docstar brief",
            "private-tool-output",
            "private-user-prompt",
            "/private/secret/project",
        ):
            self.assertNotIn(secret, serialized)

    def test_python_docstar_script_commands_and_safe_options(self) -> None:
        cases = (
            ("/usr/bin/python /opt/docstar.py brief T1", "brief"),
            ("python3.12 -I -B /opt/tools/docstar.py scan", "scan"),
            ("python3.11 -X dev -W ignore ./bin/docstar.py validate", "validate"),
            ("python3 -m docstar brief T1", "brief"),
        )
        for command, subcommand in cases:
            with self.subTest(command=command):
                self.run_hook(self.bash_payload(command))
                record = self.read_records()[-1]
                self.assertEqual(record["classification"], "docstar")
                self.assertEqual(record["docstar_subcommand"], subcommand)

        for command in (
            "python3 -c /opt/docstar.py brief",
            "python3 --unknown /opt/docstar.py brief",
            "python3 docstar.py brief",
        ):
            with self.subTest(command=command):
                self.run_hook(self.bash_payload(command))
                self.assertEqual(self.read_records()[-1]["classification"], "other")

    def test_bash_classification_is_conservative(self) -> None:
        cases = (
            ("rg needle README.md", "grep", None),
            ("rg --files", "other", None),
            ("cat docs/Guide.md", "markdown_read", None),
            (
                "sed -n '1,80p' /tmp/skills/run-task/SKILL.md",
                "skill_load",
                "run-task",
            ),
            ("printf done", "other", None),
            ("cd /tmp && rg needle", "unclassified_compound", None),
        )
        for command, expected, skill_name in cases:
            with self.subTest(command=command):
                self.run_hook(self.bash_payload(command))
                record = self.read_records()[-1]
                self.assertEqual(record["classification"], expected)
                if skill_name is None:
                    self.assertNotIn("skill_name", record)
                else:
                    self.assertEqual(record["skill_name"], skill_name)

    def test_agent_metadata_and_stop_output_length(self) -> None:
        secret = "do-not-store-agent-prompt"
        self.run_hook(
            {
                "hook_event_name": "PreToolUse",
                "session_id": "session-a",
                "turn_id": "turn-a",
                "tool_name": "spawn_agent",
                "tool_use_id": "use-a",
                "model": "gpt-parent",
                "cwd": "/private/agent/project",
                "tool_input": {
                    "message": (
                        f"{secret}\ncard_id: FAKE-CARD\nrun_id=FAKE-RUN\n"
                        "lane_key: FAKE-LANE\ntarget_milestone_id: FAKE-MILESTONE"
                    ),
                    "metadata": {
                        "card_id": "T0.7",
                        "run_id": "run-42",
                        "lane_key": "project:T0.7",
                        "target_milestone_id": "M0",
                    },
                    "forkContext": False,
                    "forkTurns": "none",
                },
            }
        )
        record = self.read_records()[0]
        self.assertEqual(record["classification"], "agent")
        self.assertIs(record["fork_context"], False)
        self.assertEqual(record["fork_turns"], "none")
        self.assertEqual(record["card_id"], "T0.7")
        self.assertEqual(record["run_id"], "run-42")
        self.assertEqual(record["lane_key"], "project:T0.7")
        self.assertEqual(record["target_milestone_id"], "M0")

        self.run_hook(
            {
                "hook_event_name": "PreToolUse",
                "session_id": "session-message-only",
                "tool_name": "spawn_agent",
                "tool_input": {
                    "message": (
                        "card_id: MESSAGE-CARD\nrun_id: MESSAGE-RUN\n"
                        "lane_key: MESSAGE-LANE\n"
                        "target_milestone_id: MESSAGE-MILESTONE"
                    )
                },
            }
        )
        message_only = self.read_records()[-1]
        for field_name in (
            "card_id",
            "run_id",
            "lane_key",
            "target_milestone_id",
        ):
            self.assertNotIn(field_name, message_only)

        stop_secret = "private-last-assistant-message"
        self.run_hook(
            {
                "hookEventName": "Stop",
                "sessionId": "session-stop",
                "lastAssistantMessage": stop_secret,
            }
        )
        stop = self.read_records()[-1]
        self.assertEqual(stop["output_bytes"], len(stop_secret.encode("utf-8")))
        serialized = json.dumps(self.read_records(), ensure_ascii=False)
        self.assertNotIn(secret, serialized)
        self.assertNotIn(stop_secret, serialized)
        self.assertNotIn("/private/agent/project", serialized)
        self.assertNotIn("FAKE-CARD", serialized)
        self.assertNotIn("MESSAGE-CARD", serialized)

    def test_wait_hook_records_result_without_output(self) -> None:
        secret = "private-agent-update"
        self.run_hook(
            {
                "hookEventName": "PostToolUse",
                "sessionId": "session-wait",
                "turnId": "turn-wait",
                "toolName": "collaboration.wait_agent",
                "toolUseId": "wait-use",
                "toolInput": {"timeout_ms": 30000},
                "toolResponse": {"summary": secret, "timed_out": True},
            }
        )
        record = self.read_records()[-1]
        self.assertEqual(record["classification"], "agent")
        self.assertEqual(record["agent_action"], "wait")
        self.assertEqual(record["wait_result"], "timeout")
        self.assertNotIn(secret, json.dumps(record, ensure_ascii=False))

        self.run_hook(
            {
                "hookEventName": "PostToolUse",
                "sessionId": "session-wait",
                "toolName": "wait_agent",
                "toolUseId": "wait-invalid",
                "toolInput": {"timeout_ms": 1},
                "toolResponse": "timeout_ms must be at least 10000",
            }
        )
        invalid = self.read_records()[-1]
        self.assertEqual(invalid["agent_action"], "wait")
        self.assertEqual(invalid["wait_result"], "unknown")

        self.run_hook(
            {
                "hookEventName": "PostToolUse",
                "sessionId": "session-wait",
                "toolName": "wait_agent",
                "toolUseId": "wait-structured-error",
                "toolResponse": {"status": "failed"},
            }
        )
        failed = self.read_records()[-1]
        self.assertFalse(failed["success"])
        self.assertEqual(failed["wait_result"], "error")

        self.run_hook(
            {
                "hookEventName": "PostToolUse",
                "sessionId": "session-wait",
                "toolName": "wait_agent",
                "toolUseId": "wait-status-timeout",
                "toolResponse": {"status": "timed_out"},
            }
        )
        timed_out = self.read_records()[-1]
        self.assertFalse(timed_out["success"])
        self.assertEqual(timed_out["wait_result"], "timeout")

    def test_daily_rotation_retention_and_permissions(self) -> None:
        now = self.hook.utc_now()
        expired = self.output_dir / f"hooks-{(now.date() - timedelta(days=2)).isoformat()}.jsonl"
        retained = self.output_dir / f"hooks-{(now.date() - timedelta(days=1)).isoformat()}.jsonl"
        legacy = self.output_dir / "hooks.jsonl"
        unrelated = self.output_dir / f"{(now.date() - timedelta(days=2)).isoformat()}.jsonl"
        self.output_dir.mkdir()
        for path in (expired, retained, legacy, unrelated):
            path.write_text("old\n", encoding="utf-8")

        self.run_hook(self.bash_payload("rg needle"), retention_days=2)
        current = self.output_dir / f"hooks-{now.date().isoformat()}.jsonl"
        self.assertTrue(current.is_file())
        self.assertFalse(expired.exists())
        self.assertTrue(retained.exists())
        self.assertFalse(legacy.exists())
        self.assertTrue(unrelated.exists())
        self.assertEqual(stat.S_IMODE(self.output_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(current.stat().st_mode), 0o600)

    def test_malformed_input_and_write_failure_are_silent_fail_open(self) -> None:
        self.run_hook(raw=b"{broken-json")
        self.assertEqual(self.read_records(), [])

        output_file = Path(self.temporary.name) / "not-a-directory"
        output_file.write_text("occupied", encoding="utf-8")
        result = self.run_hook(
            self.bash_payload("rg needle"),
            output_dir=output_file,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(output_file.read_text(encoding="utf-8"), "occupied")


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.installer = load_module("gmgn_test_installer", INSTALLER)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name) / "home"
        self.codex_home = self.home / ".codex-test"
        self.home.mkdir()
        self.layout = self.installer.make_layout(self.home, self.codex_home)
        self.python_path = Path("/opt/gmgn-python3.12")
        self.launchctl_calls: list[list[str]] = []
        self.environment = os.environ.copy()
        self.environment["HOME"] = str(self.home)
        self.environment["CODEX_HOME"] = str(self.codex_home)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def launchctl(self, command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.launchctl_calls.append(list(command))
        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertIs(kwargs["check"], False)
        return subprocess.CompletedProcess(command, 0, "", "")

    def install_runtime(self, launchctl_runner: object = None) -> None:
        self.installer.install(
            layout=self.layout,
            source_dir=ROOT / "telemetry",
            python_path=self.python_path,
            host="127.0.0.1",
            port=4318,
            retention_days=7,
            max_body_bytes=4096,
            max_write_bytes=2048,
            max_data_bytes=8192,
            read_timeout_seconds=1.5,
            max_concurrent_requests=3,
            launchctl_runner=launchctl_runner or self.launchctl,
            launchctl_uid=501,
        )

    def run_installer(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(INSTALLER), *arguments],
            env=self.environment,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def write_foreign_hooks(self) -> dict:
        lookalike = (
            f"echo {self.python_path} {self.layout.bin_dir / 'hook.py'} "
            f"--output-dir {self.layout.data_dir} --retention-days 7"
        )
        different_output = (
            f"{self.python_path} {self.layout.bin_dir / 'hook.py'} "
            "--output-dir /foreign/data --retention-days 8"
        )
        document = {
            "description": "keep this description",
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "^Write$",
                        "hooks": [
                            {"type": "command", "command": "python3 /foreign/post.py"},
                            {"type": "command", "command": lookalike},
                            {"type": "command", "command": different_output},
                        ],
                    }
                ],
                "Stop": [
                    {
                        "hooks": [
                            {"type": "command", "command": "python3 /foreign/stop.py"}
                        ]
                    }
                ],
                "UserPromptSubmit": [
                    {
                        "hooks": [
                            {"type": "command", "command": "python3 /foreign/prompt.py"}
                        ]
                    }
                ],
            },
        }
        self.codex_home.mkdir()
        self.layout.hooks_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return document

    def owned_handlers(self, document: dict) -> list[dict]:
        handlers = []
        for groups in document.get("hooks", {}).values():
            for group in groups:
                for handler in group.get("hooks", []):
                    if self.installer.is_owned_handler(handler, self.layout):
                        handlers.append(handler)
        return handlers

    def test_install_is_idempotent_preserves_foreign_hooks_and_copies_report(self) -> None:
        original = self.write_foreign_hooks()
        config_path = self.codex_home / "config.toml"
        config_path.write_text('model = "foreign-model"\n', encoding="utf-8")
        original_config = config_path.read_bytes()

        self.install_runtime()
        first_bytes = self.layout.hooks_path.read_bytes()
        self.install_runtime()
        self.assertEqual(self.layout.hooks_path.read_bytes(), first_bytes)
        self.assertEqual(config_path.read_bytes(), original_config)

        document = json.loads(first_bytes)
        self.assertEqual(document["description"], original["description"])
        serialized = json.dumps(document)
        for command in (
            "python3 /foreign/post.py",
            "python3 /foreign/stop.py",
            "python3 /foreign/prompt.py",
            "echo /opt/gmgn-python3.12",
            "--retention-days 8",
        ):
            self.assertIn(command, serialized)
        self.assertEqual(len(self.owned_handlers(document)), len(self.installer.HOOK_EVENTS))

        expected_command = self.installer.hook_command(self.layout, self.python_path, 7)
        for handler in self.owned_handlers(document):
            self.assertEqual(handler["command"], expected_command)
        self.assertIn("--output-dir", expected_command)
        self.assertIn("--retention-days 7", expected_command)

        for name in ("collector.py", "hook.py", "install.py", "report.py"):
            installed = self.layout.bin_dir / name
            self.assertTrue(installed.is_file())
            self.assertEqual(installed.read_bytes(), (ROOT / "telemetry" / name).read_bytes())

        with self.layout.plist_path.open("rb") as handle:
            launch_agent = plistlib.load(handle)
        arguments = launch_agent["ProgramArguments"]
        self.assertEqual(arguments[0], str(self.python_path))
        self.assertEqual(arguments[1], str(self.layout.bin_dir / "collector.py"))
        for value in (
            "--max-body-bytes",
            "4096",
            "--max-write-bytes",
            "2048",
            "--max-data-bytes",
            "8192",
            "--read-timeout-seconds",
            "1.5",
            "--max-concurrent-requests",
            "3",
        ):
            self.assertIn(value, arguments)
        self.assertTrue(launch_agent["RunAtLoad"])
        self.assertTrue(launch_agent["KeepAlive"])
        self.assertEqual(
            self.launchctl_calls,
            [
                ["launchctl", "bootout", "gui/501/com.gmgn.codex-telemetry"],
                ["launchctl", "bootstrap", "gui/501", str(self.layout.plist_path)],
                ["launchctl", "bootout", "gui/501/com.gmgn.codex-telemetry"],
                ["launchctl", "bootstrap", "gui/501", str(self.layout.plist_path)],
            ],
        )

    def test_strict_ownership_and_uninstall_remove_only_exact_handlers(self) -> None:
        self.write_foreign_hooks()
        exact = {
            "type": "command",
            "command": self.installer.hook_command(self.layout, self.python_path, 7),
        }
        variants = (
            {"type": "command", "command": exact["command"] + " --extra"},
            {"type": "command", "command": "echo " + exact["command"]},
            {
                "type": "command",
                "command": exact["command"].replace(
                    "/opt/gmgn-python3.12", "relative-python"
                ),
            },
            {
                "type": "command",
                "command": exact["command"].replace(
                    str(self.layout.data_dir), "/foreign/data"
                ),
            },
            {"type": "command", "command": exact["command"].replace(" 7", " 0")},
        )
        owned_variants = (
            exact,
            {
                "type": "command",
                "command": self.installer.hook_command(
                    self.layout, Path("/different/python3"), 7
                ),
            },
            {
                "type": "command",
                "command": self.installer.hook_command(self.layout, self.python_path, 8),
            },
        )
        for handler in owned_variants:
            self.assertTrue(self.installer.is_owned_handler(handler, self.layout))
        for handler in variants:
            self.assertFalse(self.installer.is_owned_handler(handler, self.layout))

        self.install_runtime()
        self.launchctl_calls.clear()
        self.installer.uninstall(
            self.layout,
            launchctl_runner=self.launchctl,
            launchctl_uid=501,
        )
        document = json.loads(self.layout.hooks_path.read_text(encoding="utf-8"))
        self.assertEqual(self.owned_handlers(document), [])
        serialized = json.dumps(document)
        self.assertIn("python3 /foreign/post.py", serialized)
        self.assertIn("echo /opt/gmgn-python3.12", serialized)
        self.assertIn("--retention-days 8", serialized)
        self.assertFalse(self.layout.plist_path.exists())
        self.assertTrue((self.layout.bin_dir / "hook.py").exists())
        self.assertTrue(self.layout.data_dir.exists())
        self.assertEqual(
            self.launchctl_calls,
            [["launchctl", "bootout", "gui/501/com.gmgn.codex-telemetry"]],
        )

    def test_launchctl_failure_is_explicit_and_preserves_uninstall_files(self) -> None:
        self.write_foreign_hooks()
        self.install_runtime()
        hooks_before = self.layout.hooks_path.read_bytes()
        plist_before = self.layout.plist_path.read_bytes()

        def failing_launchctl(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 5, "", "permission denied")

        with self.assertRaisesRegex(
            RuntimeError,
            r"launchctl bootout gui/501/com\.gmgn\.codex-telemetry failed with exit code 5: permission denied",
        ):
            self.installer.uninstall(
                self.layout,
                launchctl_runner=failing_launchctl,
                launchctl_uid=501,
            )
        self.assertEqual(self.layout.hooks_path.read_bytes(), hooks_before)
        self.assertEqual(self.layout.plist_path.read_bytes(), plist_before)

        def bootstrap_failure(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 9, "", "bootstrap denied")

        with self.assertRaisesRegex(RuntimeError, "bootstrap denied"):
            self.installer.run_launchctl(
                "bootstrap",
                self.layout,
                bootstrap_failure,
                501,
            )

    def test_bootout_not_found_is_idempotent(self) -> None:
        self.write_foreign_hooks()
        self.install_runtime()
        commands = []

        def unloaded_service(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess[str]:
            commands.append(list(command))
            if command[1] == "bootout":
                return subprocess.CompletedProcess(
                    command,
                    3,
                    "",
                    "Boot-out failed: 3: No such process",
                )
            return subprocess.CompletedProcess(command, 0, "", "")

        self.install_runtime(unloaded_service)
        self.assertTrue(self.layout.plist_path.exists())
        self.assertEqual([command[1] for command in commands], ["bootout", "bootstrap"])
        commands.clear()
        self.installer.uninstall(
            self.layout,
            launchctl_runner=unloaded_service,
            launchctl_uid=501,
        )
        self.assertEqual([command[1] for command in commands], ["bootout"])
        self.assertFalse(self.layout.plist_path.exists())

    def test_python_option_config_and_dry_run_do_not_write_or_launch(self) -> None:
        self.assertEqual(self.installer.stable_python(), Path(sys.executable))
        parsed = self.installer.parse_args(["--python", "/custom/python3.13"])
        self.assertEqual(parsed.python, Path("/custom/python3.13"))

        result = self.run_installer("--print-codex-config")
        self.assertIn("[otel]", result.stdout)
        self.assertIn("http://127.0.0.1:4318/v1/logs", result.stdout)
        self.assertIn('protocol = "json"', result.stdout)
        self.assertIn("log_user_prompt = false", result.stdout)
        self.assertIn('trace_exporter = "none"', result.stdout)
        self.assertIn('metrics_exporter = "none"', result.stdout)
        self.assertFalse(self.codex_home.exists())

        dry_run = self.run_installer(
            "--dry-run",
            "--python",
            "/custom/python3.13",
            "--retention-days",
            "9",
        )
        self.assertIn("report.py", dry_run.stdout)
        self.assertIn("/custom/python3.13", dry_run.stdout)
        self.assertIn("--output-dir", dry_run.stdout)
        self.assertIn("--retention-days 9", dry_run.stdout)
        self.assertIn("launchctl bootstrap", dry_run.stdout)
        self.assertFalse(self.codex_home.exists())
        self.assertFalse(self.layout.plist_path.exists())


if __name__ == "__main__":
    unittest.main()
