from unittest.mock import MagicMock, patch

import pytest

from storectl.adapters.outbound.journalctl_adapter import JournalctlAdapter
from tests.conftest import make_node

JOURNALCTL_OUTPUT = "Apr 17 10:00:00 node-1 kubelet[123]: OOMKill detected\nApr 17 10:00:01 node-1 kubelet[123]: restarting container\n"


def make_completed_process(stdout: str, returncode: int = 0) -> MagicMock:
    mock = MagicMock()
    mock.stdout = stdout
    mock.returncode = returncode
    return mock


class TestJournalctlAdapter:
    def test_returns_list_of_strings(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(JOURNALCTL_OUTPUT)
            adapter = JournalctlAdapter()
            result = adapter.get_logs(make_node("node-1"))
        assert isinstance(result, list)
        assert all(isinstance(line, str) for line in result)

    def test_returns_one_entry_per_line(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(JOURNALCTL_OUTPUT)
            adapter = JournalctlAdapter()
            result = adapter.get_logs(make_node("node-1"))
        assert len(result) == 2

    def test_empty_output_returns_empty_list(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("")
            adapter = JournalctlAdapter()
            result = adapter.get_logs(make_node("node-1"))
        assert result == []

    def test_subprocess_called_with_journalctl(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(JOURNALCTL_OUTPUT)
            adapter = JournalctlAdapter()
            adapter.get_logs(make_node("node-1"))
        args = mock_run.call_args[0][0]
        assert "journalctl" in args

    def test_subprocess_has_timeout(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(JOURNALCTL_OUTPUT)
            adapter = JournalctlAdapter()
            adapter.get_logs(make_node("node-1"))
        kwargs = mock_run.call_args[1]
        assert "timeout" in kwargs

    def test_falls_back_to_kubectl_events_when_journalctl_missing(self) -> None:
        kubectl_output = "Warning  OOMKilling  node-1  memory limit exceeded\n"
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                FileNotFoundError("journalctl not found"),
                make_completed_process(kubectl_output),
            ]
            adapter = JournalctlAdapter()
            result = adapter.get_logs(make_node("node-1"))
        assert len(result) == 1
        assert "OOMKilling" in result[0]
