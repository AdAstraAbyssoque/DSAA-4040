$ curl -s http://localhost:8000/metrics
# HELP bookstore_backend_info Static service metadata
# TYPE bookstore_backend_info gauge
bookstore_backend_info{framework="fastapi",database="postgresql",cache="redis"} 1

# HELP bookstore_http_requests_total Requests observed by path
# TYPE bookstore_http_requests_total counter
bookstore_http_requests_total{path="/api/health"}    14
bookstore_http_requests_total{path="/api/books"}     14
bookstore_http_requests_total{path="/api/cart"}      50
bookstore_http_requests_total{path="/api/orders"}    12
bookstore_http_requests_total{path="/api/categories"} 7
bookstore_http_requests_total{path="/metrics"}        2
