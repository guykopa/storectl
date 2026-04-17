from unittest.mock import MagicMock, patch

import pytest

from storectl.domain.exceptions import DeploymentFailedError, NodeNotFoundError
from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity
from tests.conftest import make_node


def run_cli(*args: str) -> int:
    from storectl.cli.cli import main
    with patch("sys.argv", ["storectl", *args]):
        return main()


class TestCliMonitor:
    def test_monitor_exits_zero_on_healthy_cluster(self) -> None:
        cluster = ClusterStatus(nodes=[make_node("node-1")])
        with patch("storectl.cli.cli.MonitorClusterUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = cluster
            with patch("storectl.cli.cli.KubectlNodeAdapter"), \
                 patch("storectl.cli.cli.ProcMetricsAdapter"):
                code = run_cli("monitor")
        assert code == 0

    def test_monitor_exits_one_on_degraded_cluster(self) -> None:
        from storectl.domain.models.node import NodeStatus
        cluster = ClusterStatus(nodes=[make_node("node-1", NodeStatus.NOT_READY)])
        with patch("storectl.cli.cli.MonitorClusterUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = cluster
            with patch("storectl.cli.cli.KubectlNodeAdapter"), \
                 patch("storectl.cli.cli.ProcMetricsAdapter"):
                code = run_cli("monitor")
        assert code == 1


class TestCliDiagnose:
    def test_diagnose_exits_zero_on_info(self) -> None:
        report = DiagnosticReport(
            node_name="node-1", root_cause="none", details=[], severity=DiagnosticSeverity.INFO
        )
        with patch("storectl.cli.cli.DiagnoseNodeUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = report
            with patch("storectl.cli.cli.KubectlNodeAdapter"), \
                 patch("storectl.cli.cli.JournalctlAdapter"):
                code = run_cli("diagnose", "node-1")
        assert code == 0

    def test_diagnose_exits_one_on_critical(self) -> None:
        report = DiagnosticReport(
            node_name="node-1", root_cause="OOMKill", details=[], severity=DiagnosticSeverity.CRITICAL
        )
        with patch("storectl.cli.cli.DiagnoseNodeUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = report
            with patch("storectl.cli.cli.KubectlNodeAdapter"), \
                 patch("storectl.cli.cli.JournalctlAdapter"):
                code = run_cli("diagnose", "node-1")
        assert code == 1

    def test_diagnose_exits_two_on_node_not_found(self) -> None:
        with patch("storectl.cli.cli.DiagnoseNodeUseCase") as mock_uc:
            mock_uc.return_value.execute.side_effect = NodeNotFoundError("node-99")
            with patch("storectl.cli.cli.KubectlNodeAdapter"), \
                 patch("storectl.cli.cli.JournalctlAdapter"):
                code = run_cli("diagnose", "node-99")
        assert code == 2


class TestCliUpdate:
    def test_update_exits_zero_on_success(self) -> None:
        with patch("storectl.cli.cli.RollingUpdateUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = True
            with patch("storectl.cli.cli.KubectlDeploymentAdapter"):
                code = run_cli("update", "my-deployment")
        assert code == 0

    def test_update_exits_zero_with_explicit_namespace(self) -> None:
        with patch("storectl.cli.cli.RollingUpdateUseCase") as mock_uc:
            mock_uc.return_value.execute.return_value = True
            with patch("storectl.cli.cli.KubectlDeploymentAdapter"):
                code = run_cli("update", "my-deployment", "--namespace", "storectl")
        assert code == 0
        _, kwargs = mock_uc.return_value.execute.call_args
        assert kwargs.get("namespace") == "storectl" or mock_uc.return_value.execute.call_args[0][1] == "storectl"

    def test_update_exits_one_on_failure(self) -> None:
        with patch("storectl.cli.cli.RollingUpdateUseCase") as mock_uc:
            mock_uc.return_value.execute.side_effect = DeploymentFailedError("my-deployment")
            with patch("storectl.cli.cli.KubectlDeploymentAdapter"):
                code = run_cli("update", "my-deployment")
        assert code == 1
