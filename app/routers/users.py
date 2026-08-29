from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, Order, RoleEnum
from app.schemas import UserWithStats, UserRead, AddAdminRequest, RoleUpdateRequest
from app.auth import require_role, get_current_user
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])
view_access = require_role("admin", "superadmin")
superadmin_only = require_role("superadmin")


@router.get("/me", response_model=UserRead, summary="Joriy foydalanuvchi profilini olish")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserWithStats], dependencies=[Depends(view_access)], summary="Barcha foydalanuvchilar ro'yxati (Statistika bilan)")
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    result = []
    for u in users:
        orders = session.exec(select(Order).where(Order.user_id == u.id)).all()
        result.append(UserWithStats(
            id=u.id,
            phone_number=u.phone_number,
            username=u.username,
            role=u.role,
            created_at=u.created_at,
            order_count=len(orders),
            last_order_at=max((o.created_at for o in orders), default=None),
        ))
    return result


@router.post("/add-admin", response_model=UserRead, dependencies=[Depends(superadmin_only)], summary="Yangi admin foydalanuvchi yaratish (superadmin uchun)")
def add_admin(data: AddAdminRequest, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where((User.phone_number == data.phone_number) | (User.username == data.username))
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu telefon raqam yoki username allaqachon band")

    new_admin = User(
        phone_number=data.phone_number,
        username=data.username,
        hashed_password=hash_password(data.password),
        role=RoleEnum.admin,
        is_active=True
    )
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)
    return new_admin


@router.patch("/{user_id}/role", response_model=UserRead, dependencies=[Depends(superadmin_only)], summary="Mavjud foydalanuvchi rolini o'zgartirish (superadmin uchun)")
def update_user_role(
    user_id: int,
    data: RoleUpdateRequest,
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if user.role == RoleEnum.superadmin:
        raise HTTPException(status_code=400, detail="Superadmin rolini o'zgartirib bo'lmaydi")
    user.role = data.role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
