from storectl.domain.models.cluster_status import ClusterStatus
from storectl.ports.outbound.i_node_port import INodePort
from storectl.ports.outbound.i_node_metrics_port import INodeMetricsPort


class MonitoringService:
    """Fetches all nodes and their metrics, returns a ClusterStatus."""

    def __init__(self, kubectl_port: INodePort, metrics_port: INodeMetricsPort) -> None:
        self._kubectl = kubectl_port
        self._metrics = metrics_port

    def execute(self) -> ClusterStatus:
        nodes = self._kubectl.get_nodes()
        for node in nodes:
            node.cpu_usage = self._metrics.get_cpu_usage(node)
            node.memory_usage = self._metrics.get_memory_usage(node)
        return ClusterStatus(nodes=nodes)
