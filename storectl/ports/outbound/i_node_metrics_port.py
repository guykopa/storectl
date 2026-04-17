from abc import ABC, abstractmethod

from storectl.domain.models.node import Node


class INodeMetricsPort(ABC):
    @abstractmethod
    def get_cpu_usage(self, node: Node) -> str: ...

    @abstractmethod
    def get_memory_usage(self, node: Node) -> str: ...
