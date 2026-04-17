from unittest.mock import mock_open, patch

from storectl.adapters.outbound.proc_metrics_adapter import ProcMetricsAdapter
from tests.conftest import make_node

PROC_STAT = "cpu  100 0 50 850 0 0 0 0 0 0\n"
PROC_MEMINFO = (
    "MemTotal:       4096000 kB\n"
    "MemFree:        2048000 kB\n"
    "MemAvailable:   3000000 kB\n"
)


class TestProcMetricsAdapterCpu:
    def test_returns_cpu_usage_string(self) -> None:
        with patch("builtins.open", mock_open(read_data=PROC_STAT)):
            adapter = ProcMetricsAdapter()
            result = adapter.get_cpu_usage(make_node())
        assert isinstance(result, str)
        assert result.endswith("m")

    def test_cpu_usage_is_percentage_in_millicores(self) -> None:
        with patch("builtins.open", mock_open(read_data=PROC_STAT)):
            adapter = ProcMetricsAdapter()
            result = adapter.get_cpu_usage(make_node())
        value = int(result.rstrip("m"))
        assert 0 <= value <= 100_000


class TestProcMetricsAdapterMemory:
    def test_returns_memory_usage_string(self) -> None:
        with patch("builtins.open", mock_open(read_data=PROC_MEMINFO)):
            adapter = ProcMetricsAdapter()
            result = adapter.get_memory_usage(make_node())
        assert isinstance(result, str)
        assert "Mi" in result

    def test_memory_usage_is_used_memory(self) -> None:
        with patch("builtins.open", mock_open(read_data=PROC_MEMINFO)):
            adapter = ProcMetricsAdapter()
            result = adapter.get_memory_usage(make_node())
        # MemTotal - MemFree = 4096000 - 2048000 = 2048000 kB = 2000 Mi
        value = int(result.rstrip("Mi"))
        assert value == 2000
