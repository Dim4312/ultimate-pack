"""Test installer argument handling with fake executables; never starts Java."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ServerLauncherTests(unittest.TestCase):
    def launch(self, no_update=False, installer_exit=0, cached_installer=b"test installer"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copy2(ROOT / "server/start.sh", folder / "start.sh")
            (folder / "packwiz-installer-bootstrap.jar").touch()
            if cached_installer is not None:
                (folder / "packwiz-installer.jar").write_bytes(cached_installer)
            (folder / "user_jvm_args.txt").write_text("-Xmx512M\n")
            (folder / "eula.txt").write_text("eula=true\n")
            (folder / "run.sh").write_text("#!/bin/sh\ntouch server-started\n")
            (folder / "run.sh").chmod(0o755)
            binary = folder / "bin"
            binary.mkdir()
            # This stands in for Java and records what the launcher would pass.
            (binary / "java").write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, sys\n"
                "from pathlib import Path\n"
                "Path('installer-args.json').write_text(json.dumps(sys.argv[1:]))\n"
                "sys.exit(int(os.environ['TEST_INSTALLER_EXIT']))\n"
            )
            (binary / "java").chmod(0o755)
            (binary / "curl").write_text("#!/bin/sh\necho Unexpected download >&2\nexit 99\n")
            (binary / "curl").chmod(0o755)
            env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"],
                       PACK_URL="https://example.invalid/pack.toml", TEST_INSTALLER_EXIT=str(installer_exit))
            env.pop("PACKWIZ_BOOTSTRAP_NO_UPDATE", None)
            if no_update:
                env["PACKWIZ_BOOTSTRAP_NO_UPDATE"] = "1"
            result = subprocess.run(["bash", str(folder / "start.sh")], env=env,
                                    capture_output=True, text=True, timeout=10)
            recorded = folder / "installer-args.json"
            args = json.loads(recorded.read_text()) if recorded.exists() else None
            return result, args, (folder / "server-started").exists()

    def test_cached_installer_skips_bootstrap_api_lookup(self):
        result, args, started = self.launch(no_update=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args, ["-jar", "packwiz-installer-bootstrap.jar", "--bootstrap-no-update", "-g", "-s", "server", "https://example.invalid/pack.toml"])
        self.assertTrue(started)

    def test_normal_player_launch_keeps_bootstrap_updates(self):
        result, args, started = self.launch(cached_installer=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args, ["-jar", "packwiz-installer-bootstrap.jar", "-g", "-s", "server", "https://example.invalid/pack.toml"])
        self.assertTrue(started)

    def test_no_update_rejects_missing_or_empty_installer_before_java(self):
        for cached in [None, b""]:
            with self.subTest(cached=cached):
                result, args, started = self.launch(no_update=True, cached_installer=cached)
                self.assertEqual(result.returncode, 1)
                self.assertIsNone(args)
                self.assertFalse(started)
                self.assertIn("requires a predownloaded packwiz-installer.jar", result.stderr)

    def test_failed_installer_does_not_start_server(self):
        result, _, started = self.launch(no_update=True, installer_exit=23)
        self.assertEqual(result.returncode, 23)
        self.assertFalse(started)


if __name__ == "__main__":
    unittest.main()
