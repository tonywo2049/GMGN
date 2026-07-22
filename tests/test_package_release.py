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
    "telemetry/",
)
ALLOWED_FILES = {"README.md", "README.zh-CN.md", "GMGN.md", "LICENSE"}
VERSION_PATHS = (
    Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"),
    Path(".agents/plugins/marketplace.json"),
    Path(".claude-plugin/marketplace.json"),
)
REQUIRED_TELEMETRY_FILES = {
    "telemetry/__init__.py",
    "telemetry/collector.py",
    "telemetry/hook.py",
    "telemetry/install.py",
    "telemetry/report.py",
    "telemetry/dashboard.html",
    "telemetry/dashboard.css",
    "telemetry/dashboard.js",
}


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
            self.assertIn("skills/gmgn/references/en/assurance-policy.json", names)
            self.assertIn("README.zh-CN.md", names)
            self.assertNotIn("GMGN.zh-CN.md", names)
            self.assertFalse(any("/references/zh-CN/" in name for name in names))
            self.assertTrue(REQUIRED_TELEMETRY_FILES <= set(names))
            self.assertEqual(create_systems, {3})
            self.assertIn("`execution/<card_id>/Card.md` first", run_task_skill)
            self.assertIn("## 6. Add a separate Verifier only for risk triggers", run_task_skill)
            self.assertIn("A fresh Verifier is exceptional, not default", run_task_skill)

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

    def test_archive_includes_telemetry_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            telemetry_files = {
                "telemetry/install.py": "print('install')\n",
                "telemetry/report.py": "print('report')\n",
                "telemetry/hooks/session.py": "print('hook')\n",
            }
            for relative_path, content in telemetry_files.items():
                path = copied_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            output_dir = Path(temporary) / "dist"
            result = self.run_copied_packager(copied_root, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            archive = next(output_dir.glob("*.zip"))
            with zipfile.ZipFile(archive) as release:
                names = set(release.namelist())
                extract_root = Path(temporary) / "extracted"
                release.extractall(extract_root)
            self.assertTrue(REQUIRED_TELEMETRY_FILES <= names, names)
            self.assertTrue(telemetry_files.keys() <= names, names)

            report_help = subprocess.run(
                ["python3", str(extract_root / "telemetry" / "report.py"), "--help"],
                text=True,
                capture_output=True,
            )
            self.assertEqual(report_help.returncode, 0, report_help.stderr)
            dry_run = subprocess.run(
                [
                    "python3",
                    str(extract_root / "telemetry" / "install.py"),
                    "--dry-run",
                    "--home",
                    str(Path(temporary) / "home"),
                    "--codex-home",
                    str(Path(temporary) / "codex"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)

    def test_archive_rejects_missing_required_telemetry_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            (copied_root / "telemetry" / "collector.py").unlink()
            output_dir = Path(temporary) / "dist"

            result = self.run_copied_packager(copied_root, output_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("发布包缺少 telemetry 运行文件", result.stderr)
            self.assert_no_release_artifacts(output_dir)

    def test_archive_rejects_non_english_normative_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_root = self.copied_repository(temporary)
            translated = copied_root / "skills" / "gmgn" / "references" / "fr"
            translated.mkdir(parents=True)
            (translated / "writing-contract.md").write_text("duplicate\n", encoding="utf-8")
            output_dir = Path(temporary) / "dist"

            result = self.run_copied_packager(copied_root, output_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("规范文档必须只保留英文单一权威", result.stderr)
            self.assert_no_release_artifacts(output_dir)

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
