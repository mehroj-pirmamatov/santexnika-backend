from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Product, OrderItem
from app.schemas import ProductCreate, ProductUpdate, ProductRead
from app.auth import require_role

router = APIRouter(prefix="/products", tags=["Products"])
admin_only = require_role("admin", "superadmin")


@router.get("/", response_model=List[ProductRead])
def list_products(
    category_id: Optional[int] = None,
    in_stock: Optional[bool] = None,
    session: Session = Depends(get_session),
):
    query = select(Product)
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    if in_stock:
        query = query.where(Product.stock > 0)
    return session.exec(query).all()


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return product


@router.post("/", response_model=ProductRead, dependencies=[Depends(admin_only)])
def create_product(data: ProductCreate, session: Session = Depends(get_session)):
    product = Product(**data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead, dependencies=[Depends(admin_only)])
def update_product(product_id: int, data: ProductUpdate, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(product, key, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", dependencies=[Depends(admin_only)])
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    has_orders = session.exec(
        select(OrderItem).where(OrderItem.product_id == product_id)
    ).first()
    if has_orders:
        raise HTTPException(
            status_code=400,
            detail="Bu mahsulot buyurtmalarda ishlatilgan, o'chirib bo'lmaydi",
        )

    session.delete(product)
    session.commit()
    return {"ok": True}