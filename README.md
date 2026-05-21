# Cloud-Native Online Bookstore

> **DSAA 4040 Course Project — E1: Cloud-Native Online Bookstore on Kubernetes**
>
> Solo project · HKUST(GZ) · Spring 2026

## 1. Project Overview

A small but complete cloud-native online bookstore aligned with the submitted proposal:

- **Vue 3 SPA** for the user interface
- **FastAPI** backend for business logic and APIs
- **PostgreSQL** for persistent state
- **Redis** cache in front of read-heavy catalog endpoints
- **Single-node Minikube** deployment target with Kubernetes manifests

### Features

| Feature | Description |
|---------|-------------|
| Browse books | View a catalog of books with cover images, categories, and stock info |
| Search & filter | Search by title/author and filter by category |
| Book details | View detailed information for each book |
| Shopping cart | Add/remove items, update quantities |
| Place orders | Checkout with stock validation and order history |
| Health check | `/api/health` endpoint for readiness probes |
| Metrics | `/metrics` endpoint for Prometheus-style request counters |

### Architecture

```
Browser
  │
  ▼
Vue 3 SPA served by Nginx
  │ /api/*
  ▼
FastAPI backend
  ├── PostgreSQL: books, carts, orders
  └── Redis: cached catalog/category reads
```

### Tech Stack

- **Frontend**: Vue 3 + Vite + Bootstrap 5 + Nginx
- **Backend**: FastAPI + SQLAlchemy + Uvicorn
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes on single-node Minikube

## 2. Quick Start (Docker Compose)

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2+

### Steps

```bash
cd bookstore

# Build and start all services
docker compose up -d --build

# Wait ~15 seconds for PostgreSQL initialization, then access:
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000/api/health
```

### Stop

```bash
docker compose down        # Stop services
docker compose down -v     # Stop + remove volumes
```

## 3. Kubernetes Deployment

### Prerequisites

- Single-node Minikube
- `kubectl` CLI configured

### Deploy

```bash
cd bookstore

# Start Minikube, then build images into Minikube's Docker daemon
minikube start
eval $(minikube docker-env)
docker build -t bookstore-backend:latest ./backend
docker build -t bookstore-frontend:latest ./frontend

# Deploy step by step
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Wait for data services to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n bookstore --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n bookstore --timeout=120s

kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for all pods
kubectl wait --for=condition=ready pod -l app=backend -n bookstore --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n bookstore --timeout=120s

# Apply Ingress and HPA
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get all -n bookstore
```

Or use the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

Access via NodePort: `http://<node-ip>:30080`

For local Minikube:

```bash
minikube service frontend-service -n bookstore
```

### Kubernetes Resources

| Resource | File | Description |
|----------|------|-------------|
| Namespace | `namespace.yaml` | Isolated `bookstore` namespace |
| ConfigMap | `configmap.yaml` | PostgreSQL and Redis connection settings |
| Secret | `secret.yaml` | PostgreSQL credentials |
| PVC | `postgres-pvc.yaml` | 1Gi persistent storage for PostgreSQL |
| PostgreSQL | `postgres-deployment.yaml` | StatefulSet + headless Service |
| Redis | `redis-deployment.yaml` | Cache Deployment + Service |
| Backend | `backend-deployment.yaml` | FastAPI (2 replicas) + ClusterIP Service |
| Frontend | `frontend-deployment.yaml` | Vue/Nginx (2 replicas) + NodePort Service |
| Ingress | `ingress.yaml` | Path-based routing for `/api` and `/` |
| HPA | `hpa.yaml` | Auto-scaling for backend (2-8) and frontend (2-4) |

### Advanced Features

- **ConfigMap & Secret**: Database configuration separated from application code
- **Ingress**: Path-based routing (`/api/*` → backend, `/*` → frontend)
- **Redis cache**: Read-heavy catalog/category endpoints cached with short TTL
- **HPA**: Horizontal Pod Autoscaler for FastAPI backend (proposal target: min=2, max=8)
- **Readiness/Liveness Probes**: Health checks for all services
- **Resource Requests/Limits**: CPU and memory constraints for every container
- **PersistentVolumeClaim**: Durable PostgreSQL storage

## 4. API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/metrics` | Prometheus-style metrics |
| GET | `/api/books?q=&category=` | List/search books |
| GET | `/api/books/<id>` | Get book details |
| GET | `/api/categories` | List all categories |
| GET | `/api/cart?session_id=` | View cart |
| POST | `/api/cart` | Add item to cart |
| PUT | `/api/cart/<id>` | Update cart item quantity |
| DELETE | `/api/cart/<id>` | Remove cart item |
| POST | `/api/orders` | Place an order |
| GET | `/api/orders?session_id=` | List orders |

## 5. Project Structure

```
bookstore/
├── backend/
│   ├── app.py              # FastAPI application with all routes and models
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container image
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Vue 3 SPA
│   │   └── main.js         # Vue app entrypoint
│   ├── index.html          # Vite HTML entrypoint
│   ├── package.json        # Frontend dependencies
│   ├── nginx.conf          # Nginx reverse proxy configuration
│   └── Dockerfile          # Frontend container image
├── k8s/
│   ├── namespace.yaml      # Kubernetes namespace
│   ├── configmap.yaml      # Application configuration
│   ├── secret.yaml         # Sensitive credentials
│   ├── postgres-pvc.yaml   # Persistent storage
│   ├── postgres-deployment.yaml # PostgreSQL StatefulSet + Service
│   ├── redis-deployment.yaml    # Redis cache Deployment + Service
│   ├── backend-deployment.yaml  # Backend Deployment + Service
│   ├── frontend-deployment.yaml # Frontend Deployment + Service
│   ├── ingress.yaml        # Ingress routing rules
│   └── hpa.yaml            # Horizontal Pod Autoscaler
├── docker-compose.yaml     # Local development deployment
├── deploy.sh               # Kubernetes deployment script
└── README.md               # This file
```

## 6. Database Schema

```
books          cart_items         orders          order_items
├── id         ├── id             ├── id          ├── id
├── title      ├── session_id     ├── session_id  ├── order_id (FK)
├── author     ├── book_id (FK)   ├── total_price ├── book_id (FK)
├── price      └── quantity       ├── status      ├── quantity
├── stock                         └── created_at  └── price
├── category
├── description
└── cover_url
```

## 7. Milestone 2 Demo Plan

For the May 7 progress presentation:

1. Show the architecture slide: Vue 3 → FastAPI → PostgreSQL + Redis on Minikube.
2. Start from a clean `docker compose up -d --build` demo if live Minikube is not available.
3. Open the homepage and point out the live deployment snapshot / health strip.
4. Search/filter books, open detail modal, add two books to cart.
5. Place an order and show order history.
6. Explain Kubernetes resources: Deployment/Service/ConfigMap/Secret/PVC/Ingress/HPA.
7. If asked about advanced items: HPA and `/metrics` are wired; Prometheus/Grafana and k6 scenarios are planned for final submission.
