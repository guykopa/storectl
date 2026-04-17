from dataclasses import dataclass
from enum import Enum

RESTART_THRESHOLD = 3


class PodStatus(Enum):
    RUNNING = "Running"
    PENDING = "Pending"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    UNKNOWN = "Unknown"


@dataclass
class Pod:
    name: str
    namespace: str
    status: PodStatus
    node_name: str
    restart_count: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Pod name cannot be empty")
        if not self.namespace:
            raise ValueError("Pod namespace cannot be empty")
        if self.restart_count < 0:
            raise ValueError("restart_count cannot be negative")

    def is_running(self) -> bool:
        return self.status == PodStatus.RUNNING

    def is_healthy(self) -> bool:
        return self.is_running() and self.restart_count < RESTART_THRESHOLD
