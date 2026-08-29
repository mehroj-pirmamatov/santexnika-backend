from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Order, OrderItem, Product, User
from app.schemas import OrderCreate, OrderRead, OrderStatusUpdate
from app.auth import require_role, get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])
admin_only = require_role("admin", "superadmin")


def calculate_item_price(product: Product, quantity: int) -> float:
    if product.wholesale_min_qty and product.wholesale_price and quantity >= product.wholesale_min_qty:
        return product.wholesale_price
    if product.discount_price:
        return product.discount_price
    return product.price


@router.post("/", response_model=OrderRead)
def create_order(
    data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = Order(
        user_id=current_user.id,
        customer_name=current_user.username,
        phone=current_user.phone_number,
        address=data.address,
        payment_method=data.payment_method,
    )

    total = 0.0
    order_items = []
    for item in data.items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Mahsulot topilmadi (id={item.product_id})")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"'{product.name}' mahsulotidan omborda yetarli emas (bor: {product.stock})")

        unit_price = calculate_item_price(product, item.quantity)
        total += unit_price * item.quantity
        product.stock -= item.quantity
        session.add(product)
        order_items.append(OrderItem(product_id=product.id, quantity=item.quantity, price_at_order=unit_price))

    order.total_price = total
    order.items = order_items
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get("/me", response_model=list[OrderRead])
def my_orders(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Order).where(Order.user_id == current_user.id)).all()


@router.get("/", response_model=list[OrderRead], dependencies=[Depends(admin_only)])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order)).all()


@router.get("/{order_id}", response_model=OrderRead, dependencies=[Depends(admin_only)])
def get_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return order


@router.put("/{order_id}/status", response_model=OrderRead, dependencies=[Depends(admin_only)])
def update_order_status(order_id: int, data: OrderStatusUpdate, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    order.status = data.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order