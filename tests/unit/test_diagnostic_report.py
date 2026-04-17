import pytest

from storectl.domain.models.diagnostic_report import DiagnosticReport, DiagnosticSeverity


class TestDiagnosticSeverity:
    def test_has_info(self) -> None:
        assert DiagnosticSeverity.INFO is not None

    def test_has_warning(self) -> None:
        assert DiagnosticSeverity.WARNING is not None

    def test_has_critical(self) -> None:
        assert DiagnosticSeverity.CRITICAL is not None


class TestDiagnosticReport:
    def test_creation(self) -> None:
        report = DiagnosticReport(
            node_name="node-1",
            root_cause="OOMKill detected",
            details=["container exceeded memory limit", "restart count: 5"],
            severity=DiagnosticSeverity.CRITICAL,
        )
        assert report.node_name == "node-1"
        assert report.root_cause == "OOMKill detected"
        assert report.details == ["container exceeded memory limit", "restart count: 5"]
        assert report.severity == DiagnosticSeverity.CRITICAL

    def test_node_name_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError):
            DiagnosticReport(
                node_name="",
                root_cause="OOMKill detected",
                details=[],
                severity=DiagnosticSeverity.CRITICAL,
            )

    def test_root_cause_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError):
            DiagnosticReport(
                node_name="node-1",
                root_cause="",
                details=[],
                severity=DiagnosticSeverity.CRITICAL,
            )

    def test_is_critical(self) -> None:
        report = DiagnosticReport(
            node_name="node-1",
            root_cause="disk full",
            details=[],
            severity=DiagnosticSeverity.CRITICAL,
        )
        assert report.is_critical() is True

    def test_is_not_critical(self) -> None:
        report = DiagnosticReport(
            node_name="node-1",
            root_cause="high cpu",
            details=[],
            severity=DiagnosticSeverity.WARNING,
        )
        assert report.is_critical() is False

    def test_details_defaults_to_empty_list(self) -> None:
        report = DiagnosticReport(
            node_name="node-1",
            root_cause="disk full",
            details=[],
            severity=DiagnosticSeverity.INFO,
        )
        assert report.details == []
