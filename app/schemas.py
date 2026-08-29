from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models import RoleEnum


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    phone_number: str = Field(..., min_length=9, max_length=20)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)


class LoginRequest(BaseModel):
    phone_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone_number: str
    username: str
    role: RoleEnum
    is_active: bool
    created_at: datetime


class RoleUpdateRequest(BaseModel):
    role: RoleEnum


# ---------- Category ----------

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# ---------- Product ----------

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    discount_price: Optional[Decimal] = Field(None, gt=0)
    wholesale_price: Optional[Decimal] = Field(None, gt=0)
    wholesale_min_qty: Optional[int] = Field(None, gt=0)
    stock: int = Field(0, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[int] = None

    @field_validator("discount_price")
    @classmethod
    def discount_below_price(cls, v, info):
        price = info.data.get("price")
        if v is not None and price is not None and v >= price:
            raise ValueError("Chegirma narxi asosiy narxdan kichik bo'lishi kerak")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    discount_price: Optional[Decimal] = Field(None, gt=0)
    wholesale_price: Optional[Decimal] = Field(None, gt=0)
    wholesale_min_qty: Optional[int] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[int] = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    discount_price: Optional[Decimal]
    wholesale_price: Optional[Decimal]
    wholesale_min_qty: Optional[int]
    stock: int
    image_url: Optional[str]
    category_id: Optional[int]


# ---------- Order ----------

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    address: Optional[str] = None
    payment_method: str = Field("cash", pattern="^(cash|payme|click)$")
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("Savatcha bo'sh bo'lishi mumkin emas")
        return v


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantity: int
    price_at_order: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    customer_name: str
    phone: str
    address: Optional[str]
    payment_method: str
    status: str
    total_price: Decimal
    created_at: datetime
    items: List[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(yangi|tayyorlanmoqda|yolda|yetkazildi|bekor_qilindi)$")




class MyRole(BaseModel):
    customer_name: str
    id: int



class UserWithStats(BaseModel):
    id: int
    phone_number: str
    username: str
    role: RoleEnum
    created_at: datetime
    order_count: int
    last_order_at: Optional[datetime] = None



class AddAdminRequest(BaseModel):
    phone_number: str