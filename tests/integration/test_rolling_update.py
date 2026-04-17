import pytest

from storectl.application.rolling_update import RollingUpdateUseCase
from storectl.domain.exceptions import DeploymentFailedError
from storectl.ports.inbound.i_deployment_use_case import IDeploymentUseCase
from tests.conftest import FakeDeploymentPort


class FakeDeploymentPortFailingRollout(FakeDeploymentPort):
    def __init__(self) -> None:
        super().__init__(rollout_succeeds=False)
        self.rollback_called = False

    def rollout_undo(self, deployment: str, namespace: str = "default") -> None:
        self.rollback_called = True


class TestRollingUpdateUseCase:
    def test_implements_inbound_port(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeDeploymentPort())
        assert isinstance(use_case, IDeploymentUseCase)

    def test_successful_update_returns_true(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeDeploymentPort())
        result = use_case.execute("my-deployment", namespace="default")
        assert result is True

    def test_failed_update_raises_deployment_failed_error(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeDeploymentPortFailingRollout())
        with pytest.raises(DeploymentFailedError):
            use_case.execute("my-deployment", namespace="default")

    def test_failed_update_triggers_rollback(self) -> None:
        kubectl = FakeDeploymentPortFailingRollout()
        use_case = RollingUpdateUseCase(kubectl_port=kubectl)
        with pytest.raises(DeploymentFailedError):
            use_case.execute("my-deployment", namespace="default")
        assert kubectl.rollback_called is True

    def test_error_contains_deployment_name(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeDeploymentPortFailingRollout())
        with pytest.raises(DeploymentFailedError) as exc_info:
            use_case.execute("my-deployment", namespace="default")
        assert "my-deployment" in str(exc_info.value)
