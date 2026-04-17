from storectl.domain.models.diagnostic_report import DiagnosticReport
from storectl.domain.services.diagnostic_service import DiagnosticService
from storectl.ports.inbound.i_diagnostic_use_case import IDiagnosticUseCase
from storectl.ports.outbound.i_node_port import INodePort
from storectl.ports.outbound.i_log_reader_port import ILogReaderPort


class DiagnoseNodeUseCase(IDiagnosticUseCase):
    """Orchestrates DiagnosticService to diagnose a node and return a report."""

    def __init__(self, kubectl_port: INodePort, log_port: ILogReaderPort) -> None:
        self._service = DiagnosticService(kubectl_port=kubectl_port, log_port=log_port)

    def execute(self, node_name: str) -> DiagnosticReport:
        return self._service.execute(node_name)
