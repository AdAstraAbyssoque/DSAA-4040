#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-bookstore}"
DURATION_SECONDS="${DURATION_SECONDS:-300}"
WORKERS="${WORKERS:-10}"
ITERATIONS="${ITERATIONS:-4500000}"
LOAD_POD="${LOAD_POD:-bookstore-hpa-load}"
OUT_DIR="${OUT_DIR:-../deliverables/evidence/hpa}"

mkdir -p "${OUT_DIR}"

kubectl_cmd="${KUBECTL:-kubectl}"

echo "=== Bookstore HPA Load Test ==="
echo "Namespace:  ${NAMESPACE}"
echo "Duration:   ${DURATION_SECONDS}s"
echo "Workers:    ${WORKERS}"
echo "Iterations: ${ITERATIONS}"
echo "Output:     ${OUT_DIR}"

${kubectl_cmd} -n "${NAMESPACE}" delete pod "${LOAD_POD}" --ignore-not-found=true >/dev/null
${kubectl_cmd} -n "${NAMESPACE}" scale deployment/backend --replicas=2
${kubectl_cmd} -n "${NAMESPACE}" rollout status deployment/backend --timeout=180s

echo "[before] Capturing Kubernetes state"
${kubectl_cmd} -n "${NAMESPACE}" get pods -o wide > "${OUT_DIR}/pods_before.txt"
${kubectl_cmd} -n "${NAMESPACE}" get hpa > "${OUT_DIR}/hpa_before.txt"
${kubectl_cmd} -n "${NAMESPACE}" top pods > "${OUT_DIR}/top_before.txt" || true
${kubectl_cmd} -n kube-system get pods > "${OUT_DIR}/kube_system_pods.txt" || true

echo "[load] Starting in-cluster curl load pod"
${kubectl_cmd} -n "${NAMESPACE}" run "${LOAD_POD}" \
  --image=curlimages/curl:8.11.1 \
  --restart=Never \
  --command -- sh -c "
    end=\$((\$(date +%s) + ${DURATION_SECONDS}));
    while [ \$(date +%s) -lt \$end ]; do
      i=0;
      while [ \$i -lt ${WORKERS} ]; do
        curl -fsS 'http://backend-service:8000/api/diagnostics/cpu?iterations=${ITERATIONS}' >/dev/null &
        i=\$((i + 1));
      done;
      wait;
    done
  "

echo "[watch] Sampling HPA and pod state"
: > "${OUT_DIR}/hpa_watch.txt"
: > "${OUT_DIR}/pod_watch.txt"
: > "${OUT_DIR}/top_watch.txt"
end_time=$((SECONDS + DURATION_SECONDS + 120))
while [ "${SECONDS}" -lt "${end_time}" ]; do
  {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
    ${kubectl_cmd} -n "${NAMESPACE}" get hpa
    echo
  } >> "${OUT_DIR}/hpa_watch.txt"
  {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
    ${kubectl_cmd} -n "${NAMESPACE}" get pods -l app=backend -o wide
    echo
  } >> "${OUT_DIR}/pod_watch.txt"
  {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
    ${kubectl_cmd} -n "${NAMESPACE}" top pods 2>/dev/null || true
    echo
  } >> "${OUT_DIR}/top_watch.txt"
  sleep 15
done

${kubectl_cmd} -n "${NAMESPACE}" wait --for=condition=Ready pod/"${LOAD_POD}" --timeout=30s >/dev/null 2>&1 || true
${kubectl_cmd} -n "${NAMESPACE}" logs "${LOAD_POD}" > "${OUT_DIR}/load_pod.log" 2>&1 || true
${kubectl_cmd} -n "${NAMESPACE}" delete pod "${LOAD_POD}" --ignore-not-found=true >/dev/null

echo "[after] Capturing final Kubernetes state"
${kubectl_cmd} -n "${NAMESPACE}" get pods -o wide > "${OUT_DIR}/pods_after.txt"
${kubectl_cmd} -n "${NAMESPACE}" get hpa > "${OUT_DIR}/hpa_after.txt"
${kubectl_cmd} -n "${NAMESPACE}" top pods > "${OUT_DIR}/top_after.txt" || true

echo "HPA load test complete. Evidence written to ${OUT_DIR}."
