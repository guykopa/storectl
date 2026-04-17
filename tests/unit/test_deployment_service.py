import pytest

from storectl.domain.exceptions import DeploymentFailedError
from storectl.domain.services.deployment_service import DeploymentService
from tests.conftest import FakeDeploymentPort


class FakeDeploymentPortFailingRollout(FakeDeploymentPort):
    """Deployment port that simulates a failed rollout."""

    def __init__(self) -> None:
        super().__init__(rollout_succeeds=False)
        self.rollback_called = False

    def rollout_undo(self, deployment: str, namespace: str = "default") -> None:
        self.rollback_called = True


class TestDeploymentService:
    def test_successful_rollout_returns_true(self) -> None:
        service = DeploymentService(kubectl_port=FakeDeploymentPort())
        result = service.execute("my-deployment", namespace="default")
        assert result is True

    def test_failed_rollout_raises_deployment_failed_error(self) -> None:
        service = DeploymentService(kubectl_port=FakeDeploymentPortFailingRollout())
        with pytest.raises(DeploymentFailedError):
            service.execute("my-deployment", namespace="default")

    def test_failed_rollout_triggers_rollback(self) -> None:
        kubectl = FakeDeploymentPortFailingRollout()
        service = DeploymentService(kubectl_port=kubectl)
        with pytest.raises(DeploymentFailedError):
            service.execute("my-deployment", namespace="default")
        assert kubectl.rollback_called is True

    def test_deployment_name_in_error_message(self) -> None:
        service = DeploymentService(kubectl_port=FakeDeploymentPortFailingRollout())
        with pytest.raises(DeploymentFailedError) as exc_info:
            service.execute("my-deployment", namespace="default")
        assert "my-deployment" in str(exc_info.value)

    def test_namespace_forwarded_to_port(self) -> None:
        received: list[tuple[str, str]] = []

        class TrackingPort(FakeDeploymentPort):
            def rollout(self, deployment: str, namespace: str = "default") -> None:
                received.append(("rollout", namespace))

            def rollout_status(self, deployment: str, namespace: str = "default") -> bool:
                received.append(("status", namespace))
                return True

        service = DeploymentService(kubectl_port=TrackingPort())
        service.execute("my-deployment", namespace="storectl")
        assert all(ns == "storectl" for _, ns in received)
