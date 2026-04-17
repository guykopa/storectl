import pytest

from storectl.domain.exceptions import DeploymentFailedError
from storectl.domain.services.deployment_service import DeploymentService
from tests.conftest import FakeKubectlPort


class FakeKubectlPortFailingRollout(FakeKubectlPort):
    """Kubectl port that simulates a failed rollout."""

    def rollout_status(self, deployment: str) -> bool:
        return False

    def rollout_undo(self, deployment: str) -> None:
        self.rollback_called = True


class TestDeploymentService:
    def test_successful_rollout_returns_true(self) -> None:
        kubectl = FakeKubectlPort()
        service = DeploymentService(kubectl_port=kubectl)
        result = service.execute("my-deployment")
        assert result is True

    def test_failed_rollout_raises_deployment_failed_error(self) -> None:
        kubectl = FakeKubectlPortFailingRollout()
        service = DeploymentService(kubectl_port=kubectl)
        with pytest.raises(DeploymentFailedError):
            service.execute("my-deployment")

    def test_failed_rollout_triggers_rollback(self) -> None:
        kubectl = FakeKubectlPortFailingRollout()
        kubectl.rollback_called = False
        service = DeploymentService(kubectl_port=kubectl)
        with pytest.raises(DeploymentFailedError):
            service.execute("my-deployment")
        assert kubectl.rollback_called is True

    def test_deployment_name_in_error_message(self) -> None:
        kubectl = FakeKubectlPortFailingRollout()
        service = DeploymentService(kubectl_port=kubectl)
        with pytest.raises(DeploymentFailedError) as exc_info:
            service.execute("my-deployment")
        assert "my-deployment" in str(exc_info.value)
