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
ALLOWED_PREFIXES = (
    ".agents/", ".claude-plugin/", ".codex-plugin/", ".docstar/", "agents/", "skills/",
)
ALLOWED_FILES = {"README.md", "README.zh-CN.md", "GMGN.md", "GMGN.zh-CN.md", "LICENSE"}
VERSION_PATHS = (
    Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"),
    Path(".agents/plugins/marketplace.json"),
    Path(".claude-plugin/marketplace.json"),
)


class PackageReleaseTests(unittest.TestCase):
    def copied_repository(self, temporary: str) -> Path:
        copied_root = Path(temporary) / "repo"
        shutil.copytree(
            ROOT,
            copied_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "dist"),
        )
        subprocess.run(["git", "init", "-q"], cwd=copied_root, check=True)
        return copied_root

    def set_version(self, root: Path, relative_path: Path, version: str) -> None:
        path = root / relative_path
        document = json.loads(path.read_text(encoding="utf-8"))
        if "plugins" in document:
            plugin_name = json.loads(
                (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )["name"]
            matches = [
                entry
                for entry in document["plugins"]
                if entry.get("name", "").casefold() == plugin_name.casefold()
            ]
            self.assertEqual(len(matches), 1)
            matches[0]["version"] = version
        else:
            document["version"] = version
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def release_drift_version(self, root: Path) -> str:
        current = json.loads(
            (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"]
        separator = "." if "+" in current else "+"
        return f"{current}{separator}test.drift"

    def run_copied_packager(
        self, copied_root: Path, output_dir: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
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

    def assert_no_release_artifacts(self, output_dir: Path) -> None:
        self.assertFalse(output_dir.exists() and any(output_dir.iterdir()))

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
                run_task_skill = release.read("skills/run-task/SKILL.md").decode("utf-8")
            self.assertTrue(names)
            self.assertTrue(
                all(name in ALLOWED_FILES or name.startswith(ALLOWED_PREFIXES) for name in names), names
            )
            self.assertIn(".agents/plugins/marketplace.json", names)
            self.assertIn(".docstar/conventions/conventions.json", names)
            self.assertIn("agents/author.md", names)
            self.assertIn("agents/critic.md", names)
            self.assertIn("agents/verifier.md", names)
            self.assertIn("README.zh-CN.md", names)
            self.assertIn("GMGN.zh-CN.md", names)
            self.assertEqual(create_systems, {3})
            self.assertIn("integration_queue_ref", run_task_skill)
            self.assertIn("post-integration-verifying", run_task_skill)

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

    def test_rejects_claude_manifest_version_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            self.set_version(
                copied_root, VERSION_PATHS[1], self.release_drift_version(copied_root)
            )
            output_dir = Path(temporary) / "dist"
            result = self.run_copied_packager(copied_root, output_dir)
            self.assertEqual(result.returncode, 1)
            self.assertIn("四处发布版本不一致", result.stderr)
            self.assert_no_release_artifacts(output_dir)

    def test_rejects_claude_marketplace_version_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            self.set_version(
                copied_root, VERSION_PATHS[3], self.release_drift_version(copied_root)
            )
            output_dir = Path(temporary) / "dist"
            result = self.run_copied_packager(copied_root, output_dir)
            self.assertEqual(result.returncode, 1)
            self.assertIn("四处发布版本不一致", result.stderr)
            self.assert_no_release_artifacts(output_dir)

    def test_rejects_codex_marketplace_version_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            self.set_version(
                copied_root, VERSION_PATHS[2], self.release_drift_version(copied_root)
            )
            output_dir = Path(temporary) / "dist"
            result = self.run_copied_packager(copied_root, output_dir)
            self.assertEqual(result.returncode, 1)
            self.assertIn("四处发布版本不一致", result.stderr)
            self.assert_no_release_artifacts(output_dir)

    def test_rejects_invalid_semver_without_artifacts(self) -> None:
        for invalid_version in ("01.2.3", "1.2.3-01", "v1.2.3", "1.2"):
            with self.subTest(version=invalid_version), tempfile.TemporaryDirectory() as temporary:
                copied_root = self.copied_repository(temporary)
                for relative_path in VERSION_PATHS:
                    self.set_version(copied_root, relative_path, invalid_version)
                output_dir = Path(temporary) / "dist"
                result = self.run_copied_packager(copied_root, output_dir)
                self.assertEqual(result.returncode, 1)
                self.assertIn("SemVer 2.0", result.stderr)
                self.assert_no_release_artifacts(output_dir)

    def test_accepts_semver_prerelease_and_build_metadata(self) -> None:
        version = "1.2.3-rc.1+build.20260719"
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            for relative_path in VERSION_PATHS:
                self.set_version(copied_root, relative_path, version)
            output_dir = Path(temporary) / "dist"
            result = self.run_copied_packager(copied_root, output_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / f"gmgn-{version}.zip").is_file())
            self.assertTrue((output_dir / f"gmgn-{version}.zip.sha256").is_file())


if __name__ == "__main__":
    unittest.main()
