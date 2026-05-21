$ curl -s http://localhost:8000/api/health | jq
{
  "status": "ok",
  "stack": {
    "frontend": "Vue 3 + Nginx",
    "backend":  "FastAPI",
    "database": "PostgreSQL",
    "cache":    "Redis"
  },
  "redis": "ok"
}

$ curl -s -o /dev/null -w 'http %{http_code}  rt %{time_total}s\n' http://localhost:8000/api/health
http 200  rt 0.027s
