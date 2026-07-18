#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / "scripts" / "package_release.py"
ALLOWED_PREFIXES = (".claude-plugin/", ".codex-plugin/", "skills/")
ALLOWED_FILES = {"README.md", "GMGN.md", "LICENSE"}


class PackageReleaseTests(unittest.TestCase):
    def test_archive_is_deterministic_and_whitelisted(self) -> None:
        version = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary)
            command = ["python3", str(PACKAGER), "--allow-dirty", "--output-dir", str(output_dir)]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            archive = output_dir / f"gmgn-{version}.zip"
            first_bytes = archive.read_bytes()
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first_bytes, archive.read_bytes())

            with zipfile.ZipFile(archive) as release:
                names = release.namelist()
                create_systems = {info.create_system for info in release.infolist()}
            self.assertTrue(names)
            self.assertTrue(
                all(name in ALLOWED_FILES or name.startswith(ALLOWED_PREFIXES) for name in names), names
            )
            self.assertEqual(create_systems, {3})

            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            checksum = (output_dir / f"gmgn-{version}.zip.sha256").read_text(encoding="utf-8")
            self.assertEqual(checksum, f"{digest}  {archive.name}\n")

    def test_archive_excludes_ignored_files_inside_whitelisted_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = Path(temporary) / "repo"
            shutil.copytree(
                ROOT,
                copied_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"),
            )
            subprocess.run(["git", "init", "-q"], cwd=copied_root, check=True)
            (copied_root / "skills" / "private.log").write_text("secret\n", encoding="utf-8")
            output_dir = Path(temporary) / "dist"
            result = subprocess.run(
                [
                    "python3",
                    str(copied_root / "scripts" / "package_release.py"),
                    "--allow-dirty",
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=copied_root,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            archive = next(output_dir.glob("*.zip"))
            with zipfile.ZipFile(archive) as release:
                self.assertNotIn("skills/private.log", release.namelist())

    def test_default_mode_accepts_clean_tree_and_rejects_dirty_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = Path(temporary) / "repo"
            shutil.copytree(
                ROOT,
                copied_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"),
            )
            subprocess.run(["git", "init", "-q"], cwd=copied_root, check=True)
            subprocess.run(["git", "add", "."], cwd=copied_root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=GMGN Tests",
                    "-c",
                    "user.email=tests@example.invalid",
                    "commit",
                    "-qm",
                    "fixture",
                ],
                cwd=copied_root,
                check=True,
            )
            output_dir = Path(temporary) / "dist"
            command = [
                "python3",
                str(copied_root / "scripts" / "package_release.py"),
                "--output-dir",
                str(output_dir),
            ]
            clean = subprocess.run(command, cwd=copied_root, text=True, capture_output=True)
            self.assertEqual(clean.returncode, 0, clean.stderr)

            (copied_root / "untracked.txt").write_text("dirty\n", encoding="utf-8")
            dirty = subprocess.run(command, cwd=copied_root, text=True, capture_output=True)
            self.assertEqual(dirty.returncode, 1)
            self.assertIn("工作树不干净", dirty.stderr)

    def test_archive_version_comes_from_codex_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = Path(temporary) / "repo"
            shutil.copytree(
                ROOT,
                copied_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"),
            )
            subprocess.run(["git", "init", "-q"], cwd=copied_root, check=True)
            codex_manifest_path = copied_root / ".codex-plugin" / "plugin.json"
            claude_manifest_path = copied_root / ".claude-plugin" / "plugin.json"
            codex_manifest = json.loads(codex_manifest_path.read_text(encoding="utf-8"))
            claude_manifest = json.loads(claude_manifest_path.read_text(encoding="utf-8"))
            claude_manifest["version"] = "99.0.0-test"
            claude_manifest_path.write_text(
                json.dumps(claude_manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            output_dir = Path(temporary) / "dist"
            result = subprocess.run(
                [
                    "python3",
                    str(copied_root / "scripts" / "package_release.py"),
                    "--allow-dirty",
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=copied_root,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / f"gmgn-{codex_manifest['version']}.zip").is_file())
            self.assertFalse((output_dir / "gmgn-99.0.0-test.zip").exists())


if __name__ == "__main__":
    unittest.main()
