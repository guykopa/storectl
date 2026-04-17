from typing import Dict, List, Optional

from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity
from storectl.ports.outbound.i_kubectl_port import IKubectlPort
from storectl.ports.outbound.i_log_reader_port import ILogReaderPort

DEFAULT_PATTERNS: Dict[str, str] = {
    "OOMKill": "OOMKill detected — container exceeded memory limit",
    "No space left on device": "disk full — no space left on device",
}


class DiagnosticService:
    """Diagnoses a node by analysing its logs and returns a DiagnosticReport."""

    def __init__(
        self,
        kubectl_port: IKubectlPort,
        log_port: ILogReaderPort,
        patterns: Optional[Dict[str, str]] = None,
    ) -> None:
        self._kubectl = kubectl_port
        self._log_port = log_port
        self._patterns = patterns if patterns is not None else DEFAULT_PATTERNS

    def execute(self, node_name: str) -> DiagnosticReport:
        node = self._kubectl.describe_node(node_name)
        logs = self._log_port.get_logs(node)
        root_cause, severity = self._analyse(logs)
        return DiagnosticReport(
            node_name=node_name,
            root_cause=root_cause,
            details=logs,
            severity=severity,
        )

    def _analyse(self, logs: List[str]) -> tuple[str, DiagnosticSeverity]:
        for line in logs:
            for pattern, cause in self._patterns.items():
                if pattern in line:
                    return cause, DiagnosticSeverity.CRITICAL
        return "no issue detected", DiagnosticSeverity.INFO
