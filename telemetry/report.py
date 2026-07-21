#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shlex
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


SCHEMA_VERSION = "gmgn.telemetry.report.v1"
SOURCE = "session_jsonl_unstable_fallback"
OTEL_SOURCE = "collector_otel"
HOOK_SOURCE = "gmgn_hook"
MIXED_SOURCE = "mixed"
OTEL_ENVELOPE_VERSION = "gmgn-otel-envelope-v1"
OTEL_EVENT_VERSION = "gmgn-otel-event-v1"
HOOK_EVENT_VERSION = "gmgn-hook-event-v1"
DEFAULT_FOLLOW_WINDOW = 5
ESTIMATED_CHARACTERS_PER_TOKEN = 4

TOKEN_FIELDS = ("input", "cached", "output", "reasoning", "total")
IDENTIFIER_FIELDS = ("card_id", "run_id", "lane_key", "target_milestone_id")
FORK_CONTEXT_VALUES = ("none", "all", "false", "true", "unspecified")
OTEL_TOKEN_ATTRIBUTES = {
    "input": ("gen_ai.usage.input_tokens", "input_token_count"),
    "cached": (
        "gen_ai.usage.cache_read.input_tokens",
        "cached_token_count",
    ),
    "output": ("gen_ai.usage.output_tokens", "output_token_count"),
    "reasoning": (
        "codex.usage.reasoning_output_tokens",
        "reasoning_token_count",
    ),
    "total": ("codex.usage.total_tokens", "tool_token_count"),
}
OTEL_COMMON_ATTRIBUTES = {
    "conversation.id",
    "event.name",
    "event.timestamp",
    "model",
}
KNOWN_OTEL_EVENTS = {
    "codex.api_request",
    "codex.conversation_starts",
    "codex.sse_event",
    "codex.tool_decision",
    "codex.tool_result",
    "codex.user_prompt",
    "codex.websocket_event",
    "codex.websocket_request",
}
OTEL_API_ATTRIBUTES = {
    "attempt",
    "duration_ms",
    "endpoint",
    "http.response.status_code",
    "status_code",
    "status",
    "success",
}
OTEL_SSE_ATTRIBUTES = {
    "event.kind",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "gen_ai.usage.cache_write.input_tokens",
    "gen_ai.usage.output_tokens",
    "codex.usage.reasoning_output_tokens",
    "codex.usage.total_tokens",
    "input_token_count",
    "cached_token_count",
    "cache_write_token_count",
    "output_token_count",
    "reasoning_token_count",
    "tool_token_count",
}
OTEL_TOOL_ATTRIBUTES = {
    "tool_name",
    "call_id",
    "duration_ms",
    "success",
    "output_length",
    "output_line_count",
    "mcp_server",
    "mcp_server_origin",
    "tool_origin",
}
HOOK_ALLOWED_FIELDS = {
    "schema_version",
    "timestamp",
    "event",
    "session_id",
    "turn_id",
    "tool_name",
    "tool_use_id",
    "model",
    "input_bytes",
    "output_bytes",
    "success",
    "exit_code",
    "classification",
    "agent_action",
    "wait_result",
    "docstar_subcommand",
    "skill_name",
    "card_id",
    "run_id",
    "lane_key",
    "target_milestone_id",
    "fork_context",
    "fork_turns",
}

CALL_TYPES = {
    "function_call": "function",
    "custom_tool_call": "custom",
}
OUTPUT_TYPES = {
    "function_call_output": "function",
    "custom_tool_call_output": "custom",
}

SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/+~=-]{0,255}$")
UUID_AT_END = re.compile(
    r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
)
SKILL_PATH = re.compile(
    r"(?:^|/)skills/([A-Za-z0-9][A-Za-z0-9._-]*)/SKILL\.md(?:\b|$)",
    re.IGNORECASE,
)
MARKDOWN_PATH = re.compile(r"\.m(?:arkdown|d)(?:\b|$)", re.IGNORECASE)

WAIT_TOOLS = {"wait", "wait_agent", "wait_agents", "wait_threads"}
WAIT_RESULT_VALUES = ("update", "timeout", "interrupted", "error", "unknown")
AGENT_TOOLS = {
    "create_thread",
    "followup_task",
    "interrupt_agent",
    "list_agents",
    "list_threads",
    "read_thread",
    "send_message",
    "send_message_to_agent",
    "send_message_to_thread",
    "spawn",
    "spawn_agent",
}
WRITE_TOOLS = {
    "apply_patch",
    "edit",
    "edit_file",
    "write",
    "write_file",
}
READ_TOOLS = {"read", "read_file"}
SPAWN_TOOLS = {"spawn", "spawn_agent"}
SEND_TOOLS = {
    "followup_task",
    "send_message",
    "send_message_to_agent",
    "send_message_to_thread",
}

READ_COMMANDS = {"awk", "cat", "head", "less", "more", "sed", "tail"}
WRITE_COMMANDS = {
    "apply_patch",
    "chmod",
    "chown",
    "cp",
    "install",
    "mkdir",
    "mv",
    "rm",
    "tee",
    "touch",
    "truncate",
}


@dataclass(frozen=True)
class _SessionDescriptor:
    path: Path
    session_id: str
    aliases: Tuple[str, ...]
    filename_aliases: Tuple[str, ...]
    is_subagent: bool


@dataclass
class _RawOutput:
    family: str
    call_id: Optional[str]
    value: Any
    sequence: int
    timestamp: Optional[str]
    timestamp_ms: Optional[float]
    matched: bool = False


@dataclass
class _RawCall:
    family: str
    session_id: str
    call_id: Optional[str]
    tool: str
    arguments: Any
    status: Any
    sequence: int
    turn_id: Optional[str]
    turn_key: str
    start: Optional[str]
    start_ms: Optional[float]
    output: Optional[_RawOutput] = None
    category: str = "other"
    docstar_commands: List[str] = field(default_factory=list)
    skill_names: List[str] = field(default_factory=list)

    @property
    def end(self) -> Optional[str]:
        return self.output.timestamp if self.output else None

    @property
    def end_ms(self) -> Optional[float]:
        return self.output.timestamp_ms if self.output else None

    @property
    def duration_ms(self) -> Optional[int]:
        if self.start_ms is None or self.end_ms is None or self.end_ms < self.start_ms:
            return None
        return int(round(self.end_ms - self.start_ms))

    @property
    def estimated_input_tokens(self) -> int:
        return _estimate_tokens(self.arguments)

    @property
    def estimated_output_tokens(self) -> int:
        if self.output is None:
            return 0
        return _estimate_tokens(self.output.value)

    def public(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "call_id": self.call_id,
            "tool": self.tool,
            "category": self.category,
            "start": self.start,
            "end": self.end,
            "duration_ms": self.duration_ms,
            "success": _infer_success(self.status, self.output),
            "estimated_input_tokens": self.estimated_input_tokens,
            "estimated_output_tokens": self.estimated_output_tokens,
        }


@dataclass(frozen=True)
class _TokenSnapshot:
    sequence: int
    turn_key: str
    values: Mapping[str, Optional[int]]


@dataclass
class _SessionData:
    descriptor: _SessionDescriptor
    calls: List[_RawCall]
    child_ids: List[str]
    actual_tokens: Dict[str, Optional[int]]
    token_snapshots: List[_TokenSnapshot]
    malformed_lines: int
    unpaired_calls: int
    completed_turn_duration_ms: int
    wall_elapsed_ms: Optional[int]
    session_end_ms: Optional[float]


@dataclass(frozen=True)
class _OtelEvent:
    session_id: str
    event_name: str
    timestamp: Optional[str]
    timestamp_ms: Optional[float]
    attributes: Mapping[str, Any]
    sequence: int


@dataclass(frozen=True)
class _HookEvent:
    session_id: str
    timestamp: Optional[str]
    timestamp_ms: Optional[float]
    fields: Mapping[str, Any]
    sequence: int


class _SessionIndex:
    def __init__(self, codex_home: Path) -> None:
        self.sessions_root = codex_home / "sessions"
        self.descriptors: List[_SessionDescriptor] = []
        self.by_alias: Dict[str, List[_SessionDescriptor]] = defaultdict(list)
        if not self.sessions_root.is_dir():
            return
        for path in sorted(self.sessions_root.rglob("*.jsonl")):
            descriptor = self._describe(path)
            self.descriptors.append(descriptor)
            for alias in descriptor.aliases:
                self.by_alias[alias].append(descriptor)

    def resolve(self, requested_id: str) -> Optional[_SessionDescriptor]:
        candidates = self.by_alias.get(requested_id, [])
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda item: (
                item.session_id != requested_id,
                requested_id not in item.filename_aliases,
                item.is_subagent,
                str(item.path),
            ),
        )

    def _describe(self, path: Path) -> _SessionDescriptor:
        filename_aliases = {path.stem}
        uuid_match = UUID_AT_END.search(path.stem)
        if uuid_match:
            filename_aliases.add(uuid_match.group(1))

        metadata: Mapping[str, Any] = {}
        try:
            with path.open("r", encoding="utf-8", errors="replace") as stream:
                for line in stream:
                    try:
                        item = json.loads(line)
                    except (json.JSONDecodeError, TypeError):
                        continue
                    if not isinstance(item, dict) or item.get("type") != "session_meta":
                        continue
                    payload = item.get("payload")
                    if isinstance(payload, dict):
                        metadata = payload
                    break
        except OSError:
            metadata = {}

        aliases: Set[str] = set(filename_aliases)
        for key in ("id", "session_id", "thread_id", "task_id"):
            value = _identifier(metadata.get(key))
            if value:
                aliases.add(value)
        session_id = (
            _identifier(metadata.get("id"))
            or _identifier(metadata.get("thread_id"))
            or _identifier(metadata.get("session_id"))
            or (uuid_match.group(1) if uuid_match else path.stem)
        )
        source = metadata.get("source")
        is_subagent = (
            metadata.get("thread_source") == "subagent"
            or _identifier(metadata.get("parent_thread_id")) is not None
            or (isinstance(source, dict) and "subagent" in source)
        )
        return _SessionDescriptor(
            path=path,
            session_id=session_id,
            aliases=tuple(sorted(aliases)),
            filename_aliases=tuple(sorted(filename_aliases)),
            is_subagent=is_subagent,
        )


def _identifier(value: Any) -> Optional[str]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (str, int)):
        candidate = str(value).strip()
        if SAFE_IDENTIFIER.fullmatch(candidate):
            return candidate
    return None


def _timestamp(value: Any) -> Tuple[Optional[str], Optional[float]]:
    if isinstance(value, bool) or value is None:
        return None, None
    if isinstance(value, (int, float)):
        seconds = float(value)
        if abs(seconds) > 100000000000:
            seconds /= 1000
        try:
            parsed = datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None, None
        public = parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        return public, seconds * 1000
    if not isinstance(value, str):
        return None, None
    candidate = value.strip()
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        try:
            return _timestamp(float(candidate))
        except ValueError:
            return None, None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return candidate, parsed.timestamp() * 1000


def _format_timestamp(milliseconds: float) -> str:
    parsed = datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _otel_time(value: Any) -> Tuple[Optional[str], Optional[float]]:
    if isinstance(value, str) and value.isdigit():
        value = int(value)
    if isinstance(value, int) and not isinstance(value, bool):
        milliseconds = value / 1000000
        try:
            return _format_timestamp(milliseconds), milliseconds
        except (OverflowError, OSError, ValueError):
            return None, None
    return _timestamp(value)


def _otel_value(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    for key in ("stringValue", "intValue", "doubleValue", "boolValue", "bytesValue"):
        if key not in value:
            continue
        candidate = value[key]
        if key == "intValue" and isinstance(candidate, str):
            try:
                return int(candidate)
            except ValueError:
                return None
        return candidate
    array_value = value.get("arrayValue")
    if isinstance(array_value, dict) and isinstance(array_value.get("values"), list):
        return [_otel_value(item) for item in array_value["values"]]
    list_value = value.get("kvlistValue")
    if isinstance(list_value, dict) and isinstance(list_value.get("values"), list):
        return _otel_attributes(list_value["values"])
    return None


def _otel_attributes(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, list):
        return {}
    result: Dict[str, Any] = {}
    for item in value:
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        if isinstance(key, str):
            result[key] = _otel_value(item.get("value"))
    return result


def _otel_allowed_attributes(event_name: str) -> Set[str]:
    if event_name not in KNOWN_OTEL_EVENTS:
        return set()
    allowed = set(OTEL_COMMON_ATTRIBUTES)
    if event_name in {"codex.api_request", "codex.websocket_request"}:
        allowed.update(OTEL_API_ATTRIBUTES)
    elif event_name in {"codex.sse_event", "codex.websocket_event"}:
        allowed.update(OTEL_SSE_ATTRIBUTES)
    elif event_name == "codex.tool_result":
        allowed.update(OTEL_TOOL_ATTRIBUTES)
    return allowed


def _otel_log_records(body: Any) -> Iterable[Tuple[Mapping[str, Any], Mapping[str, Any]]]:
    if not isinstance(body, dict):
        return
    resource_logs = body.get("resourceLogs")
    if not isinstance(resource_logs, list):
        return
    for resource_log in resource_logs:
        if not isinstance(resource_log, dict):
            continue
        resource = resource_log.get("resource")
        resource_attributes = _otel_attributes(
            resource.get("attributes") if isinstance(resource, dict) else None
        )
        scope_logs = resource_log.get("scopeLogs")
        if not isinstance(scope_logs, list):
            continue
        for scope_log in scope_logs:
            if not isinstance(scope_log, dict):
                continue
            log_records = scope_log.get("logRecords")
            if not isinstance(log_records, list):
                continue
            for log_record in log_records:
                if isinstance(log_record, dict):
                    yield resource_attributes, log_record


def _safe_integer(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value.strip()):
        return int(value.strip())
    return None


def _safe_boolean(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "false"}:
            return normalized == "true"
    return None


class _TelemetryStore:
    def __init__(self, codex_home: Path) -> None:
        self.data_dir = codex_home / "gmgn-telemetry" / "data"
        self.otel_by_session: Dict[str, List[_OtelEvent]] = defaultdict(list)
        self.hooks_by_session: Dict[str, List[_HookEvent]] = defaultdict(list)
        self.malformed_lines = 0
        self._otel_seen: Set[str] = set()
        self._hook_seen: Set[str] = set()
        self._sequence = 0
        if not self.data_dir.is_dir():
            return
        for path in sorted(self.data_dir.glob("*.jsonl")):
            self._load_path(path)

    @property
    def otel_records(self) -> int:
        return sum(len(events) for events in self.otel_by_session.values())

    @property
    def hook_records(self) -> int:
        return sum(len(events) for events in self.hooks_by_session.values())

    def has_session(self, session_id: str) -> bool:
        return session_id in self.otel_by_session or session_id in self.hooks_by_session

    def _load_path(self, path: Path) -> None:
        try:
            stream = path.open("r", encoding="utf-8", errors="replace")
        except OSError:
            self.malformed_lines += 1
            return
        with stream:
            for line in stream:
                try:
                    document = json.loads(line)
                except (json.JSONDecodeError, TypeError):
                    self.malformed_lines += 1
                    continue
                if not isinstance(document, dict):
                    self.malformed_lines += 1
                    continue
                schema_version = document.get("schema_version")
                if schema_version == HOOK_EVENT_VERSION:
                    self._add_hook(document)
                elif schema_version == OTEL_ENVELOPE_VERSION:
                    self._add_envelope(document)
                elif "event_name" in document and "conversation_id" in document:
                    self._add_flat_otel(document)

    def _add_envelope(self, envelope: Mapping[str, Any]) -> None:
        if envelope.get("signal") != "logs":
            return
        received_at = envelope.get("received_at")
        for resource_attributes, log_record in _otel_log_records(envelope.get("body")):
            attributes = dict(resource_attributes)
            attributes.update(_otel_attributes(log_record.get("attributes")))
            self._add_otel_event(attributes, log_record, received_at)

    def _add_flat_otel(self, document: Mapping[str, Any]) -> None:
        attributes = _otel_attributes(document.get("attributes"))
        attributes.setdefault("conversation.id", document.get("conversation_id"))
        attributes.setdefault("event.name", document.get("event_name"))
        attributes.setdefault("event.timestamp", document.get("timestamp"))
        attributes.setdefault("model", document.get("model"))
        event_name = _identifier(attributes.get("event.name"))
        if event_name is not None:
            for key in _otel_allowed_attributes(event_name):
                if key in document:
                    attributes.setdefault(key, document.get(key))
        self._add_otel_event(attributes, document, document.get("received_at"))

    def _add_otel_event(
        self,
        raw_attributes: Mapping[str, Any],
        record: Mapping[str, Any],
        fallback_timestamp: Any,
    ) -> None:
        session_id = _identifier(raw_attributes.get("conversation.id"))
        event_name = _identifier(raw_attributes.get("event.name"))
        if session_id is None or event_name is None:
            return
        allowed = _otel_allowed_attributes(event_name)
        if not allowed:
            return
        attributes = {
            key: value
            for key, value in raw_attributes.items()
            if key in allowed and value is not None
        }
        public_time, timestamp_ms = _timestamp(attributes.get("event.timestamp"))
        if timestamp_ms is None:
            public_time, timestamp_ms = _otel_time(record.get("timeUnixNano"))
        if timestamp_ms is None:
            public_time, timestamp_ms = _timestamp(fallback_timestamp)
        fingerprint = json.dumps(
            {
                "session_id": session_id,
                "event_name": event_name,
                "timestamp": public_time,
                "attributes": attributes,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        if fingerprint in self._otel_seen:
            return
        self._otel_seen.add(fingerprint)
        self._sequence += 1
        self.otel_by_session[session_id].append(
            _OtelEvent(
                session_id=session_id,
                event_name=event_name,
                timestamp=public_time,
                timestamp_ms=timestamp_ms,
                attributes=attributes,
                sequence=self._sequence,
            )
        )

    def _add_hook(self, document: Mapping[str, Any]) -> None:
        session_id = _identifier(document.get("session_id"))
        if session_id is None:
            return
        fields: Dict[str, Any] = {"schema_version": HOOK_EVENT_VERSION}
        for key in HOOK_ALLOWED_FIELDS - {"schema_version", "timestamp", "session_id"}:
            value = document.get(key)
            if key in {"input_bytes", "output_bytes", "exit_code"}:
                cleaned = _safe_integer(value)
            elif key in {"success", "fork_context"}:
                cleaned = _safe_boolean(value)
            else:
                cleaned = _identifier(value)
            if cleaned is not None:
                fields[key] = cleaned
        public_time, timestamp_ms = _timestamp(document.get("timestamp"))
        fields["session_id"] = session_id
        if public_time is not None:
            fields["timestamp"] = public_time
        fingerprint = json.dumps(
            fields,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        if fingerprint in self._hook_seen:
            return
        self._hook_seen.add(fingerprint)
        self._sequence += 1
        self.hooks_by_session[session_id].append(
            _HookEvent(
                session_id=session_id,
                timestamp=public_time,
                timestamp_ms=timestamp_ms,
                fields=fields,
                sequence=self._sequence,
            )
        )


def _event_time(item: Mapping[str, Any], payload: Mapping[str, Any]) -> Tuple[Optional[str], Optional[float]]:
    for value in (item.get("timestamp"), payload.get("timestamp"), payload.get("occurred_at_ms")):
        public, milliseconds = _timestamp(value)
        if milliseconds is not None:
            return public, milliseconds
    return None, None


def _task_time(
    item: Mapping[str, Any],
    payload: Mapping[str, Any],
    fallback_key: str,
) -> Tuple[Optional[str], Optional[float]]:
    public, milliseconds = _event_time(item, payload)
    if milliseconds is not None:
        return public, milliseconds
    return _timestamp(payload.get(fallback_key))


def _empty_tokens() -> Dict[str, Optional[int]]:
    return {field_name: None for field_name in TOKEN_FIELDS}


def _first_int(mapping: Mapping[str, Any], keys: Iterable[str]) -> Optional[int]:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return max(0, int(value))
    return None


def _token_usage(payload: Mapping[str, Any]) -> Optional[Dict[str, Optional[int]]]:
    info = payload.get("info")
    if not isinstance(info, dict):
        return None
    usage: Any = info.get("total_token_usage")
    if not isinstance(usage, dict):
        usage = info.get("total_usage")
    if not isinstance(usage, dict):
        usage = info
    known_keys = {
        "input_tokens",
        "input_token_count",
        "cached_input_tokens",
        "cached_tokens",
        "output_tokens",
        "output_token_count",
        "reasoning_output_tokens",
        "reasoning_tokens",
        "total_tokens",
        "total_token_count",
    }
    if not known_keys.intersection(usage):
        return None
    result = {
        "input": _first_int(usage, ("input_tokens", "input_token_count")),
        "cached": _first_int(usage, ("cached_input_tokens", "cached_tokens")),
        "output": _first_int(usage, ("output_tokens", "output_token_count")),
        "reasoning": _first_int(
            usage,
            ("reasoning_output_tokens", "reasoning_tokens"),
        ),
        "total": _first_int(usage, ("total_tokens", "total_token_count")),
    }
    if result["total"] is None and (
        result["input"] is not None and result["output"] is not None
    ):
        result["total"] = result["input"] + result["output"]
    return result


def _duration(payload: Mapping[str, Any], started_ms: Optional[float], ended_ms: Optional[float]) -> int:
    value = payload.get("duration_ms")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return max(0, int(round(value)))
    if started_ms is not None and ended_ms is not None and ended_ms >= started_ms:
        return int(round(ended_ms - started_ms))
    started = _timestamp(payload.get("started_at"))[1]
    completed = _timestamp(payload.get("completed_at"))[1]
    if started is not None and completed is not None and completed >= started:
        return int(round(completed - started))
    return 0


def _load_session(descriptor: _SessionDescriptor) -> _SessionData:
    calls: List[_RawCall] = []
    outputs: List[_RawOutput] = []
    child_ids: List[str] = []
    child_seen: Set[str] = set()
    actual_tokens = _empty_tokens()
    token_snapshots: List[_TokenSnapshot] = []
    malformed_lines = 0
    current_turn_id: Optional[str] = None
    turn_segment = 0
    current_turn_key = "outside-0"
    first_event_ms: Optional[float] = None
    last_event_ms: Optional[float] = None
    task_starts: List[float] = []
    task_ends: List[float] = []
    turn_started: Dict[str, float] = {}
    completed_turns: Dict[str, int] = {}

    try:
        stream = descriptor.path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return _SessionData(
            descriptor=descriptor,
            calls=[],
            child_ids=[],
            actual_tokens=actual_tokens,
            token_snapshots=[],
            malformed_lines=1,
            unpaired_calls=0,
            completed_turn_duration_ms=0,
            wall_elapsed_ms=None,
            session_end_ms=None,
        )

    with stream:
        for sequence, line in enumerate(stream):
            try:
                item = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                malformed_lines += 1
                continue
            if not isinstance(item, dict):
                malformed_lines += 1
                continue
            payload = item.get("payload")
            if not isinstance(payload, dict):
                continue
            payload_type = payload.get("type")
            public_time, event_ms = _event_time(item, payload)
            if event_ms is not None:
                first_event_ms = event_ms if first_event_ms is None else min(first_event_ms, event_ms)
                last_event_ms = event_ms if last_event_ms is None else max(last_event_ms, event_ms)

            if payload_type == "task_started":
                current_turn_id = _identifier(payload.get("turn_id"))
                current_turn_key = "turn:" + (current_turn_id or str(turn_segment))
                _, started_ms = _task_time(item, payload, "started_at")
                if started_ms is not None:
                    task_starts.append(started_ms)
                    turn_started[current_turn_key] = started_ms
                continue

            if payload_type in CALL_TYPES:
                family = CALL_TYPES[payload_type]
                call_id = _identifier(payload.get("call_id"))
                tool = _identifier(payload.get("name")) or "unknown"
                arguments = payload.get("input" if family == "custom" else "arguments")
                turn_id = _identifier(payload.get("turn_id")) or current_turn_id
                call = _RawCall(
                    family=family,
                    session_id=descriptor.session_id,
                    call_id=call_id,
                    tool=tool,
                    arguments=arguments,
                    status=payload.get("status"),
                    sequence=sequence,
                    turn_id=turn_id,
                    turn_key=current_turn_key,
                    start=public_time,
                    start_ms=event_ms,
                )
                calls.append(call)
                continue

            if payload_type in OUTPUT_TYPES:
                outputs.append(
                    _RawOutput(
                        family=OUTPUT_TYPES[payload_type],
                        call_id=_identifier(payload.get("call_id")),
                        value=payload.get("output"),
                        sequence=sequence,
                        timestamp=public_time,
                        timestamp_ms=event_ms,
                    )
                )
                continue

            if payload_type == "sub_agent_activity":
                child_id = _identifier(payload.get("agent_thread_id"))
                if child_id and child_id not in child_seen:
                    child_seen.add(child_id)
                    child_ids.append(child_id)
                continue

            if payload_type == "token_count":
                usage = _token_usage(payload)
                if usage is not None:
                    actual_tokens = usage
                    token_snapshots.append(
                        _TokenSnapshot(
                            sequence=sequence,
                            turn_key=current_turn_key,
                            values=dict(usage),
                        )
                    )
                continue

            if payload_type == "task_complete":
                turn_id = _identifier(payload.get("turn_id"))
                turn_key = "turn:" + (turn_id or str(turn_segment))
                _, ended_ms = _task_time(item, payload, "completed_at")
                if ended_ms is not None:
                    task_ends.append(ended_ms)
                completed_turns[turn_key] = _duration(
                    payload,
                    turn_started.get(turn_key),
                    ended_ms,
                )
                current_turn_id = None
                turn_segment += 1
                current_turn_key = "outside-" + str(turn_segment)
                continue

            if payload_type == "turn_aborted":
                _, ended_ms = _task_time(item, payload, "completed_at")
                if ended_ms is not None:
                    task_ends.append(ended_ms)
                current_turn_id = None
                turn_segment += 1
                current_turn_key = "outside-" + str(turn_segment)

    unpaired_calls = _pair_calls(calls, outputs)
    for call in calls:
        command = _command_text(call.arguments)
        call.docstar_commands = _docstar_commands(command)
        call.skill_names = _skill_names(command)
        call.category = _classify_call(call, command)

    wall_start = min(task_starts) if task_starts else first_event_ms
    wall_end = max(task_ends) if task_ends else last_event_ms
    wall_elapsed_ms: Optional[int] = None
    if wall_start is not None and wall_end is not None and wall_end >= wall_start:
        wall_elapsed_ms = int(round(wall_end - wall_start))

    return _SessionData(
        descriptor=descriptor,
        calls=calls,
        child_ids=child_ids,
        actual_tokens=actual_tokens,
        token_snapshots=token_snapshots,
        malformed_lines=malformed_lines,
        unpaired_calls=unpaired_calls,
        completed_turn_duration_ms=sum(completed_turns.values()),
        wall_elapsed_ms=wall_elapsed_ms,
        session_end_ms=last_event_ms,
    )


def _pair_calls(calls: List[_RawCall], outputs: List[_RawOutput]) -> int:
    by_key: Dict[Tuple[str, Optional[str]], List[_RawOutput]] = defaultdict(list)
    for output in outputs:
        by_key[(output.family, output.call_id)].append(output)

    for call in calls:
        if call.call_id is None:
            continue
        candidates = [
            output
            for output in by_key.get((call.family, call.call_id), [])
            if not output.matched
        ]
        if not candidates:
            continue

        def output_rank(output: _RawOutput) -> Tuple[int, float, int]:
            if call.start_ms is not None and output.timestamp_ms is not None:
                delta = output.timestamp_ms - call.start_ms
                return (0 if delta >= 0 else 1, abs(delta), output.sequence)
            sequence_delta = output.sequence - call.sequence
            return (2 if sequence_delta >= 0 else 3, abs(sequence_delta), output.sequence)

        selected = min(candidates, key=output_rank)
        selected.matched = True
        call.output = selected

    missing_outputs = sum(call.output is None for call in calls)
    orphan_outputs = sum(not output.matched for output in outputs)
    return missing_outputs + orphan_outputs


def _estimate_tokens(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError):
            text = str(value)
    if not text:
        return 0
    return int(math.ceil(len(text) / ESTIMATED_CHARACTERS_PER_TOKEN))


def _decode_arguments(arguments: Any) -> Any:
    if not isinstance(arguments, str):
        return arguments
    try:
        return json.loads(arguments)
    except (json.JSONDecodeError, TypeError):
        return arguments


def _command_text(arguments: Any) -> str:
    decoded = _decode_arguments(arguments)
    if isinstance(decoded, dict):
        for key in ("cmd", "command", "script", "code", "file_path", "path"):
            value = decoded.get(key)
            if isinstance(value, str):
                return value
        return ""
    if isinstance(decoded, str):
        return decoded
    return ""


def _tool_leaf(tool: str) -> str:
    lowered = tool.lower()
    for separator in ("::", "__", "."):
        if separator in lowered:
            lowered = lowered.rsplit(separator, 1)[-1]
    return lowered


def _shell_segments(command: str) -> List[List[str]]:
    result: List[List[str]] = []
    for segment in re.split(r"(?:&&|\|\||[;\n|])", command):
        if not segment.strip():
            continue
        try:
            tokens = shlex.split(segment, posix=True)
        except ValueError:
            tokens = re.findall(r"[^\s]+", segment)
        if tokens:
            result.append(tokens)
    return result


def _basename(token: str) -> str:
    return token.rstrip(",:(){}").rsplit("/", 1)[-1].lower()


def _docstar_commands(command: str) -> List[str]:
    commands: List[str] = []
    for tokens in _shell_segments(command):
        for index, token in enumerate(tokens):
            if _basename(token) not in {"docstar", "docstar.py"}:
                continue
            subcommand = "unknown"
            for candidate in tokens[index + 1 :]:
                if candidate.startswith("-"):
                    continue
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", candidate):
                    subcommand = candidate.lower()
                break
            commands.append(subcommand)
    return commands


def _contains_docstar(command: str) -> bool:
    if _docstar_commands(command):
        return True
    return bool(re.search(r"(?:^|[\s;&|])(?:[^\s;&|]*/)?docstar(?:\.py)?(?:\s|$)", command))


def _contains_grep(command: str, direct_tool: Optional[str] = None) -> bool:
    if direct_tool in {"grep", "egrep", "fgrep"}:
        return True
    for tokens in _shell_segments(command):
        for index, token in enumerate(tokens):
            executable = _basename(token)
            if executable in {"grep", "egrep", "fgrep"}:
                return True
            if executable == "rg":
                remaining = tokens[index + 1 :]
                if "--files" not in remaining:
                    return True
    return False


def _contains_markdown(command: str) -> bool:
    return bool(MARKDOWN_PATH.search(command))


def _is_markdown_read(command: str, direct_tool: Optional[str] = None) -> bool:
    if not _contains_markdown(command):
        return False
    if direct_tool in READ_TOOLS:
        return True
    for tokens in _shell_segments(command):
        if not any(MARKDOWN_PATH.search(token) for token in tokens):
            continue
        for index, token in enumerate(tokens):
            executable = _basename(token)
            if executable not in READ_COMMANDS:
                continue
            if executable == "sed" and "-i" in tokens[index + 1 :]:
                continue
            return True
    return False


def _is_wait_command(command: str) -> bool:
    for tokens in _shell_segments(command):
        if any(_basename(token) in {"sleep", "wait"} for token in tokens):
            return True
    return False


def _is_agent_command(command: str) -> bool:
    return bool(
        re.search(
            r"\b(?:spawn_agent|wait_agent|send_message|create_thread|wait_threads)\b",
            command,
        )
    )


def _is_write_command(command: str) -> bool:
    if re.search(r"\b(?:apply_patch|writeFileSync|write_text)\b", command):
        return True
    for tokens in _shell_segments(command):
        for index, token in enumerate(tokens):
            executable = _basename(token)
            if executable in WRITE_COMMANDS:
                return True
            if executable == "sed" and "-i" in tokens[index + 1 :]:
                return True
            if executable == "git" and any(
                candidate in {"add", "commit", "merge", "rebase", "reset"}
                for candidate in tokens[index + 1 :]
            ):
                return True
    return False


def _skill_names(command: str) -> List[str]:
    names: List[str] = []
    seen: Set[str] = set()
    for match in SKILL_PATH.finditer(command):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _classify_call(call: _RawCall, command: str) -> str:
    tool = _tool_leaf(call.tool)
    decoded = _decode_arguments(call.arguments)
    if tool in WAIT_TOOLS:
        return "wait"
    if tool in AGENT_TOOLS:
        return "agent"
    if tool in WRITE_TOOLS:
        return "write"
    if _contains_docstar(command):
        return "docstar"
    if _contains_grep(command, tool):
        return "grep"
    if _is_write_command(command):
        return "write"
    if _is_markdown_read(command, tool):
        return "read"
    if _is_wait_command(command):
        return "wait"
    if _is_agent_command(command):
        return "agent"
    if tool in READ_TOOLS and isinstance(decoded, dict):
        return "read" if _contains_markdown(command) else "other"
    return "other"


def _status_signal(value: Any) -> Optional[bool]:
    if isinstance(value, dict):
        for key in ("success", "ok"):
            candidate = value.get(key)
            if isinstance(candidate, bool):
                return candidate
        for key in ("is_error", "isError", "failed"):
            candidate = value.get(key)
            if isinstance(candidate, bool):
                return not candidate
        exit_code = value.get("exit_code", value.get("exitCode"))
        if isinstance(exit_code, (int, float)) and not isinstance(exit_code, bool):
            return exit_code == 0
        status = value.get("status")
        if isinstance(status, str):
            lowered = status.lower()
            if lowered in {"failed", "failure", "error", "cancelled", "canceled"}:
                return False
            if lowered in {"complete", "completed", "ok", "success", "succeeded"}:
                return True
        for key in ("metadata", "result"):
            nested = value.get(key)
            signal = _status_signal(nested)
            if signal is not None:
                return signal
        return None
    if isinstance(value, list):
        signals = [_status_signal(item) for item in value]
        if False in signals:
            return False
        if True in signals:
            return True
        return None
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            match = re.search(r"(?:exit[_ ]code|exited with code)\D*(-?\d+)", value, re.IGNORECASE)
            if match:
                return int(match.group(1)) == 0
            if "<tool_error>" in value:
                return False
            return None
        if decoded != value:
            return _status_signal(decoded)
    return None


def _infer_success(status: Any, output: Optional[_RawOutput]) -> Optional[bool]:
    if output is None:
        return None
    output_signal = _status_signal(output.value)
    if output_signal is not None:
        return output_signal
    status_signal = _status_signal({"status": status}) if isinstance(status, str) else None
    if status_signal is not None:
        return status_signal
    return True


def _argument_mapping(arguments: Any) -> Mapping[str, Any]:
    decoded = _decode_arguments(arguments)
    return decoded if isinstance(decoded, dict) else {}


def _gmgn_kind(call: _RawCall) -> Optional[str]:
    tool = _tool_leaf(call.tool)
    if tool in SPAWN_TOOLS:
        return "spawn"
    if tool in SEND_TOOLS:
        return "send"
    if tool in {"wait_agent", "wait_agents", "wait_threads"}:
        return "wait"
    if tool == "wait":
        arguments = _argument_mapping(call.arguments)
        agent_keys = {"ids", "targets", "agent_ids", "thread_ids", "target"}
        if agent_keys.intersection(arguments):
            return "wait"
    return None


def _decoded_output(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _nested_values(value: Any, normalized_names: Set[str]) -> List[Any]:
    result: List[Any] = []
    stack = [_decoded_output(value)]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                normalized = re.sub(r"[^a-z0-9]", "", str(key).casefold())
                if normalized in normalized_names:
                    result.append(child)
                if isinstance(child, (dict, list)):
                    stack.append(child)
        elif isinstance(current, list):
            stack.extend(current)
    return result


def _wait_result(call: _RawCall) -> str:
    if call.output is None:
        return "unknown"

    value = _decoded_output(call.output.value)
    timed_out = _nested_values(value, {"timedout", "timeout"})
    if any(candidate is True for candidate in timed_out):
        return "timeout"
    if any(candidate is False for candidate in timed_out):
        return "update"

    text_value = call.output.value
    if not isinstance(text_value, str):
        try:
            text_value = json.dumps(text_value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            text_value = str(text_value)
    normalized = text_value.casefold()
    if "timeout_ms" in normalized and "must" in normalized:
        return "error"
    if re.search(r"\b(?:interrupted|cancelled|canceled)\b", normalized):
        return "interrupted"
    if (
        "wait completed" in normalized
        or "has updates" in normalized
        or "agent updates" in normalized
        or "new user input" in normalized
    ):
        return "update"
    if re.search(r"\b(?:wait(?:ing)?[ _-]?)?timed[ _-]?out\b", normalized):
        return "timeout"
    if _infer_success(call.status, call.output) is False:
        return "error"
    return "unknown"


def _token_delta(
    baseline: Mapping[str, Optional[int]],
    current: Mapping[str, Optional[int]],
) -> Dict[str, Optional[int]]:
    result: Dict[str, Optional[int]] = {}
    for field_name in TOKEN_FIELDS:
        before = baseline.get(field_name)
        after = current.get(field_name)
        result[field_name] = (
            after - before
            if before is not None and after is not None and after >= before
            else None
        )
    return result


def _token_snapshot_changed(
    baseline: Mapping[str, Optional[int]],
    current: Mapping[str, Optional[int]],
) -> bool:
    return any(
        baseline.get(field_name) != current.get(field_name)
        for field_name in TOKEN_FIELDS
    )


def _wait_reactivation_metrics(
    calls: Sequence[_RawCall],
    sessions: Sequence[_SessionData],
) -> Dict[str, Any]:
    waits = [call for call in calls if _gmgn_kind(call) == "wait"]
    eligible = sum(call.output is not None for call in waits)
    snapshots_by_session = {
        session.descriptor.session_id: sorted(
            session.token_snapshots,
            key=lambda snapshot: snapshot.sequence,
        )
        for session in sessions
    }
    deltas: List[Dict[str, Optional[int]]] = []
    for call in waits:
        if call.output is None:
            continue
        snapshots = snapshots_by_session.get(call.session_id, [])
        baseline_index: Optional[int] = None
        for index, snapshot in enumerate(snapshots):
            if snapshot.sequence > call.output.sequence and snapshot.turn_key == call.turn_key:
                baseline_index = index
                break
        if baseline_index is None:
            continue
        baseline = snapshots[baseline_index]
        for snapshot in snapshots[baseline_index + 1 :]:
            if snapshot.turn_key != call.turn_key:
                continue
            if not _token_snapshot_changed(baseline.values, snapshot.values):
                continue
            delta = _token_delta(baseline.values, snapshot.values)
            if any(value is not None and value > 0 for value in delta.values()):
                deltas.append(delta)
            break

    tokens: Dict[str, Optional[int]] = {}
    for field_name in TOKEN_FIELDS:
        values = [delta[field_name] for delta in deltas]
        tokens[field_name] = (
            sum(value for value in values if value is not None)
            if values and all(value is not None for value in values)
            else None
        )
    matched = len(deltas)
    if not waits:
        coverage = "not_applicable"
    elif eligible and matched == eligible:
        coverage = "observed"
    elif matched:
        coverage = "partial"
    else:
        coverage = "unknown"
    return {
        "tokens": tokens,
        "matched_waits": matched,
        "eligible_waits": eligible,
        "coverage": coverage,
        "source": SOURCE if matched else "unknown",
        "linkage": "session_sequence_delta" if matched else "unavailable",
    }


def _wait_result_metrics(results: Sequence[str]) -> Dict[str, Any]:
    result_counts = {value: 0 for value in WAIT_RESULT_VALUES}
    max_streak = 0
    current_streak = 0
    storm_count = 0
    for result in results:
        if result not in result_counts:
            result = "unknown"
        result_counts[result] += 1
        if result == "timeout":
            current_streak += 1
            max_streak = max(max_streak, current_streak)
            if current_streak == 2:
                storm_count += 1
        else:
            current_streak = 0
    state_changes = {
        "changed": result_counts["update"],
        "unchanged": result_counts["timeout"],
        "unknown": sum(
            result_counts[value]
            for value in ("interrupted", "error", "unknown")
        ),
    }
    return {
        "result_counts": result_counts,
        "state_change_counts": state_changes,
        "max_consecutive_timeouts": max_streak,
        "wait_storm_count": storm_count,
        "wait_storm_detected": storm_count > 0,
    }


def _merge_wait_result_metrics(
    summaries: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    merged = _wait_result_metrics([])
    for summary in summaries:
        for key, value in summary["result_counts"].items():
            merged["result_counts"][key] += value
        for key, value in summary["state_change_counts"].items():
            merged["state_change_counts"][key] += value
        merged["max_consecutive_timeouts"] = max(
            merged["max_consecutive_timeouts"],
            summary["max_consecutive_timeouts"],
        )
        merged["wait_storm_count"] += summary["wait_storm_count"]
    merged["wait_storm_detected"] = merged["wait_storm_count"] > 0
    return merged


def _wait_metrics(
    calls: Sequence[_RawCall],
    sessions: Sequence[_SessionData],
) -> Dict[str, Any]:
    waits = [call for call in calls if _gmgn_kind(call) == "wait"]
    waits_by_session: Dict[str, List[_RawCall]] = defaultdict(list)
    for call in waits:
        waits_by_session[call.session_id].append(call)
    summaries = [
        _wait_result_metrics(
            [
                _wait_result(call)
                for call in sorted(
                    session_waits,
                    key=lambda item: item.sequence,
                )
            ]
        )
        for session_waits in waits_by_session.values()
    ]
    result = _merge_wait_result_metrics(summaries)
    result["reactivation"] = _wait_reactivation_metrics(calls, sessions)
    return result


def _fork_context_bucket(arguments: Any) -> str:
    mapping = _argument_mapping(arguments)
    if "fork_context" in mapping:
        value = mapping["fork_context"]
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            return value.lower()
        return "unspecified"
    if "fork_turns" in mapping:
        value = mapping["fork_turns"]
        if isinstance(value, str) and value.lower() in {"none", "all"}:
            return value.lower()
        return "unspecified"
    return "unspecified"


def _extract_identifiers(arguments: Any) -> Dict[str, List[str]]:
    result = {field_name: [] for field_name in IDENTIFIER_FIELDS}
    seen = {field_name: set() for field_name in IDENTIFIER_FIELDS}
    decoded = _decode_arguments(arguments)

    def add(field_name: str, value: Any) -> None:
        identifier = _identifier(value)
        if identifier and identifier not in seen[field_name]:
            seen[field_name].add(identifier)
            result[field_name].append(identifier)

    stack: List[Any] = [decoded]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            for key, child in value.items():
                lowered = str(key).lower()
                if lowered in result:
                    add(lowered, child)
                if isinstance(child, (dict, list)):
                    stack.append(child)
        elif isinstance(value, list):
            stack.extend(item for item in value if isinstance(item, (dict, list)))
    return result


def _gmgn_metrics(
    calls: Sequence[_RawCall],
    sessions: Sequence[_SessionData] = (),
) -> Dict[str, Any]:
    spawn_calls = 0
    wait_calls = 0
    send_calls = 0
    wait_duration_ms = 0
    fork_counts = {value: 0 for value in FORK_CONTEXT_VALUES}
    identifiers = {field_name: [] for field_name in IDENTIFIER_FIELDS}
    seen = {field_name: set() for field_name in IDENTIFIER_FIELDS}

    for call in calls:
        kind = _gmgn_kind(call)
        if kind == "spawn":
            spawn_calls += 1
            fork_counts[_fork_context_bucket(call.arguments)] += 1
            extracted = _extract_identifiers(call.arguments)
            for field_name in IDENTIFIER_FIELDS:
                for value in extracted[field_name]:
                    if value not in seen[field_name]:
                        seen[field_name].add(value)
                        identifiers[field_name].append(value)
        elif kind == "wait":
            wait_calls += 1
            if call.duration_ms is not None:
                wait_duration_ms += call.duration_ms
        elif kind == "send":
            send_calls += 1

    return {
        "spawn_calls": spawn_calls,
        "wait_calls": wait_calls,
        "send_calls": send_calls,
        "wait_duration_ms": wait_duration_ms,
        "wait": _wait_metrics(calls, sessions),
        "fork_context_counts": fork_counts,
        "identifiers": identifiers,
    }


def _docstar_metrics(calls: Sequence[_RawCall], follow_window: int) -> Dict[str, Any]:
    command_counts: Counter[str] = Counter()
    docstar_calls: List[_RawCall] = []
    grep_calls = 0
    read_calls = 0
    calls_by_session: Dict[str, List[_RawCall]] = defaultdict(list)
    for call in calls:
        calls_by_session[call.session_id].append(call)
        if call.category == "docstar":
            docstar_calls.append(call)
            commands = call.docstar_commands or ["unknown"]
            command_counts.update(commands)
        elif call.category == "grep":
            grep_calls += 1
        elif call.category == "read":
            read_calls += 1

    follow_up: List[Dict[str, Any]] = []
    for docstar_call in docstar_calls:
        session_calls = sorted(calls_by_session[docstar_call.session_id], key=lambda item: item.sequence)
        subsequent = [
            call
            for call in session_calls
            if call.sequence > docstar_call.sequence and call.turn_key == docstar_call.turn_key
        ][:follow_window]
        following_grep = sum(call.category == "grep" for call in subsequent)
        following_read = sum(call.category == "read" for call in subsequent)
        follow_up.append(
            {
                "session_id": docstar_call.session_id,
                "call_id": docstar_call.call_id,
                "turn_id": docstar_call.turn_id,
                "window": follow_window,
                "grep_calls": following_grep,
                "read_calls": following_read,
                "grep_read_calls": following_grep + following_read,
            }
        )

    return {
        "calls": len(docstar_calls),
        "commands": dict(sorted(command_counts.items())),
        "grep_calls": grep_calls,
        "read_calls": read_calls,
        "grep_read_calls": grep_calls + read_calls,
        "follow_up": follow_up,
        "grep_avoided": None,
        "causal_status": "causal_not_measured",
    }


def _skill_metrics(sessions: Sequence[_SessionData]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for session in sessions:
        loads = [call for call in session.calls if call.skill_names]
        loads.sort(
            key=lambda call: (
                call.start_ms is None,
                call.start_ms if call.start_ms is not None else float(call.sequence),
                call.sequence,
            )
        )
        for index, call in enumerate(loads):
            boundary_ms = session.session_end_ms
            if index + 1 < len(loads):
                boundary_ms = loads[index + 1].start_ms
            observed_span_ms: Optional[int] = None
            if call.end_ms is not None and boundary_ms is not None and boundary_ms >= call.end_ms:
                observed_span_ms = int(round(boundary_ms - call.end_ms))
            for skill_name in call.skill_names:
                result.append(
                    {
                        "session_id": call.session_id,
                        "call_id": call.call_id,
                        "skill": skill_name,
                        "load_duration_ms": call.duration_ms,
                        "observed_span_ms": observed_span_ms,
                        "estimated_context_tokens": call.estimated_output_tokens,
                    }
                )
    return result


def _sum_tokens(sessions: Sequence[_SessionData]) -> Dict[str, Optional[int]]:
    total = _empty_tokens()
    for field_name in TOKEN_FIELDS:
        values = [session.actual_tokens[field_name] for session in sessions]
        if values and all(value is not None for value in values):
            total[field_name] = sum(value for value in values if value is not None)
    return total


def _coverage(
    source: str,
    status: str,
    observed_sessions: int,
    total_sessions: int,
    *,
    fallback: bool = False,
    **details: Any,
) -> Dict[str, Any]:
    result = {
        "source": source,
        "coverage": status,
        "observed_sessions": observed_sessions,
        "total_sessions": total_sessions,
        "fallback": fallback,
    }
    result.update(details)
    return result


def _logical_session_groups(
    requested_id: str,
    run: Mapping[str, Any],
    sessions: Sequence[_SessionData],
    telemetry: _TelemetryStore,
) -> List[Tuple[str, Set[str], Optional[_SessionData]]]:
    groups: List[Tuple[str, Set[str], Optional[_SessionData]]] = []
    if sessions:
        for index, session in enumerate(sessions):
            query_ids = {session.descriptor.session_id}
            if index == 0:
                query_ids.add(requested_id)
            groups.append((session.descriptor.session_id, query_ids, session))
    elif telemetry.has_session(requested_id):
        groups.append((requested_id, {requested_id}, None))

    known_ids = {logical_id for logical_id, _, _ in groups}
    for missing_id in run["data_quality"]["missing_sessions"]:
        if missing_id not in known_ids and telemetry.has_session(missing_id):
            known_ids.add(missing_id)
            groups.append((missing_id, {missing_id}, None))
    return groups


def _events_for_ids(
    by_session: Mapping[str, Sequence[Any]],
    query_ids: Iterable[str],
) -> List[Any]:
    result: List[Any] = []
    seen: Set[Tuple[str, int]] = set()
    for session_id in query_ids:
        for event in by_session.get(session_id, []):
            key = (event.session_id, event.sequence)
            if key not in seen:
                seen.add(key)
                result.append(event)
    return result


def _otel_token_value(event: _OtelEvent, field_name: str) -> Optional[int]:
    for attribute in OTEL_TOKEN_ATTRIBUTES[field_name]:
        if attribute in event.attributes:
            value = _safe_integer(event.attributes[attribute])
            if value is not None and value >= 0:
                return value
    return None


def _token_events(events: Sequence[_OtelEvent]) -> List[_OtelEvent]:
    token_names = {
        attribute
        for attributes in OTEL_TOKEN_ATTRIBUTES.values()
        for attribute in attributes
    }
    return [event for event in events if token_names.intersection(event.attributes)]


def _telemetry_tokens(
    groups: Sequence[Tuple[str, Set[str], Optional[_SessionData]]],
    telemetry: _TelemetryStore,
) -> Tuple[Dict[str, Optional[int]], Dict[str, Any], Set[str]]:
    result = _empty_tokens()
    field_coverage: Dict[str, Any] = {}
    fallback_fields: Set[str] = set()
    for field_name in TOKEN_FIELDS:
        values: List[int] = []
        sources: Set[str] = set()
        observed_sessions = 0
        missing = False
        for _, query_ids, fallback_session in groups:
            events = _events_for_ids(telemetry.otel_by_session, query_ids)
            token_events = _token_events(events)
            otel_values = [
                _otel_token_value(event, field_name) for event in token_events
            ]
            if token_events and all(value is not None for value in otel_values):
                values.append(sum(value for value in otel_values if value is not None))
                sources.add(OTEL_SOURCE)
                observed_sessions += 1
                continue
            fallback_value = (
                fallback_session.actual_tokens[field_name]
                if fallback_session is not None
                else None
            )
            if fallback_value is not None:
                values.append(fallback_value)
                sources.add(SOURCE)
                fallback_fields.add("actual_tokens." + field_name)
                observed_sessions += 1
            else:
                missing = True
        if groups and not missing and len(values) == len(groups):
            result[field_name] = sum(values)
        if not sources:
            source = "unknown"
            status = "unknown"
        elif len(sources) > 1:
            source = OTEL_SOURCE + "+" + SOURCE
            status = "partial" if missing else "mixed"
        elif OTEL_SOURCE in sources:
            source = OTEL_SOURCE
            status = "partial" if missing else "observed"
        else:
            source = SOURCE
            status = "partial" if missing else "fallback"
        field_coverage[field_name] = _coverage(
            source,
            status,
            observed_sessions,
            len(groups),
            fallback=SOURCE in sources,
        )

    statuses = {details["coverage"] for details in field_coverage.values()}
    sources = {details["source"] for details in field_coverage.values()}
    if statuses == {"unknown"}:
        overall_status = "unknown"
        overall_source = "unknown"
    elif len(statuses) == 1:
        overall_status = next(iter(statuses))
        overall_source = next(iter(sources)) if len(sources) == 1 else MIXED_SOURCE
    else:
        overall_status = "mixed" if "unknown" not in statuses else "partial"
        overall_source = next(iter(sources)) if len(sources) == 1 else MIXED_SOURCE
    return (
        result,
        {
            "source": overall_source,
            "coverage": overall_status,
            "fields": field_coverage,
        },
        fallback_fields,
    )


def _api_metrics(events: Sequence[_OtelEvent]) -> Dict[str, Optional[int]]:
    api_events = [
        event
        for event in events
        if event.event_name in {"codex.api_request", "codex.websocket_request"}
    ]
    if not api_events:
        return {"count": None, "duration_ms": None, "success": None, "failure": None}
    durations = [_safe_integer(event.attributes.get("duration_ms")) for event in api_events]
    outcomes: List[Optional[bool]] = []
    for event in api_events:
        success = _safe_boolean(event.attributes.get("success"))
        if success is None:
            status = _safe_integer(
                event.attributes.get("http.response.status_code")
                if "http.response.status_code" in event.attributes
                else (
                    event.attributes.get("status_code")
                    if "status_code" in event.attributes
                    else event.attributes.get("status")
                )
            )
            success = 200 <= status <= 299 if status is not None else None
        outcomes.append(success)
    known_outcomes = [outcome for outcome in outcomes if outcome is not None]
    return {
        "count": len(api_events),
        "duration_ms": (
            sum(duration for duration in durations if duration is not None)
            if all(duration is not None for duration in durations)
            else None
        ),
        "success": (
            sum(known_outcomes)
            if len(known_outcomes) == len(api_events)
            else None
        ),
        "failure": (
            sum(not outcome for outcome in known_outcomes)
            if len(known_outcomes) == len(api_events)
            else None
        ),
    }


def _native_tool_metrics(events: Sequence[_OtelEvent]) -> Dict[str, Optional[int]]:
    tool_events = [event for event in events if event.event_name == "codex.tool_result"]
    if not tool_events:
        return {"count": None, "duration_ms": None, "success": None, "failure": None}
    durations = [_safe_integer(event.attributes.get("duration_ms")) for event in tool_events]
    successes = [_safe_boolean(event.attributes.get("success")) for event in tool_events]
    known_successes = [success for success in successes if success is not None]
    return {
        "count": len(tool_events),
        "duration_ms": (
            sum(duration for duration in durations if duration is not None)
            if all(duration is not None for duration in durations)
            else None
        ),
        "success": (
            sum(known_successes)
            if len(known_successes) == len(tool_events)
            else None
        ),
        "failure": (
            sum(not success for success in known_successes)
            if len(known_successes) == len(tool_events)
            else None
        ),
    }


def _hook_category(hook: _HookEvent) -> str:
    classification = hook.fields.get("classification")
    return {
        "markdown_read": "read",
        "skill_load": "read",
        "unclassified_compound": "other",
    }.get(str(classification), str(classification or "unclassified"))


def _estimated_bytes(value: Any) -> Optional[int]:
    byte_count = _safe_integer(value)
    if byte_count is None or byte_count < 0:
        return None
    return int(math.ceil(byte_count / ESTIMATED_CHARACTERS_PER_TOKEN))


def _hook_link_map(hooks: Sequence[_HookEvent]) -> Dict[Tuple[str, str], _HookEvent]:
    result: Dict[Tuple[str, str], _HookEvent] = {}
    for hook in hooks:
        call_id = _identifier(hook.fields.get("tool_use_id"))
        if call_id is not None:
            result.setdefault((hook.session_id, call_id), hook)
    return result


def _otel_tool_call(event: _OtelEvent, hook: Optional[_HookEvent]) -> Dict[str, Any]:
    duration_ms = _safe_integer(event.attributes.get("duration_ms"))
    end_ms = event.timestamp_ms
    start_ms = (
        end_ms - duration_ms
        if end_ms is not None and duration_ms is not None and duration_ms >= 0
        else None
    )
    return {
        "session_id": event.session_id,
        "call_id": _identifier(event.attributes.get("call_id")),
        "tool": _identifier(event.attributes.get("tool_name")) or "unknown",
        "category": _hook_category(hook) if hook is not None else "unclassified",
        "start": _format_timestamp(start_ms) if start_ms is not None else None,
        "end": event.timestamp,
        "duration_ms": duration_ms,
        "success": _safe_boolean(event.attributes.get("success")),
        "estimated_input_tokens": (
            _estimated_bytes(hook.fields.get("input_bytes")) if hook else None
        ),
        "estimated_output_tokens": (
            _estimated_bytes(hook.fields.get("output_bytes")) if hook else None
        ),
    }


def _group_otel_events(
    group: Tuple[str, Set[str], Optional[_SessionData]],
    telemetry: _TelemetryStore,
) -> List[_OtelEvent]:
    return _events_for_ids(telemetry.otel_by_session, group[1])


def _group_hook_events(
    group: Tuple[str, Set[str], Optional[_SessionData]],
    telemetry: _TelemetryStore,
) -> List[_HookEvent]:
    return _events_for_ids(telemetry.hooks_by_session, group[1])


def _merged_tool_calls(
    groups: Sequence[Tuple[str, Set[str], Optional[_SessionData]]],
    telemetry: _TelemetryStore,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Set[str]]:
    public_calls: List[Dict[str, Any]] = []
    native_count = 0
    linked_count = 0
    hook_tool_count = 0
    otel_sessions = 0
    fallback_sessions = 0
    fallback_fields: Set[str] = set()
    for group in groups:
        otel_events = _group_otel_events(group, telemetry)
        tool_events = [
            event for event in otel_events if event.event_name == "codex.tool_result"
        ]
        hooks = _group_hook_events(group, telemetry)
        hook_links = _hook_link_map(hooks)
        hook_tool_count += sum("tool_use_id" in hook.fields for hook in hooks)
        if tool_events:
            otel_sessions += 1
            native_count += len(tool_events)
            for event in tool_events:
                call_id = _identifier(event.attributes.get("call_id"))
                hook = hook_links.get((event.session_id, call_id)) if call_id else None
                if hook is not None:
                    linked_count += 1
                public_calls.append(_otel_tool_call(event, hook))
            continue
        fallback_session = group[2]
        if fallback_session is not None:
            fallback_sessions += 1
            fallback_fields.add("tool_calls")
            public_calls.extend(call.public() for call in fallback_session.calls)

    public_calls.sort(
        key=lambda call: (
            _timestamp(call.get("start"))[1] is None,
            _timestamp(call.get("start"))[1] or float("inf"),
            str(call.get("session_id")),
            str(call.get("call_id")),
        )
    )
    if native_count == 0 or hook_tool_count == 0:
        linkage_status = "unavailable"
    elif linked_count == native_count:
        linkage_status = "complete"
    else:
        linkage_status = "partial"
    linkage = {
        "source": OTEL_SOURCE + "+" + HOOK_SOURCE,
        "coverage": linkage_status,
        "linked": linked_count,
        "native_tool_results": native_count,
        "hook_tool_events": hook_tool_count,
    }
    if otel_sessions and fallback_sessions:
        source = OTEL_SOURCE + "+" + SOURCE
        status = "mixed"
    elif otel_sessions:
        source = OTEL_SOURCE
        status = "observed"
    elif fallback_sessions:
        source = SOURCE
        status = "fallback"
    else:
        source = "unknown"
        status = "unknown"
    coverage = _coverage(
        source,
        status,
        otel_sessions + fallback_sessions,
        len(groups),
        fallback=bool(fallback_sessions),
    )
    return public_calls, {"tool_calls": coverage, "native_hook_linkage": linkage}, fallback_fields


def _hook_fork_bucket(hook: _HookEvent) -> str:
    if "fork_context" in hook.fields:
        return "true" if hook.fields["fork_context"] is True else "false"
    fork_turns = hook.fields.get("fork_turns")
    if fork_turns in {"none", "all"}:
        return str(fork_turns)
    return "unspecified"


def _hook_gmgn_metrics(
    groups: Sequence[Tuple[str, Set[str], Optional[_SessionData]]],
    telemetry: _TelemetryStore,
) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str]]:
    fallback_sessions = [
        session for _, _, session in groups if session is not None
    ]
    all_fallback_calls = [
        call
        for _, _, session in groups
        if session is not None
        for call in session.calls
    ]
    fallback_all = _gmgn_metrics(all_fallback_calls, fallback_sessions)
    spawn_calls = 0
    fork_counts = {value: 0 for value in FORK_CONTEXT_VALUES}
    identifiers = {field_name: [] for field_name in IDENTIFIER_FIELDS}
    identifier_seen = {field_name: set() for field_name in IDENTIFIER_FIELDS}
    hook_sessions = 0
    spawn_fallback_sessions = 0
    hook_wait_summaries: List[Dict[str, Any]] = []
    hook_wait_count = 0

    def add_identifiers(source: Mapping[str, Sequence[str]]) -> None:
        for field_name in IDENTIFIER_FIELDS:
            for value in source[field_name]:
                if value not in identifier_seen[field_name]:
                    identifier_seen[field_name].add(value)
                    identifiers[field_name].append(value)

    for group in groups:
        hooks = _group_hook_events(group, telemetry)
        if group[2] is None:
            hook_wait_results = []
            for hook in hooks:
                tool = _tool_leaf(str(hook.fields.get("tool_name", "")))
                action = hook.fields.get("agent_action")
                if action != "wait" and tool not in {
                    "wait_agent",
                    "wait_agents",
                    "wait_threads",
                }:
                    continue
                wait_result = str(hook.fields.get("wait_result", "unknown"))
                hook_wait_results.append(
                    wait_result if wait_result in WAIT_RESULT_VALUES else "unknown"
                )
            if hook_wait_results:
                hook_wait_count += len(hook_wait_results)
                hook_wait_summaries.append(
                    _wait_result_metrics(hook_wait_results)
                )

        spawn_hooks = []
        for hook in hooks:
            tool = _tool_leaf(str(hook.fields.get("tool_name", "")))
            if hook.fields.get("classification") != "agent":
                continue
            if tool in SPAWN_TOOLS or tool == "agent":
                spawn_hooks.append(hook)
        if spawn_hooks:
            hook_sessions += 1
            for hook in spawn_hooks:
                spawn_calls += 1
                fork_counts[_hook_fork_bucket(hook)] += 1
                explicit = {field_name: [] for field_name in IDENTIFIER_FIELDS}
                for field_name in IDENTIFIER_FIELDS:
                    value = _identifier(hook.fields.get(field_name))
                    if value is not None:
                        explicit[field_name].append(value)
                add_identifiers(explicit)
            continue
        fallback_session = group[2]
        if fallback_session is None:
            continue
        spawn_fallback_sessions += 1
        metrics = _gmgn_metrics(fallback_session.calls)
        spawn_calls += metrics["spawn_calls"]
        for bucket in FORK_CONTEXT_VALUES:
            fork_counts[bucket] += metrics["fork_context_counts"][bucket]
        add_identifiers(metrics["identifiers"])

    fallback_fields = set()
    if all_fallback_calls:
        fallback_fields.update({"gmgn.wait_calls", "gmgn.send_calls"})
    if spawn_fallback_sessions:
        fallback_fields.add("gmgn.spawn_calls")
    wait_metrics = (
        fallback_all["wait"] if all_fallback_calls else _wait_metrics([], [])
    )
    wait_summary = _merge_wait_result_metrics(
        [wait_metrics, *hook_wait_summaries]
    )
    wait_summary["reactivation"] = wait_metrics["reactivation"]
    wait_metrics = wait_summary
    if hook_wait_count:
        wait_metrics["reactivation"]["eligible_waits"] += hook_wait_count
        wait_metrics["reactivation"]["coverage"] = (
            "partial"
            if wait_metrics["reactivation"]["matched_waits"]
            else "unknown"
        )
    if hook_sessions and spawn_fallback_sessions:
        spawn_source = HOOK_SOURCE + "+" + SOURCE
        spawn_coverage = "mixed"
    elif hook_sessions:
        spawn_source = HOOK_SOURCE
        spawn_coverage = "observed"
    elif spawn_fallback_sessions:
        spawn_source = SOURCE
        spawn_coverage = "fallback"
    else:
        spawn_source = "unknown"
        spawn_coverage = "unknown"
    if all_fallback_calls and hook_wait_count:
        wait_source = SOURCE + "+" + HOOK_SOURCE
    elif all_fallback_calls:
        wait_source = SOURCE
    elif hook_wait_count:
        wait_source = HOOK_SOURCE
    else:
        wait_source = "unknown"
    result = {
        "spawn_calls": spawn_calls if spawn_source != "unknown" else None,
        "wait_calls": (
            fallback_all["wait_calls"] + hook_wait_count
            if wait_source != "unknown"
            else None
        ),
        "send_calls": fallback_all["send_calls"] if all_fallback_calls else None,
        "wait_duration_ms": (
            fallback_all["wait_duration_ms"]
            if all_fallback_calls and not hook_wait_count
            else None
        ),
        "wait": wait_metrics,
        "fork_context_counts": fork_counts,
        "identifiers": identifiers,
        "metric_sources": {
            "spawn_calls": spawn_source,
            "fork_context_counts": spawn_source,
            "identifiers": spawn_source,
            "wait_calls": wait_source,
            "send_calls": SOURCE if all_fallback_calls else "unknown",
            "wait_duration_ms": (
                SOURCE if all_fallback_calls and not hook_wait_count else "unknown"
            ),
            "wait": wait_source,
        },
    }
    coverage = _coverage(
        spawn_source,
        spawn_coverage,
        hook_sessions + spawn_fallback_sessions,
        len(groups),
        fallback=bool(spawn_fallback_sessions or all_fallback_calls),
    )
    return result, coverage, fallback_fields


def _hook_docstar_metrics(
    groups: Sequence[Tuple[str, Set[str], Optional[_SessionData]]],
    telemetry: _TelemetryStore,
    follow_window: int,
) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str]]:
    hook_records: List[_HookEvent] = []
    fallback_calls: List[_RawCall] = []
    hook_sessions = 0
    fallback_sessions = 0
    for group in groups:
        hooks = _group_hook_events(group, telemetry)
        if hooks:
            hook_sessions += 1
            hook_records.extend(hooks)
        elif group[2] is not None:
            fallback_sessions += 1
            fallback_calls.extend(group[2].calls)

    fallback = _docstar_metrics(fallback_calls, follow_window)
    command_counts = Counter(fallback["commands"])
    docstar_hooks = [
        hook for hook in hook_records if hook.fields.get("classification") == "docstar"
    ]
    for hook in docstar_hooks:
        command = _identifier(hook.fields.get("docstar_subcommand")) or "unknown"
        command_counts[command] += 1
    grep_calls = fallback["grep_calls"] + sum(
        hook.fields.get("classification") == "grep" for hook in hook_records
    )
    read_calls = fallback["read_calls"] + sum(
        hook.fields.get("classification") == "markdown_read" for hook in hook_records
    )
    follow_up = list(fallback["follow_up"])
    by_session: Dict[str, List[_HookEvent]] = defaultdict(list)
    for hook in hook_records:
        if "tool_use_id" in hook.fields:
            by_session[hook.session_id].append(hook)
    for hook in docstar_hooks:
        ordered = sorted(
            by_session[hook.session_id],
            key=lambda item: (
                item.timestamp_ms is None,
                item.timestamp_ms if item.timestamp_ms is not None else float("inf"),
                item.sequence,
            ),
        )
        subsequent = [
            item
            for item in ordered
            if item.sequence != hook.sequence
            and (item.timestamp_ms or float("inf")) > (hook.timestamp_ms or float("-inf"))
            and item.fields.get("turn_id") == hook.fields.get("turn_id")
        ][:follow_window]
        following_grep = sum(item.fields.get("classification") == "grep" for item in subsequent)
        following_read = sum(
            item.fields.get("classification") == "markdown_read" for item in subsequent
        )
        follow_up.append(
            {
                "session_id": hook.session_id,
                "call_id": hook.fields.get("tool_use_id"),
                "turn_id": hook.fields.get("turn_id"),
                "window": follow_window,
                "grep_calls": following_grep,
                "read_calls": following_read,
                "grep_read_calls": following_grep + following_read,
            }
        )
    result = {
        "calls": fallback["calls"] + len(docstar_hooks),
        "commands": dict(sorted(command_counts.items())),
        "grep_calls": grep_calls,
        "read_calls": read_calls,
        "grep_read_calls": grep_calls + read_calls,
        "follow_up": follow_up,
        "grep_avoided": None,
        "causal_status": "causal_not_measured",
    }
    if hook_sessions and fallback_sessions:
        source = HOOK_SOURCE + "+" + SOURCE
        status = "mixed"
    elif hook_sessions:
        source = HOOK_SOURCE
        status = "observed"
    elif fallback_sessions:
        source = SOURCE
        status = "fallback"
    else:
        source = "unknown"
        status = "unknown"
        result.update(
            {
                "calls": None,
                "grep_calls": None,
                "read_calls": None,
                "grep_read_calls": None,
            }
        )
    coverage = _coverage(
        source,
        status,
        hook_sessions + fallback_sessions,
        len(groups),
        fallback=bool(fallback_sessions),
        follow_up="partial_hook_visibility" if hook_sessions else status,
    )
    fallback_fields = {"docstar"} if fallback_sessions else set()
    return result, coverage, fallback_fields


def _hook_skill_metrics(
    groups: Sequence[Tuple[str, Set[str], Optional[_SessionData]]],
    telemetry: _TelemetryStore,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Set[str]]:
    result: List[Dict[str, Any]] = []
    hook_sessions = 0
    fallback_sessions = 0
    native_links: Dict[Tuple[str, str], _OtelEvent] = {}
    fallback_links: Dict[Tuple[str, str], _RawCall] = {}
    session_ends: Dict[str, Optional[float]] = {}
    for group in groups:
        otel_events = _group_otel_events(group, telemetry)
        for event in otel_events:
            call_id = _identifier(event.attributes.get("call_id"))
            if event.event_name == "codex.tool_result" and call_id is not None:
                native_links.setdefault((event.session_id, call_id), event)
        fallback_session = group[2]
        for query_id in group[1]:
            end_candidates = [
                event.timestamp_ms for event in otel_events if event.timestamp_ms is not None
            ]
            if fallback_session is not None and fallback_session.session_end_ms is not None:
                end_candidates.append(fallback_session.session_end_ms)
            session_ends[query_id] = max(end_candidates) if end_candidates else None
        if fallback_session is not None:
            for call in fallback_session.calls:
                if call.call_id is not None:
                    fallback_links.setdefault((call.session_id, call.call_id), call)

    for group in groups:
        hooks = _group_hook_events(group, telemetry)
        if hooks:
            hook_sessions += 1
            skill_hooks = [
                hook
                for hook in hooks
                if hook.fields.get("classification") == "skill_load"
                and _identifier(hook.fields.get("skill_name")) is not None
            ]
            skill_hooks.sort(
                key=lambda item: (
                    item.timestamp_ms is None,
                    item.timestamp_ms if item.timestamp_ms is not None else float("inf"),
                    item.sequence,
                )
            )
            for index, hook in enumerate(skill_hooks):
                call_id = _identifier(hook.fields.get("tool_use_id"))
                native = native_links.get((hook.session_id, call_id)) if call_id else None
                fallback_call = (
                    fallback_links.get((hook.session_id, call_id))
                    if call_id and native is None
                    else None
                )
                if native is not None:
                    load_duration = _safe_integer(native.attributes.get("duration_ms"))
                    load_source: Optional[str] = OTEL_SOURCE
                    linkage = "exact"
                elif fallback_call is not None:
                    load_duration = fallback_call.duration_ms
                    load_source = SOURCE
                    linkage = "fallback_exact"
                else:
                    load_duration = None
                    load_source = None
                    linkage = "unlinked"
                boundary_ms = session_ends.get(hook.session_id)
                if index + 1 < len(skill_hooks):
                    boundary_ms = skill_hooks[index + 1].timestamp_ms
                observed_span = None
                if (
                    hook.timestamp_ms is not None
                    and boundary_ms is not None
                    and boundary_ms >= hook.timestamp_ms
                ):
                    observed_span = int(round(boundary_ms - hook.timestamp_ms))
                result.append(
                    {
                        "session_id": hook.session_id,
                        "call_id": call_id,
                        "skill": hook.fields["skill_name"],
                        "load_duration_ms": load_duration,
                        "observed_span_ms": observed_span,
                        "estimated_context_tokens": _estimated_bytes(
                            hook.fields.get("output_bytes")
                        ),
                        "source": HOOK_SOURCE,
                        "load_duration_source": load_source,
                        "observed_span_source": HOOK_SOURCE,
                        "estimated_context_tokens_source": "hook_output_bytes_estimate",
                        "estimated_context_tokens_is_estimate": True,
                        "linkage": linkage,
                    }
                )
            continue
        fallback_session = group[2]
        if fallback_session is None:
            continue
        fallback_sessions += 1
        for skill in _skill_metrics([fallback_session]):
            enriched = dict(skill)
            enriched.update(
                {
                    "source": SOURCE,
                    "load_duration_source": SOURCE,
                    "observed_span_source": SOURCE,
                    "estimated_context_tokens_source": "session_output_estimate",
                    "estimated_context_tokens_is_estimate": True,
                    "linkage": "fallback_exact",
                }
            )
            result.append(enriched)

    if hook_sessions and fallback_sessions:
        source = HOOK_SOURCE + "+" + SOURCE
        status = "mixed"
    elif hook_sessions:
        source = HOOK_SOURCE
        status = "observed"
    elif fallback_sessions:
        source = SOURCE
        status = "fallback"
    else:
        source = "unknown"
        status = "unknown"
    coverage = _coverage(
        source,
        status,
        hook_sessions + fallback_sessions,
        len(groups),
        fallback=bool(fallback_sessions),
        exact_duration_links=sum(
            skill.get("linkage") in {"exact", "fallback_exact"} for skill in result
        ),
        skill_loads=len(result),
    )
    fallback_fields = {"skills"} if fallback_sessions else set()
    return result, coverage, fallback_fields


def _selected_events(
    groups: Sequence[Tuple[str, Set[str], Optional[_SessionData]]],
    by_session: Mapping[str, Sequence[Any]],
) -> List[Any]:
    result: List[Any] = []
    seen: Set[Tuple[str, int]] = set()
    for _, query_ids, _ in groups:
        for event in _events_for_ids(by_session, query_ids):
            key = (event.session_id, event.sequence)
            if key not in seen:
                seen.add(key)
                result.append(event)
    return result


def _observed_session_count(events: Sequence[Any]) -> int:
    return len({event.session_id for event in events})


def _estimated_call_totals(calls: Sequence[Mapping[str, Any]]) -> Dict[str, Optional[int]]:
    if not calls:
        return {"input": 0, "output": 0, "total": 0}
    input_values = [call.get("estimated_input_tokens") for call in calls]
    output_values = [call.get("estimated_output_tokens") for call in calls]
    input_total = (
        sum(value for value in input_values if isinstance(value, int))
        if all(isinstance(value, int) for value in input_values)
        else None
    )
    output_total = (
        sum(value for value in output_values if isinstance(value, int))
        if all(isinstance(value, int) for value in output_values)
        else None
    )
    return {
        "input": input_total,
        "output": output_total,
        "total": (
            input_total + output_total
            if input_total is not None and output_total is not None
            else None
        ),
    }


def _apply_telemetry(
    run: Dict[str, Any],
    sessions: Sequence[_SessionData],
    requested_id: str,
    telemetry: _TelemetryStore,
    follow_window: int,
) -> None:
    groups = _logical_session_groups(requested_id, run, sessions, telemetry)
    covered_ids = {
        missing_id
        for missing_id in run["data_quality"]["missing_sessions"]
        if telemetry.has_session(missing_id)
    }
    if covered_ids:
        run["data_quality"]["missing_sessions"] = [
            missing_id
            for missing_id in run["data_quality"]["missing_sessions"]
            if missing_id not in covered_ids
        ]
    if groups and run["session_id"] is None:
        run["session_id"] = requested_id
    if groups:
        run["session_counts"] = {
            "main": 1,
            "descendants": len(groups) - 1,
            "total": len(groups),
        }

    otel_events: List[_OtelEvent] = _selected_events(groups, telemetry.otel_by_session)
    hook_events: List[_HookEvent] = _selected_events(groups, telemetry.hooks_by_session)
    total_sessions = len(groups)
    fallback_session_count = sum(group[2] is not None for group in groups)
    fallback_fields: Set[str] = set()
    if fallback_session_count:
        fallback_fields.update({"session_counts", "timing"})

    actual_tokens, token_coverage, token_fallback = _telemetry_tokens(groups, telemetry)
    fallback_fields.update(token_fallback)
    run["actual_tokens"] = actual_tokens

    api_events = [
        event
        for event in otel_events
        if event.event_name in {"codex.api_request", "codex.websocket_request"}
    ]
    tool_events = [event for event in otel_events if event.event_name == "codex.tool_result"]
    run["api_calls"] = _api_metrics(otel_events)
    run["native_tool_results"] = _native_tool_metrics(otel_events)

    tool_calls, tool_coverage, tool_fallback = _merged_tool_calls(groups, telemetry)
    fallback_fields.update(tool_fallback)
    run["tool_calls"] = tool_calls
    run["estimated_tool_io_tokens"] = _estimated_call_totals(tool_calls)

    gmgn, gmgn_coverage, gmgn_fallback = _hook_gmgn_metrics(groups, telemetry)
    fallback_fields.update(gmgn_fallback)
    run["gmgn"] = gmgn

    docstar, docstar_coverage, docstar_fallback = _hook_docstar_metrics(
        groups,
        telemetry,
        follow_window,
    )
    fallback_fields.update(docstar_fallback)
    run["docstar"] = docstar

    skills, skills_coverage, skills_fallback = _hook_skill_metrics(groups, telemetry)
    fallback_fields.update(skills_fallback)
    run["skills"] = skills

    if fallback_session_count == total_sessions and total_sessions:
        session_source = SOURCE
        session_status = "fallback"
    elif fallback_session_count:
        session_source = SOURCE
        session_status = "partial"
    elif total_sessions:
        session_source = OTEL_SOURCE if otel_events else HOOK_SOURCE
        session_status = "partial"
    else:
        session_source = "unknown"
        session_status = "unknown"
    timing_status = "fallback" if sessions else "unknown"
    timing_source = SOURCE if sessions else "unknown"
    coverage = {
        "session_counts": _coverage(
            session_source,
            session_status,
            fallback_session_count,
            total_sessions,
            fallback=bool(fallback_session_count),
        ),
        "timing": _coverage(
            timing_source,
            timing_status,
            1 if sessions else 0,
            1 if total_sessions else 0,
            fallback=bool(sessions),
        ),
        "actual_tokens": token_coverage,
        "api_calls": _coverage(
            OTEL_SOURCE if api_events else "unknown",
            "observed" if api_events else "unknown",
            _observed_session_count(api_events),
            total_sessions,
        ),
        "native_tool_results": _coverage(
            OTEL_SOURCE if tool_events else "unknown",
            "observed" if tool_events else "unknown",
            _observed_session_count(tool_events),
            total_sessions,
        ),
        **tool_coverage,
        "gmgn": gmgn_coverage,
        "docstar": docstar_coverage,
        "skills": skills_coverage,
    }
    run["coverage"] = coverage

    otel_session_count = _observed_session_count(otel_events)
    hook_session_count = _observed_session_count(hook_events)
    fallback_used = bool(fallback_fields)
    run["sources"] = {
        OTEL_SOURCE: {
            "available": bool(otel_events),
            "records": len(otel_events),
            "sessions": otel_session_count,
        },
        HOOK_SOURCE: {
            "available": bool(hook_events),
            "records": len(hook_events),
            "sessions": hook_session_count,
        },
        SOURCE: {
            "available": bool(sessions),
            "used": fallback_used,
            "fields": sorted(fallback_fields),
            "sessions": fallback_session_count,
        },
    }
    primary_sources = []
    if otel_events:
        primary_sources.append(OTEL_SOURCE)
    if hook_events:
        primary_sources.append(HOOK_SOURCE)
    if primary_sources and fallback_used:
        run_source = MIXED_SOURCE
    elif len(primary_sources) == 2:
        run_source = OTEL_SOURCE + "+" + HOOK_SOURCE
    elif primary_sources:
        run_source = primary_sources[0]
    else:
        run_source = SOURCE
    run["source"] = run_source
    run["data_quality"]["source"] = run_source
    run["data_quality"]["malformed_telemetry_lines"] = telemetry.malformed_lines


def _empty_run(requested_id: str) -> Dict[str, Any]:
    return {
        "requested_id": requested_id,
        "session_id": None,
        "timing": {
            "main_wall_elapsed_ms": None,
            "completed_turn_duration_ms": None,
            "agent_turn_duration_ms": None,
        },
        "session_counts": {"main": 0, "descendants": 0, "total": 0},
        "actual_tokens": _empty_tokens(),
        "estimated_tool_io_tokens": {"input": 0, "output": 0, "total": 0},
        "tool_calls": [],
        "skills": [],
        "gmgn": _gmgn_metrics([]),
        "docstar": _docstar_metrics([], DEFAULT_FOLLOW_WINDOW),
        "data_quality": {
            "malformed_lines": 0,
            "unpaired_calls": 0,
            "missing_sessions": [requested_id],
            "source": SOURCE,
        },
    }


def _build_run(
    requested_id: str,
    index: _SessionIndex,
    cache: Dict[Path, _SessionData],
    include_descendants: bool,
    follow_window: int,
) -> Tuple[Dict[str, Any], List[_SessionData]]:
    root_descriptor = index.resolve(requested_id)
    if root_descriptor is None:
        run = _empty_run(requested_id)
        run["docstar"] = _docstar_metrics([], follow_window)
        return run, []

    sessions: List[_SessionData] = []
    queue = [root_descriptor]
    seen_paths: Set[Path] = set()
    missing_sessions: List[str] = []
    missing_seen: Set[str] = set()

    while queue:
        descriptor = queue.pop(0)
        if descriptor.path in seen_paths:
            continue
        seen_paths.add(descriptor.path)
        if descriptor.path not in cache:
            cache[descriptor.path] = _load_session(descriptor)
        session = cache[descriptor.path]
        sessions.append(session)
        if not include_descendants:
            continue
        for child_id in session.child_ids:
            child = index.resolve(child_id)
            if child is None:
                if child_id not in missing_seen:
                    missing_seen.add(child_id)
                    missing_sessions.append(child_id)
                continue
            if child.path not in seen_paths:
                queue.append(child)

    root = sessions[0]
    calls = [call for session in sessions for call in session.calls]
    calls.sort(
        key=lambda call: (
            call.start_ms is None,
            call.start_ms if call.start_ms is not None else float("inf"),
            call.session_id,
            call.sequence,
        )
    )
    estimated_input = sum(call.estimated_input_tokens for call in calls)
    estimated_output = sum(call.estimated_output_tokens for call in calls)
    malformed_lines = sum(session.malformed_lines for session in sessions)
    unpaired_calls = sum(session.unpaired_calls for session in sessions)
    run = {
        "requested_id": requested_id,
        "session_id": root.descriptor.session_id,
        "timing": {
            "main_wall_elapsed_ms": root.wall_elapsed_ms,
            "completed_turn_duration_ms": root.completed_turn_duration_ms,
            "agent_turn_duration_ms": sum(
                session.completed_turn_duration_ms for session in sessions[1:]
            ),
        },
        "session_counts": {
            "main": 1,
            "descendants": len(sessions) - 1,
            "total": len(sessions),
        },
        "actual_tokens": _sum_tokens(sessions),
        "estimated_tool_io_tokens": {
            "input": estimated_input,
            "output": estimated_output,
            "total": estimated_input + estimated_output,
        },
        "tool_calls": [call.public() for call in calls],
        "skills": _skill_metrics(sessions),
        "gmgn": _gmgn_metrics(calls, sessions),
        "docstar": _docstar_metrics(calls, follow_window),
        "data_quality": {
            "malformed_lines": malformed_lines,
            "unpaired_calls": unpaired_calls,
            "missing_sessions": missing_sessions,
            "source": SOURCE,
        },
    }
    return run, sessions


def build_report(
    session_ids: Sequence[str],
    *,
    codex_home: Optional[Path] = None,
    include_descendants: bool = True,
    follow_window: int = DEFAULT_FOLLOW_WINDOW,
) -> Dict[str, Any]:
    """Build a privacy-safe report from Collector, hook, and session records."""
    requested_ids = (
        [session_ids]
        if isinstance(session_ids, str)
        else [str(session_id) for session_id in session_ids]
    )
    if not requested_ids:
        raise ValueError("at least one session ID is required")
    if follow_window < 0:
        raise ValueError("follow_window must be non-negative")
    home = Path(
        codex_home
        if codex_home is not None
        else os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
    ).expanduser()
    index = _SessionIndex(home)
    telemetry = _TelemetryStore(home)
    cache: Dict[Path, _SessionData] = {}
    runs: List[Dict[str, Any]] = []
    included: Dict[Path, _SessionData] = {}
    missing_sessions: List[str] = []
    missing_seen: Set[str] = set()
    for requested_id in requested_ids:
        run, sessions = _build_run(
            requested_id,
            index,
            cache,
            include_descendants,
            follow_window,
        )
        _apply_telemetry(run, sessions, requested_id, telemetry, follow_window)
        runs.append(run)
        for session in sessions:
            included[session.descriptor.path] = session
        for missing_id in run["data_quality"]["missing_sessions"]:
            if missing_id not in missing_seen:
                missing_seen.add(missing_id)
                missing_sessions.append(missing_id)

    run_sources = {run["source"] for run in runs}
    report_source = next(iter(run_sources)) if len(run_sources) == 1 else MIXED_SOURCE
    return {
        "schema_version": SCHEMA_VERSION,
        "source": report_source,
        "configuration": {
            "include_descendants": include_descendants,
            "follow_window": follow_window,
        },
        "runs": runs,
        "data_quality": {
            "malformed_lines": sum(item.malformed_lines for item in included.values()),
            "unpaired_calls": sum(item.unpaired_calls for item in included.values()),
            "malformed_telemetry_lines": telemetry.malformed_lines,
            "missing_sessions": missing_sessions,
            "source": report_source,
        },
    }


def _human_value(value: Any) -> str:
    return "unknown" if value is None else str(value)


def render_human(report: Mapping[str, Any]) -> str:
    lines: List[str] = []
    for run in report.get("runs", []):
        requested_id = run["requested_id"]
        if run["session_id"] is None:
            lines.append("运行 {0}：未找到 session".format(requested_id))
            continue
        timing = run["timing"]
        counts = run["session_counts"]
        actual = run["actual_tokens"]
        estimated = run["estimated_tool_io_tokens"]
        gmgn = run["gmgn"]
        wait = gmgn["wait"]
        wait_reactivation = wait["reactivation"]
        docstar = run["docstar"]
        quality = run["data_quality"]
        coverage = run["coverage"]
        sources = run["sources"]
        fallback = sources[SOURCE]
        follow_up_total = sum(
            item["grep_read_calls"] for item in docstar["follow_up"]
        )
        tool_count = (
            len(run["tool_calls"])
            if coverage["tool_calls"]["coverage"] != "unknown"
            else None
        )
        skill_count = (
            len(run["skills"])
            if coverage["skills"]["coverage"] != "unknown"
            else None
        )
        docstar_follow_up = (
            follow_up_total if coverage["docstar"]["coverage"] != "unknown" else None
        )
        lines.extend(
            [
                "运行 {0}（session {1}）".format(requested_id, run["session_id"]),
                "  数据源：{0}；fallback：{1}；coverage：token {2}，API {3}，native tool {4}，linkage {5}".format(
                    run["source"],
                    "used" if fallback["used"] else "not_used",
                    coverage["actual_tokens"]["coverage"],
                    coverage["api_calls"]["coverage"],
                    coverage["native_tool_results"]["coverage"],
                    coverage["native_hook_linkage"]["coverage"],
                ),
                "  会话：主 {main}，子 {descendants}，总计 {total}".format(**counts),
                "  主任务墙钟：{0} ms；完成 turn：{1} ms；agent turn：{2} ms".format(
                    _human_value(timing["main_wall_elapsed_ms"]),
                    _human_value(timing["completed_turn_duration_ms"]),
                    _human_value(timing["agent_turn_duration_ms"]),
                ),
                "  实际 token：input {0}，cached {1}，output {2}，reasoning {3}，total {4}".format(
                    _human_value(actual["input"]),
                    _human_value(actual["cached"]),
                    _human_value(actual["output"]),
                    _human_value(actual["reasoning"]),
                    _human_value(actual["total"]),
                ),
                "  工具调用：{0}；估算工具 I/O token：input {1}，output {2}，total {3}".format(
                    _human_value(tool_count),
                    _human_value(estimated["input"]),
                    _human_value(estimated["output"]),
                    _human_value(estimated["total"]),
                ),
                "  GMGN：spawn {0}，wait {1}（{2} ms），send {3}".format(
                    _human_value(gmgn["spawn_calls"]),
                    _human_value(gmgn["wait_calls"]),
                    _human_value(gmgn["wait_duration_ms"]),
                    _human_value(gmgn["send_calls"]),
                ),
                "  等待结果：update {0}，timeout {1}，unknown/error/interrupted {2}；最大连续超时 {3}；等待风暴 {4}".format(
                    wait["result_counts"]["update"],
                    wait["result_counts"]["timeout"],
                    (
                        wait["result_counts"]["unknown"]
                        + wait["result_counts"]["error"]
                        + wait["result_counts"]["interrupted"]
                    ),
                    wait["max_consecutive_timeouts"],
                    wait["wait_storm_count"],
                ),
                "  等待重激活 token：input {0}，cached {1}，output {2}，reasoning {3}，total {4}；matched {5}/{6}；coverage {7}；linkage {8}".format(
                    _human_value(wait_reactivation["tokens"]["input"]),
                    _human_value(wait_reactivation["tokens"]["cached"]),
                    _human_value(wait_reactivation["tokens"]["output"]),
                    _human_value(wait_reactivation["tokens"]["reasoning"]),
                    _human_value(wait_reactivation["tokens"]["total"]),
                    wait_reactivation["matched_waits"],
                    wait_reactivation["eligible_waits"],
                    wait_reactivation["coverage"],
                    wait_reactivation["linkage"],
                ),
                "  DocStar：{0} 次；grep/read {1}；DocStar follow-up grep/read {2}；{3}".format(
                    _human_value(docstar["calls"]),
                    _human_value(docstar["grep_read_calls"]),
                    _human_value(docstar_follow_up),
                    docstar["causal_status"],
                ),
                "  skill 调用：{0}".format(_human_value(skill_count)),
                "  数据质量：malformed {0}，unpaired {1}，missing {2}".format(
                    quality["malformed_lines"],
                    quality["unpaired_calls"],
                    len(quality["missing_sessions"]),
                ),
            ]
        )
        for skill in run["skills"]:
            lines.append(
                "    {0}：load {1} ms（{2}）；observed {3} ms；context {4} token（estimate）；linkage {5}".format(
                    skill["skill"],
                    _human_value(skill["load_duration_ms"]),
                    _human_value(skill.get("load_duration_source")),
                    _human_value(skill["observed_span_ms"]),
                    _human_value(skill["estimated_context_tokens"]),
                    skill.get("linkage", "fallback_exact"),
                )
            )
    return "\n".join(lines)


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a privacy-safe GMGN report from Codex session JSONL.",
    )
    parser.add_argument("session_ids", nargs="+", metavar="SESSION_ID")
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))),
        help="Codex home containing sessions/",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON")
    descendants = parser.add_mutually_exclusive_group()
    descendants.add_argument(
        "--include-descendants",
        action="store_true",
        dest="include_descendants",
        default=True,
        help="Recursively include sub-agent sessions (default)",
    )
    descendants.add_argument(
        "--no-descendants",
        action="store_false",
        dest="include_descendants",
        help="Report only requested sessions",
    )
    parser.add_argument(
        "--follow-window",
        type=_non_negative_int,
        default=DEFAULT_FOLLOW_WINDOW,
        help="Post-DocStar tool window (default: %(default)s)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = _parser().parse_args(argv)
    report = build_report(
        arguments.session_ids,
        codex_home=arguments.codex_home,
        include_descendants=arguments.include_descendants,
        follow_window=arguments.follow_window,
    )
    if arguments.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
