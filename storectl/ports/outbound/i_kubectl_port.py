from abc import ABC, abstractmethod
from typing import List

from storectl.domain.models.node import Node


class IKubectlPort(ABC):
    @abstractmethod
    def get_nodes(self) -> List[Node]: ...

    @abstractmethod
    def describe_node(self, name: str) -> Node: ...

    @abstractmethod
    def rollout(self, deployment: str) -> None: ...

    @abstractmethod
    def rollout_status(self, deployment: str) -> bool: ...

    @abstractmethod
    def rollout_undo(self, deployment: str) -> None: ...
