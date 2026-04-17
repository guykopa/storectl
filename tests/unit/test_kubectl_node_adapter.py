import json
from unittest.mock import MagicMock, patch

import pytest

from storectl.domain.exceptions import NodeNotFoundError
from storectl.domain.models.node import NodeStatus
from storectl.adapters.outbound.kubectl_node_adapter import KubectlNodeAdapter

NODES_JSON = {
    "items": [
        {
            "metadata": {"name": "node-1"},
            "status": {
                "conditions": [{"type": "Ready", "status": "True"}],
                "capacity": {"cpu": "2", "memory": "4Gi"},
            },
        }
    ]
}

NODE_JSON = {
    "metadata": {"name": "node-1"},
    "status": {
        "conditions": [{"type": "Ready", "status": "True"}],
        "capacity": {"cpu": "2", "memory": "4Gi"},
    },
}

NODE_NOT_READY_JSON = {
    "metadata": {"name": "node-2"},
    "status": {
        "conditions": [{"type": "Ready", "status": "False"}],
        "capacity": {"cpu": "2", "memory": "4Gi"},
    },
}


def make_completed_process(stdout: str, returncode: int = 0) -> MagicMock:
    mock = MagicMock()
    mock.stdout = stdout
    mock.returncode = returncode
    return mock


class TestKubectlNodeAdapterGetNodes:
    def test_returns_list_of_nodes(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(json.dumps(NODES_JSON))
            adapter = KubectlNodeAdapter()
            nodes = adapter.get_nodes()
        assert len(nodes) == 1
        assert nodes[0].name == "node-1"

    def test_node_status_ready(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(json.dumps(NODES_JSON))
            adapter = KubectlNodeAdapter()
            nodes = adapter.get_nodes()
        assert nodes[0].status == NodeStatus.READY

    def test_node_status_not_ready(self) -> None:
        data = {"items": [NODE_NOT_READY_JSON]}
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(json.dumps(data))
            adapter = KubectlNodeAdapter()
            nodes = adapter.get_nodes()
        assert nodes[0].status == NodeStatus.NOT_READY

    def test_subprocess_called_with_correct_args(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(json.dumps(NODES_JSON))
            adapter = KubectlNodeAdapter()
            adapter.get_nodes()
        args = mock_run.call_args[0][0]
        assert "kubectl" in args
        assert "get" in args
        assert "nodes" in args
        assert "-o" in args
        assert "json" in args


class TestKubectlNodeAdapterDescribeNode:
    def test_returns_node(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process(json.dumps(NODE_JSON))
            adapter = KubectlNodeAdapter()
            node = adapter.describe_node("node-1")
        assert node.name == "node-1"

    def test_raises_node_not_found_on_error(self) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = make_completed_process("", returncode=1)
            adapter = KubectlNodeAdapter()
            with pytest.raises(NodeNotFoundError):
                adapter.describe_node("node-99")
