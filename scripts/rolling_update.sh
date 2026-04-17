#!/bin/bash
set -euo pipefail

DEPLOYMENT="${1:?Usage: rolling_update.sh <deployment-name>}"
NAMESPACE="${2:-default}"
TIMEOUT="${3:-120}"

echo "Starting rolling update: ${DEPLOYMENT} (namespace: ${NAMESPACE})"

kubectl rollout restart "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"

if ! kubectl rollout status "deployment/${DEPLOYMENT}" -n "${NAMESPACE}" --timeout="${TIMEOUT}s"; then
    echo "Rollout failed — rolling back ${DEPLOYMENT}"
    kubectl rollout undo "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"
    echo "Rollback complete"
    exit 1
fi

echo "Rollout successful: ${DEPLOYMENT}"
exit 0
