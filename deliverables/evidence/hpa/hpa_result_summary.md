# HPA Load Test Result Summary

Environment: single-node K3s in Docker with Traefik and metrics-server enabled.

Load generator:

- Source: in-cluster Pod `bookstore-hpa-load`
- Target: `http://backend-service:8000/api/diagnostics/cpu?iterations=6000000`
- Duration: 240 seconds
- Parallel workers: 14
- Purpose: generate controlled CPU pressure for backend HPA validation

Observed autoscaling timeline:

| UTC Time | Backend HPA CPU Target | Backend Replicas | Evidence |
| --- | --- | ---: | --- |
| 17:07:10 | `2%/60%` | 2 | baseline before load |
| 17:07:55 | `231%/60%` | 2 | CPU spike detected |
| 17:08:11 | `463%/60%` | 4 | HPA scaled backend from 2 to 4 |
| 17:08:26 | `462%/60%` | 8 | HPA reached configured max replicas |
| 17:09:12 | `231%/60%` | 8 | load distributed across 8 backend Pods |
| 17:12:16 | `2%/60%` | 8 | load ended; downscale delay observed |

Key findings:

- metrics-server was working: HPA displayed resolved CPU utilization values instead of `<unknown>`.
- The backend HPA reacted to CPU load and increased backend replicas from 2 to 8.
- `kubectl top pods` showed backend CPU rising from a few millicores to hundreds of millicores per Pod during load.
- After load stopped, CPU returned to around 2%, while replicas remained temporarily at 8 due to Kubernetes HPA downscale stabilization behavior.

Evidence files:

- `hpa_before.txt`: baseline HPA state
- `hpa_watch.txt`: 15-second HPA samples during and after load
- `pod_watch.txt`: backend Pod count and readiness over time
- `top_watch.txt`: CPU/memory samples over time
- `pods_after.txt`: final Pod state after the test
- `top_after.txt`: final CPU/memory state after the test
