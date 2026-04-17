import pytest

from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.models.node import Node, NodeStatus


def make_node(name: str, status: NodeStatus) -> Node:
    return Node(
        name=name,
        status=status,
        cpu_capacity="2",
        memory_capacity="4Gi",
        cpu_usage="100m",
        memory_usage="512Mi",
    )


class TestClusterStatus:
    def test_creation(self) -> None:
        nodes = [make_node("node-1", NodeStatus.READY)]
        cluster = ClusterStatus(nodes=nodes)
        assert cluster.nodes == nodes

    def test_nodes_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError):
            ClusterStatus(nodes=[])

    def test_is_healthy_all_ready(self) -> None:
        cluster = ClusterStatus(nodes=[
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.READY),
        ])
        assert cluster.is_healthy() is True

    def test_is_not_healthy_one_not_ready(self) -> None:
        cluster = ClusterStatus(nodes=[
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.NOT_READY),
        ])
        assert cluster.is_healthy() is False

    def test_get_degraded_nodes_none(self) -> None:
        cluster = ClusterStatus(nodes=[
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.READY),
        ])
        assert cluster.get_degraded_nodes() == []

    def test_get_degraded_nodes_returns_not_ready(self) -> None:
        node_bad = make_node("node-2", NodeStatus.NOT_READY)
        cluster = ClusterStatus(nodes=[
            make_node("node-1", NodeStatus.READY),
            node_bad,
        ])
        assert cluster.get_degraded_nodes() == [node_bad]

    def test_get_degraded_nodes_includes_unknown(self) -> None:
        node_unknown = make_node("node-3", NodeStatus.UNKNOWN)
        cluster = ClusterStatus(nodes=[
            make_node("node-1", NodeStatus.READY),
            node_unknown,
        ])
        assert cluster.get_degraded_nodes() == [node_unknown]

    def test_node_count(self) -> None:
        cluster = ClusterStatus(nodes=[
            make_node("node-1", NodeStatus.READY),
            make_node("node-2", NodeStatus.READY),
        ])
        assert cluster.node_count() == 2
