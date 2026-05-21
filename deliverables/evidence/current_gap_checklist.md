# E1 Completion Gap Checklist

Final status after the recovery pass:

- Code exists for frontend, backend, PostgreSQL, Redis, Docker Compose, and Kubernetes manifests.
- Docker Compose has been run and verified end to end.
- Kubernetes has been run on a local K3s cluster with Traefik enabled.
- NodePort and Traefik Ingress access were both verified.
- ConfigMap, Secret, PVC, Deployment, Service, Ingress, probes, resource limits, and HPA were verified.
- HPA autoscaling was tested with a controlled in-cluster CPU load and backend scaled from 2 replicas to 8 replicas.
- Frontend and backend Pod recovery were tested by deleting Pods and waiting for Deployment recovery.
- PostgreSQL PVC persistence was tested by creating an order, restarting the PostgreSQL Pod, and reading the order afterward.
- Final report PDF is kept as a local review copy at `deliverables/report/final_report.pdf` and is intentionally not pushed before review.
- Final demo video has been generated at `deliverables/video/final_demo.mp4`.

Residual limitations:

1. PostgreSQL is single-Pod local storage, so database restart is not zero-downtime.
2. HPA load testing used a diagnostics CPU endpoint, not real user browsing traffic.
3. The demo video is an edited screen/evidence walkthrough, not a live narrated screen recording.
