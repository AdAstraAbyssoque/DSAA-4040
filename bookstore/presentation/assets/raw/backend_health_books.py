@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    redis_ok = True
    try:
        redis_client.ping()
    except redis.RedisError:
        redis_ok = False
    return {
        "status": "ok",
        "stack": {"frontend": "Vue 3 + Nginx", "backend": "FastAPI",
                   "database": "PostgreSQL",   "cache": "Redis"},
        "redis":  "ok" if redis_ok else "degraded",
    }


@app.get("/api/books")
def list_books(q: str = "", category: str = "",
                db: Session = Depends(get_db)):
    cache_key = f"catalog:books:q={q}:category={category}"
    if (cached := cache_get(cache_key)) is not None:
        return cached
    query = db.query(Book)
    if q.strip():
        query = query.filter(or_(Book.title.ilike(f"%{q}%"),
                                  Book.author.ilike(f"%{q}%")))
    if category.strip():
        query = query.filter(Book.category == category)
    books = [b.to_dict() for b in query.order_by(Book.id).all()]
    cache_set(cache_key, books)
    return books
