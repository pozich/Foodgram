from sqlalchemy import (
        ForeignKey, Integer, BigInteger, Float, 
        String,
        Boolean, DateTime
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    role: Mapped[str] = mapped_column(String(16), default='customer')

class Bakery(Base):
    __tablename__ = 'bakers'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    
    price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    org_id: Mapped[int] = mapped_column(ForeignKey('bakers.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    status: Mapped[str] = mapped_column(String(16), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
