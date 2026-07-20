#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
from typing import Any, Optional, cast
from urllib.parse import urlsplit


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4318
DEFAULT_RETENTION_DAYS = 30
DEFAULT_MAX_BODY_BYTES = 1024 * 1024
ENVELOPE_VERSION = "gmgn-otel-envelope-v1"
SIGNALS = {
    "/v1/logs": ("logs", "resourceLogs"),
    "/v1/traces": ("traces", "resourceSpans"),
    "/v1/metrics": ("metrics", "resourceMetrics"),
}
SIGNAL_ROOTS = {root for _, root in SIGNALS.values()}
DATED_JSONL = re.compile(r"(?:^|\D)(\d{4}-\d{2}-\d{2})(?:\D|$)")
SENSITIVE_TERMS = {
    "argument",
    "arguments",
    "body",
    "command",
    "completion",
    "completions",
    "content",
    "contents",
    "instruction",
    "instructions",
    "message",
    "messages",
    "prompt",
    "prompts",
    "text",
}
SENSITIVE_COMPOUNDS = {
    "assistant_message",
    "input_message",
    "input_messages",
    "last_assistant_message",
    "output_message",
    "output_messages",
    "system_instruction",
    "system_instructions",
    "tool_argument",
    "tool_arguments",
}
GENERIC_CONTENT_TERMS = {"error", "input", "output", "request", "response", "result"}
CRITICAL_METADATA_TERMS = {
    "bytes",
    "code",
    "count",
    "duration",
    "id",
    "ids",
    "latency",
    "length",
    "status",
    "success",
    "timestamp",
    "token",
    "tokens",
}
DESCRIPTIVE_METADATA_TERMS = {"model", "name", "type", "version"}
OTEL_VALUE_KEYS = {
    "arrayValue",
    "bytesValue",
    "doubleValue",
    "intValue",
    "kvlistValue",
    "stringValue",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def normalized_terms(name: str) -> list[str]:
    separated = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return [term for term in re.split(r"[^A-Za-z0-9]+", separated.casefold()) if term]


def has_critical_metadata(name: str) -> bool:
    terms = normalized_terms(name)
    if not terms:
        return False
    if any(term in CRITICAL_METADATA_TERMS for term in terms):
        return True
    return any(term.endswith("id") and len(term) > 2 for term in terms)


def is_metadata_name(name: str) -> bool:
    terms = normalized_terms(name)
    if not terms:
        return False
    if has_critical_metadata(name) or "model" in terms:
        return True
    if any(term in SENSITIVE_TERMS or term in GENERIC_CONTENT_TERMS for term in terms):
        return False
    return any(term in DESCRIPTIVE_METADATA_TERMS for term in terms)


def is_sensitive_name(name: str) -> bool:
    if is_metadata_name(name):
        return False
    terms = normalized_terms(name)
    compound = "_".join(terms)
    if compound in SENSITIVE_COMPOUNDS:
        return True
    return any(term in SENSITIVE_TERMS for term in terms)


def is_generic_content_name(name: str) -> bool:
    if is_metadata_name(name):
        return False
    return any(term in GENERIC_CONTENT_TERMS for term in normalized_terms(name))


def compact_json(value: Any) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def reject_json_constant(value: str) -> Any:
    raise ValueError(f"invalid JSON constant: {value}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key: {key}")
        document[key] = value
    return document


def redaction_source(value: Any) -> Any:
    if isinstance(value, dict) and len(value) == 1:
        key = next(iter(value))
        if key in OTEL_VALUE_KEYS:
            return value[key]
    return value


def is_otel_value(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and len(value) == 1
        and next(iter(value)) in OTEL_VALUE_KEYS
    )


def redact(value: Any) -> dict[str, Any]:
    encoded = compact_json(redaction_source(value))
    return {
        "length": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "redacted": True,
    }


def sanitize_content(value: Any) -> Any:
    if is_otel_value(value) or not isinstance(value, (dict, list)):
        return redact(value)
    if isinstance(value, list):
        return [sanitize_content(item) for item in value]
    sanitized = {}
    for key, child in value.items():
        if isinstance(key, str) and (
            has_critical_metadata(key) or "model" in normalized_terms(key)
        ):
            sanitized[key] = sanitize(child, key)
        else:
            sanitized[key] = sanitize_content(child)
    return sanitized


def sanitize(value: Any, field_name: Optional[str] = None) -> Any:
    content_field = field_name is not None and (
        is_sensitive_name(field_name) or is_generic_content_name(field_name)
    )
    if content_field:
        return sanitize_content(value)
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if not isinstance(value, dict):
        return value

    attribute_name = value.get("key")
    sensitive_attribute = isinstance(attribute_name, str) and (
        is_sensitive_name(attribute_name) or is_generic_content_name(attribute_name)
    )
    sanitized = {}
    for key, child in value.items():
        if sensitive_attribute and key == "value":
            sanitized[key] = redact(child)
        else:
            sanitized[key] = sanitize(child, key)
    return sanitized


def ensure_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


class JsonlStore:
    def __init__(self, data_dir: Path, retention_days: int) -> None:
        if retention_days < 1:
            raise ValueError("retention_days must be positive")
        self.data_dir = Path(data_dir).expanduser()
        self.retention_days = retention_days
        self.lock = threading.RLock()
        ensure_private_directory(self.data_dir)
        self.cleanup()

    def cleanup(self, now: Optional[datetime] = None) -> None:
        current = now or utc_now()
        cutoff = current.date() - timedelta(days=self.retention_days - 1)
        with self.lock:
            ensure_private_directory(self.data_dir)
            for path in self.data_dir.glob("*.jsonl"):
                match = DATED_JSONL.search(path.name)
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

    def append(self, signal: str, content_type: str, body: Any) -> None:
        received_at = utc_now()
        envelope = {
            "schema_version": ENVELOPE_VERSION,
            "received_at": isoformat_utc(received_at),
            "signal": signal,
            "content_type": content_type,
            "body": body,
        }
        encoded = (
            json.dumps(envelope, ensure_ascii=False, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        path = self.data_dir / f"{received_at.date().isoformat()}.jsonl"
        with self.lock:
            self.cleanup(received_at)
            descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                0o600,
            )
            try:
                os.fchmod(descriptor, 0o600)
                os.write(descriptor, encoded)
            finally:
                os.close(descriptor)


class CollectorServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        store: JsonlStore,
        max_body_bytes: int,
    ) -> None:
        self.store = store
        self.max_body_bytes = max_body_bytes
        super().__init__(server_address, CollectorHandler)


class CollectorHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    @property
    def collector(self) -> CollectorServer:
        return cast(CollectorServer, self.server)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, status: int) -> None:
        body = b"{}"
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/healthz":
            self.send_json(200)
        else:
            self.send_json(404)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        signal_spec = SIGNALS.get(path)
        if signal_spec is None:
            self.close_connection = True
            self.send_json(404)
            return

        media_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        if media_type.casefold() != "application/json":
            self.close_connection = True
            self.send_json(415)
            return

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self.close_connection = True
            self.send_json(411)
            return
        try:
            content_length = int(raw_length, 10)
        except ValueError:
            self.close_connection = True
            self.send_json(400)
            return
        if content_length < 0:
            self.close_connection = True
            self.send_json(400)
            return
        if content_length > self.collector.max_body_bytes:
            self.close_connection = True
            self.send_json(413)
            return

        raw_body = self.rfile.read(content_length)
        if len(raw_body) != content_length:
            self.close_connection = True
            self.send_json(400)
            return
        try:
            document = json.loads(
                raw_body.decode("utf-8"),
                object_pairs_hook=unique_object,
                parse_constant=reject_json_constant,
            )
        except (UnicodeDecodeError, ValueError, RecursionError):
            self.send_json(400)
            return

        signal, expected_root = signal_spec
        if not isinstance(document, dict):
            self.send_json(400)
            return
        roots = SIGNAL_ROOTS.intersection(document)
        if roots != {expected_root} or set(document) != {expected_root}:
            self.send_json(400)
            return
        if not isinstance(document[expected_root], list):
            self.send_json(400)
            return

        try:
            sanitized = sanitize(document)
            self.collector.store.append(signal, "application/json", sanitized)
        except (OSError, TypeError, ValueError, RecursionError):
            self.send_json(500)
            return
        self.send_json(200)


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    data_dir: Path = Path("."),
    retention_days: int = DEFAULT_RETENTION_DAYS,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
) -> CollectorServer:
    if not 0 <= port <= 65535:
        raise ValueError("port out of range")
    if max_body_bytes < 1:
        raise ValueError("max_body_bytes must be positive")
    store = JsonlStore(Path(data_dir), retention_days)
    return CollectorServer((host, port), store, max_body_bytes)


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def valid_port(value: str) -> int:
    parsed = int(value)
    if not 0 <= parsed <= 65535:
        raise argparse.ArgumentTypeError("must be between 0 and 65535")
    return parsed


def default_data_dir() -> Path:
    configured = os.environ.get("CODEX_HOME")
    codex_home = Path(configured).expanduser() if configured else Path.home() / ".codex"
    return codex_home / "gmgn-telemetry" / "data"


def parse_args(arguments: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local JSON-only OTLP collector")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=valid_port, default=DEFAULT_PORT)
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
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


def main(arguments: Optional[list[str]] = None) -> int:
    options = parse_args(arguments)
    server = create_server(
        host=options.host,
        port=options.port,
        data_dir=options.data_dir,
        retention_days=options.retention_days,
        max_body_bytes=options.max_body_bytes,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
