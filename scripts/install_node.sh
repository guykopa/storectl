#!/bin/bash
set -euo pipefail

NODE_NAME="${1:?Usage: install_node.sh <node-name>}"

echo "Installing storectl agent on node: ${NODE_NAME}"

kubectl get node "${NODE_NAME}" > /dev/null

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

echo "Waiting for rollout..."
kubectl rollout status deployment/storectl -n storectl --timeout=120s

echo "storectl agent installed on ${NODE_NAME}"
