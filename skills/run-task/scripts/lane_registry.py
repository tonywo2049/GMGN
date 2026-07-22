#!/usr/bin/env python3
"""Atomically coordinate GMGN writer lanes across sessions and worktrees."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


REGISTRY_REF = "refs/gmgn/lane-registry"
SCHEMA_VERSION = 1
MAX_CAS_ATTEMPTS = 32


class RegistryError(Exception):
    """A stable, user-actionable registry failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_git(
    project_root: Path,
    arguments: list[str],
    *,
    input_bytes: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-C", str(project_root), *arguments],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RegistryError("git_error", detail or f"git {' '.join(arguments)} failed")
    return result


def canonical_directory(raw_path: str, label: str) -> Path:
    try:
        path = Path(raw_path).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RegistryError("invalid_path", f"{label} cannot be resolved: {exc}") from exc
    if not path.is_dir():
        raise RegistryError("invalid_path", f"{label} is not a directory: {path}")
    return path


def require_value(value: str | None, label: str) -> str:
    if value is None or not value.strip():
        raise RegistryError("invalid_argument", f"{label} must be non-empty")
    return value.strip()


def authority_context(raw_project_root: str) -> tuple[Path, str]:
    project_root = canonical_directory(raw_project_root, "project_root")
    common_raw = (
        run_git(project_root, ["rev-parse", "--git-common-dir"])
        .stdout.decode()
        .strip()
    )
    common_dir = Path(common_raw)
    if not common_dir.is_absolute():
        common_dir = project_root / common_dir
    common_dir = common_dir.resolve(strict=True)
    scope_material = f"git-common-dir:{common_dir}".encode("utf-8")
    project_scope_id = hashlib.sha256(scope_material).hexdigest()
    return project_root, project_scope_id


def resolve_git_directory(worktree_path: Path, option: str) -> Path:
    raw_path = run_git(worktree_path, ["rev-parse", option]).stdout.decode().strip()
    directory = Path(raw_path)
    if not directory.is_absolute():
        directory = worktree_path / directory
    try:
        directory = directory.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RegistryError(
            "repository_identity_unavailable",
            f"{option} cannot be resolved: {exc}",
        ) from exc
    if not directory.is_dir():
        raise RegistryError(
            "repository_identity_unavailable",
            f"{option} is not a directory: {directory}",
        )
    return directory


def directory_identity(directory: Path) -> dict[str, Any]:
    try:
        metadata = directory.stat()
    except OSError as exc:
        raise RegistryError(
            "repository_identity_unavailable",
            f"cannot stat Git metadata directory {directory}: {exc}",
        ) from exc
    return {
        "path": str(directory),
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
    }


def resolve_baseline(worktree_path: Path, baseline_anchor: str) -> str:
    result = run_git(
        worktree_path,
        ["rev-parse", "--verify", f"{baseline_anchor}^{{commit}}"],
        check=False,
    )
    if result.returncode != 0:
        raise RegistryError(
            "baseline_missing",
            f"baseline_anchor no longer exists in the assigned repository: {baseline_anchor}",
        )
    return result.stdout.decode().strip()


def inspect_worktree_repository(
    worktree_path: Path,
    baseline_anchor: str,
    *,
    require_baseline_head: bool,
) -> tuple[str, dict[str, Any]]:
    root = run_git(worktree_path, ["rev-parse", "--show-toplevel"]).stdout.decode().strip()
    if Path(root).resolve(strict=True) != worktree_path:
        raise RegistryError(
            "worktree_root_mismatch",
            f"worktree_path is not the Git root: {worktree_path}",
        )
    baseline_commit = resolve_baseline(worktree_path, baseline_anchor)
    if require_baseline_head:
        head = run_git(worktree_path, ["rev-parse", "HEAD"]).stdout.decode().strip()
    else:
        head = baseline_commit
    if head != baseline_commit:
        raise RegistryError(
            "baseline_mismatch",
            f"HEAD {head} does not equal baseline_anchor {baseline_commit}",
        )
    common_dir = resolve_git_directory(worktree_path, "--git-common-dir")
    git_dir = resolve_git_directory(worktree_path, "--git-dir")
    object_format = (
        run_git(worktree_path, ["rev-parse", "--show-object-format"])
        .stdout.decode()
        .strip()
    )
    repository_identity = {
        "git_common_dir": directory_identity(common_dir),
        "git_dir": directory_identity(git_dir),
        "object_format": object_format,
    }
    return baseline_commit, repository_identity


def resolve_candidate(worktree_path: Path, candidate_anchor: str) -> str:
    return run_git(
        worktree_path,
        ["rev-parse", "--verify", f"{candidate_anchor}^{{commit}}"],
    ).stdout.decode().strip()


def require_head_anchor(worktree_path: Path, expected_anchor: str) -> str:
    expected = resolve_candidate(worktree_path, expected_anchor)
    head = run_git(worktree_path, ["rev-parse", "HEAD"]).stdout.decode().strip()
    if head != expected:
        raise RegistryError(
            "candidate_mismatch",
            f"HEAD {head} does not equal candidate_anchor {expected}",
        )
    return expected


def empty_registry(project_scope_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project_scope_id": project_scope_id,
        "registry_revision": 0,
        "updated_at": None,
        "lanes": {},
    }


def read_ref(project_root: Path) -> str | None:
    result = run_git(
        project_root,
        ["rev-parse", "--verify", "--quiet", REGISTRY_REF],
        check=False,
    )
    if result.returncode == 1:
        return None
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RegistryError("git_error", detail or f"cannot read {REGISTRY_REF}")
    return result.stdout.decode().strip()


def read_registry(
    project_root: Path, project_scope_id: str
) -> tuple[str | None, dict[str, Any]]:
    object_id = read_ref(project_root)
    if object_id is None:
        return None, empty_registry(project_scope_id)
    payload = run_git(project_root, ["cat-file", "blob", object_id]).stdout
    try:
        registry = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegistryError("registry_corrupt", f"registry JSON is invalid: {exc}") from exc
    if not isinstance(registry, dict) or not isinstance(registry.get("lanes"), dict):
        raise RegistryError("registry_corrupt", "registry root or lanes map is invalid")
    if registry.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError("schema_mismatch", "registry schema_version is unsupported")
    if registry.get("project_scope_id") != project_scope_id:
        raise RegistryError(
            "scope_mismatch",
            "registry project_scope_id does not match this authority",
        )
    return object_id, registry


def write_blob(project_root: Path, registry: dict[str, Any]) -> str:
    payload = (
        json.dumps(registry, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")
    return (
        run_git(project_root, ["hash-object", "-w", "--stdin"], input_bytes=payload)
        .stdout.decode()
        .strip()
    )


def zero_object_id(project_root: Path) -> str:
    result = run_git(project_root, ["rev-parse", "--show-object-format"], check=False)
    object_format = result.stdout.decode().strip() if result.returncode == 0 else "sha1"
    return "0" * (64 if object_format == "sha256" else 40)


def compare_and_swap_ref(
    project_root: Path, new_object_id: str, expected_object_id: str | None
) -> bool:
    expected = expected_object_id or zero_object_id(project_root)
    result = run_git(
        project_root,
        ["update-ref", REGISTRY_REF, new_object_id, expected],
        check=False,
    )
    if result.returncode == 0:
        return True
    if read_ref(project_root) != expected_object_id:
        return False
    detail = result.stderr.decode("utf-8", errors="replace").strip()
    raise RegistryError("git_error", detail or f"cannot update {REGISTRY_REF}")


Mutation = Callable[[dict[str, Any]], dict[str, Any]]


def atomic_mutation(
    project_root: Path,
    project_scope_id: str,
    operation: str,
    mutate: Mutation,
) -> dict[str, Any]:
    for _ in range(MAX_CAS_ATTEMPTS):
        expected_object_id, current = read_registry(project_root, project_scope_id)
        updated = deepcopy(current)
        result = mutate(updated)
        updated["registry_revision"] = int(current.get("registry_revision", 0)) + 1
        updated["updated_at"] = utc_now()
        new_object_id = write_blob(project_root, updated)
        if compare_and_swap_ref(project_root, new_object_id, expected_object_id):
            return {
                "ok": True,
                "operation": operation,
                "project_scope_id": project_scope_id,
                "registry_revision": updated["registry_revision"],
                "registry_object_id": new_object_id,
                **result,
            }
    raise RegistryError("cas_exhausted", "registry changed too often; retry the operation")


def assert_common_identity(
    lane: dict[str, Any], args: argparse.Namespace, *, require_baseline_head: bool = False
) -> Path:
    if not lane.get("active"):
        raise RegistryError(
            "lane_inactive",
            "lane is released and cannot accept this operation",
        )
    worktree_path = canonical_directory(args.worktree_path, "worktree_path")
    expected = {
        "owner_thread_id": require_value(args.owner_thread_id, "owner_thread_id"),
        "owner_run_id": require_value(args.owner_run_id, "owner_run_id"),
        "ownership_epoch": args.ownership_epoch,
        "worktree_path": str(worktree_path),
    }
    mismatches = {
        key: {"expected": value, "actual": lane.get(key)}
        for key, value in expected.items()
        if lane.get(key) != value
    }
    if mismatches:
        raise RegistryError(
            "ownership_mismatch",
            "lane owner, epoch, or worktree does not match the active claim: "
            + json.dumps(mismatches, sort_keys=True),
        )
    baseline_commit, repository_identity = inspect_worktree_repository(
        worktree_path,
        require_value(lane.get("baseline_anchor"), "registered baseline_anchor"),
        require_baseline_head=require_baseline_head,
    )
    if baseline_commit != lane.get("baseline_anchor"):
        raise RegistryError(
            "baseline_identity_mismatch",
            "registered baseline_anchor resolves to a different commit",
        )
    if repository_identity != lane.get("repository_identity"):
        raise RegistryError(
            "repository_identity_mismatch",
            "assigned worktree now resolves to different Git metadata or object format",
        )
    return worktree_path


def assert_bound_identity(
    lane: dict[str, Any], args: argparse.Namespace, *, require_baseline_head: bool = False
) -> Path:
    worktree_path = assert_common_identity(
        lane,
        args,
        require_baseline_head=require_baseline_head,
    )
    registered_coder = lane.get("coder_ref")
    if registered_coder is None:
        raise RegistryError(
            "coder_unbound",
            "lane has no bound coder_ref; bind-coder must succeed first",
        )
    coder_ref = require_value(args.coder_ref, "coder_ref")
    if coder_ref != registered_coder:
        raise RegistryError(
            "ownership_mismatch",
            "coder_ref does not match the active writer claim",
        )
    registered_coder_epoch = lane.get("coder_epoch")
    if registered_coder_epoch is None and registered_coder is not None:
        registered_coder_epoch = 1
    if args.coder_epoch != registered_coder_epoch:
        raise RegistryError(
            "ownership_mismatch",
            "coder_epoch does not match the active writer generation",
        )
    return worktree_path


def get_lane(registry: dict[str, Any], card_id: str) -> dict[str, Any]:
    lane = registry["lanes"].get(card_id)
    if not isinstance(lane, dict):
        raise RegistryError("lane_not_found", f"card_id is not registered: {card_id}")
    return lane


def claim(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")
    owner_thread_id = require_value(args.owner_thread_id, "owner_thread_id")
    owner_run_id = require_value(args.owner_run_id, "owner_run_id")
    run_id = require_value(args.run_id, "run_id") if args.run_id else owner_run_id
    baseline_anchor = require_value(args.baseline_anchor, "baseline_anchor")
    worktree_path = canonical_directory(args.worktree_path, "worktree_path")
    baseline_commit, repository_identity = inspect_worktree_repository(
        worktree_path,
        baseline_anchor,
        require_baseline_head=True,
    )

    def mutate(registry: dict[str, Any]) -> dict[str, Any]:
        previous = registry["lanes"].get(card_id)
        if isinstance(previous, dict) and previous.get("active"):
            raise RegistryError(
                "card_claimed",
                f"card_id already has an active writer: {card_id}",
            )
        for other_card_id, other_lane in registry["lanes"].items():
            if (
                other_card_id != card_id
                and isinstance(other_lane, dict)
                and other_lane.get("active")
                and other_lane.get("worktree_path") == str(worktree_path)
            ):
                raise RegistryError(
                    "worktree_claimed",
                    f"worktree_path is active for card_id: {other_card_id}",
                )
        epoch = (
            int(previous.get("ownership_epoch", 0)) + 1
            if isinstance(previous, dict)
            else 1
        )
        timestamp = utc_now()
        lane = {
            "project_scope_id": project_scope_id,
            "lane_key": f"{project_scope_id}:{card_id}",
            "run_id": run_id,
            "card_id": card_id,
            "owner_thread_id": owner_thread_id,
            "owner_run_id": owner_run_id,
            "ownership_epoch": epoch,
            "coder_ref": None,
            "coder_epoch": 0,
            "worktree_path": str(worktree_path),
            "repository_identity": repository_identity,
            "baseline_anchor": baseline_commit,
            "candidate_anchor": None,
            "candidate_coder_epoch": None,
            "state": "claimed",
            "active": True,
            "claimed_at": timestamp,
            "updated_at": timestamp,
            "released_at": None,
        }
        registry["lanes"][card_id] = lane
        return {"lane": lane}

    return atomic_mutation(project_root, project_scope_id, "claim", mutate)


def bind_coder(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")
    coder_ref = require_value(args.coder_ref, "coder_ref")

    def mutate(registry: dict[str, Any]) -> dict[str, Any]:
        lane = get_lane(registry, card_id)
        assert_common_identity(lane, args, require_baseline_head=True)
        registered_coder = lane.get("coder_ref")
        if registered_coder not in (None, coder_ref):
            raise RegistryError("coder_already_bound", "lane already has a different coder_ref")
        if registered_coder is not None and lane.get("state") != "coder-active":
            raise RegistryError(
                "coder_attempt_completed",
                "bind-coder cannot reactivate a completed Coder attempt",
            )
        lane["coder_ref"] = coder_ref
        lane["coder_epoch"] = int(lane.get("coder_epoch") or 1)
        lane["state"] = "coder-active"
        lane["updated_at"] = utc_now()
        return {"lane": lane}

    return atomic_mutation(project_root, project_scope_id, "bind-coder", mutate)


def rotate_coder(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")
    new_coder_ref = require_value(args.new_coder_ref, "new_coder_ref")
    candidate_anchor = require_value(args.candidate_anchor, "candidate_anchor")

    def mutate(registry: dict[str, Any]) -> dict[str, Any]:
        lane = get_lane(registry, card_id)
        worktree_path = assert_bound_identity(lane, args)
        if lane.get("state") != "candidate-anchored":
            raise RegistryError(
                "candidate_not_anchored",
                "rotate-coder requires the current candidate to be anchored",
            )
        registered_candidate = require_value(
            lane.get("candidate_anchor"), "registered candidate_anchor"
        )
        expected_candidate = require_head_anchor(worktree_path, candidate_anchor)
        if expected_candidate != registered_candidate:
            raise RegistryError(
                "candidate_mismatch",
                "candidate_anchor does not match the lane's current candidate",
            )
        if new_coder_ref == lane.get("coder_ref"):
            raise RegistryError(
                "coder_unchanged",
                "new_coder_ref must identify a fresh Coder thread",
            )
        lane["coder_ref"] = new_coder_ref
        lane["coder_epoch"] = int(lane.get("coder_epoch") or 1) + 1
        lane["state"] = "coder-active"
        lane["updated_at"] = utc_now()
        return {"lane": lane}

    return atomic_mutation(project_root, project_scope_id, "rotate-coder", mutate)


def verify(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")
    object_id, registry = read_registry(project_root, project_scope_id)
    lane = get_lane(registry, card_id)
    assert_bound_identity(lane, args)
    return {
        "ok": True,
        "operation": "verify",
        "project_scope_id": project_scope_id,
        "registry_revision": registry["registry_revision"],
        "registry_object_id": object_id,
        "lane": lane,
    }


def anchor(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")
    candidate_anchor = require_value(args.candidate_anchor, "candidate_anchor")

    def mutate(registry: dict[str, Any]) -> dict[str, Any]:
        lane = get_lane(registry, card_id)
        worktree_path = assert_bound_identity(lane, args)
        resolved = resolve_candidate(worktree_path, candidate_anchor)
        current_coder_epoch = int(lane.get("coder_epoch") or 1)
        if lane.get("candidate_coder_epoch") == current_coder_epoch:
            if lane.get("candidate_anchor") == resolved:
                return {"lane": lane}
            raise RegistryError(
                "candidate_already_anchored",
                "the current Coder attempt already produced an immutable candidate",
            )
        if lane.get("state") != "coder-active":
            raise RegistryError(
                "coder_not_active",
                "anchor requires the current Coder attempt to be active",
            )
        lane["candidate_anchor"] = resolved
        lane["candidate_coder_epoch"] = current_coder_epoch
        lane["state"] = "candidate-anchored"
        lane["updated_at"] = utc_now()
        return {"lane": lane}

    return atomic_mutation(project_root, project_scope_id, "anchor", mutate)


def release(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")

    def mutate(registry: dict[str, Any]) -> dict[str, Any]:
        lane = get_lane(registry, card_id)
        assert_bound_identity(lane, args)
        timestamp = utc_now()
        lane["active"] = False
        lane["state"] = "released"
        lane["released_at"] = timestamp
        lane["updated_at"] = timestamp
        return {"lane": lane}

    return atomic_mutation(project_root, project_scope_id, "release", mutate)


def cancel_unbound(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    card_id = require_value(args.card_id, "card_id")

    def mutate(registry: dict[str, Any]) -> dict[str, Any]:
        lane = get_lane(registry, card_id)
        assert_common_identity(lane, args)
        if lane.get("coder_ref") is not None:
            raise RegistryError(
                "lane_bound",
                "cancel-unbound cannot cancel a lane after coder_ref is bound",
            )
        timestamp = utc_now()
        lane["active"] = False
        lane["state"] = "cancelled-unbound"
        lane["released_at"] = timestamp
        lane["updated_at"] = timestamp
        return {"lane": lane}

    return atomic_mutation(project_root, project_scope_id, "cancel-unbound", mutate)


def status(
    args: argparse.Namespace, project_root: Path, project_scope_id: str
) -> dict[str, Any]:
    object_id, registry = read_registry(project_root, project_scope_id)
    card_id = args.card_id.strip() if args.card_id else None
    if card_id:
        lane = registry["lanes"].get(card_id)
        return {
            "ok": True,
            "operation": "status",
            "project_scope_id": project_scope_id,
            "registry_revision": registry["registry_revision"],
            "registry_object_id": object_id,
            "lane": lane,
        }
    lanes = [registry["lanes"][key] for key in sorted(registry["lanes"])]
    return {
        "ok": True,
        "operation": "status",
        "project_scope_id": project_scope_id,
        "registry_revision": registry["registry_revision"],
        "registry_object_id": object_id,
        "lanes": lanes,
    }


def add_identity_arguments(
    parser: argparse.ArgumentParser,
    *,
    include_coder_ref: bool = True,
) -> None:
    parser.add_argument("--card-id", required=True)
    parser.add_argument("--owner-thread-id", required=True)
    parser.add_argument("--owner-run-id", required=True)
    parser.add_argument("--ownership-epoch", required=True, type=int)
    parser.add_argument("--worktree-path", required=True)
    if include_coder_ref:
        parser.add_argument("--coder-ref", required=True)
        parser.add_argument("--coder-epoch", required=True, type=int)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        required=True,
        help="coordination root in the authority Git repository",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    claim_parser = commands.add_parser("claim", help="atomically claim a card and worktree")
    claim_parser.add_argument("--card-id", required=True)
    claim_parser.add_argument("--owner-thread-id", required=True)
    claim_parser.add_argument("--owner-run-id", required=True)
    claim_parser.add_argument("--run-id")
    claim_parser.add_argument("--worktree-path", required=True)
    claim_parser.add_argument("--baseline-anchor", required=True)

    bind_parser = commands.add_parser(
        "bind-coder", help="bind the lane's first writer identity"
    )
    add_identity_arguments(bind_parser, include_coder_ref=False)
    bind_parser.add_argument("--coder-ref", required=True)

    rotate_parser = commands.add_parser(
        "rotate-coder", help="replace a completed Coder attempt at an anchored candidate"
    )
    add_identity_arguments(rotate_parser)
    rotate_parser.add_argument("--new-coder-ref", required=True)
    rotate_parser.add_argument("--candidate-anchor", required=True)

    verify_parser = commands.add_parser("verify", help="verify active lane ownership")
    add_identity_arguments(verify_parser)

    anchor_parser = commands.add_parser("anchor", help="record an immutable candidate commit")
    add_identity_arguments(anchor_parser)
    anchor_parser.add_argument("--candidate-anchor", required=True)

    release_parser = commands.add_parser(
        "release", help="release writer ownership and retain a tombstone"
    )
    add_identity_arguments(release_parser)

    cancel_parser = commands.add_parser(
        "cancel-unbound", help="cancel a claim before coder_ref is bound"
    )
    add_identity_arguments(cancel_parser, include_coder_ref=False)

    status_parser = commands.add_parser("status", help="read one lane or the whole registry")
    status_parser.add_argument("--card-id")
    return parser


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        project_root, project_scope_id = authority_context(args.project_root)
        handlers = {
            "claim": claim,
            "bind-coder": bind_coder,
            "rotate-coder": rotate_coder,
            "verify": verify,
            "anchor": anchor,
            "release": release,
            "cancel-unbound": cancel_unbound,
            "status": status,
        }
        emit(handlers[args.command](args, project_root, project_scope_id))
        return 0
    except RegistryError as exc:
        emit(
            {
                "ok": False,
                "operation": getattr(args, "command", None),
                "error": {"code": exc.code, "message": exc.message},
            }
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
