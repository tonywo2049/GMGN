import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "skills" / "gmgn" / "scripts" / "install_codex_agents.py"
SOURCE_DIR = ROOT / ".codex" / "agents"


class InstallCodexAgentsTests(unittest.TestCase):
    def test_installs_updates_and_preserves_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex_home = Path(temporary) / "codex-home"
            environment = {**os.environ, "CODEX_HOME": str(codex_home)}

            first = subprocess.run(
                [sys.executable, str(INSTALLER)],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            destination = codex_home / "agents"
            sources = sorted(SOURCE_DIR.glob("gmgn_*.toml"))
            self.assertTrue(sources)
            self.assertIn("已同步:", first.stdout)
            for source in sources:
                self.assertEqual(
                    (destination / source.name).read_bytes(), source.read_bytes()
                )

            unrelated = destination / "personal_agent.toml"
            unrelated.write_text("name = \"personal_agent\"\n", encoding="utf-8")
            stale = destination / sources[0].name
            stale.write_text("stale\n", encoding="utf-8")

            second = subprocess.run(
                [sys.executable, str(INSTALLER)],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(stale.read_bytes(), sources[0].read_bytes())
            self.assertEqual(
                unrelated.read_text(encoding="utf-8"), "name = \"personal_agent\"\n"
            )
            self.assertIn("未变化:", second.stdout)


if __name__ == "__main__":
    unittest.main()
