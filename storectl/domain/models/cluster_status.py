from dataclasses import dataclass, field
from typing import List

from storectl.domain.models.node import Node, NodeStatus


@dataclass
class ClusterStatus:
    nodes: List[Node] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.nodes:
            raise ValueError("ClusterStatus must contain at least one node")

    def is_healthy(self) -> bool:
        return all(node.is_ready() for node in self.nodes)

    def get_degraded_nodes(self) -> List[Node]:
        return [node for node in self.nodes if node.status != NodeStatus.READY]

    def node_count(self) -> int:
        return len(self.nodes)
