#!/bin/bash
set -e

echo "=== Cloud Bookstore K8s Deployment ==="

echo "[1/6] Building Docker images..."
docker build -t bookstore-backend:latest ./backend
docker build -t bookstore-frontend:latest ./frontend

echo "[2/6] Creating namespace and configs..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

echo "[3/6] Creating persistent storage..."
kubectl apply -f k8s/postgres-pvc.yaml

echo "[4/6] Deploying PostgreSQL and Redis..."
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
echo "  Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n bookstore --timeout=120s
echo "  Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n bookstore --timeout=120s

echo "[5/6] Deploying backend and frontend..."
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
echo "  Waiting for backend pods..."
kubectl wait --for=condition=ready pod -l app=backend -n bookstore --timeout=120s
echo "  Waiting for frontend pods..."
kubectl wait --for=condition=ready pod -l app=frontend -n bookstore --timeout=120s

echo "[6/6] Applying Ingress and HPA..."
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

echo ""
echo "=== Deployment Complete ==="
echo ""
kubectl get all -n bookstore
echo ""
FRONTEND_PORT=$(kubectl get svc frontend-service -n bookstore -o jsonpath='{.spec.ports[0].nodePort}')
echo "Access the bookstore at: http://localhost:${FRONTEND_PORT}"
