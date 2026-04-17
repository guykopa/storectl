from storectl.domain.services.deployment_service import DeploymentService
from storectl.ports.inbound.i_deployment_use_case import IDeploymentUseCase
from storectl.ports.outbound.i_kubectl_port import IKubectlPort


class RollingUpdateUseCase(IDeploymentUseCase):
    """Orchestrates DeploymentService to perform a rolling update with auto-rollback."""

    def __init__(self, kubectl_port: IKubectlPort) -> None:
        self._service = DeploymentService(kubectl_port=kubectl_port)

    def execute(self, deployment: str) -> bool:
        return self._service.execute(deployment)
