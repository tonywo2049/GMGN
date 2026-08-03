#!/usr/bin/env python3
"""Synchronize GMGN's named Codex agents into the effective Codex home."""

import os
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / ".codex" / "agents"


def effective_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def install() -> tuple[Path, list[str], list[str]]:
    sources = sorted(SOURCE_DIR.glob("gmgn_*.toml"))
    if not sources:
        raise ValueError(f"未找到 GMGN Agent 配置: {SOURCE_DIR}")

    destination_dir = effective_codex_home() / "agents"
    destination_dir.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    unchanged: list[str] = []

    for source in sources:
        destination = destination_dir / source.name
        if destination.is_symlink():
            raise ValueError(f"拒绝覆盖符号链接: {destination}")
        if destination.is_file() and destination.read_bytes() == source.read_bytes():
            unchanged.append(source.name)
            continue
        shutil.copyfile(source, destination)
        installed.append(source.name)

    return destination_dir, installed, unchanged


def main() -> int:
    try:
        destination, installed, unchanged = install()
    except (OSError, ValueError) as exc:
        print(f"GMGN Agent 安装失败: {exc}", file=sys.stderr)
        return 1

    print(f"GMGN Agent 目录: {destination}")
    print(f"已同步: {', '.join(installed) if installed else 'none'}")
    print(f"未变化: {', '.join(unchanged) if unchanged else 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
