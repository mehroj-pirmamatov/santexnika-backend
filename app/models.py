from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.user)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    orders: List["Order"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    discount_price: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    wholesale_price: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    wholesale_min_qty: Optional[int] = None
    stock: int = 0
    image_url: Optional[str] = None

    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="products")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    customer_name: str
    phone: str
    address: Optional[str] = None
    payment_method: str = "cash"
    status: str = "yangi"
    total_price: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional["User"] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int
    price_at_order: Decimal = Field(sa_column=Column(Numeric(10, 2)))

    order: Optional[Order] = Relationship(back_populates="items")


