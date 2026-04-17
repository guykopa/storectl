from storectl.domain.exceptions.base import StorectlError


class DeploymentFailedError(StorectlError):
    """Raised when a deployment fails or cannot be rolled out."""

    def __init__(self, deployment_name: str) -> None:
        super().__init__(f"Deployment failed: {deployment_name}")
