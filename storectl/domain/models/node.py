from dataclasses import dataclass
from enum import Enum


class NodeStatus(Enum):
    READY = "Ready"
    NOT_READY = "NotReady"
    UNKNOWN = "Unknown"


@dataclass
class Node:
    name: str
    status: NodeStatus
    cpu_capacity: str
    memory_capacity: str
    cpu_usage: str
    memory_usage: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Node name cannot be empty")

    def is_ready(self) -> bool:
        return self.status == NodeStatus.READY
