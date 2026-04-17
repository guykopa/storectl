from pathlib import Path

README = Path(__file__).parent.parent.parent / "README.md"


def content() -> str:
    return README.read_text()


class TestReadme:
    def test_file_exists(self) -> None:
        assert README.exists()

    def test_has_title(self) -> None:
        assert "# storectl" in content()

    def test_has_installation_section(self) -> None:
        assert "## Installation" in content()

    def test_has_usage_section(self) -> None:
        assert "## Usage" in content()

    def test_has_monitor_command(self) -> None:
        assert "monitor" in content()

    def test_has_diagnose_command(self) -> None:
        assert "diagnose" in content()

    def test_has_update_command(self) -> None:
        assert "update" in content()

    def test_has_architecture_section(self) -> None:
        assert "## Architecture" in content()

    def test_has_development_section(self) -> None:
        assert "## Development" in content()

    def test_mentions_tdd(self) -> None:
        assert "TDD" in content()
