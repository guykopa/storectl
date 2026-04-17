from storectl.domain.models.cluster_status import ClusterStatus
from storectl.domain.services.monitoring_service import MonitoringService
from storectl.ports.inbound.i_monitoring_use_case import IMonitoringUseCase
from storectl.ports.outbound.i_kubectl_port import IKubectlPort
from storectl.ports.outbound.i_node_metrics_port import INodeMetricsPort


class MonitorClusterUseCase(IMonitoringUseCase):
    """Orchestrates MonitoringService to return the current cluster status."""

    def __init__(self, kubectl_port: IKubectlPort, metrics_port: INodeMetricsPort) -> None:
        self._service = MonitoringService(kubectl_port=kubectl_port, metrics_port=metrics_port)

    def execute(self) -> ClusterStatus:
        return self._service.execute()
