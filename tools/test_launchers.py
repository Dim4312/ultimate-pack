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
    def launch(self, token=None, installer_exit=0):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copy2(ROOT / "server/start.sh", folder / "start.sh")
            (folder / "packwiz-installer-bootstrap.jar").touch()
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
            env.pop("PACKWIZ_INSTALLER_TOKEN", None)
            if token is not None:
                env["PACKWIZ_INSTALLER_TOKEN"] = token
            result = subprocess.run(["bash", str(folder / "start.sh")], env=env,
                                    capture_output=True, text=True, timeout=10)
            args = json.loads((folder / "installer-args.json").read_text())
            return result, args, (folder / "server-started").exists()

    def test_token_authenticates_bootstrap_and_is_not_logged(self):
        token = "test_token_not_a_real_credential"
        result, args, started = self.launch(token=token)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args[:4], ["-jar", "packwiz-installer-bootstrap.jar", "--bootstrap-update-token", "Bearer " + token])
        self.assertNotIn(token, result.stdout + result.stderr)
        self.assertTrue(started)

    def test_normal_player_launch_requires_no_token(self):
        result, args, started = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(args, ["-jar", "packwiz-installer-bootstrap.jar", "-g", "-s", "server", "https://example.invalid/pack.toml"])
        self.assertTrue(started)

    def test_authentication_preserves_server_side_and_pack_url(self):
        _, args, _ = self.launch(token="test_token")
        self.assertEqual(args[4:], ["-g", "-s", "server", "https://example.invalid/pack.toml"])

    def test_failed_installer_does_not_start_server(self):
        result, _, started = self.launch(token="test_token", installer_exit=23)
        self.assertEqual(result.returncode, 23)
        self.assertFalse(started)


if __name__ == "__main__":
    unittest.main()
