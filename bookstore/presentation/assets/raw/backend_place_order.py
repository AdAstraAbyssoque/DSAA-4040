@app.post("/api/orders", status_code=201)
def place_order(payload: OrderPayload, db: Session = Depends(get_db)):
    items = db.query(CartItem).filter_by(session_id=payload.session_id).all()
    if not items:
        raise HTTPException(400, "Cart is empty")

    order = Order(session_id=payload.session_id,
                   total_price=0, status="confirmed")
    db.add(order)
    db.flush()

    total = 0.0
    for ci in items:
        if ci.book.stock < ci.quantity:
            db.rollback()
            raise HTTPException(400, f"Insufficient stock: {ci.book.title!r}")
        ci.book.stock -= ci.quantity
        total         += ci.book.price * ci.quantity
        db.add(OrderItem(order_id=order.id, book_id=ci.book_id,
                          quantity=ci.quantity, price=ci.book.price))

    order.total_price = round(total, 2)
    for ci in items:
        db.delete(ci)
    db.commit()
    db.refresh(order)
    invalidate_catalog_cache()
    return order.to_dict()
