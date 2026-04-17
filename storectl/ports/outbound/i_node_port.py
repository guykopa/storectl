from abc import ABC, abstractmethod
from typing import List

from storectl.domain.models.node import Node


class INodePort(ABC):
    @abstractmethod
    def get_nodes(self) -> List[Node]: ...

    @abstractmethod
    def describe_node(self, name: str) -> Node: ...
