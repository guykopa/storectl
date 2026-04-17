import pytest

from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity
from storectl.domain.exceptions import NodeNotFoundError
from storectl.domain.services.diagnostic_service import DiagnosticService
from tests.conftest import FakeKubectlPort, FakeLogReaderPort, make_node


class TestDiagnosticService:
    def test_returns_diagnostic_report(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=["everything is fine"])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        result = service.execute("node-1")
        assert isinstance(result, DiagnosticReport)

    def test_report_contains_node_name(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=[])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        result = service.execute("node-1")
        assert result.node_name == "node-1"

    def test_oomkill_detected_in_logs(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=["OOMKill: container exceeded memory limit"])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        result = service.execute("node-1")
        assert "OOMKill" in result.root_cause
        assert result.severity == DiagnosticSeverity.CRITICAL

    def test_disk_full_detected_in_logs(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=["No space left on device"])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        result = service.execute("node-1")
        assert "disk" in result.root_cause.lower()
        assert result.severity == DiagnosticSeverity.CRITICAL

    def test_no_issue_detected(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=["normal operation"])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        result = service.execute("node-1")
        assert result.severity == DiagnosticSeverity.INFO

    def test_raises_when_node_not_found(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=[])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        with pytest.raises(NodeNotFoundError):
            service.execute("node-99")

    def test_custom_pattern_injected_without_modifying_service(self) -> None:
        custom_patterns = {"NetworkTimeout": "network timeout detected"}
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=["NetworkTimeout: connection refused"])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs, patterns=custom_patterns)
        result = service.execute("node-1")
        assert "network timeout" in result.root_cause
        assert result.severity == DiagnosticSeverity.CRITICAL

    def test_default_patterns_still_work_without_injection(self) -> None:
        kubectl = FakeKubectlPort(nodes=[make_node("node-1")])
        logs = FakeLogReaderPort(logs=["OOMKill: memory exceeded"])
        service = DiagnosticService(kubectl_port=kubectl, log_port=logs)
        result = service.execute("node-1")
        assert result.severity == DiagnosticSeverity.CRITICAL
