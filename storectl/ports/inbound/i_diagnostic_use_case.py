from abc import ABC, abstractmethod

from storectl.domain.models.diagnostic_report import DiagnosticReport


class IDiagnosticUseCase(ABC):
    @abstractmethod
    def execute(self, node_name: str) -> DiagnosticReport: ...
