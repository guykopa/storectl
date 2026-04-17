from pathlib import Path
import yaml

CI_FILE = Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci.yml"


def load() -> dict:
    return yaml.safe_load(CI_FILE.read_text())


class TestCiWorkflowExists:
    def test_file_exists(self) -> None:
        assert CI_FILE.exists()

    def test_valid_yaml(self) -> None:
        assert isinstance(load(), dict)


class TestCiWorkflowStructure:
    def test_has_on_trigger(self) -> None:
        # pyyaml parses YAML `on` as Python True
        assert True in load()

    def test_triggers_on_push_and_pull_request(self) -> None:
        triggers = load()[True]
        assert "push" in triggers
        assert "pull_request" in triggers

    def test_has_jobs(self) -> None:
        assert "jobs" in load()

    def test_has_test_job(self) -> None:
        assert "test" in load()["jobs"]

    def test_has_lint_job(self) -> None:
        assert "lint" in load()["jobs"]


class TestCiTestJob:
    def test_runs_on_ubuntu(self) -> None:
        job = load()["jobs"]["test"]
        assert "ubuntu" in job["runs-on"]

    def test_uses_python_311(self) -> None:
        steps = load()["jobs"]["test"]["steps"]
        setup_step = next(
            (s for s in steps if "python-version" in str(s.get("with", {}))), None
        )
        assert setup_step is not None
        assert "3.11" in str(setup_step["with"]["python-version"])

    def test_installs_dependencies(self) -> None:
        steps = load()["jobs"]["test"]["steps"]
        cmds = " ".join(str(s.get("run", "")) for s in steps)
        assert "pip install" in cmds

    def test_runs_pytest(self) -> None:
        steps = load()["jobs"]["test"]["steps"]
        cmds = " ".join(str(s.get("run", "")) for s in steps)
        assert "pytest" in cmds


class TestCiLintJob:
    def test_runs_flake8(self) -> None:
        steps = load()["jobs"]["lint"]["steps"]
        cmds = " ".join(str(s.get("run", "")) for s in steps)
        assert "flake8" in cmds

    def test_runs_mypy(self) -> None:
        steps = load()["jobs"]["lint"]["steps"]
        cmds = " ".join(str(s.get("run", "")) for s in steps)
        assert "mypy" in cmds
