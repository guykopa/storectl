import pytest

from storectl.application.rolling_update import RollingUpdateUseCase
from storectl.domain.exceptions import DeploymentFailedError
from storectl.ports.inbound.i_deployment_use_case import IDeploymentUseCase
from tests.conftest import FakeKubectlPort


class FakeKubectlPortFailingRollout(FakeKubectlPort):
    def __init__(self) -> None:
        super().__init__()
        self.rollback_called = False

    def rollout_status(self, deployment: str) -> bool:
        return False

    def rollout_undo(self, deployment: str) -> None:
        self.rollback_called = True


class TestRollingUpdateUseCase:
    def test_implements_inbound_port(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeKubectlPort())
        assert isinstance(use_case, IDeploymentUseCase)

    def test_successful_update_returns_true(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeKubectlPort())
        result = use_case.execute("my-deployment")
        assert result is True

    def test_failed_update_raises_deployment_failed_error(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeKubectlPortFailingRollout())
        with pytest.raises(DeploymentFailedError):
            use_case.execute("my-deployment")

    def test_failed_update_triggers_rollback(self) -> None:
        kubectl = FakeKubectlPortFailingRollout()
        use_case = RollingUpdateUseCase(kubectl_port=kubectl)
        with pytest.raises(DeploymentFailedError):
            use_case.execute("my-deployment")
        assert kubectl.rollback_called is True

    def test_error_contains_deployment_name(self) -> None:
        use_case = RollingUpdateUseCase(kubectl_port=FakeKubectlPortFailingRollout())
        with pytest.raises(DeploymentFailedError) as exc_info:
            use_case.execute("my-deployment")
        assert "my-deployment" in str(exc_info.value)
