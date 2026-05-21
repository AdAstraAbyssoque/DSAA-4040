$ SID=demo_$(date +%s)
$ curl -sX POST http://localhost:8000/api/cart -d "{\"session_id\":\"$SID\",\"book_id\":3,\"quantity\":1}"
{"message":"Added to cart"}
$ curl -sX POST http://localhost:8000/api/cart -d "{\"session_id\":\"$SID\",\"book_id\":6,\"quantity\":1}"
{"message":"Added to cart"}

$ curl -sX POST http://localhost:8000/api/orders -d "{\"session_id\":\"$SID\"}" | jq
{
  "id": 5, "session_id": "demo_1778087604",
  "total_price": 92.98, "status": "confirmed",
  "items": [
    {"book_title": "Kubernetes in Action",        "quantity": 1, "price": 49.99},
    {"book_title": "Spark: The Definitive Guide", "quantity": 1, "price": 42.99}
  ]
}
