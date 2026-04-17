import subprocess
from typing import List

from storectl.domain.models.node import Node
from storectl.ports.outbound.i_log_reader_port import ILogReaderPort

_TIMEOUT = 30


class JournalctlAdapter(ILogReaderPort):
    """Reads system logs via journalctl for a given node."""

    def get_logs(self, node: Node) -> List[str]:
        try:
            result = subprocess.run(
                ["journalctl", "-u", "kubelet", "--no-pager", "-n", "100"],
                capture_output=True, text=True, timeout=_TIMEOUT,
            )
        except FileNotFoundError:
            result = subprocess.run(
                ["kubectl", "get", "events", "--field-selector",
                 f"involvedObject.name={node.name}", "--no-headers"],
                capture_output=True, text=True, timeout=_TIMEOUT,
            )
        lines = result.stdout.splitlines()
        return [line for line in lines if line.strip()]
