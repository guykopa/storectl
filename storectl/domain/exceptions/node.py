from storectl.domain.exceptions.base import StorectlError


class NodeNotFoundError(StorectlError):
    """Raised when a node cannot be found in the cluster."""

    def __init__(self, node_name: str) -> None:
        super().__init__(f"Node not found: {node_name}")
