from abc import ABC, abstractmethod

from storectl.domain.models.cluster_status import ClusterStatus


class IMonitoringUseCase(ABC):
    @abstractmethod
    def execute(self) -> ClusterStatus: ...
