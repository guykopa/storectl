from storectl.domain.models.node import Node
from storectl.ports.outbound.i_node_metrics_port import INodeMetricsPort


class ProcMetricsAdapter(INodeMetricsPort):
    """Reads CPU and memory metrics from the local /proc filesystem."""

    def get_cpu_usage(self, node: Node) -> str:
        with open("/proc/stat") as f:
            line = f.readline()
        values = list(map(int, line.split()[1:]))
        total = sum(values)
        idle = values[3]
        used = total - idle
        millicores = int((used / total) * 1000) if total > 0 else 0
        return f"{millicores}m"

    def get_memory_usage(self, node: Node) -> str:
        stats: dict[str, int] = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                if parts[0].rstrip(":") in ("MemTotal", "MemFree"):
                    stats[parts[0].rstrip(":")] = int(parts[1])
        used_kb = stats.get("MemTotal", 0) - stats.get("MemFree", 0)
        used_mi = used_kb // 1024
        return f"{used_mi}Mi"
