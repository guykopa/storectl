import pytest

from storectl.application.diagnose_node import DiagnoseNodeUseCase
from storectl.domain.exceptions import NodeNotFoundError
from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity
from storectl.ports.inbound.i_diagnostic_use_case import IDiagnosticUseCase
from tests.conftest import FakeKubectlPort, FakeLogReaderPort, make_node


class TestDiagnoseNodeUseCase:
    def test_implements_inbound_port(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeKubectlPort(),
            log_port=FakeLogReaderPort(),
        )
        assert isinstance(use_case, IDiagnosticUseCase)

    def test_execute_returns_diagnostic_report(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeKubectlPort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(logs=["normal operation"]),
        )
        result = use_case.execute("node-1")
        assert isinstance(result, DiagnosticReport)

    def test_full_flow_oomkill_detected(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeKubectlPort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(logs=["OOMKill: container exceeded memory limit"]),
        )
        result = use_case.execute("node-1")
        assert result.severity == DiagnosticSeverity.CRITICAL
        assert "OOMKill" in result.root_cause

    def test_full_flow_no_issue(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeKubectlPort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(logs=["everything is fine"]),
        )
        result = use_case.execute("node-1")
        assert result.severity == DiagnosticSeverity.INFO

    def test_full_flow_node_not_found(self) -> None:
        use_case = DiagnoseNodeUseCase(
            kubectl_port=FakeKubectlPort(nodes=[make_node("node-1")]),
            log_port=FakeLogReaderPort(),
        )
        with pytest.raises(NodeNotFoundError):
            use_case.execute("node-99")
