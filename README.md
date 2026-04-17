# storectl

CLI tool for monitoring, diagnosing, and managing a distributed object storage cluster on Kubernetes.

**Documentation:** [https://guykopa.github.io/storectl/](https://guykopa.github.io/storectl/)

## Installation

```bash
git clone <repo>
cd storectl
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or: pip install rich pyyaml
```

## Usage

```bash
source .venv/bin/activate
```

### Monitor cluster health

```bash
python -m storectl.cli.cli monitor
```

Displays the status of every node with CPU and memory usage.
Exits 0 if all nodes are ready, 1 if any node is degraded.

### Diagnose a node

```bash
python -m storectl.cli.cli diagnose <node-name>
```

Analyses system logs for the given node and returns a root cause report.
Exits 0 if INFO, 1 if CRITICAL, 2 if node not found.

### Rolling update a deployment

```bash
python -m storectl.cli.cli update <deployment-name> --namespace <namespace>
```

Performs a rolling update and automatically rolls back on failure.
`--namespace` / `-n` defaults to `default`.
Exits 0 on success, 1 on failure.

**Examples:**
```bash
python -m storectl.cli.cli update storectl --namespace storectl
python -m storectl.cli.cli update coredns --namespace kube-system
```

### Bash scripts

```bash
scripts/health_check.sh                      # quick cluster health check
scripts/install_node.sh <node-name>          # install storectl agent on a node
scripts/rolling_update.sh <deployment>       # rolling update with rollback
```

## Architecture

storectl uses Hexagonal Architecture (Ports & Adapters):

```
cli/ → application/ → domain/ → ports/ ← adapters/
                                            KubectlNodeAdapter      (kubectl node ops)
                                            KubectlDeploymentAdapter(kubectl rollout ops)
                                            ProcMetricsAdapter      (/proc)
                                            JournalctlAdapter       (journalctl)
```

- `domain/` — pure Python business logic, no infrastructure
- `ports/` — abstract interfaces: `INodePort`, `IDeploymentPort`, `INodeMetricsPort`, `ILogReaderPort`
- `adapters/` — concrete implementations, one responsibility per adapter
- `application/` — use cases that orchestrate domain services
- `cli/` — entry point, wires adapters into use cases

SOLID principles are strictly applied: each port and adapter has a single responsibility,
and every client depends only on the interface it actually uses (Interface Segregation).

See `ARCHITECTURE.md` for full details.

## Development

### Run tests

```bash
pytest tests/
pytest tests/unit/
pytest tests/integration/
pytest tests/non_regression/
```

### TDD cycle

This project enforces TDD strictly — every file has its test written first:

1. RED: write a failing test
2. GREEN: write the minimum code to pass
3. REFACTOR: clean without breaking tests

Never write implementation code before the corresponding test exists.

### Lint

```bash
flake8 storectl/ --max-line-length=100
mypy storectl/ --ignore-missing-imports
```

## Stack

- Python 3.11+
- pytest, pytest-cov
- flake8, mypy
- rich
- pyyaml
- minikube (integration tests)
