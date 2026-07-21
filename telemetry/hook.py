#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import sys
from typing import Any, Optional


SCHEMA_VERSION = "gmgn-hook-event-v1"
MISSING = object()
SAFE_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+#~\-]{0,255}\Z")
MARKDOWN_PATH = re.compile(r"\.(?:md|markdown|mdx)(?:(?::|#)\d.*)?\Z", re.IGNORECASE)
EXIT_CODE_TEXT = re.compile(r"(?i)\bexit[ _-]?code\s*[:=]\s*(-?\d+)\b")
SEMANTIC_FIELDS = {
    "card_id": "cardid",
    "run_id": "runid",
    "lane_key": "lanekey",
    "target_milestone_id": "targetmilestoneid",
}
READ_COMMANDS = {"awk", "bat", "batcat", "cat", "head", "less", "more", "sed", "tail"}
GREP_COMMANDS = {"egrep", "fgrep", "grep", "rg", "ripgrep"}
SHELL_COMMANDS = {"bash", "dash", "sh", "zsh"}
SUCCESS_WORDS = {"completed", "ok", "passed", "success", "succeeded"}
FAILURE_WORDS = {"error", "failed", "failure", "timed_out", "timeout"}
WAIT_STATUS_RESULTS = {
    "timeout": "timeout",
    "timedout": "timeout",
    "interrupted": "interrupted",
    "cancelled": "interrupted",
    "canceled": "interrupted",
}
WAIT_TOOLS = {"wait_agent", "wait_agents", "wait_threads"}
SPAWN_TOOLS = {"agent", "spawn", "spawn_agent"}
SEND_TOOLS = {
    "followup_task",
    "send_message",
    "send_message_to_agent",
    "send_message_to_thread",
}
OBSERVE_TOOLS = {"list_agents", "list_threads", "read_thread"}
PYTHON_EXECUTABLE = re.compile(r"python(?:3(?:\.\d+)*)?\Z", re.IGNORECASE)
PYTHON_OPTIONS = {"-B", "-E", "-I", "-O", "-OO", "-P", "-s", "-S", "-u"}
PYTHON_VALUE_OPTIONS = {"-W", "-X", "--check-hash-based-pycs"}
HOOK_FILE = re.compile(r"hooks-(\d{4}-\d{2}-\d{2})\.jsonl\Z")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(now: Optional[datetime] = None) -> str:
    current = now or utc_now()
    return current.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def get_value(mapping: Any, *names: str, default: Any = MISSING) -> Any:
    if not isinstance(mapping, dict):
        return default
    wanted = {normalize_key(name) for name in names}
    for key, value in mapping.items():
        if isinstance(key, str) and normalize_key(key) in wanted:
            return value
    return default


def find_value(value: Any, normalized_name: str) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str) and normalize_key(key) == normalized_name:
                return child
        for child in value.values():
            found = find_value(child, normalized_name)
            if found is not MISSING:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_value(child, normalized_name)
            if found is not MISSING:
                return found
    return MISSING


def safe_token(value: Any, limit: int = 256) -> Optional[str]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        value = str(value)
    if not isinstance(value, str):
        return None
    candidate = value.strip().strip("`\"'")
    if len(candidate) > limit or SAFE_TOKEN.fullmatch(candidate) is None:
        return None
    return candidate


def serialized_bytes(value: Any) -> int:
    if value is MISSING:
        return 0
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return len(encoded)


def basename(token: str) -> str:
    return PurePosixPath(token).name.casefold()


def contains_unquoted_compound(command: str) -> bool:
    quote = ""
    escaped = False
    index = 0
    while index < len(command):
        character = command[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if quote == "'":
            if character == "'":
                quote = ""
            index += 1
            continue
        if quote == '"':
            if character == "\\":
                escaped = True
            elif character == '"':
                quote = ""
            elif character == "`" or (
                character == "$" and index + 1 < len(command) and command[index + 1] == "("
            ):
                return True
            index += 1
            continue
        if character == "\\":
            escaped = True
        elif character in {"'", '"'}:
            quote = character
        elif character in {";", "|", "&", "`", "\n", "\r"}:
            return True
        elif character == "$" and index + 1 < len(command) and command[index + 1] == "(":
            return True
        elif character in {"<", ">"} and index + 1 < len(command) and command[index + 1] == "(":
            return True
        index += 1
    return False


def shell_tokens(command: Any) -> tuple[list[str], bool]:
    if isinstance(command, list) and all(isinstance(item, str) for item in command):
        return list(command), False
    if not isinstance(command, str):
        return [], False
    if contains_unquoted_compound(command):
        return [], True
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return [], False
    control_words = {"case", "for", "if", "until", "while"}
    if tokens and tokens[0].casefold() in control_words:
        return [], True
    return tokens, False


def executable_index(tokens: list[str]) -> int:
    index = 0
    while index < len(tokens) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[index]):
        index += 1
    if index < len(tokens) and basename(tokens[index]) == "env":
        index += 1
        while index < len(tokens):
            token = tokens[index]
            if token.startswith("-") or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token):
                index += 1
                continue
            break
    return index


def python_docstar_index(tokens: list[str], start: int) -> Optional[int]:
    index = start + 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            index += 1
            break
        if token == "-m":
            if index + 1 < len(tokens) and tokens[index + 1].casefold() == "docstar":
                return index + 1
            return None
        if token in PYTHON_OPTIONS:
            index += 1
            continue
        if token in PYTHON_VALUE_OPTIONS:
            if index + 1 >= len(tokens):
                return None
            index += 2
            continue
        if any(
            token.startswith(prefix) and token != prefix
            for prefix in ("-W", "-X", "--check-hash-based-pycs=")
        ):
            index += 1
            continue
        if token.startswith("-"):
            return None
        break
    if index >= len(tokens):
        return None
    script = tokens[index]
    if "/" not in script or basename(script) != "docstar.py":
        return None
    return index


def docstar_index(tokens: list[str], start: int) -> Optional[int]:
    if start >= len(tokens):
        return None
    executable = basename(tokens[start])
    if executable == "docstar":
        return start
    if PYTHON_EXECUTABLE.fullmatch(executable) is not None:
        return python_docstar_index(tokens, start)
    if executable in {"npx", "pipx", "uvx"} and len(tokens) > start + 1:
        if basename(tokens[start + 1]) == "docstar":
            return start + 1
    return None


def docstar_subcommand(tokens: list[str], marker: int) -> Optional[str]:
    options_with_values = {
        "--config",
        "--corpus",
        "--format",
        "--log-level",
        "--project-root",
    }
    index = marker + 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            index += 1
            break
        if not token.startswith("-"):
            return safe_token(token, 64)
        if "=" not in token and token in options_with_values:
            index += 2
        else:
            index += 1
    if index < len(tokens):
        return safe_token(tokens[index], 64)
    return None


def markdown_skill(tokens: list[str]) -> Optional[str]:
    for token in tokens:
        cleaned = token.rstrip(":")
        path = PurePosixPath(cleaned)
        if path.name.casefold() == "skill.md":
            return safe_token(path.parent.name, 128)
    return None


def is_markdown_path(token: str) -> bool:
    return MARKDOWN_PATH.search(token.rstrip(",;")) is not None


def classify_bash(command: Any) -> tuple[str, Optional[str], Optional[str]]:
    tokens, compound = shell_tokens(command)
    if compound:
        return "unclassified_compound", None, None
    if not tokens:
        return "other", None, None
    start = executable_index(tokens)
    if start >= len(tokens):
        return "other", None, None
    executable = basename(tokens[start])
    if executable in SHELL_COMMANDS and any(
        token in {"-c", "-lc"} for token in tokens[start + 1 :]
    ):
        return "unclassified_compound", None, None

    marker = docstar_index(tokens, start)
    if marker is not None:
        return "docstar", docstar_subcommand(tokens, marker), None

    if executable in READ_COMMANDS:
        skill_name = markdown_skill(tokens[start + 1 :])
        if skill_name is not None:
            return "skill_load", None, skill_name

    if executable in GREP_COMMANDS:
        if executable in {"rg", "ripgrep"} and "--files" in tokens[start + 1 :]:
            return "other", None, None
        return "grep", None, None
    if executable == "git" and len(tokens) > start + 1 and tokens[start + 1] == "grep":
        return "grep", None, None

    if executable in READ_COMMANDS and any(
        is_markdown_path(token) for token in tokens[start + 1 :]
    ):
        return "markdown_read", None, None
    return "other", None, None


def is_bash_tool(tool_name: Any) -> bool:
    return isinstance(tool_name, str) and tool_name.casefold() in {
        "bash",
        "exec_command",
        "shell",
        "shell_command",
    }


def agent_action(tool_name: Any) -> Optional[str]:
    if not isinstance(tool_name, str):
        return None
    normalized = tool_name.casefold().replace("::", ".").replace("__", ".")
    leaf = normalized.rsplit(".", 1)[-1]
    if leaf in WAIT_TOOLS:
        return "wait"
    if leaf in SPAWN_TOOLS:
        return "spawn"
    if leaf in SEND_TOOLS:
        return "send"
    if leaf in OBSERVE_TOOLS:
        return "observe"
    return None


def is_agent_tool(tool_name: Any) -> bool:
    return agent_action(tool_name) is not None


def is_skill_tool(tool_name: Any) -> bool:
    if not isinstance(tool_name, str):
        return False
    normalized = normalize_key(tool_name)
    return normalized in {"skill", "loadskill", "useskill"}


def command_from_input(tool_input: Any) -> Any:
    if isinstance(tool_input, str) or isinstance(tool_input, list):
        return tool_input
    return get_value(tool_input, "command", "cmd", default=MISSING)


def extract_semantic_ids(tool_input: Any) -> dict[str, str]:
    extracted = {}
    for output_name, normalized_name in SEMANTIC_FIELDS.items():
        direct = safe_token(find_value(tool_input, normalized_name))
        if direct is not None:
            extracted[output_name] = direct
    return extracted


def extract_fork_context(tool_input: Any) -> Optional[bool]:
    raw = find_value(tool_input, "forkcontext")
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str) and raw.casefold() in {"false", "true"}:
        return raw.casefold() == "true"
    return None


def extract_fork_turns(tool_input: Any) -> Optional[str]:
    raw = find_value(tool_input, "forkturns")
    if isinstance(raw, int) and raw > 0:
        return str(raw)
    if not isinstance(raw, str):
        return None
    candidate = raw.strip().casefold()
    if candidate in {"all", "none"} or (candidate.isdigit() and int(candidate) > 0):
        return candidate
    return None


def extract_exit_code(tool_output: Any) -> Optional[int]:
    for normalized_name in ("exitcode", "returncode"):
        raw = find_value(tool_output, normalized_name)
        if isinstance(raw, int) and not isinstance(raw, bool):
            return raw
        if isinstance(raw, str) and re.fullmatch(r"-?\d+", raw.strip()):
            return int(raw.strip())
    if isinstance(tool_output, str):
        match = EXIT_CODE_TEXT.search(tool_output)
        if match is not None:
            return int(match.group(1))
    return None


def extract_success(payload: dict, tool_output: Any, exit_code: Optional[int]) -> Optional[bool]:
    for source in (tool_output, payload):
        raw = get_value(source, "success", "ok", default=MISSING)
        if isinstance(raw, bool):
            return raw
        raw_error = get_value(source, "is_error", "isError", default=MISSING)
        if isinstance(raw_error, bool):
            return not raw_error
        status_value = get_value(source, "status", default=MISSING)
        if isinstance(status_value, str):
            normalized = status_value.strip().casefold().replace(" ", "_")
            if normalized in SUCCESS_WORDS:
                return True
            if normalized in FAILURE_WORDS:
                return False
    if exit_code is not None:
        return exit_code == 0
    return None


def extract_wait_result(tool_output: Any, success: Optional[bool]) -> str:
    timed_out: list[bool] = []
    for normalized_name in ("timedout", "timeout"):
        raw = find_value(tool_output, normalized_name)
        if isinstance(raw, bool):
            timed_out.append(raw)
    if True in timed_out:
        return "timeout"
    status = find_value(tool_output, "status")
    if isinstance(status, str):
        structured_result = WAIT_STATUS_RESULTS.get(normalize_key(status))
        if structured_result is not None:
            return structured_result
    if success is False:
        return "error"
    if False in timed_out:
        return "update"
    if isinstance(tool_output, str):
        normalized = tool_output.casefold()
    else:
        try:
            normalized = json.dumps(
                tool_output,
                ensure_ascii=False,
                sort_keys=True,
            ).casefold()
        except (TypeError, ValueError):
            normalized = str(tool_output).casefold()
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
    return "unknown"


def extract_skill_name(tool_input: Any) -> Optional[str]:
    direct = get_value(tool_input, "skill_name", "skillName", "skill", "name", default=MISSING)
    return safe_token(direct, 128)


def build_record(payload: dict, now: Optional[datetime] = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": timestamp(now),
    }
    fields = (
        ("event", get_value(payload, "hook_event_name", "hookEventName", "event"), 64),
        ("session_id", get_value(payload, "session_id", "sessionId"), 256),
        ("turn_id", get_value(payload, "turn_id", "turnId"), 256),
        ("tool_name", get_value(payload, "tool_name", "toolName", "tool"), 128),
        ("tool_use_id", get_value(payload, "tool_use_id", "toolUseId", "use_id", "useId"), 256),
        ("model", get_value(payload, "model", "model_name", "modelName"), 128),
    )
    for output_name, raw, limit in fields:
        cleaned = safe_token(raw, limit)
        if cleaned is not None:
            record[output_name] = cleaned

    project_path = get_value(payload, "cwd", "project_path", "projectPath")
    if isinstance(project_path, str):
        record["project_path_hash"] = hashlib.sha256(
            project_path.encode("utf-8")
        ).hexdigest()

    tool_input = get_value(payload, "tool_input", "toolInput", "input", "arguments", "args")
    tool_output = get_value(
        payload,
        "tool_response",
        "toolResponse",
        "tool_output",
        "toolOutput",
        "tool_result",
        "toolResult",
        "last_assistant_message",
        "lastAssistantMessage",
        "output",
    )
    record["input_bytes"] = serialized_bytes(tool_input)
    record["output_bytes"] = serialized_bytes(tool_output)

    exit_code = extract_exit_code(tool_output)
    if exit_code is None:
        exit_code = extract_exit_code(payload)
    if exit_code is not None:
        record["exit_code"] = exit_code
    success = extract_success(payload, tool_output, exit_code)
    if success is not None:
        record["success"] = success

    raw_tool_name = get_value(payload, "tool_name", "toolName", "tool")
    if is_bash_tool(raw_tool_name):
        classification, subcommand, skill_name = classify_bash(
            command_from_input(tool_input)
        )
        record["classification"] = classification
        if subcommand is not None:
            record["docstar_subcommand"] = subcommand
        if skill_name is not None:
            record["skill_name"] = skill_name
    elif is_agent_tool(raw_tool_name):
        record["classification"] = "agent"
        action = agent_action(raw_tool_name)
        if action is not None:
            record["agent_action"] = action
        if action == "spawn":
            record.update(extract_semantic_ids(tool_input))
            fork_context = extract_fork_context(tool_input)
            if fork_context is not None:
                record["fork_context"] = fork_context
            fork_turns = extract_fork_turns(tool_input)
            if fork_turns is not None:
                record["fork_turns"] = fork_turns
        elif action == "wait":
            record["wait_result"] = extract_wait_result(tool_output, success)
    elif is_skill_tool(raw_tool_name):
        record["classification"] = "skill_load"
        skill_name = extract_skill_name(tool_input)
        if skill_name is not None:
            record["skill_name"] = skill_name
    else:
        record["classification"] = "other"
    return record


def output_config(arguments: list[str]) -> Optional[tuple[Path, int]]:
    output_dir = None
    retention_days = None
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--output-dir" and index + 1 < len(arguments):
            if output_dir is not None:
                return None
            output_dir = Path(arguments[index + 1]).expanduser()
            index += 2
            continue
        if argument.startswith("--output-dir="):
            if output_dir is not None:
                return None
            output_dir = Path(argument.split("=", 1)[1]).expanduser()
            index += 1
            continue
        if argument == "--retention-days" and index + 1 < len(arguments):
            if retention_days is not None:
                return None
            raw_retention = arguments[index + 1]
            index += 2
        elif argument.startswith("--retention-days="):
            if retention_days is not None:
                return None
            raw_retention = argument.split("=", 1)[1]
            index += 1
        else:
            return None
        if not raw_retention.isdigit() or int(raw_retention) < 1:
            return None
        retention_days = int(raw_retention)
    if output_dir is None or retention_days is None:
        return None
    return output_dir, retention_days


def cleanup_outputs(output_dir: Path, retention_days: int, now: datetime) -> None:
    cutoff = now.date() - timedelta(days=retention_days - 1)
    for path in output_dir.glob("hooks-*.jsonl"):
        match = HOOK_FILE.fullmatch(path.name)
        if match is None:
            continue
        try:
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if file_date < cutoff:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
    try:
        (output_dir / "hooks.jsonl").unlink()
    except FileNotFoundError:
        pass


def append_record(
    output_dir: Path,
    record: dict[str, Any],
    retention_days: int,
    now: datetime,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    output_dir.chmod(0o700)
    cleanup_outputs(output_dir, retention_days, now)
    path = output_dir / f"hooks-{now.date().isoformat()}.jsonl"
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError("output is not a regular file")
        os.fchmod(descriptor, 0o600)
        encoded = (
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        os.write(descriptor, encoded)
    finally:
        os.close(descriptor)


def main(arguments: Optional[list[str]] = None) -> int:
    try:
        configuration = output_config(
            list(arguments) if arguments is not None else sys.argv[1:]
        )
        if configuration is None:
            return 0
        output_dir, retention_days = configuration
        raw = sys.stdin.buffer.read()
        document = json.loads(raw.decode("utf-8"))
        if not isinstance(document, dict):
            return 0
        now = utc_now()
        append_record(
            output_dir,
            build_record(document, now),
            retention_days,
            now,
        )
    except BaseException:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
