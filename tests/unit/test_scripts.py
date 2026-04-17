import os
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
SCRIPTS = ["install_node.sh", "health_check.sh", "rolling_update.sh"]


class TestScriptsExist:
    def test_scripts_directory_exists(self) -> None:
        assert SCRIPTS_DIR.is_dir()

    def test_all_scripts_present(self) -> None:
        for name in SCRIPTS:
            assert (SCRIPTS_DIR / name).exists(), f"{name} is missing"


class TestScriptsSyntax:
    def test_all_scripts_pass_bash_syntax_check(self) -> None:
        for name in SCRIPTS:
            result = subprocess.run(
                ["bash", "-n", str(SCRIPTS_DIR / name)],
                capture_output=True, text=True,
            )
            assert result.returncode == 0, f"{name} has syntax errors: {result.stderr}"


class TestScriptsQuality:
    def test_all_scripts_have_shebang(self) -> None:
        for name in SCRIPTS:
            content = (SCRIPTS_DIR / name).read_text()
            assert content.startswith("#!/bin/bash"), f"{name} missing #!/bin/bash"

    def test_all_scripts_have_strict_mode(self) -> None:
        for name in SCRIPTS:
            content = (SCRIPTS_DIR / name).read_text()
            assert "set -euo pipefail" in content, f"{name} missing set -euo pipefail"

    def test_all_scripts_are_executable(self) -> None:
        for name in SCRIPTS:
            path = SCRIPTS_DIR / name
            assert os.access(path, os.X_OK), f"{name} is not executable"
