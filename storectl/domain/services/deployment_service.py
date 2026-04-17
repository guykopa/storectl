from storectl.domain.exceptions import DeploymentFailedError
from storectl.ports.outbound.i_kubectl_port import IKubectlPort


class DeploymentService:
    """Performs a rolling update and rolls back automatically on failure."""

    def __init__(self, kubectl_port: IKubectlPort) -> None:
        self._kubectl = kubectl_port

    def execute(self, deployment: str) -> bool:
        self._kubectl.rollout(deployment)
        success = self._kubectl.rollout_status(deployment)
        if not success:
            self._kubectl.rollout_undo(deployment)
            raise DeploymentFailedError(deployment)
        return True
