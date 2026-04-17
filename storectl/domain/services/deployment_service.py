from storectl.domain.exceptions import DeploymentFailedError
from storectl.ports.outbound.i_deployment_port import IDeploymentPort


class DeploymentService:
    """Performs a rolling update and rolls back automatically on failure."""

    def __init__(self, kubectl_port: IDeploymentPort) -> None:
        self._kubectl = kubectl_port

    def execute(self, deployment: str, namespace: str = "default") -> bool:
        self._kubectl.rollout(deployment, namespace)
        success = self._kubectl.rollout_status(deployment, namespace)
        if not success:
            self._kubectl.rollout_undo(deployment, namespace)
            raise DeploymentFailedError(deployment)
        return True
