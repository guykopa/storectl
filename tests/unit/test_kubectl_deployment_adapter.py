from unittest.mock import MagicMock, patch

from storectl.adapters.outbound.kubectl_deployment_adapter import KubectlDeploymentAdapter


def make_completed_process(stdout: str, returncode: int = 0) -> MagicMock:
    mock = MagicMock()
    mock.stdout = stdout
    mock.returncode = returncode
    return mock


class TestKubectlDeploymentAdapterRollout:
    def test_rollout_calls_kubectl(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("")
            adapter = KubectlDeploymentAdapter()
            adapter.rollout("my-deployment", namespace="default")
        args = mock_run.call_args[0][0]
        assert "rollout" in args
        assert "my-deployment" in " ".join(args)

    def test_rollout_passes_namespace(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("")
            adapter = KubectlDeploymentAdapter()
            adapter.rollout("my-deployment", namespace="storectl")
        args = mock_run.call_args[0][0]
        assert "-n" in args
        assert "storectl" in args

    def test_rollout_status_true_when_success(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("", returncode=0)
            adapter = KubectlDeploymentAdapter()
            assert adapter.rollout_status("my-deployment", namespace="default") is True

    def test_rollout_status_false_when_failure(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("", returncode=1)
            adapter = KubectlDeploymentAdapter()
            assert adapter.rollout_status("my-deployment", namespace="default") is False

    def test_rollout_status_passes_namespace(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("", returncode=0)
            adapter = KubectlDeploymentAdapter()
            adapter.rollout_status("my-deployment", namespace="kube-system")
        args = mock_run.call_args[0][0]
        assert "-n" in args
        assert "kube-system" in args

    def test_rollout_undo_calls_kubectl(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("")
            adapter = KubectlDeploymentAdapter()
            adapter.rollout_undo("my-deployment", namespace="default")
        args = mock_run.call_args[0][0]
        assert "undo" in args

    def test_rollout_undo_passes_namespace(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("")
            adapter = KubectlDeploymentAdapter()
            adapter.rollout_undo("my-deployment", namespace="storectl")
        args = mock_run.call_args[0][0]
        assert "-n" in args
        assert "storectl" in args
