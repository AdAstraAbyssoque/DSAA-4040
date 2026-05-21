#!/usr/bin/env bash
set -euo pipefail

TARGET="${TARGET:-auto}"
NAMESPACE="${NAMESPACE:-bookstore}"
BACKEND_IMAGE="${BACKEND_IMAGE:-bookstore-backend:latest}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-bookstore-frontend:latest}"
K3S_CONTAINER="${K3S_CONTAINER:-dsaa4040-k3s-server}"

if [ "${TARGET}" = "auto" ]; then
  if command -v minikube >/dev/null 2>&1; then
    TARGET="minikube"
  elif docker ps --format '{{.Names}}' | grep -qx "${K3S_CONTAINER}"; then
    TARGET="k3s-docker"
  else
    TARGET="kubectl"
  fi
fi

case "${TARGET}" in
  minikube)
    KUBECTL=(kubectl)
    ;;
  k3s-docker)
    KUBECTL=(docker exec "${K3S_CONTAINER}" kubectl)
    ;;
  kubectl)
    KUBECTL=(kubectl)
    ;;
  *)
    echo "Unknown TARGET=${TARGET}. Use auto, minikube, k3s-docker, or kubectl." >&2
    exit 2
    ;;
esac

run_kubectl() {
  "${KUBECTL[@]}" "$@"
}

apply_file() {
  if [ "${TARGET}" = "k3s-docker" ]; then
    docker exec -i "${K3S_CONTAINER}" kubectl apply -f - < "$1"
  else
    run_kubectl apply -f "$1"
  fi
}

echo "=== Cloud Bookstore Kubernetes Deployment ==="
echo "Target: ${TARGET}"

if [ "${TARGET}" = "minikube" ]; then
  echo "[0/7] Starting Minikube and enabling addons..."
  minikube status >/dev/null 2>&1 || minikube start
  minikube addons enable ingress
  minikube addons enable metrics-server
fi

echo "[1/7] Building Docker images..."
docker build -t "${BACKEND_IMAGE}" ./backend
docker build -t "${FRONTEND_IMAGE}" ./frontend

echo "[2/7] Loading images into the Kubernetes runtime..."
case "${TARGET}" in
  minikube)
    minikube image load "${BACKEND_IMAGE}"
    minikube image load "${FRONTEND_IMAGE}"
    ;;
  k3s-docker)
    docker save "${BACKEND_IMAGE}" "${FRONTEND_IMAGE}" | docker exec -i "${K3S_CONTAINER}" ctr images import -
    ;;
  kubectl)
    echo "Skipping image load for generic kubectl target. Ensure images are available to the cluster."
    ;;
esac

echo "[3/7] Creating namespace and configuration..."
apply_file k8s/namespace.yaml
apply_file k8s/configmap.yaml
apply_file k8s/secret.yaml

echo "[4/7] Creating persistent storage..."
apply_file k8s/postgres-pvc.yaml

echo "[5/7] Deploying PostgreSQL and Redis..."
apply_file k8s/postgres-deployment.yaml
apply_file k8s/redis-deployment.yaml
run_kubectl wait --for=condition=ready pod -l app=postgres -n "${NAMESPACE}" --timeout=180s
run_kubectl wait --for=condition=ready pod -l app=redis -n "${NAMESPACE}" --timeout=120s

echo "[6/7] Deploying backend and frontend..."
apply_file k8s/backend-deployment.yaml
apply_file k8s/frontend-deployment.yaml
run_kubectl rollout restart deployment/backend -n "${NAMESPACE}"
run_kubectl rollout restart deployment/frontend -n "${NAMESPACE}"
run_kubectl rollout status deployment/backend -n "${NAMESPACE}" --timeout=180s
run_kubectl rollout status deployment/frontend -n "${NAMESPACE}" --timeout=180s

echo "[7/7] Applying Ingress and HPA..."
apply_file k8s/ingress.yaml
apply_file k8s/hpa.yaml
run_kubectl get pods -n "${NAMESPACE}" -o wide
run_kubectl get svc -n "${NAMESPACE}"
run_kubectl get ingress -n "${NAMESPACE}"
run_kubectl get hpa -n "${NAMESPACE}"

echo ""
echo "=== Deployment Complete ==="
if [ "${TARGET}" = "minikube" ]; then
  NODE_IP="$(minikube ip)"
  echo "NodePort: http://${NODE_IP}:30080"
  echo "Ingress:  http://bookstore.local/ after adding '${NODE_IP} bookstore.local' to /etc/hosts"
elif [ "${TARGET}" = "k3s-docker" ]; then
  echo "NodePort: http://localhost:30080"
  echo "Ingress:  http://localhost:18081"
else
  echo "NodePort: http://<node-ip>:30080"
fi
