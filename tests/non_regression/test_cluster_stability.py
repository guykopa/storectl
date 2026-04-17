"""
Non-regression tests for cluster stability scenarios.
These tests verify that the full stack behaves correctly end-to-end
and that no regression is introduced across layers.
All tests run without a real Kubernetes cluster.
"""
import pytest

from storectl.application.diagnose_node import DiagnoseNodeUseCase
from storectl.application.monitor_cluster import MonitorClusterUseCase
from storectl.application.rolling_update import RollingUpdateUseCase
from storectl.domain.exceptions import DeploymentFailedError, NodeNotFoundError
from storectl.domain.models.diagnostic_report import DiagnosticSeverity
from storectl.domain.models.node import NodeStatus
from tests.conftest import (
    FakeNodePort,
    FakeDeploymentPort,
    FakeLogReaderPort,
    FakeNodeMetricsPort,
    make_node,
)


class FakeDeploymentPortFailingRollout(FakeDeploymentPort):
    def __init__(self) -> None:
        super().__init__(rollout_succeeds=False)
        self.rollback_called = False

    def rollout_undo(self, deployment: str, namespace: str = "default") -> None:
        self.rollback_called = True


class TestClusterMonitoringStability:
    def test_stable_cluster_is_always_reported_healthy(self) -> None:
        nodes = [make_node(f"node-{i}") for i in range(1, 4)]
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeNodePort(nodes=nodes),
            metrics_port=FakeNodeMetricsPort(),
        )
        for _ in range(3):
            result = use_case.execute()
            assert result.is_healthy() is True

    def test_degraded_node_always_appears_in_degraded_list(self) -> None:
        nodes = [
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.NOT_READY),
            make_node("node-3", NodeStatus.UNKNOWN),
        ]
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeNodePort(nodes=nodes),
            metrics_port=FakeNodeMetricsPort(),
        )
        result = use_case.execute()
        degraded_names = [n.name for n in result.get_degraded_nodes()]
        assert "node-2" in degraded_names
        assert "node-3" in degraded_names
        assert "node-1" not in degraded_names

    def test_node_count_never_changes_between_calls(self) -> None:
        nodes = [make_node(f"node-{i}") for i in range(1, 6)]
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeNodePort(nodes=nodes),
            metrics_port=FakeNodeMetricsPort(),
        )
        counts = [use_case.execute().node_count() for _ in range(3)]
        assert all(c == 5 for c in counts)


class TestDiagnosticStability:
    def test_oomkill_always_returns_critical(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeNodePort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(logs=["OOMKill: container exceeded memory limit"]),
        )
        for _ in range(3):
            result = use_case.execute("node-1")
            assert result.severity == DiagnosticSeverity.CRITICAL

    def test_disk_full_always_returns_critical(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeNodePort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(logs=["No space left on device"]),
        )
        result = use_case.execute("node-1")
        assert result.severity == DiagnosticSeverity.CRITICAL

    def test_unknown_node_always_raises(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeNodePort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(),
        )
        for _ in range(3):
            with pytest.raises(NodeNotFoundError):
                use_case.execute("ghost-node")


class TestDeploymentStability:
    def test_successful_deployment_always_returns_true(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeDeploymentPort())
        for _ in range(3):
            assert use_case.execute("my-deployment", namespace="default") is True

    def test_failed_deployment_always_raises_and_rolls_back(self) -> None:
        for _ in range(3):
            kubectl = FakeDeploymentPortFailingRollout()
            use_case = RollingUpdateUseCase(kubectl_port=kubectl)
            with pytest.raises(DeploymentFailedError):
                use_case.execute("my-deployment", namespace="default")
            assert kubectl.rollback_called is True

    def test_domain_layer_never_imports_adapters(self) -> None:
        import storectl.domain.services.monitoring_service as ms
        import storectl.domain.services.diagnostic_service as ds
        import storectl.domain.services.deployment_service as dep
        for module in (ms, ds, dep):
            source = module.__file__ or ""
            with open(source) as f:
                content = f.read()
            assert "adapters" not in content, (
                f"{source} must not import from adapters"
            )
