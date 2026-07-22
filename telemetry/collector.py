#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import socket
import stat
import sys
import threading
from typing import Any, Optional, cast
from urllib.parse import parse_qs, urlsplit


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4318
DEFAULT_RETENTION_DAYS = 30
DEFAULT_MAX_BODY_BYTES = 1024 * 1024
DEFAULT_MAX_WRITE_BYTES = 256 * 1024
DEFAULT_MAX_DATA_BYTES = 100 * 1024 * 1024
DEFAULT_READ_TIMEOUT_SECONDS = 5.0
DEFAULT_MAX_CONCURRENT_REQUESTS = 8
DEFAULT_DASHBOARD_SESSION_LIMIT = 500
DEFAULT_DASHBOARD_FOLLOW_WINDOW = 5
MAX_DASHBOARD_FOLLOW_WINDOW = 1000
SCHEMA_VERSION = "gmgn-otel-event-v1"
LOGS_PATH = "/v1/logs"
DATED_JSONL = re.compile(r"(?:^|\D)(\d{4}-\d{2}-\d{2})(?:\D|$)")
SAFE_METADATA = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+#~\-=]{0,255}\Z")
NONNEGATIVE_NUMBER_TEXT = re.compile(
    r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z"
)
OTEL_VALUE_KEYS = {
    "arrayValue",
    "boolValue",
    "bytesValue",
    "doubleValue",
    "intValue",
    "kvlistValue",
    "stringValue",
}
TOKEN_ATTRIBUTES = {
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
TOOL_ATTRIBUTES = {
    "tool_name",
    "call_id",
    "source",
    "duration_ms",
    "success",
    "output_length",
    "output_line_count",
    "mcp_server",
    "mcp_server_origin",
    "tool_origin",
}
REQUEST_ATTRIBUTES = {
    "duration_ms",
    "success",
    "attempt",
    "endpoint",
    "status",
    "status_code",
    "http.response.status_code",
}
STREAM_ATTRIBUTES = {"event.kind", "duration_ms"} | TOKEN_ATTRIBUTES
EVENT_ATTRIBUTES = {
    "codex.conversation_starts": set(),
    "codex.api_request": REQUEST_ATTRIBUTES,
    "codex.sse_event": STREAM_ATTRIBUTES,
    "codex.user_prompt": set(),
    "codex.tool_decision": {"tool_name", "call_id", "source"},
    "codex.tool_result": TOOL_ATTRIBUTES,
    "codex.websocket_event": STREAM_ATTRIBUTES,
    "codex.websocket_request": REQUEST_ATTRIBUTES,
}
INTEGER_ATTRIBUTES = (
    TOKEN_ATTRIBUTES
    | {
        "attempt",
        "http.response.status_code",
        "output_length",
        "output_line_count",
        "status_code",
    }
)
TEXT_ATTRIBUTES = {
    "event.kind",
    "tool_name",
    "call_id",
    "source",
    "mcp_server",
    "mcp_server_origin",
    "tool_origin",
}
BUSY_RESPONSE = (
    b"HTTP/1.1 503 Service Unavailable\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: 2\r\n"
    b"Cache-Control: no-store\r\n"
    b"Connection: close\r\n\r\n{}"
)
DASHBOARD_ASSETS = {
    "/": ("dashboard.html", "text/html; charset=utf-8"),
    "/dashboard": ("dashboard.html", "text/html; charset=utf-8"),
    "/assets/dashboard.css": ("dashboard.css", "text/css; charset=utf-8"),
    "/assets/dashboard.js": ("dashboard.js", "text/javascript; charset=utf-8"),
}
DASHBOARD_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
    "form-action 'none'; frame-ancestors 'none'"
)


class RequestValidationError(ValueError):
    pass


class WriteLimitExceeded(ValueError):
    pass


class DataQuotaExceeded(OSError):
    pass


class DashboardBusy(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def reject_json_constant(value: str) -> Any:
    raise ValueError(f"invalid JSON constant: {value}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key: {key}")
        document[key] = value
    return document


def decode_otel_value(value: Any, path: str) -> Any:
    if not isinstance(value, dict) or len(value) != 1:
        raise RequestValidationError(f"{path} must be an OTLP AnyValue object")
    value_type = next(iter(value))
    if value_type not in OTEL_VALUE_KEYS:
        raise RequestValidationError(f"{path} has an unknown OTLP AnyValue type")
    candidate = value[value_type]
    if value_type in {"stringValue", "bytesValue"}:
        if not isinstance(candidate, str):
            raise RequestValidationError(f"{path}.{value_type} must be a string")
        return candidate
    if value_type == "boolValue":
        if not isinstance(candidate, bool):
            raise RequestValidationError(f"{path}.boolValue must be a boolean")
        return candidate
    if value_type == "intValue":
        if isinstance(candidate, bool):
            raise RequestValidationError(f"{path}.intValue must be an integer")
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, str) and re.fullmatch(r"-?\d+", candidate):
            return int(candidate)
        raise RequestValidationError(f"{path}.intValue must be an integer")
    if value_type == "doubleValue":
        if (
            isinstance(candidate, bool)
            or not isinstance(candidate, (int, float))
            or not math.isfinite(candidate)
        ):
            raise RequestValidationError(f"{path}.doubleValue must be finite")
        return candidate
    if not isinstance(candidate, dict) or set(candidate) != {"values"}:
        raise RequestValidationError(f"{path}.{value_type} must contain values")
    values = candidate["values"]
    if value_type == "arrayValue":
        if not isinstance(values, list):
            raise RequestValidationError(f"{path}.arrayValue.values must be an array")
        return [
            decode_otel_value(item, f"{path}.arrayValue.values[{index}]")
            for index, item in enumerate(values)
        ]
    return decode_attributes(values, f"{path}.kvlistValue.values")


def decode_attributes(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, list):
        raise RequestValidationError(f"{path} must be an array")
    attributes = {}
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict) or set(item) != {"key", "value"}:
            raise RequestValidationError(f"{item_path} must contain key and value")
        key = item["key"]
        if not isinstance(key, str) or not key:
            raise RequestValidationError(f"{item_path}.key must be a non-empty string")
        if key in attributes:
            raise RequestValidationError(f"{path} contains duplicate key {key}")
        attributes[key] = decode_otel_value(item["value"], f"{item_path}.value")
    return attributes


def metadata_text(value: Any, field_name: str, limit: int = 256) -> str:
    if not isinstance(value, str):
        raise RequestValidationError(f"{field_name} must be a string")
    candidate = value.strip()
    if (
        not candidate
        or len(candidate) > limit
        or SAFE_METADATA.fullmatch(candidate) is None
    ):
        raise RequestValidationError(f"{field_name} is not safe metadata")
    return candidate


def nonnegative_integer(value: Any, field_name: str) -> int:
    if isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RequestValidationError(f"{field_name} must be a non-negative integer")
    return value


def nonnegative_number(value: Any, field_name: str) -> int | float:
    if isinstance(value, str) and NONNEGATIVE_NUMBER_TEXT.fullmatch(value):
        value = float(value) if any(char in value for char in ".eE") else int(value)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        raise RequestValidationError(f"{field_name} must be a non-negative number")
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def event_timestamp(value: Any, record: dict[str, Any]) -> str:
    if value is None:
        raw_nanos = record.get("timeUnixNano")
        if isinstance(raw_nanos, str) and raw_nanos.isdigit():
            raw_nanos = int(raw_nanos)
        if isinstance(raw_nanos, bool) or not isinstance(raw_nanos, int) or raw_nanos < 0:
            raise RequestValidationError("event.timestamp is required")
        try:
            return isoformat_utc(
                datetime.fromtimestamp(raw_nanos / 1_000_000_000, tz=timezone.utc)
            )
        except (OSError, OverflowError, ValueError) as error:
            raise RequestValidationError("timeUnixNano is invalid") from error
    if not isinstance(value, str):
        raise RequestValidationError("event.timestamp must be an RFC3339 string")
    candidate = value.strip()
    if not candidate or len(candidate) > 128:
        raise RequestValidationError("event.timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError as error:
        raise RequestValidationError("event.timestamp is invalid") from error
    if parsed.tzinfo is None:
        raise RequestValidationError("event.timestamp must include a timezone")
    return isoformat_utc(parsed)


def safe_endpoint(value: Any) -> str:
    if not isinstance(value, str):
        raise RequestValidationError("endpoint must be a string")
    candidate = value.strip()
    if not candidate or len(candidate) > 512 or any(ord(char) < 32 for char in candidate):
        raise RequestValidationError("endpoint is invalid")
    parsed = urlsplit(candidate)
    if parsed.scheme:
        if (
            parsed.scheme.casefold() not in {"http", "https"}
            or parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise RequestValidationError("endpoint is invalid")
        try:
            parsed.port
        except ValueError as error:
            raise RequestValidationError("endpoint is invalid") from error
        endpoint_path = parsed.path or "/"
        if len(endpoint_path) > 512 or any(ord(char) < 32 for char in endpoint_path):
            raise RequestValidationError("endpoint is invalid")
        return endpoint_path
    if "?" in candidate or "#" in candidate or SAFE_METADATA.fullmatch(candidate) is None:
        raise RequestValidationError("endpoint is invalid")
    return candidate


def normalize_event_attribute(field_name: str, value: Any) -> Any:
    if field_name in INTEGER_ATTRIBUTES:
        return nonnegative_integer(value, field_name)
    if field_name == "duration_ms":
        return nonnegative_number(value, field_name)
    if field_name == "success":
        if isinstance(value, str) and value.casefold() in {"true", "false"}:
            value = value.casefold() == "true"
        if not isinstance(value, bool):
            raise RequestValidationError("success must be a boolean")
        return value
    if field_name == "endpoint":
        return safe_endpoint(value)
    if field_name == "status":
        if isinstance(value, int) and not isinstance(value, bool):
            return nonnegative_integer(value, field_name)
        return metadata_text(value, field_name, 64)
    if field_name in TEXT_ATTRIBUTES:
        return metadata_text(value, field_name)
    raise RequestValidationError(f"unsupported event attribute {field_name}")


def normalize_log_record(
    resource_attributes: dict[str, Any],
    record: dict[str, Any],
    record_path: str,
    received_at: str,
) -> Optional[dict[str, Any]]:
    if "attributes" not in record:
        raise RequestValidationError(f"{record_path}.attributes is required")
    record_attributes = decode_attributes(
        record["attributes"], f"{record_path}.attributes"
    )
    merged_attributes = dict(resource_attributes)
    merged_attributes.update(record_attributes)

    event_name = merged_attributes.get("event.name")
    if event_name is None:
        return None
    if not isinstance(event_name, str):
        raise RequestValidationError("event.name must be a string")
    if event_name not in EVENT_ATTRIBUTES:
        return None
    if "conversation.id" not in merged_attributes or "model" not in merged_attributes:
        return None
    conversation_id = metadata_text(
        merged_attributes.get("conversation.id"), "conversation.id"
    )
    model = metadata_text(merged_attributes.get("model"), "model", 128)
    timestamp = event_timestamp(merged_attributes.get("event.timestamp"), record)

    attributes = {}
    for field_name in sorted(EVENT_ATTRIBUTES[event_name]):
        if field_name in merged_attributes:
            attributes[field_name] = normalize_event_attribute(
                field_name, merged_attributes[field_name]
            )

    normalized = {
        "schema_version": SCHEMA_VERSION,
        "received_at": received_at,
        "event_name": event_name,
        "conversation_id": conversation_id,
        "timestamp": timestamp,
        "model": model,
        "attributes": attributes,
    }
    return normalized


def normalize_logs(document: Any, received_at: datetime) -> list[dict[str, Any]]:
    if not isinstance(document, dict) or set(document) != {"resourceLogs"}:
        raise RequestValidationError("request root must contain only resourceLogs")
    resource_logs = document["resourceLogs"]
    if not isinstance(resource_logs, list):
        raise RequestValidationError("resourceLogs must be an array")

    normalized = []
    received_timestamp = isoformat_utc(received_at)
    for resource_index, resource_log in enumerate(resource_logs):
        resource_path = f"resourceLogs[{resource_index}]"
        if not isinstance(resource_log, dict):
            raise RequestValidationError(f"{resource_path} must be an object")
        resource_attributes = {}
        if "resource" in resource_log:
            resource = resource_log["resource"]
            if not isinstance(resource, dict):
                raise RequestValidationError(f"{resource_path}.resource must be an object")
            if "attributes" in resource:
                resource_attributes = decode_attributes(
                    resource["attributes"], f"{resource_path}.resource.attributes"
                )
        scope_logs = resource_log.get("scopeLogs")
        if not isinstance(scope_logs, list):
            raise RequestValidationError(f"{resource_path}.scopeLogs must be an array")
        for scope_index, scope_log in enumerate(scope_logs):
            scope_path = f"{resource_path}.scopeLogs[{scope_index}]"
            if not isinstance(scope_log, dict):
                raise RequestValidationError(f"{scope_path} must be an object")
            log_records = scope_log.get("logRecords")
            if not isinstance(log_records, list):
                raise RequestValidationError(f"{scope_path}.logRecords must be an array")
            for record_index, record in enumerate(log_records):
                record_path = f"{scope_path}.logRecords[{record_index}]"
                if not isinstance(record, dict):
                    raise RequestValidationError(f"{record_path} must be an object")
                normalized_record = normalize_log_record(
                    resource_attributes,
                    record,
                    record_path,
                    received_timestamp,
                )
                if normalized_record is not None:
                    normalized.append(normalized_record)
    return normalized


def ensure_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


class JsonlStore:
    def __init__(
        self,
        data_dir: Path,
        retention_days: int,
        max_write_bytes: int,
        max_data_bytes: int,
    ) -> None:
        if retention_days < 1:
            raise ValueError("retention_days must be positive")
        if max_write_bytes < 1:
            raise ValueError("max_write_bytes must be positive")
        if max_data_bytes < 1:
            raise ValueError("max_data_bytes must be positive")
        self.data_dir = Path(data_dir).expanduser()
        self.retention_days = retention_days
        self.max_write_bytes = max_write_bytes
        self.max_data_bytes = max_data_bytes
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

    def directory_size(self) -> int:
        total = 0
        for path in self.data_dir.iterdir():
            try:
                metadata = path.stat(follow_symlinks=False)
            except FileNotFoundError:
                continue
            if stat.S_ISREG(metadata.st_mode):
                total += metadata.st_size
        return total

    def append(self, records: list[dict[str, Any]], received_at: datetime) -> None:
        if not records:
            return
        encoded = b"".join(
            (
                json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            for record in records
        )
        if len(encoded) > self.max_write_bytes:
            raise WriteLimitExceeded("normalized write exceeds max_write_bytes")
        path = self.data_dir / f"{received_at.date().isoformat()}.jsonl"
        with self.lock:
            self.cleanup(received_at)
            if self.directory_size() + len(encoded) > self.max_data_bytes:
                raise DataQuotaExceeded("data directory quota exceeded")
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(path, flags, 0o600)
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise OSError("output is not a regular file")
                os.fchmod(descriptor, 0o600)
                offset = 0
                while offset < len(encoded):
                    written = os.write(descriptor, encoded[offset:])
                    if written < 1:
                        raise OSError("short telemetry write")
                    offset += written
            finally:
                os.close(descriptor)


def is_loopback_host(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def is_loopback_request_host(value: Optional[str]) -> bool:
    if not value:
        return False
    try:
        hostname = urlsplit("//" + value).hostname
    except ValueError:
        return False
    return hostname is not None and is_loopback_host(hostname)


class DashboardService:
    def __init__(
        self,
        codex_home: Path,
        asset_dir: Path,
        report_path: Path,
        enabled: bool,
    ) -> None:
        self.codex_home = Path(codex_home).expanduser()
        self.asset_dir = Path(asset_dir)
        self.report_path = Path(report_path)
        self.enabled = enabled
        self.asset_cache: dict[str, bytes] = {}
        self.asset_lock = threading.Lock()
        self.report_lock = threading.Lock()
        self.module_lock = threading.Lock()
        self.report_module: Any = None

    def asset(self, path: str) -> Optional[tuple[bytes, str]]:
        if not self.enabled or path not in DASHBOARD_ASSETS:
            return None
        filename, content_type = DASHBOARD_ASSETS[path]
        with self.asset_lock:
            body = self.asset_cache.get(filename)
            if body is None:
                try:
                    body = (self.asset_dir / filename).read_bytes()
                except OSError:
                    return None
                self.asset_cache[filename] = body
        return body, content_type

    def _module(self) -> Any:
        with self.module_lock:
            if self.report_module is not None:
                return self.report_module
            module_name = "_gmgn_dashboard_report_{0}".format(
                abs(hash(str(self.report_path.resolve())))
            )
            specification = importlib.util.spec_from_file_location(
                module_name,
                self.report_path,
            )
            if specification is None or specification.loader is None:
                raise RuntimeError("dashboard report module unavailable")
            module = importlib.util.module_from_spec(specification)
            sys.modules[module_name] = module
            try:
                specification.loader.exec_module(module)
            except BaseException:
                sys.modules.pop(module_name, None)
                raise
            self.report_module = module
            return module

    def sessions(self) -> dict[str, Any]:
        document = self._module().list_observed_sessions(codex_home=self.codex_home)
        sessions = document.get("sessions", [])
        document["total_sessions"] = len(sessions)
        document["sessions"] = sessions[:DEFAULT_DASHBOARD_SESSION_LIMIT]
        return document

    def report(
        self,
        session_id: str,
        include_descendants: bool,
        follow_window: int,
    ) -> dict[str, Any]:
        if not self.report_lock.acquire(blocking=False):
            raise DashboardBusy("dashboard report already running")
        try:
            return self._module().build_dashboard_report(
                session_id,
                codex_home=self.codex_home,
                include_descendants=include_descendants,
                follow_window=follow_window,
            )
        finally:
            self.report_lock.release()


class CollectorServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        store: JsonlStore,
        max_body_bytes: int,
        read_timeout_seconds: float,
        max_concurrent_requests: int,
        dashboard: DashboardService,
    ) -> None:
        self.store = store
        self.max_body_bytes = max_body_bytes
        self.read_timeout_seconds = read_timeout_seconds
        self.request_slots = threading.BoundedSemaphore(max_concurrent_requests)
        self.dashboard = dashboard
        super().__init__(server_address, CollectorHandler)

    def process_request(self, request: Any, client_address: Any) -> None:
        if not self.request_slots.acquire(blocking=False):
            try:
                request.sendall(BUSY_RESPONSE)
            except OSError:
                pass
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.request_slots.release()
            raise

    def process_request_thread(self, request: Any, client_address: Any) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.request_slots.release()


class CollectorHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    @property
    def collector(self) -> CollectorServer:
        return cast(CollectorServer, self.server)

    def setup(self) -> None:
        self.request.settimeout(self.collector.read_timeout_seconds)
        super().setup()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_body(self, status_code: int, body: bytes, content_type: str) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", DASHBOARD_CSP)
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status_code: int, document: Any = None) -> None:
        body = json.dumps(
            {} if document is None else document,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_body(status_code, body, "application/json")

    def dashboard_report(self, query: str) -> None:
        try:
            parameters = parse_qs(
                query,
                keep_blank_values=True,
                strict_parsing=True,
                max_num_fields=8,
            )
        except ValueError:
            self.send_json(400)
            return
        if set(parameters) - {"session_id", "descendants", "follow_window"}:
            self.send_json(400)
            return
        session_values = parameters.get("session_id", [])
        if len(session_values) != 1:
            self.send_json(400)
            return
        descendant_values = parameters.get("descendants", ["true"])
        if len(descendant_values) != 1 or descendant_values[0] not in {"true", "false"}:
            self.send_json(400)
            return
        follow_values = parameters.get(
            "follow_window",
            [str(DEFAULT_DASHBOARD_FOLLOW_WINDOW)],
        )
        maximum_follow_digits = len(str(MAX_DASHBOARD_FOLLOW_WINDOW))
        if (
            len(follow_values) != 1
            or re.fullmatch(
                rf"[0-9]{{1,{maximum_follow_digits}}}",
                follow_values[0],
            )
            is None
        ):
            self.send_json(400)
            return
        follow_window = int(follow_values[0])
        if follow_window > MAX_DASHBOARD_FOLLOW_WINDOW:
            self.send_json(400)
            return
        try:
            document = self.collector.dashboard.report(
                session_values[0],
                descendant_values[0] == "true",
                follow_window,
            )
        except DashboardBusy:
            self.send_json(503)
            return
        except ValueError:
            self.send_json(400)
            return
        except (OSError, RuntimeError, TypeError):
            self.send_json(500)
            return
        self.send_json(200, document)

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/healthz":
            self.send_json(200)
            return
        if (
            not self.collector.dashboard.enabled
            or not is_loopback_request_host(self.headers.get("Host"))
        ):
            self.send_json(404)
            return
        if path == "/api/sessions":
            if parsed.query:
                self.send_json(400)
                return
            try:
                self.send_json(200, self.collector.dashboard.sessions())
            except (OSError, RuntimeError, TypeError):
                self.send_json(500)
            return
        if path == "/api/report":
            self.dashboard_report(parsed.query)
            return
        asset = self.collector.dashboard.asset(path)
        if asset is not None:
            body, content_type = asset
            self.send_body(200, body, content_type)
            return
        self.send_json(404)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path != LOGS_PATH:
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

        try:
            raw_body = self.rfile.read(content_length)
        except socket.timeout:
            self.close_connection = True
            self.send_json(408)
            return
        except OSError:
            self.close_connection = True
            return
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
            received_at = utc_now()
            records = normalize_logs(document, received_at)
            self.collector.store.append(records, received_at)
        except WriteLimitExceeded:
            self.send_json(413)
            return
        except DataQuotaExceeded:
            self.send_json(507)
            return
        except (UnicodeDecodeError, RequestValidationError, ValueError, RecursionError):
            self.send_json(400)
            return
        except (OSError, TypeError):
            self.send_json(500)
            return
        self.send_json(200)


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    data_dir: Path = Path("."),
    retention_days: int = DEFAULT_RETENTION_DAYS,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    max_write_bytes: int = DEFAULT_MAX_WRITE_BYTES,
    max_data_bytes: int = DEFAULT_MAX_DATA_BYTES,
    read_timeout_seconds: float = DEFAULT_READ_TIMEOUT_SECONDS,
    max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
    codex_home: Optional[Path] = None,
    dashboard_dir: Optional[Path] = None,
    report_path: Optional[Path] = None,
) -> CollectorServer:
    if not 0 <= port <= 65535:
        raise ValueError("port out of range")
    if max_body_bytes < 1:
        raise ValueError("max_body_bytes must be positive")
    if read_timeout_seconds <= 0 or not math.isfinite(read_timeout_seconds):
        raise ValueError("read_timeout_seconds must be positive")
    if max_concurrent_requests < 1:
        raise ValueError("max_concurrent_requests must be positive")
    store = JsonlStore(
        Path(data_dir),
        retention_days,
        max_write_bytes,
        max_data_bytes,
    )
    resolved_codex_home = (
        Path(codex_home).expanduser()
        if codex_home is not None
        else default_codex_home()
    )
    runtime_dir = Path(__file__).resolve().parent
    dashboard = DashboardService(
        codex_home=resolved_codex_home,
        asset_dir=Path(dashboard_dir) if dashboard_dir is not None else runtime_dir,
        report_path=Path(report_path) if report_path is not None else runtime_dir / "report.py",
        enabled=is_loopback_host(host),
    )
    return CollectorServer(
        (host, port),
        store,
        max_body_bytes,
        read_timeout_seconds,
        max_concurrent_requests,
        dashboard,
    )


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0 or not math.isfinite(parsed):
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def valid_port(value: str) -> int:
    parsed = int(value)
    if not 0 <= parsed <= 65535:
        raise argparse.ArgumentTypeError("must be between 0 and 65535")
    return parsed


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def default_data_dir() -> Path:
    return default_codex_home() / "gmgn-telemetry" / "data"


def parse_args(arguments: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local allowlisted Codex OTLP collector")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=valid_port, default=DEFAULT_PORT)
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
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
    parser.add_argument(
        "--max-write-bytes",
        type=positive_integer,
        default=DEFAULT_MAX_WRITE_BYTES,
    )
    parser.add_argument(
        "--max-data-bytes",
        type=positive_integer,
        default=DEFAULT_MAX_DATA_BYTES,
    )
    parser.add_argument(
        "--read-timeout-seconds",
        type=positive_float,
        default=DEFAULT_READ_TIMEOUT_SECONDS,
    )
    parser.add_argument(
        "--max-concurrent-requests",
        type=positive_integer,
        default=DEFAULT_MAX_CONCURRENT_REQUESTS,
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
        max_write_bytes=options.max_write_bytes,
        max_data_bytes=options.max_data_bytes,
        read_timeout_seconds=options.read_timeout_seconds,
        max_concurrent_requests=options.max_concurrent_requests,
        codex_home=options.codex_home,
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
