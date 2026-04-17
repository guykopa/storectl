import json
import subprocess
from typing import List

from storectl.domain.exceptions import NodeNotFoundError
from storectl.domain.models.node import Node, NodeStatus
from storectl.ports.outbound.i_node_port import INodePort

_TIMEOUT = 30


def _parse_node_status(conditions: list) -> NodeStatus:
    for condition in conditions:
        if condition.get("type") == "Ready":
            return NodeStatus.READY if condition.get("status") == "True" else NodeStatus.NOT_READY
    return NodeStatus.UNKNOWN


def _parse_node(data: dict) -> Node:
    status = data["status"]
    return Node(
        name=data["metadata"]["name"],
        status=_parse_node_status(status.get("conditions", [])),
        cpu_capacity=status.get("capacity", {}).get("cpu", "0"),
        memory_capacity=status.get("capacity", {}).get("memory", "0"),
        cpu_usage="0",
        memory_usage="0",
    )


class KubectlNodeAdapter(INodePort):
    """Calls kubectl via subprocess to read node state from the cluster."""

    def get_nodes(self) -> List[Node]:
        result = subprocess.run(
            ["kubectl", "get", "nodes", "-o", "json"],
            capture_output=True, text=True, timeout=_TIMEOUT,
        )
        data = json.loads(result.stdout)
        return [_parse_node(item) for item in data["items"]]

    def describe_node(self, name: str) -> Node:
        result = subprocess.run(
            ["kubectl", "get", "node", name, "-o", "json"],
            capture_output=True, text=True, timeout=_TIMEOUT,
        )
        if result.returncode != 0:
            raise NodeNotFoundError(name)
        return _parse_node(json.loads(result.stdout))
