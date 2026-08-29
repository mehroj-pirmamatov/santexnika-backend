from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Category, Product
from app.schemas import CategoryCreate, CategoryRead
from app.auth import require_role

router = APIRouter(prefix="/categories", tags=["Categories"])
admin_only = require_role("admin", "superadmin")


@router.get("/", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


@router.post("/", response_model=CategoryRead, dependencies=[Depends(admin_only)])
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    category = Category(name=data.name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return category


@router.delete("/{category_id}", dependencies=[Depends(admin_only)])
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    has_products = session.exec(select(Product).where(Product.category_id == category_id)).first()
    if has_products:
        raise HTTPException(status_code=400, detail="Bu kategoriyada mahsulotlar bor — avval ularni boshqa kategoriyaga o'tkazing yoki o'chiring")
    session.delete(category)
    session.commit()
    return {"ok": True}