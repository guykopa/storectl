#!/bin/bash
set -euo pipefail

echo "Running cluster health check..."

NOT_READY=$(kubectl get nodes --no-headers | grep -v " Ready" | wc -l || true)

if [ "${NOT_READY}" -gt 0 ]; then
    echo "DEGRADED: ${NOT_READY} node(s) not ready"
    kubectl get nodes
    exit 1
fi

echo "OK: all nodes are ready"
kubectl get nodes
exit 0
