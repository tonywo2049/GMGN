#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import plistlib
import shlex
import stat
import sys
import tempfile
from typing import Any, Optional


LABEL = "com.gmgn.codex-telemetry"
PLIST_NAME = f"{LABEL}.plist"
SCRIPT_NAMES = ("collector.py", "hook.py", "install.py")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4318
DEFAULT_RETENTION_DAYS = 30
DEFAULT_MAX_BODY_BYTES = 1024 * 1024
HOOK_EVENTS = (
    ("SessionStart", None),
    ("PostToolUse", "^Bash$"),
    ("PreToolUse", "^Agent$"),
    ("SubagentStart", None),
    ("SubagentStop", None),
    ("Stop", None),
)


@dataclass(frozen=True)
class Layout:
    home: Path
    codex_home: Path
    telemetry_root: Path
    bin_dir: Path
    data_dir: Path
    logs_dir: Path
    hook_output: Path
    hooks_path: Path
    launch_agents_dir: Path
    plist_path: Path


def absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def make_layout(home: Path, codex_home: Path) -> Layout:
    resolved_home = absolute_path(home)
    resolved_codex_home = absolute_path(codex_home)
    telemetry_root = resolved_codex_home / "gmgn-telemetry"
    return Layout(
        home=resolved_home,
        codex_home=resolved_codex_home,
        telemetry_root=telemetry_root,
        bin_dir=telemetry_root / "bin",
        data_dir=telemetry_root / "data",
        logs_dir=telemetry_root / "logs",
        hook_output=telemetry_root / "data" / "hooks.jsonl",
        hooks_path=resolved_codex_home / "hooks.json",
        launch_agents_dir=resolved_home / "Library" / "LaunchAgents",
        plist_path=resolved_home / "Library" / "LaunchAgents" / PLIST_NAME,
    )


def default_home() -> Path:
    configured = os.environ.get("HOME")
    return Path(configured) if configured else Path.home()


def default_codex_home(home: Path) -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured) if configured else home / ".codex"


def stable_python() -> Path:
    return Path(sys.executable).resolve()


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def endpoint_host(host: str) -> str:
    if ":" in host and not host.startswith("["):
        return f"[{host}]"
    return host


def render_codex_config(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    endpoint = f"http://{endpoint_host(host)}:{port}/v1/logs"
    exporter = (
        "exporter = { otlp-http = { "
        f"endpoint = {toml_string(endpoint)}, protocol = \"json\""
        " } }\n"
    )
    return (
        "[otel]\n"
        f"{exporter}"
        "log_user_prompt = false\n"
        'trace_exporter = "none"\n'
        'metrics_exporter = "none"\n'
    )


def render_launch_agent(
    layout: Layout,
    python_path: Path,
    host: str,
    port: int,
    retention_days: int,
    max_body_bytes: int,
) -> bytes:
    collector = layout.bin_dir / "collector.py"
    document = {
        "Label": LABEL,
        "ProgramArguments": [
            str(python_path),
            str(collector),
            "--host",
            host,
            "--port",
            str(port),
            "--data-dir",
            str(layout.data_dir),
            "--retention-days",
            str(retention_days),
            "--max-body-bytes",
            str(max_body_bytes),
        ],
        "WorkingDirectory": str(layout.telemetry_root),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ProcessType": "Background",
        "StandardOutPath": str(layout.logs_dir / "collector.stdout.log"),
        "StandardErrorPath": str(layout.logs_dir / "collector.stderr.log"),
        "Umask": 0o077,
    }
    return plistlib.dumps(document, fmt=plistlib.FMT_XML, sort_keys=True)


def ensure_directory(path: Path, mode: int) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    path.chmod(mode)


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=str(path.parent),
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        path.chmod(mode)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def copy_scripts(source_dir: Path, layout: Layout) -> None:
    ensure_directory(layout.bin_dir, 0o700)
    for name in SCRIPT_NAMES:
        source = source_dir / name
        destination = layout.bin_dir / name
        if source.resolve() == destination.resolve():
            destination.chmod(0o700)
            continue
        atomic_write(destination, source.read_bytes(), 0o700)


def load_hooks(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"hooks": {}}
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("hooks.json root must be an object")
    hooks = document.get("hooks")
    if hooks is None:
        document["hooks"] = {}
    elif not isinstance(hooks, dict):
        raise ValueError("hooks.json hooks must be an object")
    return document


def is_owned_handler(handler: Any) -> bool:
    if not isinstance(handler, dict) or handler.get("type") != "command":
        return False
    command = handler.get("command")
    if not isinstance(command, str):
        return False
    normalized = command.replace("\\", "/")
    return "/gmgn-telemetry/bin/hook.py" in normalized


def remove_owned_handlers(document: dict[str, Any]) -> int:
    hooks = document.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("hooks.json hooks must be an object")
    removed = 0
    for event, groups in list(hooks.items()):
        if not isinstance(groups, list):
            raise ValueError(f"hooks.json event {event} must be an array")
        retained_groups = []
        for group in groups:
            if not isinstance(group, dict):
                raise ValueError(f"hooks.json event {event} contains a non-object group")
            handlers = group.get("hooks")
            if not isinstance(handlers, list):
                raise ValueError(f"hooks.json event {event} group hooks must be an array")
            retained_handlers = [
                handler for handler in handlers if not is_owned_handler(handler)
            ]
            removed += len(handlers) - len(retained_handlers)
            if retained_handlers or len(retained_handlers) == len(handlers):
                retained_group = dict(group)
                retained_group["hooks"] = retained_handlers
                retained_groups.append(retained_group)
        hooks[event] = retained_groups
    return removed


def hook_command(layout: Layout, python_path: Path) -> str:
    return shlex.join(
        [
            str(python_path),
            str(layout.bin_dir / "hook.py"),
            "--output",
            str(layout.hook_output),
        ]
    )


def merge_hooks(
    document: dict[str, Any], layout: Layout, python_path: Path
) -> dict[str, Any]:
    remove_owned_handlers(document)
    hooks = document["hooks"]
    command = hook_command(layout, python_path)
    for event, matcher in HOOK_EVENTS:
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            raise ValueError(f"hooks.json event {event} must be an array")
        group: dict[str, Any] = {}
        if matcher is not None:
            group["matcher"] = matcher
        group["hooks"] = [
            {
                "type": "command",
                "command": command,
                "timeout": 5,
            }
        ]
        groups.append(group)
    return document


def hooks_bytes(document: dict[str, Any]) -> bytes:
    return (
        json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def hooks_mode(path: Path) -> int:
    if not path.exists():
        return 0o600
    return stat.S_IMODE(path.stat().st_mode)


def install(
    layout: Layout,
    source_dir: Path,
    python_path: Path,
    host: str,
    port: int,
    retention_days: int,
    max_body_bytes: int,
) -> None:
    ensure_directory(layout.codex_home, 0o700)
    ensure_directory(layout.telemetry_root, 0o700)
    ensure_directory(layout.data_dir, 0o700)
    ensure_directory(layout.logs_dir, 0o700)
    copy_scripts(source_dir, layout)

    document = merge_hooks(load_hooks(layout.hooks_path), layout, python_path)
    atomic_write(layout.hooks_path, hooks_bytes(document), hooks_mode(layout.hooks_path))

    ensure_directory(layout.launch_agents_dir, 0o755)
    plist = render_launch_agent(
        layout,
        python_path,
        host,
        port,
        retention_days,
        max_body_bytes,
    )
    atomic_write(layout.plist_path, plist, 0o644)


def uninstall(layout: Layout) -> None:
    if layout.hooks_path.exists():
        document = load_hooks(layout.hooks_path)
        removed = remove_owned_handlers(document)
        if removed:
            atomic_write(
                layout.hooks_path,
                hooks_bytes(document),
                hooks_mode(layout.hooks_path),
            )
    try:
        layout.plist_path.unlink()
    except FileNotFoundError:
        pass


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def valid_port(value: str) -> int:
    parsed = int(value)
    if not 1 <= parsed <= 65535:
        raise argparse.ArgumentTypeError("must be between 1 and 65535")
    return parsed


def parse_args(arguments: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install local GMGN Codex telemetry")
    parser.add_argument(
        "action",
        nargs="?",
        choices=("install", "uninstall"),
        default="install",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-codex-config", action="store_true")
    parser.add_argument("--home", type=Path)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=valid_port, default=DEFAULT_PORT)
    parser.add_argument(
        "--retention-days",
        type=positive_integer,
        default=DEFAULT_RETENTION_DAYS,
    )
    parser.add_argument(
        "--max-body-bytes",
        type=positive_integer,
        default=DEFAULT_MAX_BODY_BYTES,
    )
    return parser.parse_args(arguments)


def dry_run_output(layout: Layout, action: str, host: str, port: int) -> str:
    if action == "uninstall":
        return (
            f"Would remove GMGN handlers from {layout.hooks_path}\n"
            f"Would remove {layout.plist_path}\n"
        )
    copied = "\n".join(
        f"Would copy {name} to {layout.bin_dir / name}" for name in SCRIPT_NAMES
    )
    return (
        f"{copied}\n"
        f"Would merge GMGN handlers into {layout.hooks_path}\n"
        f"Would write {layout.plist_path}\n"
        f"Would create data directory {layout.data_dir}\n\n"
        f"Codex config to add manually:\n{render_codex_config(host, port)}"
    )


def main(arguments: Optional[list[str]] = None) -> int:
    options = parse_args(arguments)
    home = absolute_path(options.home) if options.home else absolute_path(default_home())
    codex_home = (
        absolute_path(options.codex_home)
        if options.codex_home
        else absolute_path(default_codex_home(home))
    )
    layout = make_layout(home, codex_home)

    if options.print_codex_config:
        sys.stdout.write(render_codex_config(options.host, options.port))
        return 0
    if options.dry_run:
        sys.stdout.write(
            dry_run_output(layout, options.action, options.host, options.port)
        )
        return 0

    try:
        if options.action == "uninstall":
            uninstall(layout)
            sys.stdout.write(f"Removed GMGN hooks and {layout.plist_path}\n")
        else:
            install(
                layout=layout,
                source_dir=Path(__file__).resolve().parent,
                python_path=stable_python(),
                host=options.host,
                port=options.port,
                retention_days=options.retention_days,
                max_body_bytes=options.max_body_bytes,
            )
            sys.stdout.write(
                f"Installed local telemetry under {layout.telemetry_root}\n"
                "Add this Codex config manually; config.toml was not changed:\n"
                f"{render_codex_config(options.host, options.port)}"
                "Codex must explicitly trust the new hooks before they run.\n"
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(f"telemetry installer failed: {error}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
