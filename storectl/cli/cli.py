import argparse
import sys

from rich.console import Console
from rich.table import Table

from storectl.adapters.outbound.journalctl_adapter import JournalctlAdapter
from storectl.adapters.outbound.kubectl_deployment_adapter import KubectlDeploymentAdapter
from storectl.adapters.outbound.kubectl_node_adapter import KubectlNodeAdapter
from storectl.adapters.outbound.proc_metrics_adapter import ProcMetricsAdapter
from storectl.application.diagnose_node import DiagnoseNodeUseCase
from storectl.application.monitor_cluster import MonitorClusterUseCase
from storectl.application.rolling_update import RollingUpdateUseCase
from storectl.domain.exceptions import DeploymentFailedError, NodeNotFoundError

console = Console()


def _cmd_monitor() -> int:
    use_case = MonitorClusterUseCase(
        kubectl_port=KubectlNodeAdapter(),
        metrics_port=ProcMetricsAdapter(),
    )
    status = use_case.execute()
    table = Table(title="Cluster Status")
    table.add_column("Node")
    table.add_column("Status")
    table.add_column("CPU")
    table.add_column("Memory")
    for node in status.nodes:
        table.add_row(node.name, node.status.value, node.cpu_usage, node.memory_usage)
    console.print(table)
    return 0 if status.is_healthy() else 1


def _cmd_diagnose(node_name: str) -> int:
    use_case = DiagnoseNodeUseCase(
        kubectl_port=KubectlNodeAdapter(),
        log_port=JournalctlAdapter(),
    )
    try:
        report = use_case.execute(node_name)
    except NodeNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        return 2
    console.print(f"Node:       {report.node_name}")
    console.print(f"Severity:   {report.severity.value}")
    console.print(f"Root cause: {report.root_cause}")
    for detail in report.details:
        console.print(f"  {detail}")
    return 1 if report.is_critical() else 0


def _cmd_update(deployment: str, namespace: str = "default") -> int:
    use_case = RollingUpdateUseCase(kubectl_port=KubectlDeploymentAdapter())
    try:
        use_case.execute(deployment, namespace=namespace)
    except DeploymentFailedError as e:
        console.print(f"[red]Deployment failed:[/red] {e}")
        return 1
    console.print(f"[green]Deployment {deployment} updated successfully.[/green]")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="storectl", description="Storage cluster control CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("monitor", help="Check cluster health")

    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose a node")
    diagnose_parser.add_argument("node", help="Node name")

    update_parser = subparsers.add_parser("update", help="Rolling update a deployment")
    update_parser.add_argument("deployment", help="Deployment name")
    update_parser.add_argument("--namespace", "-n", default="default", help="Kubernetes namespace")

    args = parser.parse_args()

    if args.command == "monitor":
        return _cmd_monitor()
    if args.command == "diagnose":
        return _cmd_diagnose(args.node)
    if args.command == "update":
        return _cmd_update(args.deployment, namespace=args.namespace)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
