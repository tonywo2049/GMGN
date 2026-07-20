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
DEFAULT_FOLLOW_WINDOW = 5
ESTIMATED_CHARACTERS_PER_TOKEN = 4

TOKEN_FIELDS = ("input", "cached", "output", "reasoning", "total")
IDENTIFIER_FIELDS = ("card_id", "run_id", "lane_key", "target_milestone_id")
FORK_CONTEXT_VALUES = ("none", "all", "false", "true", "unspecified")

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


@dataclass
class _SessionData:
    descriptor: _SessionDescriptor
    calls: List[_RawCall]
    child_ids: List[str]
    actual_tokens: Dict[str, int]
    malformed_lines: int
    unpaired_calls: int
    completed_turn_duration_ms: int
    wall_elapsed_ms: Optional[int]
    session_end_ms: Optional[float]


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


def _empty_tokens() -> Dict[str, int]:
    return {field_name: 0 for field_name in TOKEN_FIELDS}


def _first_int(mapping: Mapping[str, Any], keys: Iterable[str]) -> int:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return max(0, int(value))
    return 0


def _token_usage(payload: Mapping[str, Any]) -> Optional[Dict[str, int]]:
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
    if result["total"] == 0 and (result["input"] or result["output"]):
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


def _walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from _walk_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_values(nested)
    else:
        yield value


def _extract_identifiers(arguments: Any) -> Dict[str, List[str]]:
    result = {field_name: [] for field_name in IDENTIFIER_FIELDS}
    seen = {field_name: set() for field_name in IDENTIFIER_FIELDS}
    decoded = _decode_arguments(arguments)

    def add(field_name: str, value: Any) -> None:
        identifier = _identifier(value)
        if identifier and identifier not in seen[field_name]:
            seen[field_name].add(identifier)
            result[field_name].append(identifier)

    if isinstance(decoded, dict):
        stack: List[Mapping[str, Any]] = [decoded]
        while stack:
            mapping = stack.pop()
            for key, value in mapping.items():
                lowered = str(key).lower()
                if lowered in result:
                    add(lowered, value)
                if isinstance(value, dict):
                    stack.append(value)

    identifier_pattern = r"([A-Za-z0-9][A-Za-z0-9._:@/+~=-]{0,255})"
    patterns = {
        field_name: re.compile(
            r"(?:[\"']?" + re.escape(field_name) + r"[\"']?)\s*(?:=|:)\s*[\"']?" + identifier_pattern,
            re.IGNORECASE,
        )
        for field_name in IDENTIFIER_FIELDS
    }
    for value in _walk_values(decoded):
        if not isinstance(value, str):
            continue
        for field_name, pattern in patterns.items():
            for match in pattern.finditer(value):
                add(field_name, match.group(1))
    return result


def _gmgn_metrics(calls: Sequence[_RawCall]) -> Dict[str, Any]:
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


def _sum_tokens(sessions: Sequence[_SessionData]) -> Dict[str, int]:
    total = _empty_tokens()
    for session in sessions:
        for field_name in TOKEN_FIELDS:
            total[field_name] += session.actual_tokens[field_name]
    return total


def _empty_run(requested_id: str) -> Dict[str, Any]:
    return {
        "requested_id": requested_id,
        "session_id": None,
        "timing": {
            "main_wall_elapsed_ms": None,
            "completed_turn_duration_ms": 0,
            "agent_turn_duration_ms": 0,
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
        "gmgn": _gmgn_metrics(calls),
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
    """Build a privacy-safe report from Codex session JSONL files."""
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
        runs.append(run)
        for session in sessions:
            included[session.descriptor.path] = session
        for missing_id in run["data_quality"]["missing_sessions"]:
            if missing_id not in missing_seen:
                missing_seen.add(missing_id)
                missing_sessions.append(missing_id)

    return {
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE,
        "configuration": {
            "include_descendants": include_descendants,
            "follow_window": follow_window,
        },
        "runs": runs,
        "data_quality": {
            "malformed_lines": sum(item.malformed_lines for item in included.values()),
            "unpaired_calls": sum(item.unpaired_calls for item in included.values()),
            "missing_sessions": missing_sessions,
            "source": SOURCE,
        },
    }


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
        docstar = run["docstar"]
        quality = run["data_quality"]
        lines.extend(
            [
                "运行 {0}（session {1}）".format(requested_id, run["session_id"]),
                "  会话：主 {main}，子 {descendants}，总计 {total}".format(**counts),
                "  主任务墙钟：{0} ms；完成 turn：{1} ms；agent turn：{2} ms".format(
                    timing["main_wall_elapsed_ms"],
                    timing["completed_turn_duration_ms"],
                    timing["agent_turn_duration_ms"],
                ),
                "  实际 token：input {input}，cached {cached}，output {output}，reasoning {reasoning}，total {total}".format(
                    **actual
                ),
                "  工具调用：{0}；估算工具 I/O token：input {1}，output {2}，total {3}".format(
                    len(run["tool_calls"]),
                    estimated["input"],
                    estimated["output"],
                    estimated["total"],
                ),
                "  GMGN：spawn {0}，wait {1}（{2} ms），send {3}".format(
                    gmgn["spawn_calls"],
                    gmgn["wait_calls"],
                    gmgn["wait_duration_ms"],
                    gmgn["send_calls"],
                ),
                "  DocStar：{0} 次；grep/read {1}".format(
                    docstar["calls"], docstar["grep_read_calls"]
                ),
                "  数据质量：malformed {0}，unpaired {1}，missing {2}".format(
                    quality["malformed_lines"],
                    quality["unpaired_calls"],
                    len(quality["missing_sessions"]),
                ),
            ]
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
