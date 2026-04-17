import pytest

from storectl.domain.models.node import Node, NodeStatus


class TestNodeStatus:
    def test_has_ready(self) -> None:
        assert NodeStatus.READY is not None

    def test_has_not_ready(self) -> None:
        assert NodeStatus.NOT_READY is not None

    def test_has_unknown(self) -> None:
        assert NodeStatus.UNKNOWN is not None


class TestNode:
    def test_creation(self) -> None:
        node = Node(
            name="node-1",
            status=NodeStatus.READY,
            cpu_capacity="2",
            memory_capacity="4Gi",
            cpu_usage="100m",
            memory_usage="512Mi",
        )
        assert node.name == "node-1"
        assert node.status == NodeStatus.READY
        assert node.cpu_capacity == "2"
        assert node.memory_capacity == "4Gi"
        assert node.cpu_usage == "100m"
        assert node.memory_usage == "512Mi"

    def test_name_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError):
            Node(
                name="",
                status=NodeStatus.READY,
                cpu_capacity="2",
                memory_capacity="4Gi",
                cpu_usage="100m",
                memory_usage="512Mi",
            )

    def test_is_ready(self) -> None:
        node = Node(
            name="node-1",
            status=NodeStatus.READY,
            cpu_capacity="2",
            memory_capacity="4Gi",
            cpu_usage="100m",
            memory_usage="512Mi",
        )
        assert node.is_ready() is True

    def test_is_not_ready(self) -> None:
        node = Node(
            name="node-1",
            status=NodeStatus.NOT_READY,
            cpu_capacity="2",
            memory_capacity="4Gi",
            cpu_usage="100m",
            memory_usage="512Mi",
        )
        assert node.is_ready() is False
