$ docker compose exec postgres \
    psql -U bookstore -d bookstore \
    -c 'SELECT id, title, price, stock FROM books ORDER BY id LIMIT 6;'

 id |                     title                       |  price | stock
----+-------------------------------------------------+--------+-------
  1 | Cloud Computing: Concepts, Tech & Architecture  |  59.99 |    14
  2 | Designing Data-Intensive Applications           |  45.99 |    19
  3 | Kubernetes in Action                            |  49.99 |     8
  4 | Docker Deep Dive                                |  35.99 |    17
  5 | Site Reliability Engineering                    |  55.99 |    10
  6 | Spark: The Definitive Guide                     |  42.99 |    10
