import pytest

from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.models.node import NodeStatus
from storectl.domain.services.monitoring_service import MonitoringService
from tests.conftest import FakeKubectlPort, FakeNodeMetricsPort, make_node


class TestMonitoringService:
    def test_returns_cluster_status(
        self,
        fake_kubectl: FakeKubectlPort,
        fake_metrics: FakeNodeMetricsPort,
    ) -> None:
        service = MonitoringService(kubectl_port=fake_kubectl, metrics_port=fake_metrics)
        result = service.execute()
        assert isinstance(result, ClusterStatus)

    def test_cluster_contains_all_nodes(self, fake_metrics: FakeNodeMetricsPort) -> None:
        nodes = [make_node("node-1"), make_node("node-2")]
        kubectl = FakeKubectlPort(nodes=nodes)
        service = MonitoringService(kubectl_port=kubectl, metrics_port=fake_metrics)
        result = service.execute()
        assert result.node_count() == 2

    def test_healthy_cluster_when_all_nodes_ready(
        self,
        fake_kubectl: FakeKubectlPort,
        fake_metrics: FakeNodeMetricsPort,
    ) -> None:
        service = MonitoringService(kubectl_port=fake_kubectl, metrics_port=fake_metrics)
        result = service.execute()
        assert result.is_healthy() is True

    def test_degraded_cluster_when_node_not_ready(
        self, fake_metrics: FakeNodeMetricsPort
    ) -> None:
        nodes = [
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.NOT_READY),
        ]
        kubectl = FakeKubectlPort(nodes=nodes)
        service = MonitoringService(kubectl_port=kubectl, metrics_port=fake_metrics)
        result = service.execute()
        assert result.is_healthy() is False
        assert len(result.get_degraded_nodes()) == 1

    def test_node_metrics_are_updated(self, fake_metrics: FakeNodeMetricsPort) -> None:
        node = make_node("node-1", cpu_usage="200m", memory_usage="1Gi")
        kubectl = FakeKubectlPort(nodes=[node])
        service = MonitoringService(kubectl_port=kubectl, metrics_port=fake_metrics)
        result = service.execute()
        assert result.nodes[0].cpu_usage == "200m"
        assert result.nodes[0].memory_usage == "1Gi"
