# storectl

CLI tool for monitoring, diagnosing, and managing a distributed object storage cluster on Kubernetes.

**Documentation:** [https://guykopa.github.io/storectl/](https://guykopa.github.io/storectl/)

## Installation

```bash
git clone <repo>
cd storectl
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Usage

### Monitor cluster health

```bash
storectl monitor
```

Displays the status of every node with CPU and memory usage.
Exits 0 if all nodes are ready, 1 if any node is degraded.

### Diagnose a node

```bash
storectl diagnose <node-name>
```

Analyses system logs for the given node and returns a root cause report.
Exits 0 if INFO, 1 if CRITICAL, 2 if node not found.

### Rolling update a deployment

```bash
storectl update <deployment-name>
```

Performs a rolling update and automatically rolls back on failure.
Exits 0 on success, 1 on failure.

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
                                            kubectl
                                            /proc
                                            journalctl
```

- `domain/` — pure Python business logic, no infrastructure
- `ports/` — abstract interfaces only
- `adapters/` — concrete implementations (kubectl, /proc, journalctl)
- `application/` — use cases that orchestrate domain services
- `cli/` — entry point, wires adapters into use cases

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
