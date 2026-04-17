from abc import ABC, abstractmethod


class IDeploymentUseCase(ABC):
    @abstractmethod
    def execute(self, deployment: str) -> bool: ...
