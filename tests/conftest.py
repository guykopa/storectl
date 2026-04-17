import pytest
from typing import List

from storectl.domain.models.node import Node, NodeStatus
from storectl.domain.models.pod import Pod, PodStatus
from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity
from storectl.ports.outbound.i_node_port import INodePort
from storectl.ports.outbound.i_deployment_port import IDeploymentPort
from storectl.ports.outbound.i_node_metrics_port import INodeMetricsPort
from storectl.ports.outbound.i_log_reader_port import ILogReaderPort


# --- Builders ---

def make_node(
    name: str = "node-1",
    status: NodeStatus = NodeStatus.READY,
    cpu_capacity: str = "2",
    memory_capacity: str = "4Gi",
    cpu_usage: str = "100m",
    memory_usage: str = "512Mi",
) -> Node:
    return Node(
        name=name,
        status=status,
        cpu_capacity=cpu_capacity,
        memory_capacity=memory_capacity,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
    )


def make_pod(
    name: str = "pod-1",
    namespace: str = "default",
    status: PodStatus = PodStatus.RUNNING,
    node_name: str = "node-1",
    restart_count: int = 0,
) -> Pod:
    return Pod(
        name=name,
        namespace=namespace,
        status=status,
        node_name=node_name,
        restart_count=restart_count,
    )


# --- Fake ports ---

class FakeNodePort(INodePort):
    """In-memory node port for unit tests."""

    def __init__(self, nodes: List[Node] | None = None) -> None:
        self._nodes = nodes or [make_node()]

    def get_nodes(self) -> List[Node]:
        return self._nodes

    def describe_node(self, name: str) -> Node:
        for node in self._nodes:
            if node.name == name:
                return node
        from storectl.domain.exceptions import NodeNotFoundError
        raise NodeNotFoundError(name)


class FakeDeploymentPort(IDeploymentPort):
    """In-memory deployment port for unit tests."""

    def __init__(self, rollout_succeeds: bool = True) -> None:
        self._rollout_succeeds = rollout_succeeds

    def rollout(self, deployment: str, namespace: str = "default") -> None:
        pass

    def rollout_status(self, deployment: str, namespace: str = "default") -> bool:
        return self._rollout_succeeds

    def rollout_undo(self, deployment: str, namespace: str = "default") -> None:
        pass


class FakeNodeMetricsPort(INodeMetricsPort):
    """In-memory metrics port for unit tests."""

    def get_cpu_usage(self, node: Node) -> str:
        return node.cpu_usage

    def get_memory_usage(self, node: Node) -> str:
        return node.memory_usage


class FakeLogReaderPort(ILogReaderPort):
    """In-memory log reader port for unit tests."""

    def __init__(self, logs: List[str] | None = None) -> None:
        self._logs = logs or []

    def get_logs(self, node: Node) -> List[str]:
        return self._logs


# --- Fixtures ---

@pytest.fixture
def ready_node() -> Node:
    return make_node()


@pytest.fixture
def not_ready_node() -> Node:
    return make_node(name="node-2", status=NodeStatus.NOT_READY)


@pytest.fixture
def healthy_cluster(ready_node: Node) -> ClusterStatus:
    return ClusterStatus(nodes=[ready_node])


@pytest.fixture
def fake_node_port() -> FakeNodePort:
    return FakeNodePort()


@pytest.fixture
def fake_deployment_port() -> FakeDeploymentPort:
    return FakeDeploymentPort()


@pytest.fixture
def fake_metrics() -> FakeNodeMetricsPort:
    return FakeNodeMetricsPort()


@pytest.fixture
def fake_logs() -> FakeLogReaderPort:
    return FakeLogReaderPort()
