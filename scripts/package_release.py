#!/usr/bin/env python3
"""Build a deterministic GMGN release archive from the Codex manifest."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
import zipfile


ROOT = Path(__file__).resolve().parents[1]
RELEASE_METADATA_PATHS = {
    "codex_manifest": Path(".codex-plugin/plugin.json"),
    "claude_manifest": Path(".claude-plugin/plugin.json"),
    "codex_marketplace": Path(".agents/plugins/marketplace.json"),
    "claude_marketplace": Path(".claude-plugin/marketplace.json"),
}
SEMVER_2_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
PACKAGE_PATHS = (
    ".agents",
    ".claude-plugin",
    ".codex-plugin",
    ".docstar",
    "agents",
    "skills",
    "telemetry",
    "README.md",
    "README.zh-CN.md",
    "GMGN.md",
    "LICENSE",
)
REQUIRED_PACKAGE_FILES = (
    Path("telemetry/__init__.py"),
    Path("telemetry/collector.py"),
    Path("telemetry/hook.py"),
    Path("telemetry/install.py"),
    Path("telemetry/report.py"),
    Path("telemetry/dashboard.html"),
    Path("telemetry/dashboard.css"),
    Path("telemetry/dashboard.js"),
)
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def validate_normative_layout(root: Path = ROOT) -> None:
    methodology = root / "GMGN.md"
    references = root / "skills/gmgn/references"
    english_references = references / "en"
    if not methodology.is_file() or not english_references.is_dir():
        raise ValueError("英文规范权威缺失: GMGN.md 或 skills/gmgn/references/en")

    extra_methodologies = sorted(
        path.relative_to(root).as_posix() for path in root.glob("GMGN.*.md")
    )
    extra_reference_roots = sorted(
        path.relative_to(root).as_posix()
        for path in references.iterdir()
        if path.name != "en"
    )
    extras = extra_methodologies + extra_reference_roots
    if extras:
        raise ValueError(f"规范文档必须只保留英文单一权威: {extras}")


def release_files() -> list[Path]:
    validate_normative_layout(ROOT)
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            *PACKAGE_PATHS,
        ],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    # `git ls-files --cached` also reports tracked paths deleted in a dirty development
    # worktree. They are not release artifacts; filter them before checking the allowlist.
    relative_files = [
        Path(value.decode("utf-8"))
        for value in result.stdout.split(b"\0")
        if value and (ROOT / Path(value.decode("utf-8"))).exists()
    ]
    for relative in PACKAGE_PATHS:
        if not any(path == Path(relative) or Path(relative) in path.parents for path in relative_files):
            raise ValueError(f"发布白名单路径不存在: {relative}")
    missing_required = [
        relative for relative in REQUIRED_PACKAGE_FILES if relative not in relative_files
    ]
    if missing_required:
        joined = ", ".join(path.as_posix() for path in missing_required)
        raise ValueError(f"发布包缺少 telemetry 运行文件: {joined}")
    files: list[Path] = []
    for relative in relative_files:
        path = ROOT / relative
        if path.is_symlink():
            raise ValueError(f"发布包不能包含符号链接: {relative}")
        if not path.is_file():
            raise ValueError(f"发布包路径不是普通文件: {relative}")
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def worktree_is_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    return bool(result.stdout.strip())


def load_release_json(root: Path, key: str) -> dict[str, Any]:
    relative_path = RELEASE_METADATA_PATHS[key]
    try:
        document = json.loads((root / relative_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"发布元数据 JSON 无效或缺失: {relative_path}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"发布元数据根必须是对象: {relative_path}")
    return document


def manifest_identity(document: dict[str, Any], path: Path) -> tuple[str, str]:
    name = document.get("name")
    version = document.get("version")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"插件 manifest name 无效: {path}")
    if not isinstance(version, str):
        raise ValueError(f"插件 manifest version 无效: {path}")
    return name, version


def unique_marketplace_entry(
    document: dict[str, Any], path: Path, plugin_name: str
) -> dict[str, Any]:
    entries = document.get("plugins")
    if not isinstance(entries, list):
        raise ValueError(f"marketplace plugins 必须是数组: {path}")
    matches = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and entry["name"].casefold() == plugin_name.casefold()
    ]
    if len(matches) != 1:
        raise ValueError(
            f"marketplace 必须有且只有一个 {plugin_name} 条目: {path}，实际 {len(matches)} 个"
        )
    return matches[0]


def validate_semver_2(version: Any, source: Path) -> str:
    if not isinstance(version, str) or SEMVER_2_PATTERN.fullmatch(version) is None:
        raise ValueError(f"版本不是合法 SemVer 2.0: {source}={version!r}")
    return version


def release_metadata(root: Path = ROOT) -> dict[str, Any]:
    documents = {
        key: load_release_json(root, key)
        for key in RELEASE_METADATA_PATHS
    }
    codex_name, codex_version = manifest_identity(
        documents["codex_manifest"], RELEASE_METADATA_PATHS["codex_manifest"]
    )
    claude_name, claude_version = manifest_identity(
        documents["claude_manifest"], RELEASE_METADATA_PATHS["claude_manifest"]
    )
    if claude_name != codex_name:
        raise ValueError(
            f"双 manifest name 不一致: {codex_name!r} != {claude_name!r}"
        )

    codex_entry = unique_marketplace_entry(
        documents["codex_marketplace"],
        RELEASE_METADATA_PATHS["codex_marketplace"],
        codex_name,
    )
    claude_entry = unique_marketplace_entry(
        documents["claude_marketplace"],
        RELEASE_METADATA_PATHS["claude_marketplace"],
        codex_name,
    )
    versions = {
        RELEASE_METADATA_PATHS["codex_manifest"]: codex_version,
        RELEASE_METADATA_PATHS["claude_manifest"]: claude_version,
        RELEASE_METADATA_PATHS["codex_marketplace"]: codex_entry.get("version"),
        RELEASE_METADATA_PATHS["claude_marketplace"]: claude_entry.get("version"),
    }
    validated = {
        path: validate_semver_2(version, path)
        for path, version in versions.items()
    }
    if len(set(validated.values())) != 1:
        detail = ", ".join(f"{path}={version}" for path, version in validated.items())
        raise ValueError(f"四处发布版本不一致: {detail}")

    return {
        **documents,
        "codex_marketplace_entry": codex_entry,
        "claude_marketplace_entry": claude_entry,
        "plugin_name": codex_name,
        "version": codex_version,
    }


def manifest_version(root: Path = ROOT) -> str:
    return release_metadata(root)["version"]


def write_archive(destination: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), ZIP_TIMESTAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 GMGN 可复现发布包")
    parser.add_argument("--allow-dirty", action="store_true", help="允许未提交的工作树，仅供开发验证")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist", help="发布产物目录")
    args = parser.parse_args()

    try:
        if not args.allow_dirty and worktree_is_dirty():
            raise ValueError("工作树不干净；开发验证请显式传 --allow-dirty")
        version = manifest_version()
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        archive_path = output_dir / f"gmgn-{version}.zip"
        write_archive(archive_path, release_files())
        digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        checksum_path = archive_path.with_suffix(".zip.sha256")
        checksum_path.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"打包失败: {exc}", file=sys.stderr)
        return 1

    print(f"已生成 {archive_path}")
    print(f"SHA256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
