import subprocess

from storectl.ports.outbound.i_deployment_port import IDeploymentPort

_TIMEOUT = 30


class KubectlDeploymentAdapter(IDeploymentPort):
    """Calls kubectl via subprocess to manage deployment rollouts."""

    def rollout(self, deployment: str, namespace: str = "default") -> None:
        subprocess.run(
            ["kubectl", "rollout", "restart", f"deployment/{deployment}", "-n", namespace],
            capture_output=True, text=True, timeout=_TIMEOUT,
        )

    def rollout_status(self, deployment: str, namespace: str = "default") -> bool:
        result = subprocess.run(
            ["kubectl", "rollout", "status", f"deployment/{deployment}", "-n", namespace],
            capture_output=True, text=True, timeout=_TIMEOUT,
        )
        return result.returncode == 0

    def rollout_undo(self, deployment: str, namespace: str = "default") -> None:
        subprocess.run(
            ["kubectl", "rollout", "undo", f"deployment/{deployment}", "-n", namespace],
            capture_output=True, text=True, timeout=_TIMEOUT,
        )
