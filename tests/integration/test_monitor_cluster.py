from storectl.application.monitor_cluster import MonitorClusterUseCase
from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.models.node import NodeStatus
from storectl.ports.inbound.i_monitoring_use_case import IMonitoringUseCase
from tests.conftest import FakeKubectlPort, FakeNodeMetricsPort, make_node


class TestMonitorClusterUseCase:
    def test_implements_inbound_port(self) -> None:
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeKubectlPort(),
            metrics_port=FakeNodeMetricsPort(),
        )
        assert isinstance(use_case, IMonitoringUseCase)

    def test_execute_returns_cluster_status(self) -> None:
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeKubectlPort(),
            metrics_port=FakeNodeMetricsPort(),
        )
        result = use_case.execute()
        assert isinstance(result, ClusterStatus)

    def test_full_flow_healthy_cluster(self) -> None:
        nodes = [make_node("node-1"), make_node("node-2")]
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeKubectlPort(nodes=nodes),
            metrics_port=FakeNodeMetricsPort(),
        )
        result = use_case.execute()
        assert result.is_healthy() is True
        assert result.node_count() == 2

    def test_full_flow_degraded_cluster(self) -> None:
        nodes = [
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.NOT_READY),
        ]
        use_case = MonitorClusterUseCase(
            kubectl_port=FakeKubectlPort(nodes=nodes),
            metrics_port=FakeNodeMetricsPort(),
        )
        result = use_case.execute()
        assert result.is_healthy() is False
        assert len(result.get_degraded_nodes()) == 1
        assert result.get_degraded_nodes()[0].name == "node-2"
