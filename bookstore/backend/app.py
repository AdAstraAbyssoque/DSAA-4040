import json
import os
import time
from datetime import datetime, timezone
from typing import Generator

import redis
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, func, or_, text
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "bookstore")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "bookstore123")
DB_NAME = os.environ.get("DB_NAME", "bookstore")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
CACHE_TTL_SECONDS = 30

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

app = FastAPI(title="Cloud Bookstore API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
request_counts: dict[str, int] = {}


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(String(50), nullable=False, default="General")
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "description": self.description,
            "cover_url": self.cover_url,
        }


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    book = relationship("Book")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "book_id": self.book_id,
            "quantity": self.quantity,
            "book": self.book.to_dict() if self.book else None,
        }


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    book = relationship("Book")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "book_id": self.book_id,
            "quantity": self.quantity,
            "price": self.price,
            "book_title": self.book.title if self.book else None,
        }


class CartPayload(BaseModel):
    session_id: str = "default"
    book_id: int
    quantity: int = Field(default=1, ge=1)


class QuantityPayload(BaseModel):
    quantity: int


class OrderPayload(BaseModel):
    session_id: str = "default"


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    path = request.url.path
    request_counts[path] = request_counts.get(path, 0) + 1
    return await call_next(request)


def seed_books(db: Session) -> None:
    if db.query(func.count(Book.id)).scalar() > 0:
        return
    books = [
        Book(title="Cloud Computing: Concepts, Technology & Architecture", author="Thomas Erl", price=59.99, stock=15, category="Cloud Computing", description="A comprehensive guide to cloud computing concepts and architecture patterns.", cover_url="https://placehold.co/200x280/3498db/fff?text=Cloud+Computing"),
        Book(title="Designing Data-Intensive Applications", author="Martin Kleppmann", price=45.99, stock=20, category="Big Data", description="The big ideas behind reliable, scalable, and maintainable systems.", cover_url="https://placehold.co/200x280/e74c3c/fff?text=DDIA"),
        Book(title="Kubernetes in Action", author="Marko Luksa", price=49.99, stock=12, category="DevOps", description="Learn how to use Kubernetes to deploy container-based distributed applications.", cover_url="https://placehold.co/200x280/2ecc71/fff?text=K8s+in+Action"),
        Book(title="Docker Deep Dive", author="Nigel Poulton", price=35.99, stock=18, category="DevOps", description="Zero to Docker in a single book. Covers containers, images, networking and more.", cover_url="https://placehold.co/200x280/9b59b6/fff?text=Docker+Deep+Dive"),
        Book(title="Site Reliability Engineering", author="Betsy Beyer et al.", price=55.99, stock=10, category="Cloud Computing", description="How Google runs production systems. The SRE bible.", cover_url="https://placehold.co/200x280/f39c12/fff?text=SRE"),
        Book(title="Spark: The Definitive Guide", author="Bill Chambers & Matei Zaharia", price=42.99, stock=14, category="Big Data", description="Big data processing made simple with Apache Spark.", cover_url="https://placehold.co/200x280/e67e22/fff?text=Spark+Guide"),
        Book(title="The Phoenix Project", author="Gene Kim", price=29.99, stock=25, category="DevOps", description="A novel about IT, DevOps, and helping your business win.", cover_url="https://placehold.co/200x280/1abc9c/fff?text=Phoenix+Project"),
        Book(title="Database Internals", author="Alex Petrov", price=48.99, stock=8, category="Database", description="A deep dive into how distributed data systems work.", cover_url="https://placehold.co/200x280/34495e/fff?text=DB+Internals"),
        Book(title="Microservices Patterns", author="Chris Richardson", price=44.99, stock=16, category="Cloud Computing", description="With examples in Java. Patterns for developing microservices-based applications.", cover_url="https://placehold.co/200x280/8e44ad/fff?text=Microservices"),
        Book(title="Learning Spark, 2nd Edition", author="Jules Damji et al.", price=39.99, stock=11, category="Big Data", description="Lightning-fast data analytics with Apache Spark.", cover_url="https://placehold.co/200x280/c0392b/fff?text=Learning+Spark"),
        Book(title="Python for Data Analysis", author="Wes McKinney", price=37.99, stock=22, category="Big Data", description="Data wrangling with pandas, NumPy, and Jupyter.", cover_url="https://placehold.co/200x280/27ae60/fff?text=Python+Data"),
        Book(title="Clean Architecture", author="Robert C. Martin", price=34.99, stock=19, category="Software Engineering", description="A craftsman's guide to software structure and design.", cover_url="https://placehold.co/200x280/2980b9/fff?text=Clean+Arch"),
    ]
    db.add_all(books)
    db.commit()


def init_db() -> None:
    for attempt in range(1, 31):
        try:
            with engine.begin() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                seed_books(db)
            print("PostgreSQL initialized successfully.")
            return
        except Exception as exc:
            print(f"DB connection attempt {attempt}/30 failed: {exc}")
            time.sleep(2)
    raise RuntimeError("Failed to connect to PostgreSQL after retries")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


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
        "stack": {
            "frontend": "Vue 3 + Nginx",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "cache": "Redis",
        },
        "redis": "ok" if redis_ok else "degraded",
    }


@app.get("/metrics", response_class=Response)
def metrics():
    lines = [
        "# HELP bookstore_backend_info Static service metadata",
        "# TYPE bookstore_backend_info gauge",
        'bookstore_backend_info{framework="fastapi",database="postgresql",cache="redis"} 1',
        "# HELP bookstore_http_requests_total Requests observed by path",
        "# TYPE bookstore_http_requests_total counter",
    ]
    lines.extend(f'bookstore_http_requests_total{{path="{path}"}} {count}' for path, count in sorted(request_counts.items()))
    return Response("\n".join(lines) + "\n", media_type="text/plain")


@app.get("/api/books")
def list_books(q: str = "", category: str = "", db: Session = Depends(get_db)):
    cache_key = f"catalog:books:q={q}:category={category}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    query = db.query(Book)
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(or_(Book.title.ilike(term), Book.author.ilike(term)))
    if category.strip():
        query = query.filter(Book.category == category.strip())
    books = [book.to_dict() for book in query.order_by(Book.id).all()]
    cache_set(cache_key, books)
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.to_dict()


@app.get("/api/categories")
def list_categories(db: Session = Depends(get_db)):
    cache_key = "catalog:categories"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    categories = [row[0] for row in db.query(Book.category).distinct().order_by(Book.category).all()]
    cache_set(cache_key, categories)
    return categories


@app.get("/api/diagnostics/cpu")
def diagnostics_cpu(iterations: int = 2_000_000):
    """CPU-bound endpoint used only for HPA/autoscaling demonstrations."""
    bounded_iterations = min(max(iterations, 10_000), 8_000_000)
    started = time.perf_counter()
    checksum = 0
    for i in range(bounded_iterations):
        checksum = (checksum + (i * i)) % 1_000_000_007
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "purpose": "hpa-load-test",
        "iterations": bounded_iterations,
        "duration_ms": elapsed_ms,
        "checksum": checksum,
    }


@app.get("/api/cart")
def get_cart(session_id: str = "default", db: Session = Depends(get_db)):
    items = db.query(CartItem).filter(CartItem.session_id == session_id).order_by(CartItem.id).all()
    return [item.to_dict() for item in items]


@app.post("/api/cart", status_code=201)
def add_to_cart(payload: CartPayload, db: Session = Depends(get_db)):
    book = db.get(Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    existing = db.query(CartItem).filter(CartItem.session_id == payload.session_id, CartItem.book_id == payload.book_id).first()
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(CartItem(session_id=payload.session_id, book_id=payload.book_id, quantity=payload.quantity))
    db.commit()
    return {"message": "Added to cart"}


@app.put("/api/cart/{item_id}")
def update_cart_item(item_id: int, payload: QuantityPayload, db: Session = Depends(get_db)):
    item = db.get(CartItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if payload.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = payload.quantity
    db.commit()
    return {"message": "Cart updated"}


@app.delete("/api/cart/{item_id}")
def delete_cart_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CartItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed"}


@app.post("/api/orders", status_code=201)
def place_order(payload: OrderPayload, db: Session = Depends(get_db)):
    cart_items = db.query(CartItem).filter(CartItem.session_id == payload.session_id).order_by(CartItem.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = Order(session_id=payload.session_id, total_price=0, status="confirmed")
    db.add(order)
    db.flush()

    total = 0.0
    for cart_item in cart_items:
        book = cart_item.book
        if book.stock < cart_item.quantity:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{book.title}'")
        book.stock -= cart_item.quantity
        total += book.price * cart_item.quantity
        db.add(OrderItem(order_id=order.id, book_id=book.id, quantity=cart_item.quantity, price=book.price))

    order.total_price = round(total, 2)
    for cart_item in cart_items:
        db.delete(cart_item)
    db.commit()
    db.refresh(order)
    invalidate_catalog_cache()
    return order.to_dict()


@app.get("/api/orders")
def list_orders(session_id: str = "default", db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.session_id == session_id).order_by(Order.created_at.desc()).all()
    return [order.to_dict() for order in orders]
