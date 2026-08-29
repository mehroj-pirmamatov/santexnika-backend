from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.database import get_session
from app.models import User
from app.schemas import RoleUpdateRequest, UserRead, MyRole
from app.security import decode_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Token yaroqsiz yoki muddati o'tgan")

    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="Foydalanuvchi topilmadi")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Hisobingiz bloklangan")
    return user


def require_role(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Sizda bu amal uchun ruxsat yo'q")
        return user
    return dependency


router = APIRouter(prefix="/users", tags=["Users"])
superadmin_only = require_role("superadmin")


@router.patch("/{user_id}/role", response_model=UserRead, dependencies=[Depends(superadmin_only)])
def update_user_role(
    user_id: int,
    data: RoleUpdateRequest,
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.role = data.role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# @router.get('/{user_id}', response_model=MyRole)
# def getUuser():
    