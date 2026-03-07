# api/app/models.py
from sqlalchemy import (
        ForeignKey, Integer, BigInteger, Float, 
        String, DateTime, Boolean, func
        )
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from typing import Optional, List

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Tier(Base):
    __tablename__ = 'tiers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16))
    commission: Mapped[float] = mapped_column(Float)
    bakery_limit: Mapped[int] = mapped_column(Integer)
    staff_limit: Mapped[int] = mapped_column(Integer)

    owners: Mapped[List["OwnerProfile"]] = relationship(back_populates="tier")

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    role: Mapped[str] = mapped_column(String(16), default='client')

class OwnerProfile(Base):
    __tablename__ = 'owner_profiles'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tier_id: Mapped[int] = mapped_column(ForeignKey('tiers.id'), default=1)
    is_manual_tier: Mapped[bool] = mapped_column(Boolean, default=False) 
    revenue_last_month: Mapped[int] = mapped_column(Integer, default=0)

    tier: Mapped["Tier"] = relationship(back_populates="owners")
    bakeries: Mapped[List["Bakery"]] = relationship(back_populates="owner")
    staff_list: Mapped[List["Staff"]] = relationship(back_populates="owner")

class Bakery(Base):
    __tablename__ = 'bakers'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(1024))
    owner_id: Mapped[int] = mapped_column(ForeignKey('owner_profiles.id', ondelete='CASCADE'))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    owner: Mapped["OwnerProfile"] = relationship(back_populates="bakeries")
    products: Mapped[List["Product"]] = relationship(back_populates="bakery")

class Staff(Base):
    __tablename__ = 'staff'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    owner_id: Mapped[int] = mapped_column(ForeignKey('owner_profiles.id', ondelete='CASCADE'))
    bakery_id: Mapped[Optional[int]] = mapped_column(ForeignKey('bakers.id', ondelete='SET NULL'))

    owner: Mapped["OwnerProfile"] = relationship(back_populates="staff_list")
    user: Mapped["User"] = relationship()
    bakery: Mapped[Optional["Bakery"]] = relationship()

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(String(255)) # Описание не помешает
    
    old_price: Mapped[int] = mapped_column(Integer) # Цена до скидки
    price: Mapped[int] = mapped_column(Integer)     # Цена в приложении
    
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    bakery_id: Mapped[int] = mapped_column(ForeignKey('bakers.id', ondelete='CASCADE'))
    
    # Чтобы еда не висела в приложении вечно
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    available_until: Mapped[datetime] = mapped_column(DateTime) 
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    bakery: Mapped["Bakery"] = relationship(back_populates="products")

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    bakery_id: Mapped[int] = mapped_column(ForeignKey('bakers.id'))
    
    quantity: Mapped[int] = mapped_column(Integer, default=1) # Сколько штук купили
    total_price: Mapped[int] = mapped_column(Integer)
    
    # Статус: pending, confirmed, cancelled, completed
    status: Mapped[str] = mapped_column(String(16), default='pending')
    
    # Секретный код для получения заказа (чтобы юзер не забрал еду просто так)
    pickup_code: Mapped[str] = mapped_column(String(8)) 
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
