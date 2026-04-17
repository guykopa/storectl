import pytest

from storectl.domain.exceptions import StorectlError, NodeNotFoundError, DeploymentFailedError


class TestStorectlError:
    def test_is_exception(self) -> None:
        with pytest.raises(StorectlError):
            raise StorectlError("base error")

    def test_message(self) -> None:
        error = StorectlError("base error")
        assert str(error) == "base error"


class TestNodeNotFoundError:
    def test_is_storectl_error(self) -> None:
        with pytest.raises(StorectlError):
            raise NodeNotFoundError("node-1")

    def test_message(self) -> None:
        error = NodeNotFoundError("node-1")
        assert "node-1" in str(error)


class TestDeploymentFailedError:
    def test_is_storectl_error(self) -> None:
        with pytest.raises(StorectlError):
            raise DeploymentFailedError("deploy-1")

    def test_message(self) -> None:
        error = DeploymentFailedError("deploy-1")
        assert "deploy-1" in str(error)
