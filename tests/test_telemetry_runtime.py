#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import stat
import subprocess
import sys
import tempfile
import threading
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
        self.server = self.collector.create_server(
            host="127.0.0.1",
            port=0,
            data_dir=self.data_dir,
            retention_days=7,
            max_body_bytes=4096,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address[:2]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.temporary.cleanup()

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

    def records(self) -> list[dict]:
        records = []
        for path in sorted(self.data_dir.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        return records

    def test_health_and_valid_logs_are_persisted(self) -> None:
        status, body, headers = self.request("GET", "/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {})
        self.assertEqual(headers["content-type"], "application/json")

        payload = {"resourceLogs": []}
        status, body, _ = self.post_json("/v1/logs", payload)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {})

        records = self.records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["schema_version"], "gmgn-otel-envelope-v1")
        self.assertEqual(records[0]["signal"], "logs")
        self.assertEqual(records[0]["content_type"], "application/json")
        self.assertEqual(records[0]["body"], payload)
        self.assertTrue(records[0]["received_at"].endswith("Z"))

    def test_path_schema_content_type_and_size_fail_closed(self) -> None:
        status, _, _ = self.post_json("/v1/logs", {"resourceSpans": []})
        self.assertEqual(status, 400)

        status, _, _ = self.post_json("/v1/unknown", {"resourceLogs": []})
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
            "POST",
            "/v1/logs",
            b'{"resourceLogs":[],"resourceLogs":[]}',
        )
        self.assertEqual(status, 400)

        status, _, _ = self.request(
            "POST",
            "/v1/logs",
            b'{"resourceLogs":[NaN]}',
        )
        self.assertEqual(status, 400)

        oversized = json.dumps({"resourceLogs": [], "padding": "x" * 5000}).encode()
        status, _, _ = self.request("POST", "/v1/logs", oversized)
        self.assertEqual(status, 413)
        self.assertEqual(self.records(), [])

    def test_traces_and_metrics_use_their_matching_roots(self) -> None:
        for path, root in (
            ("/v1/traces", "resourceSpans"),
            ("/v1/metrics", "resourceMetrics"),
        ):
            with self.subTest(path=path):
                status, body, _ = self.post_json(path, {root: []})
                self.assertEqual(status, 200)
                self.assertEqual(json.loads(body), {})
        self.assertEqual(
            [record["signal"] for record in self.records()],
            ["traces", "metrics"],
        )

    def test_sensitive_bodies_are_redacted_without_losing_metadata(self) -> None:
        prompt = "prompt-绝密"
        tool_output = "tool-output-绝密"
        nested_output = "nested-output-绝密"
        payload = {
            "resourceLogs": [
                {
                    "resource": {
                        "attributes": [
                            {
                                "key": "gen_ai.prompt",
                                "value": {"stringValue": prompt},
                            },
                            {
                                "key": "gen_ai.usage.input_tokens",
                                "value": {"intValue": "42"},
                            },
                            {
                                "key": "session.id",
                                "value": {"stringValue": "session-123"},
                            },
                        ]
                    },
                    "scopeLogs": [
                        {
                            "logRecords": [
                                {
                                    "body": {"stringValue": tool_output},
                                    "toolOutput": {
                                        "output": nested_output,
                                        "status": "ok",
                                        "tokenCount": 3,
                                        "responseId": "response-123",
                                    },
                                    "attributes": [
                                        {
                                            "key": "duration_ms",
                                            "value": {"intValue": "15"},
                                        },
                                        {
                                            "key": "status",
                                            "value": {"stringValue": "ok"},
                                        },
                                    ],
                                }
                            ]
                        }
                    ],
                }
            ]
        }

        status, _, _ = self.post_json("/v1/logs", payload)
        self.assertEqual(status, 200)
        record = self.records()[0]
        serialized = json.dumps(record, ensure_ascii=False)
        self.assertNotIn(prompt, serialized)
        self.assertNotIn(tool_output, serialized)
        self.assertNotIn(nested_output, serialized)
        self.assertIn("gen_ai.usage.input_tokens", serialized)
        self.assertIn('"intValue": "42"', serialized)
        self.assertIn("session-123", serialized)
        self.assertIn("duration_ms", serialized)
        self.assertIn('"stringValue": "ok"', serialized)
        self.assertIn("response-123", serialized)
        self.assertIn('"tokenCount": 3', serialized)

        redactions = []

        def visit(value: object) -> None:
            if isinstance(value, dict):
                if value.get("redacted") is True:
                    redactions.append(value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(record["body"])
        self.assertGreaterEqual(len(redactions), 2)
        expected_hashes = {
            hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            hashlib.sha256(tool_output.encode("utf-8")).hexdigest(),
            hashlib.sha256(nested_output.encode("utf-8")).hexdigest(),
        }
        self.assertTrue(expected_hashes.issubset({item["sha256"] for item in redactions}))
        for redaction in redactions:
            self.assertEqual(set(redaction), {"length", "sha256", "redacted"})

    def test_data_permissions_are_private(self) -> None:
        status, _, _ = self.post_json("/v1/logs", {"resourceLogs": []})
        self.assertEqual(status, 200)
        output = next(self.data_dir.glob("*.jsonl"))
        self.assertEqual(stat.S_IMODE(self.data_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_startup_removes_expired_dated_jsonl(self) -> None:
        old_data = Path(self.temporary.name) / "old"
        old_data.mkdir()
        expired = old_data / "2000-01-01.jsonl"
        expired.write_text("old\n", encoding="utf-8")
        unrelated = old_data / "hooks.jsonl"
        unrelated.write_text("keep\n", encoding="utf-8")

        server = self.collector.create_server(
            host="127.0.0.1",
            port=0,
            data_dir=old_data,
            retention_days=2,
            max_body_bytes=1024,
        )
        server.server_close()
        self.assertFalse(expired.exists())
        self.assertTrue(unrelated.exists())


class HookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.output = Path(self.temporary.name) / "data" / "hooks.jsonl"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_hook(self, payload: object = None, raw: bytes = b"") -> subprocess.CompletedProcess:
        if payload is not None:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        result = subprocess.run(
            [sys.executable, str(HOOK), "--output", str(self.output)],
            input=raw,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"")
        return result

    def read_records(self) -> list[dict]:
        if not self.output.exists():
            return []
        return [
            json.loads(line)
            for line in self.output.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

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
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)

        serialized = self.output.read_text(encoding="utf-8")
        for secret in (
            "docstar brief",
            "private-tool-output",
            "private-user-prompt",
            "/private/secret/project",
        ):
            self.assertNotIn(secret, serialized)

        allowed = {
            "schema_version",
            "timestamp",
            "event",
            "session_id",
            "turn_id",
            "tool_name",
            "tool_use_id",
            "model",
            "project_path_hash",
            "input_bytes",
            "output_bytes",
            "success",
            "exit_code",
            "classification",
            "docstar_subcommand",
            "skill_name",
            "card_id",
            "run_id",
            "lane_key",
            "target_milestone_id",
            "fork_context",
            "fork_turns",
        }
        self.assertLessEqual(set(record), allowed)

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

    def test_agent_pretool_extracts_policy_and_semantic_ids_only(self) -> None:
        secret = "do-not-store-agent-prompt"
        payload = {
            "hook_event_name": "PreToolUse",
            "session_id": "session-a",
            "turn_id": "turn-a",
            "tool_name": "spawn_agent",
            "tool_use_id": "use-a",
            "model": "gpt-parent",
            "cwd": "/private/agent/project",
            "tool_input": {
                "message": (
                    f"{secret}\ncard_id: T0.7\nrun_id=run-42\n"
                    "lane_key: project:T0.7\ntarget_milestone_id: M0"
                ),
                "forkContext": False,
                "forkTurns": "none",
            },
        }
        self.run_hook(payload)
        record = self.read_records()[0]
        self.assertEqual(record["classification"], "agent")
        self.assertIs(record["fork_context"], False)
        self.assertEqual(record["fork_turns"], "none")
        self.assertEqual(record["card_id"], "T0.7")
        self.assertEqual(record["run_id"], "run-42")
        self.assertEqual(record["lane_key"], "project:T0.7")
        self.assertEqual(record["target_milestone_id"], "M0")
        serialized = self.output.read_text(encoding="utf-8")
        self.assertNotIn(secret, serialized)
        self.assertNotIn("/private/agent/project", serialized)

    def test_stop_counts_last_message_without_persisting_it(self) -> None:
        secret = "private-last-assistant-message"
        self.run_hook(
            {
                "hookEventName": "Stop",
                "sessionId": "session-stop",
                "turnId": "turn-stop",
                "model": "gpt-test",
                "cwd": "/private/stop/project",
                "lastAssistantMessage": secret,
            }
        )
        record = self.read_records()[0]
        self.assertEqual(record["output_bytes"], len(secret.encode("utf-8")))
        self.assertNotIn(secret, self.output.read_text(encoding="utf-8"))

    def test_malformed_input_and_write_failure_are_silent_fail_open(self) -> None:
        self.run_hook(raw=b"{broken-json")
        self.assertEqual(self.read_records(), [])

        self.output.parent.mkdir(parents=True)
        directory_output = self.output.parent / "directory"
        directory_output.mkdir()
        result = subprocess.run(
            [sys.executable, str(HOOK), "--output", str(directory_output)],
            input=json.dumps(self.bash_payload("rg needle")).encode(),
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"")


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name) / "home"
        self.codex_home = self.home / ".codex-test"
        self.home.mkdir()
        self.environment = os.environ.copy()
        self.environment["HOME"] = str(self.home)
        self.environment["CODEX_HOME"] = str(self.codex_home)
        self.hooks_path = self.codex_home / "hooks.json"
        self.plist_path = (
            self.home
            / "Library"
            / "LaunchAgents"
            / "com.gmgn.codex-telemetry.plist"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

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
        document = {
            "description": "keep this description",
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "^Write$",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python3 /foreign/post.py",
                            }
                        ],
                    }
                ],
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python3 /foreign/stop.py",
                            }
                        ]
                    }
                ],
                "UserPromptSubmit": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python3 /foreign/prompt.py",
                            }
                        ]
                    }
                ],
            },
        }
        self.codex_home.mkdir()
        self.hooks_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return document

    def owned_handlers(self, document: dict) -> list[dict]:
        handlers = []
        for groups in document.get("hooks", {}).values():
            for group in groups:
                for handler in group.get("hooks", []):
                    if "gmgn-telemetry/bin/hook.py" in handler.get("command", ""):
                        handlers.append(handler)
        return handlers

    def test_install_is_idempotent_and_preserves_foreign_hooks(self) -> None:
        original = self.write_foreign_hooks()
        config_path = self.codex_home / "config.toml"
        config_path.write_text('model = "foreign-model"\n', encoding="utf-8")
        original_config = config_path.read_bytes()
        self.run_installer()
        first_bytes = self.hooks_path.read_bytes()
        self.run_installer()
        self.assertEqual(self.hooks_path.read_bytes(), first_bytes)
        self.assertEqual(config_path.read_bytes(), original_config)

        document = json.loads(first_bytes)
        self.assertEqual(document["description"], original["description"])
        serialized = json.dumps(document)
        for command in (
            "python3 /foreign/post.py",
            "python3 /foreign/stop.py",
            "python3 /foreign/prompt.py",
        ):
            self.assertIn(command, serialized)

        expected_events = {
            "SessionStart",
            "PostToolUse",
            "PreToolUse",
            "SubagentStart",
            "SubagentStop",
            "Stop",
        }
        self.assertEqual(len(self.owned_handlers(document)), len(expected_events))
        for event in expected_events:
            event_handlers = [
                handler
                for group in document["hooks"][event]
                for handler in group["hooks"]
                if "gmgn-telemetry/bin/hook.py" in handler.get("command", "")
            ]
            self.assertEqual(len(event_handlers), 1, event)

        telemetry_root = self.codex_home / "gmgn-telemetry"
        for name in ("collector.py", "hook.py", "install.py"):
            self.assertTrue((telemetry_root / "bin" / name).is_file())
        self.assertTrue((telemetry_root / "data").is_dir())
        self.assertEqual(stat.S_IMODE((telemetry_root / "data").stat().st_mode), 0o700)

        with self.plist_path.open("rb") as handle:
            launch_agent = plistlib.load(handle)
        arguments = launch_agent["ProgramArguments"]
        self.assertEqual(arguments[0], str(Path(sys.executable).resolve()))
        self.assertEqual(arguments[1], str(telemetry_root / "bin" / "collector.py"))
        self.assertIn("127.0.0.1", arguments)
        self.assertIn("4318", arguments)
        self.assertTrue(launch_agent["RunAtLoad"])
        self.assertTrue(launch_agent["KeepAlive"])
        self.assertEqual(
            launch_agent["StandardOutPath"],
            str(telemetry_root / "logs" / "collector.stdout.log"),
        )
        self.assertEqual(
            launch_agent["StandardErrorPath"],
            str(telemetry_root / "logs" / "collector.stderr.log"),
        )

    def test_uninstall_removes_only_owned_hooks_and_launch_agent(self) -> None:
        self.write_foreign_hooks()
        self.run_installer()
        telemetry_root = self.codex_home / "gmgn-telemetry"
        self.run_installer("uninstall")

        document = json.loads(self.hooks_path.read_text(encoding="utf-8"))
        self.assertEqual(self.owned_handlers(document), [])
        serialized = json.dumps(document)
        self.assertIn("python3 /foreign/post.py", serialized)
        self.assertIn("python3 /foreign/stop.py", serialized)
        self.assertIn("python3 /foreign/prompt.py", serialized)
        self.assertFalse(self.plist_path.exists())
        self.assertTrue((telemetry_root / "bin" / "hook.py").exists())
        self.assertTrue((telemetry_root / "data").exists())

    def test_print_config_and_dry_run_do_not_write(self) -> None:
        result = self.run_installer("--print-codex-config")
        self.assertIn("[otel]", result.stdout)
        self.assertIn("otlp-http", result.stdout)
        self.assertIn("http://127.0.0.1:4318/v1/logs", result.stdout)
        self.assertIn('protocol = "json"', result.stdout)
        self.assertIn("log_user_prompt = false", result.stdout)
        self.assertIn('trace_exporter = "none"', result.stdout)
        self.assertIn('metrics_exporter = "none"', result.stdout)
        self.assertFalse(self.codex_home.exists())
        self.assertFalse(self.plist_path.exists())

        dry_run = self.run_installer("--dry-run")
        self.assertIn(str(self.hooks_path), dry_run.stdout)
        self.assertIn(str(self.plist_path), dry_run.stdout)
        self.assertFalse(self.codex_home.exists())
        self.assertFalse(self.plist_path.exists())


if __name__ == "__main__":
    unittest.main()
