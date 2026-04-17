from dataclasses import dataclass
from enum import Enum
from typing import List


class DiagnosticSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DiagnosticReport:
    node_name: str
    root_cause: str
    details: List[str]
    severity: DiagnosticSeverity

    def __post_init__(self) -> None:
        if not self.node_name:
            raise ValueError("node_name cannot be empty")
        if not self.root_cause:
            raise ValueError("root_cause cannot be empty")

    def is_critical(self) -> bool:
        return self.severity == DiagnosticSeverity.CRITICAL
