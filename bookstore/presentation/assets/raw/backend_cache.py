CACHE_TTL_SECONDS = 30
redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
)


def cache_get(key: str):
    try:
        raw = redis_client.get(key)
        return json.loads(raw) if raw else None
    except redis.RedisError:
        return None


def cache_set(key: str, value) -> None:
    try:
        redis_client.setex(key, CACHE_TTL_SECONDS, json.dumps(value))
    except redis.RedisError:
        pass


def invalidate_catalog_cache() -> None:
    try:
        for key in redis_client.scan_iter("catalog:*"):
            redis_client.delete(key)
    except redis.RedisError:
        pass


@app.middleware("http")
async def collect_request_metrics(request: Request, call_next):
    request_counts[request.url.path] = (
        request_counts.get(request.url.path, 0) + 1
    )
    return await call_next(request)
