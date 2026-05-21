$ docker compose exec redis redis-cli keys 'catalog:*'
catalog:books:q=:category=
catalog:categories
catalog:books:q=:category=DevOps

$ for k in $(redis-cli keys 'catalog:*'); do
>   echo "$k  TTL=$(redis-cli ttl $k)s  TYPE=$(redis-cli type $k)"
> done
catalog:books:q=:category=         TTL=19s  TYPE=string
catalog:categories                 TTL=19s  TYPE=string
catalog:books:q=:category=DevOps   TTL=19s  TYPE=string

$ redis-cli del 'catalog:books:q=Spark:category='   # force a cold read
1

$ python3 bench.py 'http://localhost:8000/api/books?q=Spark'
miss      24.7 ms   bytes=538
hit        2.2 ms   bytes=538
hit        1.5 ms   bytes=538
