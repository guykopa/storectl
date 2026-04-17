from abc import ABC, abstractmethod


class IDeploymentPort(ABC):
    @abstractmethod
    def rollout(self, deployment: str, namespace: str = "default") -> None: ...

    @abstractmethod
    def rollout_status(self, deployment: str, namespace: str = "default") -> bool: ...

    @abstractmethod
    def rollout_undo(self, deployment: str, namespace: str = "default") -> None: ...
