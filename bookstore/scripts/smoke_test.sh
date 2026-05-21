#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:30080}"
NAMESPACE="${NAMESPACE:-bookstore}"
SESSION_ID="${SESSION_ID:-smoke-$(date +%s)}"
KUBECTL="${KUBECTL:-kubectl}"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

echo "=== Bookstore Smoke Test ==="
echo "Base URL: ${BASE_URL}"
echo "Session:  ${SESSION_ID}"

echo "[1/6] Health check"
curl -fsS "${BASE_URL}/api/health" | tee "${tmp_dir}/health.json"
grep -q '"status":"ok"' "${tmp_dir}/health.json"

echo "[2/6] List books"
curl -fsS "${BASE_URL}/api/books" | tee "${tmp_dir}/books.json" >/dev/null
grep -q '"title"' "${tmp_dir}/books.json"

echo "[3/6] Add item to cart"
curl -fsS -X POST "${BASE_URL}/api/cart" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"${SESSION_ID}\",\"book_id\":1,\"quantity\":1}" \
  | tee "${tmp_dir}/cart_add.json"

echo "[4/6] Read cart"
curl -fsS "${BASE_URL}/api/cart?session_id=${SESSION_ID}" | tee "${tmp_dir}/cart.json" >/dev/null
grep -q '"book_id":1' "${tmp_dir}/cart.json"

echo "[5/6] Place order"
curl -fsS -X POST "${BASE_URL}/api/orders" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"${SESSION_ID}\"}" \
  | tee "${tmp_dir}/order.json"
grep -q '"status":"confirmed"' "${tmp_dir}/order.json"

echo "[6/6] Query orders"
curl -fsS "${BASE_URL}/api/orders?session_id=${SESSION_ID}" | tee "${tmp_dir}/orders.json" >/dev/null
grep -q "\"session_id\":\"${SESSION_ID}\"" "${tmp_dir}/orders.json"

postgres_pod="$(${KUBECTL} get pod -n "${NAMESPACE}" -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"
if [ -n "${postgres_pod}" ]; then
  echo "[extra] PostgreSQL order count"
  ${KUBECTL} exec -n "${NAMESPACE}" "${postgres_pod}" -- \
    psql -U bookstore -d bookstore -tAc "select count(*) from orders where session_id='${SESSION_ID}';"
fi

echo "Smoke test passed."
