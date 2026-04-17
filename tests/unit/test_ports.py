import pytest
from typing import List

from storectl.domain.models.node import Node, NodeStatus
from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity
from storectl.ports.outbound.i_node_port import INodePort
from storectl.ports.outbound.i_deployment_port import IDeploymentPort
from storectl.ports.outbound.i_node_metrics_port import INodeMetricsPort
from storectl.ports.outbound.i_log_reader_port import ILogReaderPort
from storectl.ports.inbound.i_monitoring_use_case import IMonitoringUseCase
from storectl.ports.inbound.i_diagnostic_use_case import IDiagnosticUseCase
from storectl.ports.inbound.i_deployment_use_case import IDeploymentUseCase


def make_node(name: str = "node-1") -> Node:
    return Node(
        name=name,
        status=NodeStatus.READY,
        cpu_capacity="2",
        memory_capacity="4Gi",
        cpu_usage="100m",
        memory_usage="512Mi",
    )


# --- Outbound ports ---

class TestINodePort:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            INodePort()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeNodePort(INodePort):
            def get_nodes(self) -> List[Node]:
                return [make_node()]

            def describe_node(self, name: str) -> Node:
                return make_node(name)

        port = FakeNodePort()
        assert port.get_nodes() == [make_node()]


class TestIDeploymentPort:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            IDeploymentPort()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeDeploymentPort(IDeploymentPort):
            def rollout(self, deployment: str, namespace: str = "default") -> None:
                pass

            def rollout_status(self, deployment: str, namespace: str = "default") -> bool:
                return True

            def rollout_undo(self, deployment: str, namespace: str = "default") -> None:
                pass

        port = FakeDeploymentPort()
        assert port.rollout_status("app", namespace="kube-system") is True


class TestINodeMetricsPort:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            INodeMetricsPort()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeNodeMetricsPort(INodeMetricsPort):
            def get_cpu_usage(self, node: Node) -> str:
                return "100m"

            def get_memory_usage(self, node: Node) -> str:
                return "512Mi"

        port = FakeNodeMetricsPort()
        assert port.get_cpu_usage(make_node()) == "100m"


class TestILogReaderPort:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            ILogReaderPort()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeLogReaderPort(ILogReaderPort):
            def get_logs(self, node: Node) -> List[str]:
                return ["log line 1", "log line 2"]

        port = FakeLogReaderPort()
        assert port.get_logs(make_node()) == ["log line 1", "log line 2"]


# --- Inbound ports ---

class TestIMonitoringUseCase:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            IMonitoringUseCase()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeMonitoringUseCase(IMonitoringUseCase):
            def execute(self) -> ClusterStatus:
                return ClusterStatus(nodes=[make_node()])

        use_case = FakeMonitoringUseCase()
        assert isinstance(use_case.execute(), ClusterStatus)


class TestIDiagnosticUseCase:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            IDiagnosticUseCase()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeDiagnosticUseCase(IDiagnosticUseCase):
            def execute(self, node_name: str) -> DiagnosticReport:
                return DiagnosticReport(
                    node_name=node_name,
                    root_cause="none",
                    details=[],
                    severity=DiagnosticSeverity.INFO,
                )

        use_case = FakeDiagnosticUseCase()
        assert use_case.execute("node-1").node_name == "node-1"


class TestIDeploymentUseCase:
    def test_cannot_instantiate_without_implementation(self) -> None:
        with pytest.raises(TypeError):
            IDeploymentUseCase()  # type: ignore

    def test_concrete_implementation_is_accepted(self) -> None:
        class FakeDeploymentUseCase(IDeploymentUseCase):
            def execute(self, deployment: str, namespace: str = "default") -> bool:
                return True

        use_case = FakeDeploymentUseCase()
        assert use_case.execute("deploy-1", namespace="storectl") is True
