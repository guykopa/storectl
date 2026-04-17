from abc import ABC, abstractmethod
from typing import List

from storectl.domain.models.node import Node


class ILogReaderPort(ABC):
    @abstractmethod
    def get_logs(self, node: Node) -> List[str]: ...
