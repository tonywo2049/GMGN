#!/usr/bin/env python3
"""Build a deterministic GMGN release archive from the Codex manifest."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
PACKAGE_PATHS = (
    ".agents",
    ".claude-plugin",
    ".codex-plugin",
    ".docstar",
    "agents",
    "skills",
    "README.md",
    "README.zh-CN.md",
    "GMGN.md",
    "GMGN.zh-CN.md",
    "LICENSE",
)
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def release_files() -> list[Path]:
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


def manifest_version() -> str:
    try:
        version = json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        raise ValueError(f"无法从 {MANIFEST.relative_to(ROOT)} 读取版本") from exc
    if not isinstance(version, str) or not version:
        raise ValueError("Codex manifest version 必须是非空字符串")
    if any(character in version for character in "/\\\\"):
        raise ValueError("Codex manifest version 不能包含路径分隔符")
    return version


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
