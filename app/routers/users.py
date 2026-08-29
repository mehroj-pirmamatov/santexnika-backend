from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, Order, RoleEnum
from app.schemas import UserWithStats, UserRead
from app.auth import require_role, get_current_user
from typing import Optional
from datetime import datetime
from app.schemas import UserWithStats, UserRead, AddAdminRequest
router = APIRouter(prefix="/users", tags=["Users"])
view_access = require_role("admin", "superadmin")
superadmin_only = require_role("superadmin")


@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserWithStats], dependencies=[Depends(view_access)])
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


from app.schemas import UserWithStats, UserRead, AddAdminRequest


@router.post("/add-admin", response_model=UserRead, dependencies=[Depends(superadmin_only)])
def add_admin(data: AddAdminRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.phone_number == data.phone_number)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Bu telefon raqamli foydalanuvchi topilmadi")
    if user.role == RoleEnum.superadmin:
        raise HTTPException(status_code=400, detail="Superadmin rolini o'zgartirib bo'lmaydi")
    user.role = RoleEnum.admin
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


